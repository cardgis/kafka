#!/usr/bin/env python3
"""
Exercice 5 - Agrégats en temps réel avec Spark
Calcule des agrégats sur des fenêtres glissantes à partir du flux weather_transformed
"""

import json
import sys
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.streaming import *

class WeatherAggregatesProcessor:
    def __init__(self, kafka_servers='localhost:9092', 
                 input_topic='weather_transformed', 
                 output_topic='weather_aggregates',
                 checkpoint_location='checkpoint/weather_aggregates'):
        
        self.kafka_servers = kafka_servers
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.checkpoint_location = checkpoint_location
        
        # Initialiser Spark
        self.spark = self._create_spark_session()
        
        # Schema pour les données transformées
        self.transformed_schema = self._create_transformed_schema()
    
    def _create_spark_session(self):
        """Créer la session Spark avec les configurations pour aggregates"""
        return SparkSession.builder \
            .appName("WeatherAggregatesProcessor") \
            .config("spark.sql.streaming.checkpointLocation", self.checkpoint_location) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.streaming.stateStore.providerClass", 
                   "org.apache.spark.sql.execution.streaming.state.HDFSBackedStateStoreProvider") \
            .getOrCreate()
    
    def _create_transformed_schema(self):
        """Définir le schéma des données weather_transformed"""
        return StructType([
            StructField("event_time", StringType(), True),
            StructField("original_timestamp", StringType(), True),
            StructField("location", StructType([
                StructField("latitude", DoubleType(), True),
                StructField("longitude", DoubleType(), True),
                StructField("timezone", StringType(), True)
            ]), True),
            StructField("weather_data", StructType([
                StructField("temperature", DoubleType(), True),
                StructField("apparent_temperature", DoubleType(), True),
                StructField("windspeed", DoubleType(), True),
                StructField("wind_speed_kmh", DoubleType(), True),
                StructField("wind_direction", DoubleType(), True),
                StructField("wind_gusts", DoubleType(), True),
                StructField("humidity", DoubleType(), True),
                StructField("precipitation", DoubleType(), True),
                StructField("weather_code", IntegerType(), True),
                StructField("cloud_cover", DoubleType(), True),
                StructField("pressure", DoubleType(), True),
                StructField("is_day", BooleanType(), True)
            ]), True),
            StructField("alerts", StructType([
                StructField("wind_alert_level", StringType(), True),
                StructField("heat_alert_level", StringType(), True),
                StructField("alert_count", IntegerType(), True),
                StructField("high_alert", BooleanType(), True)
            ]), True),
            StructField("processing_info", StructType([
                StructField("data_source", StringType(), True),
                StructField("processor", StringType(), True),
                StructField("version", StringType(), True)
            ]), True)
        ])
    
    def _calculate_sliding_window_aggregates(self, df, window_duration="5 minutes", slide_duration="1 minute"):
        """Calculer les agrégats sur fenêtres glissantes"""
        
        # Convertir event_time en timestamp
        df_with_timestamp = df.withColumn(
            "timestamp", 
            to_timestamp(col("event_time"))
        )
        
        # Agrégats par fenêtre temporelle
        windowed_aggregates = df_with_timestamp \
            .withWatermark("timestamp", "2 minutes") \
            .groupBy(
                window(col("timestamp"), window_duration, slide_duration),
                col("location.latitude").alias("latitude"),
                col("location.longitude").alias("longitude")
            ) \
            .agg(
                # Métriques de température
                avg("weather_data.temperature").alias("avg_temperature"),
                min("weather_data.temperature").alias("min_temperature"),
                max("weather_data.temperature").alias("max_temperature"),
                stddev("weather_data.temperature").alias("stddev_temperature"),
                
                # Métriques de vent
                avg("weather_data.windspeed").alias("avg_windspeed"),
                max("weather_data.windspeed").alias("max_windspeed"),
                avg("weather_data.wind_gusts").alias("avg_wind_gusts"),
                max("weather_data.wind_gusts").alias("max_wind_gusts"),
                
                # Comptages d'alertes par niveau
                sum(when(col("alerts.wind_alert_level") == "level_1", 1).otherwise(0)).alias("wind_level_1_count"),
                sum(when(col("alerts.wind_alert_level") == "level_2", 1).otherwise(0)).alias("wind_level_2_count"),
                sum(when(col("alerts.heat_alert_level") == "level_1", 1).otherwise(0)).alias("heat_level_1_count"),
                sum(when(col("alerts.heat_alert_level") == "level_2", 1).otherwise(0)).alias("heat_level_2_count"),
                
                # Alertes totales
                sum("alerts.alert_count").alias("total_alerts"),
                sum(when(col("alerts.high_alert") == True, 1).otherwise(0)).alias("high_alert_count"),
                
                # Autres métriques météo
                avg("weather_data.humidity").alias("avg_humidity"),
                avg("weather_data.pressure").alias("avg_pressure"),
                sum("weather_data.precipitation").alias("total_precipitation"),
                
                # Métadonnées
                count("*").alias("message_count"),
                collect_set("weather_data.weather_code").alias("weather_codes"),
                first("location.timezone").alias("timezone")
            )
        
        # Ajouter des métriques calculées
        enriched_aggregates = windowed_aggregates.withColumn(
            "temperature_range", 
            col("max_temperature") - col("min_temperature")
        ).withColumn(
            "wind_alert_percentage",
            (col("wind_level_1_count") + col("wind_level_2_count")) * 100.0 / col("message_count")
        ).withColumn(
            "heat_alert_percentage", 
            (col("heat_level_1_count") + col("heat_level_2_count")) * 100.0 / col("message_count")
        ).withColumn(
            "location_key",
            concat(col("latitude"), lit(","), col("longitude"))
        ).withColumn(
            "window_start",
            col("window.start")
        ).withColumn(
            "window_end", 
            col("window.end")
        )
        
        return enriched_aggregates
    
    def _calculate_regional_aggregates(self, df, window_duration="10 minutes"):
        """Calculer les agrégats par région (approximation par troncature des coordonnées)"""
        
        # Créer des "régions" en tronquant les coordonnées
        df_with_regions = df.withColumn(
            "region_lat", 
            (floor(col("location.latitude") * 10) / 10).cast("decimal(10,1)")
        ).withColumn(
            "region_lon",
            (floor(col("location.longitude") * 10) / 10).cast("decimal(10,1)")
        ).withColumn(
            "timestamp",
            to_timestamp(col("event_time"))
        )
        
        # Agrégats par région et fenêtre temporelle
        regional_aggregates = df_with_regions \
            .withWatermark("timestamp", "2 minutes") \
            .groupBy(
                window(col("timestamp"), window_duration),
                col("region_lat"),
                col("region_lon")
            ) \
            .agg(
                count("*").alias("location_count"),
                approx_count_distinct(concat(col("location.latitude"), lit(","), col("location.longitude"))).alias("unique_locations"),
                
                # Températures régionales
                avg("weather_data.temperature").alias("regional_avg_temp"),
                min("weather_data.temperature").alias("regional_min_temp"),
                max("weather_data.temperature").alias("regional_max_temp"),
                
                # Alertes régionales
                sum(when(col("alerts.wind_alert_level") == "level_2", 1).otherwise(0)).alias("regional_wind_critical"),
                sum(when(col("alerts.heat_alert_level") == "level_2", 1).otherwise(0)).alias("regional_heat_critical"),
                sum("alerts.alert_count").alias("regional_total_alerts"),
                
                # Codes météo dominants
                collect_list("weather_data.weather_code").alias("all_weather_codes"),
                
                # Métadonnées
                collect_set("location.timezone").alias("timezones")
            )
        
        # Enrichir avec des métriques calculées
        enriched_regional = regional_aggregates.withColumn(
            "regional_key",
            concat(col("region_lat"), lit(","), col("region_lon"))
        ).withColumn(
            "alert_density",
            col("regional_total_alerts").cast("double") / col("location_count")
        ).withColumn(
            "window_start",
            col("window.start")
        ).withColumn(
            "window_end",
            col("window.end")
        )
        
        return enriched_regional
    
    def _format_aggregates_output(self, windowed_df, regional_df):
        """Formater les agrégats pour la sortie Kafka"""
        
        # Format des agrégats par localisation
        windowed_output = windowed_df.select(
            col("location_key").alias("key"),
            to_json(struct(
                lit("location_aggregates").alias("type"),
                col("window_start"),
                col("window_end"),
                struct(
                    col("latitude"),
                    col("longitude"),
                    col("location_key"),
                    col("timezone")
                ).alias("location"),
                struct(
                    col("avg_temperature"),
                    col("min_temperature"), 
                    col("max_temperature"),
                    col("temperature_range"),
                    col("stddev_temperature")
                ).alias("temperature_metrics"),
                struct(
                    col("avg_windspeed"),
                    col("max_windspeed"),
                    col("avg_wind_gusts"),
                    col("max_wind_gusts")
                ).alias("wind_metrics"),
                struct(
                    col("wind_level_1_count"),
                    col("wind_level_2_count"),
                    col("heat_level_1_count"),
                    col("heat_level_2_count"),
                    col("total_alerts"),
                    col("high_alert_count"),
                    col("wind_alert_percentage"),
                    col("heat_alert_percentage")
                ).alias("alert_metrics"),
                struct(
                    col("avg_humidity"),
                    col("avg_pressure"),
                    col("total_precipitation")
                ).alias("weather_metrics"),
                struct(
                    col("message_count"),
                    col("weather_codes")
                ).alias("metadata"),
                struct(
                    lit("spark_aggregates_processor").alias("processor"),
                    current_timestamp().alias("processed_at"),
                    lit("1.0").alias("version")
                ).alias("processing_info")
            )).alias("value")
        )
        
        # Format des agrégats régionaux
        regional_output = regional_df.select(
            col("regional_key").alias("key"),
            to_json(struct(
                lit("regional_aggregates").alias("type"),
                col("window_start"),
                col("window_end"),
                struct(
                    col("region_lat").alias("latitude"),
                    col("region_lon").alias("longitude"),
                    col("regional_key"),
                    col("timezones")
                ).alias("region"),
                struct(
                    col("regional_avg_temp"),
                    col("regional_min_temp"),
                    col("regional_max_temp")
                ).alias("temperature_metrics"),
                struct(
                    col("regional_wind_critical"),
                    col("regional_heat_critical"),
                    col("regional_total_alerts"),
                    col("alert_density")
                ).alias("alert_metrics"),
                struct(
                    col("location_count"),
                    col("unique_locations"),
                    col("all_weather_codes")
                ).alias("metadata"),
                struct(
                    lit("spark_aggregates_processor").alias("processor"),
                    current_timestamp().alias("processed_at"),
                    lit("1.0").alias("version")
                ).alias("processing_info")
            )).alias("value")
        )
        
        return windowed_output, regional_output
    
    def start_processing(self, window_duration="5 minutes", slide_duration="1 minute", 
                        regional_window="10 minutes", output_mode="append", 
                        trigger_interval="30 seconds"):
        """Démarrer le traitement des agrégats en streaming"""
        
        print("🚀 Démarrage du processeur d'agrégats météo Spark")
        print(f"📥 Topic d'entrée: {self.input_topic}")
        print(f"📤 Topic de sortie: {self.output_topic}")
        print(f"🕐 Fenêtre glissante: {window_duration} (slide: {slide_duration})")
        print(f"🌍 Fenêtre régionale: {regional_window}")
        print(f"⏱️  Intervalle: {trigger_interval}")
        print()
        
        try:
            # Lecture du stream Kafka d'entrée
            input_stream = self.spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_servers) \
                .option("subscribe", self.input_topic) \
                .option("startingOffsets", "latest") \
                .option("failOnDataLoss", "false") \
                .load()
            
            # Décoder les messages JSON
            decoded_stream = input_stream.select(
                col("key").cast("string").alias("kafka_key"),
                col("value").cast("string").alias("json_data"),
                col("timestamp").alias("kafka_timestamp")
            )
            
            # Parser le JSON avec le schéma
            parsed_stream = decoded_stream.select(
                "*",
                from_json(col("json_data"), self.transformed_schema).alias("weather")
            ).select("kafka_key", "weather.*", "kafka_timestamp")
            
            # Filtrer les messages valides
            valid_stream = parsed_stream.filter(col("weather").isNotNull())
            
            # Calculer les agrégats par localisation
            windowed_aggregates = self._calculate_sliding_window_aggregates(
                valid_stream, window_duration, slide_duration
            )
            
            # Calculer les agrégats régionaux
            regional_aggregates = self._calculate_regional_aggregates(
                valid_stream, regional_window
            )
            
            # Formater pour la sortie Kafka
            windowed_output, regional_output = self._format_aggregates_output(
                windowed_aggregates, regional_aggregates
            )
            
            # Union des deux types d'agrégats
            combined_output = windowed_output.union(regional_output)
            
            # Écrire vers le topic de sortie Kafka
            query = combined_output \
                .writeStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_servers) \
                .option("topic", self.output_topic) \
                .option("checkpointLocation", self.checkpoint_location) \
                .outputMode(output_mode) \
                .trigger(processingTime=trigger_interval) \
                .start()
            
            print("✅ Streaming d'agrégats démarré avec succès!")
            print("📊 Calcul des métriques en cours...")
            print("🛑 Appuyez sur Ctrl+C pour arrêter")
            print()
            
            # Attendre la fin du streaming
            query.awaitTermination()
            
        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé par l'utilisateur")
        except Exception as e:
            print(f"\n❌ Erreur during le traitement: {e}")
            raise
        finally:
            print("🔄 Nettoyage des ressources...")
            if hasattr(self, 'spark'):
                self.spark.stop()
            print("✅ Processeur d'agrégats arrêté proprement")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Exercice 5 - Agrégats météo en temps réel avec Spark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python weather_aggregates.py
  python weather_aggregates.py --window "1 minute" --slide "30 seconds"
  python weather_aggregates.py --regional-window "15 minutes"
  python weather_aggregates.py --output-topic aggregates_live
        """
    )
    
    parser.add_argument('--kafka-servers', 
                       default='localhost:9092',
                       help='Serveurs Kafka (défaut: localhost:9092)')
    parser.add_argument('--input-topic', 
                       default='weather_transformed',
                       help='Topic d\'entrée (défaut: weather_transformed)')
    parser.add_argument('--output-topic', 
                       default='weather_aggregates',
                       help='Topic de sortie (défaut: weather_aggregates)')
    parser.add_argument('--checkpoint-location', 
                       default='checkpoint/weather_aggregates',
                       help='Répertoire de checkpoint (défaut: checkpoint/weather_aggregates)')
    parser.add_argument('--window', 
                       default='5 minutes',
                       help='Durée de fenêtre glissante (défaut: 5 minutes)')
    parser.add_argument('--slide', 
                       default='1 minute',
                       help='Intervalle de glissement (défaut: 1 minute)')
    parser.add_argument('--regional-window', 
                       default='10 minutes',
                       help='Fenêtre pour agrégats régionaux (défaut: 10 minutes)')
    parser.add_argument('--output-mode', 
                       default='append',
                       choices=['append', 'update', 'complete'],
                       help='Mode de sortie (défaut: append)')
    parser.add_argument('--trigger-interval', 
                       default='30 seconds',
                       help='Intervalle de trigger (défaut: 30 seconds)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("📊 EXERCICE 5 - AGRÉGATS MÉTÉO TEMPS RÉEL AVEC SPARK")
    print("="*70)
    
    # Créer et démarrer le processeur d'agrégats
    processor = WeatherAggregatesProcessor(
        kafka_servers=args.kafka_servers,
        input_topic=args.input_topic,
        output_topic=args.output_topic,
        checkpoint_location=args.checkpoint_location
    )
    
    processor.start_processing(
        window_duration=args.window,
        slide_duration=args.slide,
        regional_window=args.regional_window,
        output_mode=args.output_mode,
        trigger_interval=args.trigger_interval
    )

if __name__ == "__main__":
    main()