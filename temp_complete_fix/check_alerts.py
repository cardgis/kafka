#!/usr/bin/env python3
"""
Simple script to check for alert messages in weather_transformed topic
"""

from kafka import KafkaConsumer
import json

def main():
    consumer = KafkaConsumer(
        'weather_transformed',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=5000,
        group_id='hdfs-test-consumer-2',
        auto_offset_reset='earliest'
    )
    
    count = 0
    alerts_count = 0
    
    print("Checking for alert messages...")
    
    for message in consumer:
        count += 1
        data = message.value
        
        wind_alert = data.get('wind_alert_level', 'level_0')
        heat_alert = data.get('heat_alert_level', 'level_0')
        
        if wind_alert in ['level_1', 'level_2'] or heat_alert in ['level_1', 'level_2']:
            alerts_count += 1
            temp = data.get('temperature', 'N/A')
            wind_speed = data.get('windspeed', 'N/A')
            print(f'Message {count}: ALERT - Wind: {wind_alert}, Heat: {heat_alert}')
            print(f'  Temp: {temp}°C, Wind: {wind_speed} m/s')
            print(f'  Location: {data.get("latitude", "N/A")}, {data.get("longitude", "N/A")}')
        else:
            print(f'Message {count}: No significant alerts - Wind: {wind_alert}, Heat: {heat_alert}')
        
        if count >= 20:  # Limit output
            break
    
    consumer.close()
    print(f'\nTotal: {count} messages, {alerts_count} with alerts')

if __name__ == "__main__":
    main()