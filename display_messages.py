#!/usr/bin/env python3
"""
Display recent messages from weather_stream topic with enhanced city/country metadata
"""

import json
from kafka import KafkaConsumer

def display_recent_messages(max_messages=5):
    """Display the most recent messages from weather_stream"""
    consumer = KafkaConsumer(
        'weather_stream',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest',
        enable_auto_commit=False,
        group_id='display-messages-group',
        value_deserializer=lambda x: x.decode('utf-8') if x else None,
        consumer_timeout_ms=3000
    )
    
    print("🔍 Checking recent messages from weather_stream...")
    print("="*80)
    
    message_count = 0
    messages = []
    
    # Collect messages
    for message in consumer:
        try:
            data = json.loads(message.value)
            messages.append(data)
            message_count += 1
            if message_count >= max_messages:
                break
        except json.JSONDecodeError:
            continue
    
    consumer.close()
    
    if not messages:
        print("❌ No recent messages found")
        return
    
    # Display messages
    for i, msg in enumerate(messages, 1):
        print(f"\n📩 Message #{i}:")
        print(f"   🕒 Timestamp: {msg.get('timestamp', 'N/A')}")
        
        location = msg.get('location', {})
        if 'city' in location and 'country' in location:
            # Enhanced format from Exercise 6
            print(f"   📍 Location: {location.get('city')}, {location.get('country')}")
            print(f"   🗺️  Coordinates: {location.get('latitude')}, {location.get('longitude')}")
            print(f"   🌐 Timezone: {location.get('timezone')}")
            print(f"   🏛️  Admin1: {location.get('admin1', 'N/A')}")
            print(f"   🏙️  Admin2: {location.get('admin2', 'N/A')}")
            
            weather = msg.get('current_weather', {})
            print(f"   🌡️  Temperature: {weather.get('temperature')}°C")
            print(f"   💨 Wind: {weather.get('wind_speed')} m/s")
            print(f"   💧 Humidity: {weather.get('humidity')}%")
            print(f"   🔄 Pressure: {weather.get('pressure', 'N/A')} hPa")
            
            metadata = msg.get('metadata', {})
            if metadata:
                print(f"   📊 Source: {metadata.get('source', 'N/A')}")
                print(f"   🎯 Geocoded: {metadata.get('geocoded', False)}")
        else:
            # Old format
            print(f"   📍 Coordinates: {location.get('latitude')}, {location.get('longitude')}")
            weather = msg.get('current_weather', {})
            print(f"   🌡️  Temperature: {weather.get('temperature')}°C")
            print(f"   💨 Wind: {weather.get('wind_speed')} m/s")
            
        print("-" * 60)
    
    print(f"\n✅ Displayed {len(messages)} recent messages")

if __name__ == "__main__":
    display_recent_messages()