#!/usr/bin/env python3
"""
Exercise 4: Weather Data Transformation and Alert Detection (Simple Version)
Process weather_stream and create weather_transformed topic with alerts.

Usage: python weather_transformer_simple.py
"""

import json
import time
import sys
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

class SimpleWeatherTransformer:
    def __init__(self, kafka_servers='localhost:9092', input_topic='weather_stream', output_topic='weather_transformed'):
        self.kafka_servers = kafka_servers
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.consumer = None
        self.producer = None
        self._init_kafka()
    
    def _init_kafka(self):
        """Initialize Kafka consumer and producer"""
        try:
            # Create consumer
            self.consumer = KafkaConsumer(
                self.input_topic,
                bootstrap_servers=self.kafka_servers,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='weather-transformer-group',
                value_deserializer=lambda x: x.decode('utf-8') if x else None,
                consumer_timeout_ms=5000  # 5 second timeout
            )
            
            # Create producer
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all'
            )
            
            print("✅ Kafka consumer and producer initialized successfully")
            
        except KafkaError as e:
            print(f"❌ Failed to initialize Kafka: {e}")
            sys.exit(1)
    
    def calculate_wind_alert(self, wind_speed):
        """Calculate wind alert level based on wind speed"""
        if wind_speed is None:
            return "unknown"
        
        if wind_speed < 10:
            return "level_0"  # Vent faible (< 10 m/s)
        elif 10 <= wind_speed < 20:
            return "level_1"  # Vent modéré (10-20 m/s)
        else:
            return "level_2"  # Vent fort (>= 20 m/s)
    
    def calculate_heat_alert(self, temperature):
        """Calculate heat alert level based on temperature"""
        if temperature is None:
            return "unknown"
        
        if temperature < 25:
            return "level_0"  # Température normale (< 25°C)
        elif 25 <= temperature < 35:
            return "level_1"  # Chaleur modérée (25-35°C)
        else:
            return "level_2"  # Canicule (>= 35°C)
    
    def transform_weather_message(self, message_value):
        """Transform a single weather message"""
        try:
            # Parse the original message
            data = json.loads(message_value)
            
            # Skip non-weather messages (like test messages)
            if 'current_weather' not in data:
                return None
            
            # Extract weather data
            location = data.get('location', {})
            weather = data.get('current_weather', {})
            
            # Transform the message
            transformed = {
                'event_time': datetime.utcnow().isoformat() + 'Z',
                'original_timestamp': data.get('timestamp'),
                
                # Location data
                'latitude': location.get('latitude'),
                'longitude': location.get('longitude'),
                'timezone': location.get('timezone'),
                
                # Weather data (transformed if necessary)
                'temperature': weather.get('temperature'),
                'windspeed': weather.get('wind_speed'),
                'humidity': weather.get('humidity'),
                'apparent_temperature': weather.get('apparent_temperature'),
                'weather_code': weather.get('weather_code'),
                'wind_direction': weather.get('wind_direction'),
                'weather_time': weather.get('time'),
                
                # Alert levels
                'wind_alert_level': self.calculate_wind_alert(weather.get('wind_speed')),
                'heat_alert_level': self.calculate_heat_alert(weather.get('temperature'))
            }
            
            return transformed
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"⚠️  Error parsing message: {e}")
            return None
    
    def process_batch(self):
        """Process all existing messages in the topic"""
        print(f"🔄 Processing existing messages from {self.input_topic}...")
        print(f"📤 Sending transformed data to {self.output_topic}")
        print("-" * 60)
        
        processed_count = 0
        transformed_count = 0
        
        try:
            # Use consumer timeout to avoid waiting forever
            for message in self.consumer:
                processed_count += 1
                
                print(f"📩 Processing message #{processed_count}")
                print(f"   Original: {message.value[:100]}...")
                
                # Transform the message
                transformed = self.transform_weather_message(message.value)
                
                if transformed:
                    # Send to output topic
                    try:
                        future = self.producer.send(self.output_topic, value=transformed)
                        future.get(timeout=10)
                        transformed_count += 1
                        
                        print(f"✅ Transformed message sent:")
                        print(f"   Temperature: {transformed['temperature']}°C")
                        print(f"   Wind Speed: {transformed['windspeed']} m/s")
                        print(f"   Wind Alert: {transformed['wind_alert_level']}")
                        print(f"   Heat Alert: {transformed['heat_alert_level']}")
                        
                    except KafkaError as e:
                        print(f"❌ Failed to send transformed message: {e}")
                else:
                    print("⏭️  Skipped non-weather message")
                
                print("-" * 60)
                
                # Break after processing a reasonable number of messages
                if processed_count >= 10:
                    break
            
            print(f"🏁 Batch processing completed!")
            print(f"📊 Processed: {processed_count} messages")
            print(f"✅ Transformed: {transformed_count} weather messages")
            
        except Exception as e:
            print(f"❌ Error during processing: {e}")
        finally:
            self.close()
    
    def start_streaming(self):
        """Start continuous streaming transformation"""
        print(f"🚀 Starting continuous weather transformation...")
        print(f"📥 Input topic: {self.input_topic}")
        print(f"📤 Output topic: {self.output_topic}")
        print("Press Ctrl+C to stop...")
        print("-" * 60)
        
        processed_count = 0
        
        try:
            for message in self.consumer:
                processed_count += 1
                
                print(f"📩 New message #{processed_count} received")
                
                # Transform the message
                transformed = self.transform_weather_message(message.value)
                
                if transformed:
                    # Send to output topic
                    try:
                        future = self.producer.send(self.output_topic, value=transformed)
                        future.get(timeout=10)
                        
                        print(f"✅ Transformed and sent:")
                        print(f"   🌡️  Temp: {transformed['temperature']}°C → Heat Alert: {transformed['heat_alert_level']}")
                        print(f"   💨 Wind: {transformed['windspeed']} m/s → Wind Alert: {transformed['wind_alert_level']}")
                        
                    except KafkaError as e:
                        print(f"❌ Failed to send: {e}")
                else:
                    print("⏭️  Skipped non-weather message")
                
                print("-" * 40)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Streaming stopped. Processed {processed_count} messages.")
        except Exception as e:
            print(f"❌ Streaming error: {e}")
        finally:
            self.close()
    
    def close(self):
        """Close Kafka connections"""
        if self.consumer:
            self.consumer.close()
        if self.producer:
            self.producer.flush()
            self.producer.close()
        print("🔌 Kafka connections closed")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Weather Data Transformer')
    parser.add_argument('--kafka-servers', default='localhost:9092', help='Kafka bootstrap servers')
    parser.add_argument('--input-topic', default='weather_stream', help='Input topic name')
    parser.add_argument('--output-topic', default='weather_transformed', help='Output topic name')
    parser.add_argument('--mode', choices=['stream', 'batch'], default='batch', 
                        help='Processing mode: stream (continuous) or batch (existing data)')
    
    args = parser.parse_args()
    
    print(f"🌍 Weather Transformer Starting...")
    print(f"🔧 Mode: {args.mode}")
    print(f"📥 Input: {args.input_topic}")
    print(f"📤 Output: {args.output_topic}")
    print("="*60)
    
    # Create transformer
    transformer = SimpleWeatherTransformer(
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