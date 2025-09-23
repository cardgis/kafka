#!/usr/bin/env python3
"""
Exercise 3: Current Weather Producer
Queries Open-Meteo API for weather data and sends it to Kafka weather_stream topic.

Usage: python current_weather.py <latitude> <longitude>
Example: python current_weather.py 48.8566 2.3522  # Paris coordinates
"""

import sys
import json
import time
import requests
import argparse
from kafka import KafkaProducer
from kafka.errors import KafkaError
from datetime import datetime

class WeatherProducer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='weather_stream'):
        self.topic = topic
        self.producer = None
        self._connect(bootstrap_servers)
    
    def _connect(self, bootstrap_servers):
        """Initialize Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            print(f"✅ Connected to Kafka cluster at {bootstrap_servers}")
        except KafkaError as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            sys.exit(1)
    
    def get_weather_data(self, latitude, longitude):
        """Fetch weather data from Open-Meteo API"""
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m',
            'timezone': 'auto',
            'forecast_days': 1
        }
        
        try:
            print(f"🌍 Fetching weather data for coordinates: {latitude}, {longitude}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract current weather data
            current = data.get('current', {})
            
            # Create structured message
            weather_message = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'location': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'timezone': data.get('timezone', 'UTC')
                },
                'current_weather': {
                    'temperature': current.get('temperature_2m'),
                    'humidity': current.get('relative_humidity_2m'),
                    'apparent_temperature': current.get('apparent_temperature'),
                    'weather_code': current.get('weather_code'),
                    'wind_speed': current.get('wind_speed_10m'),
                    'wind_direction': current.get('wind_direction_10m'),
                    'time': current.get('time')
                }
            }
            
            print(f"🌡️  Temperature: {current.get('temperature_2m')}°C")
            print(f"💨 Wind Speed: {current.get('wind_speed_10m')} m/s")
            print(f"💧 Humidity: {current.get('relative_humidity_2m')}%")
            
            return weather_message
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching weather data: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing weather data: {e}")
            return None
    
    def send_message(self, message):
        """Send message to Kafka topic"""
        try:
            future = self.producer.send(self.topic, value=message)
            record_metadata = future.get(timeout=10)
            
            print(f"📤 Message sent successfully!")
            print(f"   Topic: {record_metadata.topic}")
            print(f"   Partition: {record_metadata.partition}")
            print(f"   Offset: {record_metadata.offset}")
            return True
            
        except KafkaError as e:
            print(f"❌ Failed to send message: {e}")
            return False
    
    def stream_weather(self, latitude, longitude, interval=30):
        """Stream weather data continuously"""
        print(f"🚀 Starting weather stream for coordinates: {latitude}, {longitude}")
        print(f"📡 Sending data every {interval} seconds to topic '{self.topic}'")
        print("Press Ctrl+C to stop...")
        print("-" * 60)
        
        message_count = 0
        
        try:
            while True:
                weather_data = self.get_weather_data(latitude, longitude)
                
                if weather_data:
                    if self.send_message(weather_data):
                        message_count += 1
                        print(f"✅ Message #{message_count} sent at {weather_data['timestamp']}")
                    else:
                        print(f"❌ Failed to send message #{message_count + 1}")
                else:
                    print("⚠️  No weather data received, skipping...")
                
                print(f"⏰ Waiting {interval} seconds...")
                print("-" * 60)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Weather streaming stopped. Total messages sent: {message_count}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            self.close()
    
    def send_single_message(self, latitude, longitude):
        """Send a single weather message"""
        weather_data = self.get_weather_data(latitude, longitude)
        
        if weather_data:
            success = self.send_message(weather_data)
            self.close()
            return success
        else:
            self.close()
            return False
    
    def close(self):
        """Close producer connection"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            print("🔌 Producer connection closed.")

def main():
    parser = argparse.ArgumentParser(description='Weather Data Producer for Kafka')
    parser.add_argument('latitude', type=float, help='Latitude coordinate')
    parser.add_argument('longitude', type=float, help='Longitude coordinate')
    parser.add_argument('--topic', default='weather_stream', help='Kafka topic (default: weather_stream)')
    parser.add_argument('--bootstrap-servers', default='localhost:9092', help='Kafka bootstrap servers')
    parser.add_argument('--stream', action='store_true', help='Stream continuously (default: send single message)')
    parser.add_argument('--interval', type=int, default=30, help='Streaming interval in seconds (default: 30)')
    
    args = parser.parse_args()
    
    # Validate coordinates
    if not (-90 <= args.latitude <= 90):
        print("❌ Invalid latitude. Must be between -90 and 90.")
        sys.exit(1)
    
    if not (-180 <= args.longitude <= 180):
        print("❌ Invalid longitude. Must be between -180 and 180.")
        sys.exit(1)
    
    # Create producer
    producer = WeatherProducer(args.bootstrap_servers, args.topic)
    
    if args.stream:
        # Stream continuously
        producer.stream_weather(args.latitude, args.longitude, args.interval)
    else:
        # Send single message
        success = producer.send_single_message(args.latitude, args.longitude)
        if success:
            print("✅ Weather data sent successfully!")
            sys.exit(0)
        else:
            print("❌ Failed to send weather data!")
            sys.exit(1)

if __name__ == "__main__":
    main()