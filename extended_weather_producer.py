#!/usr/bin/env python3
"""
Exercise 6: Extended Weather Producer
Accepts city and country as arguments, uses geocoding API to get coordinates,
and includes location metadata for HDFS partitioning and regional aggregates.

Usage: python extended_weather_producer.py <city> <country>
Example: python extended_weather_producer.py Paris France
Example: python extended_weather_producer.py "New York" "United States"
"""

import sys
import json
import time
import requests
import argparse
from kafka import KafkaProducer
from kafka.errors import KafkaError
from datetime import datetime
import urllib.parse

class ExtendedWeatherProducer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='weather_stream'):
        self.topic = topic
        self.producer = None
        self.geocoding_api_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.weather_api_url = "https://api.open-meteo.com/v1/forecast"
        self._connect(bootstrap_servers)
    
    def _connect(self, bootstrap_servers):
        """Initialize Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            print(f"Connected to Kafka cluster at {bootstrap_servers}")
        except KafkaError as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            sys.exit(1)
    
    def geocode_location(self, city, country):
        """Get coordinates and detailed location info using Open-Meteo Geocoding API"""
        try:
            # Build search query
            query = f"{city}, {country}"
            params = {
                'name': city,
                'count': 5,  # Get multiple results to find the best match
                'language': 'en',
                'format': 'json'
            }
            
            print(f"Searching coordinates for: {query}")
            response = requests.get(self.geocoding_api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                print(f"❌ No coordinates found for {query}")
                return None
            
            # Find the best match (try to match country)
            best_match = None
            country_lower = country.lower()
            
            for result in results:
                result_country = result.get('country', '').lower()
                if country_lower in result_country or result_country in country_lower:
                    best_match = result
                    break
            
            # If no country match, use the first result
            if not best_match:
                best_match = results[0]
            
            location_info = {
                'latitude': best_match.get('latitude'),
                'longitude': best_match.get('longitude'),
                'city': best_match.get('name'),
                'country': best_match.get('country'),
                'country_code': best_match.get('country_code'),
                'admin1': best_match.get('admin1'),  # State/Region
                'admin2': best_match.get('admin2'),  # County/District
                'timezone': best_match.get('timezone'),
                'elevation': best_match.get('elevation')
            }
            
            print(f"Found: {location_info['city']}, {location_info['country']}")
            print(f"Coordinates: {location_info['latitude']}, {location_info['longitude']}")
            print(f"Timezone: {location_info['timezone']}")
            
            return location_info
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error geocoding location: {e}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            print(f"❌ Error parsing geocoding response: {e}")
            return None
    
    def get_weather_data(self, location_info):
        """Fetch weather data using location info"""
        if not location_info:
            return None
        
        latitude = location_info['latitude']
        longitude = location_info['longitude']
        
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl',
            'timezone': location_info.get('timezone', 'auto'),
            'forecast_days': 1
        }
        
        try:
            print(f"🌤️  Fetching weather data for {location_info['city']}, {location_info['country']}")
            response = requests.get(self.weather_api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            current = data.get('current', {})
            
            # Enhanced weather message with full location metadata
            weather_message = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'location': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'city': location_info['city'],
                    'country': location_info['country'],
                    'country_code': location_info['country_code'],
                    'admin1': location_info.get('admin1'),  # State/Region for partitioning
                    'admin2': location_info.get('admin2'),  # District for detailed analysis
                    'timezone': location_info.get('timezone'),
                    'elevation': location_info.get('elevation')
                },
                'current_weather': {
                    'temperature': current.get('temperature_2m'),
                    'humidity': current.get('relative_humidity_2m'),
                    'apparent_temperature': current.get('apparent_temperature'),
                    'weather_code': current.get('weather_code'),
                    'wind_speed': current.get('wind_speed_10m'),
                    'wind_direction': current.get('wind_direction_10m'),
                    'pressure': current.get('pressure_msl'),
                    'time': current.get('time')
                },
                'metadata': {
                    'source': 'extended_weather_producer',
                    'api_version': 'open_meteo_v1',
                    'geocoded': True,
                    'request_city': location_info['city'],
                    'request_country': location_info['country']
                }
            }
            
            # Display weather info
            temp = current.get('temperature_2m')
            wind = current.get('wind_speed_10m')
            humidity = current.get('relative_humidity_2m')
            pressure = current.get('pressure_msl')
            
            print(f"🌡️  Temperature: {temp}°C")
            print(f"💨 Wind Speed: {wind} m/s")
            print(f"💧 Humidity: {humidity}%")
            print(f"🔄 Pressure: {pressure} hPa")
            
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
            
            city = message['location']['city']
            country = message['location']['country']
            
            print(f"📤 Message sent successfully!")
            print(f"   📍 Location: {city}, {country}")
            print(f"   📨 Topic: {record_metadata.topic}")
            print(f"   📊 Partition: {record_metadata.partition}")
            print(f"   📈 Offset: {record_metadata.offset}")
            return True
            
        except KafkaError as e:
            print(f"❌ Failed to send message: {e}")
            return False
    
    def stream_weather(self, city, country, interval=30):
        """Stream weather data continuously for a city/country"""
        print(f"🚀 Starting weather stream for {city}, {country}")
        print(f"📡 Sending data every {interval} seconds to topic '{self.topic}'")
        print("Press Ctrl+C to stop...")
        print("-" * 60)
        
        # Get location info once
        location_info = self.geocode_location(city, country)
        if not location_info:
            print(f"❌ Cannot start streaming: Failed to geocode {city}, {country}")
            return False
        
        message_count = 0
        
        try:
            while True:
                weather_data = self.get_weather_data(location_info)
                
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
        
        return True
    
    def send_single_message(self, city, country):
        """Send a single weather message for a city/country"""
        location_info = self.geocode_location(city, country)
        
        if not location_info:
            print(f"❌ Failed to geocode {city}, {country}")
            self.close()
            return False
        
        weather_data = self.get_weather_data(location_info)
        
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
    parser = argparse.ArgumentParser(description='Extended Weather Data Producer with Geocoding')
    parser.add_argument('city', help='City name (use quotes for multi-word cities)')
    parser.add_argument('country', help='Country name')
    parser.add_argument('--topic', default='weather_stream', help='Kafka topic (default: weather_stream)')
    parser.add_argument('--bootstrap-servers', default='localhost:9092', help='Kafka bootstrap servers')
    parser.add_argument('--stream', action='store_true', help='Stream continuously (default: send single message)')
    parser.add_argument('--interval', type=int, default=30, help='Streaming interval in seconds (default: 30)')
    
    args = parser.parse_args()
    
    print(f"Extended Weather Producer Starting...")
    print(f"Location: {args.city}, {args.country}")
    print(f"Topic: {args.topic}")
    print("="*60)
    
    # Create producer
    producer = ExtendedWeatherProducer(args.bootstrap_servers, args.topic)
    
    if args.stream:
        # Stream continuously
        success = producer.stream_weather(args.city, args.country, args.interval)
    else:
        # Send single message
        success = producer.send_single_message(args.city, args.country)
    
    if success:
        print("✅ Operation completed successfully!")
        sys.exit(0)
    else:
        print("❌ Operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()