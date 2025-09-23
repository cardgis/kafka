#!/usr/bin/env python3
"""
Continuous data generator for testing aggregations
Sends weather data every few seconds to create a stream
"""

import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime

def generate_test_weather():
    """Generate realistic test weather data"""
    # Different locations
    locations = [
        (48.8566, 2.3522, "Paris"),      # Paris
        (40.7128, -74.0060, "NYC"),      # New York
        (35.6762, 139.6503, "Tokyo"),    # Tokyo
        (51.5074, -0.1278, "London"),    # London
        (-33.8688, 151.2093, "Sydney"),  # Sydney
    ]
    
    lat, lon, name = random.choice(locations)
    
    # Generate realistic weather ranges
    base_temp = random.uniform(5, 35)  # 5-35°C
    temp_variation = random.uniform(-5, 5)
    temperature = base_temp + temp_variation
    
    # Generate wind speed with some correlation to alerts
    if random.random() < 0.2:  # 20% chance of high wind
        wind_speed = random.uniform(15, 30)  # High wind
    elif random.random() < 0.3:  # 30% chance of medium wind
        wind_speed = random.uniform(8, 15)   # Medium wind
    else:
        wind_speed = random.uniform(0, 10)   # Low wind
    
    return {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'location': {
            'latitude': lat,
            'longitude': lon,
            'timezone': 'UTC'
        },
        'current_weather': {
            'temperature': round(temperature, 1),
            'humidity': random.randint(30, 90),
            'apparent_temperature': round(temperature + random.uniform(-2, 2), 1),
            'weather_code': random.randint(0, 3),
            'wind_speed': round(wind_speed, 1),
            'wind_direction': random.randint(0, 360),
            'time': datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
        },
        'test_location': name
    }

def main():
    # Create producer
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    print("🌊 Starting continuous weather data stream...")
    print("📡 Sending data every 3 seconds to weather_stream")
    print("🔄 This will generate alerts and test the aggregator")
    print("Press Ctrl+C to stop...")
    print("-" * 60)
    
    message_count = 0
    
    try:
        while True:
            # Generate and send weather data
            weather_data = generate_test_weather()
            producer.send('weather_stream', value=weather_data)
            
            message_count += 1
            temp = weather_data['current_weather']['temperature']
            wind = weather_data['current_weather']['wind_speed']
            location = weather_data['test_location']
            
            print(f"📤 #{message_count}: {location} - {temp}°C, {wind} m/s")
            
            time.sleep(3)  # Send every 3 seconds
            
    except KeyboardInterrupt:
        print(f"\n🛑 Stream stopped. Sent {message_count} messages.")
    finally:
        producer.flush()
        producer.close()
        print("🔌 Producer closed")

if __name__ == "__main__":
    main()