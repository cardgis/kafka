#!/usr/bin/env python3
"""
Exercise 2: Kafka Consumer
Consumes messages from a Kafka topic passed as argument and displays them in real-time.

Usage: python consumer.py <topic_name>
Example: python consumer.py weather_stream
"""

import sys
import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import argparse

def create_consumer(topic, bootstrap_servers='localhost:9092'):
    """Create and configure Kafka consumer"""
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='latest',  # Start from latest messages
            enable_auto_commit=True,
            group_id='weather-consumer-group',
            value_deserializer=lambda x: x.decode('utf-8') if x else None,
            consumer_timeout_ms=1000  # Timeout after 1 second of no messages
        )
        print(f"✅ Connected to Kafka topic '{topic}'")
        print(f"📡 Listening for messages... (Press Ctrl+C to stop)")
        print("-" * 50)
        return consumer
    except KafkaError as e:
        print(f"❌ Error connecting to Kafka: {e}")
        return None

def consume_messages(consumer, topic):
    """Consume and display messages in real-time"""
    message_count = 0
    
    try:
        for message in consumer:
            message_count += 1
            timestamp = message.timestamp
            value = message.value
            
            # Try to parse as JSON for better formatting
            try:
                json_data = json.loads(value)
                formatted_value = json.dumps(json_data, indent=2)
            except (json.JSONDecodeError, TypeError):
                formatted_value = value
            
            print(f"📩 Message #{message_count}")
            print(f"🕐 Timestamp: {timestamp}")
            print(f"📄 Content:\n{formatted_value}")
            print("-" * 50)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Consumer stopped. Total messages received: {message_count}")
    except Exception as e:
        print(f"❌ Error consuming messages: {e}")
    finally:
        consumer.close()
        print("🔌 Consumer connection closed.")

def main():
    parser = argparse.ArgumentParser(description='Kafka Consumer for weather data')
    parser.add_argument('topic', help='Kafka topic name to consume from')
    parser.add_argument('--bootstrap-servers', default='localhost:9092', 
                        help='Kafka bootstrap servers (default: localhost:9092)')
    
    args = parser.parse_args()
    
    print(f"🚀 Starting Kafka Consumer for topic: {args.topic}")
    
    # Create consumer
    consumer = create_consumer(args.topic, args.bootstrap_servers)
    if consumer is None:
        sys.exit(1)
    
    # Start consuming messages
    consume_messages(consumer, args.topic)

if __name__ == "__main__":
    main()