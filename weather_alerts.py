#!/usr/bin/env python3
"""
Exercice 4 - Transformation des données et détection d'alertes
Traite le flux weather_stream en temps réel avec Spark et produit weather_transformed
"""

import json
import sys
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.streaming import *

class WeatherAlertProcessor:
    def __init__(self, kafka_servers='localhost:9092', 
                 input_topic='weather_stream', 
                 output_topic='weather_transformed',
                 checkpoint_location='checkpoint/weather_alerts'):
        
        self.kafka_servers = kafka_servers
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.checkpoint_location = checkpoint_location
        
        # Initialiser Spark
        self.spark = self._create_spark_session()
        
        # Schema pour les données météo
        self.weather_schema = self._create_weather_schema()
    
    def _create_spark_session(self):
        """Créer la session Spark avec les configurations Kafka"""
        return SparkSession.builder \
            .appName("WeatherAlertProcessor") \
            .config("spark.sql.streaming.checkpointLocation", self.checkpoint_location) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
    
    def _create_weather_schema(self):
        """Définir le schéma des données météo"""
        return StructType([
            StructField("timestamp", StringType(), True),
            StructField("api_timestamp", StringType(), True),
            StructField("location", StructType([
                StructField("latitude", DoubleType(), True),
                StructField("longitude", DoubleType(), True),
                StructField("timezone", StringType(), True),
                StructField("timezone_abbreviation", StringType(), True),
                StructField("elevation", DoubleType(), True)
            ]), True),
            StructField("current_weather", StructType([
                StructField("temperature", DoubleType(), True),
                StructField("temperature_unit", StringType(), True),
                StructField("apparent_temperature", DoubleType(), True),
                StructField("humidity", DoubleType(), True),
                StructField("humidity_unit", StringType(), True),
                StructField("precipitation", DoubleType(), True),
                StructField("precipitation_unit", StringType(), True),
                StructField("rain", DoubleType(), True),
                StructField("showers", DoubleType(), True),
                StructField("snowfall", DoubleType(), True),
                StructField("weather_code", IntegerType(), True),
                StructField("cloud_cover", DoubleType(), True),
                StructField("cloud_cover_unit", StringType(), True),
                StructField("pressure_msl", DoubleType(), True),
                StructField("pressure_unit", StringType(), True),
                StructField("wind_speed", DoubleType(), True),
                StructField("wind_speed_unit", StringType(), True),
                StructField("wind_direction", DoubleType(), True),
                StructField("wind_direction_unit", StringType(), True),
                StructField("wind_gusts", DoubleType(), True),
                StructField("is_day", BooleanType(), True)
            ]), True),
            StructField("producer_info", StructType([
                StructField("source", StringType(), True),
                StructField("producer_id", StringType(), True),
                StructField("version", StringType(), True)
            ]), True)
        ])
    
    def _convert_wind_speed_to_ms(self, wind_speed_kmh):
        """Convertir la vitesse du vent de km/h en m/s"""
        return when(wind_speed_kmh.isNotNull(), wind_speed_kmh / 3.6).otherwise(None)
    
    def _calculate_wind_alert_level(self, wind_speed_ms):
        """Calculer le niveau d'alerte vent (en m/s)"""
        return when(wind_speed_ms.isNull(), "unknown") \
               .when(wind_speed_ms < 10, "level_0") \
               .when((wind_speed_ms >= 10) & (wind_speed_ms < 20), "level_1") \
               .when(wind_speed_ms >= 20, "level_2") \
               .otherwise("unknown")
    
    def _calculate_heat_alert_level(self, temperature):
        """Calculer le niveau d'alerte chaleur (en °C)"""
        return when(temperature.isNull(), "unknown") \
               .when(temperature < 25, "level_0") \
               .when((temperature >= 25) & (temperature < 35), "level_1") \
               .when(temperature >= 35, "level_2") \
               .otherwise("unknown")
    
    def _transform_weather_data(self, df):
        """Transformer les données météo et ajouter les alertes"""
        
        # Extraire les champs principaux
        transformed_df = df.select(
            col("timestamp").alias("original_timestamp"),
            current_timestamp().alias("event_time"),
            col("location.latitude").alias("latitude"),
            col("location.longitude").alias("longitude"),
            col("location.timezone").alias("timezone"),
            col("current_weather.temperature").alias("temperature"),
            col("current_weather.apparent_temperature").alias("apparent_temperature"),
            col("current_weather.humidity").alias("humidity"),
            col("current_weather.precipitation").alias("precipitation"),
            col("current_weather.weather_code").alias("weather_code"),
            col("current_weather.cloud_cover").alias("cloud_cover"),
            col("current_weather.pressure_msl").alias("pressure"),
            col("current_weather.wind_speed").alias("wind_speed_kmh"),
            col("current_weather.wind_direction").alias("wind_direction"),
            col("current_weather.wind_gusts").alias("wind_gusts"),
            col("current_weather.is_day").alias("is_day"),
            col("producer_info.source").alias("data_source")
        )
        
        # Convertir la vitesse du vent en m/s
        transformed_df = transformed_df.withColumn(
            "windspeed", 
            self._convert_wind_speed_to_ms(col("wind_speed_kmh"))
        )
        
        # Calculer les niveaux d'alerte
        transformed_df = transformed_df.withColumn(
            "wind_alert_level",
            self._calculate_wind_alert_level(col("windspeed"))
        ).withColumn(
            "heat_alert_level", 
            self._calculate_heat_alert_level(col("temperature"))
        )
        
        # Ajouter des métriques dérivées
        transformed_df = transformed_df.withColumn(
            "alert_count",
            when((col("wind_alert_level") != "level_0") | 
                 (col("heat_alert_level") != "level_0"), 1).otherwise(0)
        ).withColumn(
            "high_alert",
            when((col("wind_alert_level") == "level_2") | 
                 (col("heat_alert_level") == "level_2"), True).otherwise(False)
        ).withColumn(
            "location_key",
            concat(col("latitude"), lit(","), col("longitude"))
        )
        
        # Sélectionner les colonnes finales dans l'ordre souhaité
        final_df = transformed_df.select(
            "event_time",
            "original_timestamp", 
            "latitude",
            "longitude",
            "location_key",
            "timezone",
            "temperature",
            "apparent_temperature",
            "windspeed",
            "wind_speed_kmh", 
            "wind_direction",
            "wind_gusts",
            "wind_alert_level",
            "heat_alert_level",
            "alert_count",
            "high_alert",
            "humidity",
            "precipitation",
            "weather_code",
            "cloud_cover", 
            "pressure",
            "is_day",
            "data_source"
        )
        
        return final_df
    
    def _format_output_message(self, df):
        """Formater les données pour la sortie Kafka"""
        
        # Créer la structure JSON de sortie
        output_df = df.select(
            col("location_key").alias("key"),
            to_json(struct(
                col("event_time"),
                col("original_timestamp"),
                struct(
                    col("latitude"),
                    col("longitude"),
                    col("timezone")
                ).alias("location"),
                struct(
                    col("temperature"),
                    col("apparent_temperature"), 
                    col("windspeed"),
                    col("wind_speed_kmh"),
                    col("wind_direction"),
                    col("wind_gusts"),
                    col("humidity"),
                    col("precipitation"),
                    col("weather_code"),
                    col("cloud_cover"),
                    col("pressure"),
                    col("is_day")
                ).alias("weather_data"),
                struct(
                    col("wind_alert_level"),
                    col("heat_alert_level"),
                    col("alert_count"),
                    col("high_alert")
                ).alias("alerts"),
                struct(
                    col("data_source"),
                    lit("spark_weather_processor").alias("processor"),
                    lit("1.0").alias("version")
                ).alias("processing_info")
            )).alias("value")
        )
        
        return output_df
    
    def start_processing(self, output_mode="append", trigger_interval="10 seconds"):
        """Démarrer le traitement en streaming"""
        
        print("🚀 Démarrage du processeur d'alertes météo Spark")
        print(f"📥 Topic d'entrée: {self.input_topic}")
        print(f"📤 Topic de sortie: {self.output_topic}")
        print(f"🔄 Mode de sortie: {output_mode}")
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
                col("topic"),
                col("partition"), 
                col("offset"),
                col("timestamp").alias("kafka_timestamp")
            )
            
            # Parser le JSON avec le schéma
            parsed_stream = decoded_stream.select(
                "*",
                from_json(col("json_data"), self.weather_schema).alias("weather")
            ).select("kafka_key", "weather.*", "topic", "partition", "offset", "kafka_timestamp")
            
            # Filtrer les messages valides
            valid_stream = parsed_stream.filter(col("weather").isNotNull())
            
            # Transformer les données et calculer les alertes
            transformed_stream = self._transform_weather_data(valid_stream)
            
            # Formater pour la sortie Kafka
            output_stream = self._format_output_message(transformed_stream)
            
            # Écrire vers le topic de sortie Kafka
            query = output_stream \
                .writeStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_servers) \
                .option("topic", self.output_topic) \
                .option("checkpointLocation", self.checkpoint_location) \
                .outputMode(output_mode) \
                .trigger(processingTime=trigger_interval) \
                .start()
            
            print("✅ Streaming démarré avec succès!")
            print("📊 Monitoring des alertes en cours...")
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
            print("✅ Processeur arrêté proprement")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Exercice 4 - Processeur d'alertes météo Spark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python weather_alerts.py
  python weather_alerts.py --input-topic weather_stream --output-topic alerts
  python weather_alerts.py --trigger-interval "5 seconds"
  python weather_alerts.py --output-mode update --checkpoint custom_checkpoint
        """
    )
    
    parser.add_argument('--kafka-servers', 
                       default='localhost:9092',
                       help='Serveurs Kafka (défaut: localhost:9092)')
    parser.add_argument('--input-topic', 
                       default='weather_stream',
                       help='Topic d\'entrée (défaut: weather_stream)')
    parser.add_argument('--output-topic', 
                       default='weather_transformed',
                       help='Topic de sortie (défaut: weather_transformed)')
    parser.add_argument('--checkpoint-location', 
                       default='checkpoint/weather_alerts',
                       help='Répertoire de checkpoint (défaut: checkpoint/weather_alerts)')
    parser.add_argument('--output-mode', 
                       default='append',
                       choices=['append', 'update', 'complete'],
                       help='Mode de sortie (défaut: append)')
    parser.add_argument('--trigger-interval', 
                       default='10 seconds',
                       help='Intervalle de trigger (défaut: 10 seconds)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("⚡ EXERCICE 4 - TRANSFORMATION SPARK ET ALERTES MÉTÉO")
    print("="*70)
    
    # Créer et démarrer le processeur
    processor = WeatherAlertProcessor(
        kafka_servers=args.kafka_servers,
        input_topic=args.input_topic,
        output_topic=args.output_topic,
        checkpoint_location=args.checkpoint_location
    )
    
    processor.start_processing(
        output_mode=args.output_mode,
        trigger_interval=args.trigger_interval
    )

if __name__ == "__main__":
    main()