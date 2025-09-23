#!/usr/bin/env python3
import json
from datetime import datetime
from kafka import KafkaProducer

def main():
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    message = {
        "msg": "Hello Kafka",
        "timestamp": datetime.now().isoformat()
    }
    
    future = producer.send('weather_stream', value=message)
    result = future.get(timeout=10)
    
    print(f"Message sent: partition {result.partition}, offset {result.offset}")
    producer.close()

if __name__ == "__main__":
    main()
