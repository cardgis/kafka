#!/usr/bin/env python3
"""
Manual Alert Generator for Exercise 7 Testing
Creates weather data with guaranteed alerts for HDFS testing
"""

import json
import time
from datetime import datetime
from kafka import KafkaProducer

def create_alert_message(city, country, temperature, wind_speed):
    """Create a weather message with specified temperature and wind speed"""
    return {
        "location": {
            "city": city,
            "country": country,
            "country_code": "TEST",
            "admin1": "Test Region",
            "admin2": "Test Subregion",
            "latitude": 40.0,
            "longitude": -74.0,
            "timezone": "America/New_York",
            "elevation": 10
        },
        "weather": {
            "temperature": temperature,
            "humidity": 60,
            "pressure": 1013.25,
            "wind_speed": wind_speed,
            "wind_direction": 270,
            "weather_code": 0,
            "precipitation": 0.0
        },
        "timestamp": datetime.now().isoformat()
    }

def main():
    print("Manual Alert Generator - Exercise 7")
    print("=" * 50)
    
    # Connect to Kafka
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    # Test cases with guaranteed alerts
    test_cases = [
        ("Phoenix", "United States", 38.0, 5.0),    # Heat level 2
        ("Chicago", "United States", 20.0, 25.0),   # Wind level 2
        ("Miami", "United States", 32.0, 15.0),     # Heat level 2 + Wind level 1
        ("Denver", "United States", 28.0, 22.0),    # Heat level 1 + Wind level 2
        ("Boston", "United States", 26.0, 12.0),    # Heat level 1 + Wind level 1
    ]
    
    print("Sending alert-worthy weather data...")
    
    for i, (city, country, temp, wind) in enumerate(test_cases):
        message = create_alert_message(city, country, temp, wind)
        
        # Send to weather_stream topic
        future = producer.send('weather_stream', value=message)
        result = future.get(timeout=10)
        
        print(f"{i+1}. {city}: {temp}°C, {wind} m/s -> Partition {result.partition}, Offset {result.offset}")
        
        # Small delay between messages
        time.sleep(0.5)
    
    producer.flush()
    producer.close()
    
    print(f"\nSent {len(test_cases)} alert messages to weather_stream topic")
    print("These should trigger alerts in the transformer and be stored by HDFS consumer")

if __name__ == "__main__":
    main()