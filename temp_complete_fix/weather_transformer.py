#!/usr/bin/env python3
"""
Exercise 4: Weather Data Transformation and Alert Detection
Process weather_stream with Spark and create weather_transformed topic with alerts.

Usage: python weather_transformer.py
"""

import json
import sys
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

class WeatherTransformer:
    def __init__(self, kafka_servers='localhost:9092', input_topic='weather_stream', output_topic='weather_transformed'):
        self.kafka_servers = kafka_servers
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.spark = None
        self._init_spark()
    
    def _init_spark(self):
        """Initialize Spark session with Kafka support"""
        try:
            self.spark = SparkSession.builder \
                .appName("WeatherTransformer") \
                .config("spark.sql.adaptive.enabled", "true") \
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                .getOrCreate()
            
            # Set log level to reduce noise
            self.spark.sparkContext.setLogLevel("WARN")
            print("✅ Spark session initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Spark: {e}")
            sys.exit(1)
    
    def create_weather_schema(self):
        """Define schema for weather data"""
        return StructType([
            StructField("timestamp", StringType(), True),
            StructField("location", StructType([
                StructField("latitude", DoubleType(), True),
                StructField("longitude", DoubleType(), True),
                StructField("timezone", StringType(), True)
            ]), True),
            StructField("current_weather", StructType([
                StructField("temperature", DoubleType(), True),
                StructField("humidity", DoubleType(), True),
                StructField("apparent_temperature", DoubleType(), True),
                StructField("weather_code", IntegerType(), True),
                StructField("wind_speed", DoubleType(), True),
                StructField("wind_direction", DoubleType(), True),
                StructField("time", StringType(), True)
            ]), True)
        ])
    
    def calculate_wind_alert(self, wind_speed):
        """Calculate wind alert level based on wind speed"""
        return when(wind_speed < 10, "level_0") \
               .when((wind_speed >= 10) & (wind_speed < 20), "level_1") \
               .when(wind_speed >= 20, "level_2") \
               .otherwise("unknown")
    
    def calculate_heat_alert(self, temperature):
        """Calculate heat alert level based on temperature"""
        return when(temperature < 25, "level_0") \
               .when((temperature >= 25) & (temperature < 35), "level_1") \
               .when(temperature >= 35, "level_2") \
               .otherwise("unknown")
    
    def transform_weather_data(self, df):
        """Transform weather data and add alert levels"""
        try:
            # Parse JSON and extract fields
            weather_df = df.select(
                from_json(col("value").cast("string"), self.create_weather_schema()).alias("data")
            ).select("data.*")
            
            # Filter out non-weather messages (like test messages)
            weather_df = weather_df.filter(col("current_weather").isNotNull())
            
            # Extract and transform fields
            transformed_df = weather_df.select(
                # Event time (current timestamp)
                current_timestamp().alias("event_time"),
                
                # Original timestamp
                col("timestamp").alias("original_timestamp"),
                
                # Location data
                col("location.latitude").alias("latitude"),
                col("location.longitude").alias("longitude"),
                col("location.timezone").alias("timezone"),
                
                # Weather data
                col("current_weather.temperature").alias("temperature"),
                col("current_weather.wind_speed").alias("windspeed"),
                col("current_weather.humidity").alias("humidity"),
                col("current_weather.apparent_temperature").alias("apparent_temperature"),
                col("current_weather.weather_code").alias("weather_code"),
                col("current_weather.wind_direction").alias("wind_direction"),
                col("current_weather.time").alias("weather_time"),
                
                # Calculate alert levels
                self.calculate_wind_alert(col("current_weather.wind_speed")).alias("wind_alert_level"),
                self.calculate_heat_alert(col("current_weather.temperature")).alias("heat_alert_level")
            )
            
            return transformed_df
            
        except Exception as e:
            print(f"❌ Error in transformation: {e}")
            return None
    
    def start_streaming(self):
        """Start the streaming transformation process"""
        try:
            print(f"🚀 Starting weather transformation stream...")
            print(f"📥 Input topic: {self.input_topic}")
            print(f"📤 Output topic: {self.output_topic}")
            print("Press Ctrl+C to stop...")
            print("-" * 60)
            
            # Read from Kafka
            kafka_df = self.spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_servers) \
                .option("subscribe", self.input_topic) \
                .option("startingOffsets", "latest") \
                .load()
            
            # Transform the data
            transformed_df = self.transform_weather_data(kafka_df)
            
            if transformed_df is None:
                print("❌ Failed to create transformation")
                return
            
            # Convert to JSON for output
            output_df = transformed_df.select(
                to_json(struct("*")).alias("value")
            )
            
            # Write to output topic
            query = output_df \
                .writeStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_servers) \
                .option("topic", self.output_topic) \
                .option("checkpointLocation", "./checkpoint") \
                .outputMode("append") \
                .trigger(processingTime='10 seconds') \
                .start()
            
            # Also write to console for monitoring
            console_query = transformed_df \
                .writeStream \
                .outputMode("append") \
                .format("console") \
                .option("truncate", False) \
                .trigger(processingTime='10 seconds') \
                .start()
            
            print("✅ Streaming started successfully!")
            print("💡 Monitor the console output below for transformed data...")
            print("="*60)
            
            # Wait for termination
            query.awaitTermination()
            
        except KeyboardInterrupt:
            print("\n🛑 Streaming stopped by user")
        except Exception as e:
            print(f"❌ Streaming error: {e}")
        finally:
            self.stop()
    
    def process_batch(self):
        """Process existing messages as a batch (for testing)"""
        try:
            print(f"🔄 Processing existing messages from {self.input_topic}...")
            
            # Read existing data from Kafka
            kafka_df = self.spark \
                .read \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_servers) \
                .option("subscribe", self.input_topic) \
                .option("startingOffsets", "earliest") \
                .option("endingOffsets", "latest") \
                .load()
            
            if kafka_df.count() == 0:
                print("📭 No messages found in the topic")
                return
            
            print(f"📊 Found {kafka_df.count()} messages to process")
            
            # Transform the data
            transformed_df = self.transform_weather_data(kafka_df)
            
            if transformed_df is None:
                print("❌ Failed to create transformation")
                return
            
            # Show results
            print("🔍 Transformed data preview:")
            transformed_df.show(10, truncate=False)
            
            # Write to output topic
            output_df = transformed_df.select(
                to_json(struct("*")).alias("value")
            )
            
            output_df \
                .write \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_servers) \
                .option("topic", self.output_topic) \
                .save()
            
            print(f"✅ Batch processing completed! Data sent to {self.output_topic}")
            
        except Exception as e:
            print(f"❌ Batch processing error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop Spark session"""
        if self.spark:
            self.spark.stop()
            print("🔌 Spark session stopped")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Weather Data Transformer with Spark')
    parser.add_argument('--kafka-servers', default='localhost:9092', help='Kafka bootstrap servers')
    parser.add_argument('--input-topic', default='weather_stream', help='Input topic name')
    parser.add_argument('--output-topic', default='weather_transformed', help='Output topic name')
    parser.add_argument('--mode', choices=['stream', 'batch'], default='batch', 
                        help='Processing mode: stream (continuous) or batch (existing data)')
    
    args = parser.parse_args()
    
    # Create transformer
    transformer = WeatherTransformer(
        kafka_servers=args.kafka_servers,
        input_topic=args.input_topic,
        output_topic=args.output_topic
    )
    
    if args.mode == 'stream':
        transformer.start_streaming()
    else:
        transformer.process_batch()

if __name__ == "__main__":
    main()