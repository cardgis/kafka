#!/usr/bin/env python3
"""
Générateur de données de test pour l'exercice 7
Crée des données météo géolocalisées pour tester le consommateur HDFS
"""

import json
import time
from kafka import KafkaProducer
from datetime import datetime, timezone

def create_test_producer():
    """Crée un producteur Kafka pour les tests"""
    return KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8'),
        key_serializer=lambda x: x.encode('utf-8') if x else None
    )

def generate_test_data():
    """Génère des données de test géolocalisées"""
    test_locations = [
        {"city": "Paris", "country": "France", "country_code": "FR", "latitude": 48.8566, "longitude": 2.3522},
        {"city": "Tokyo", "country": "Japan", "country_code": "JP", "latitude": 35.6762, "longitude": 139.6503},
        {"city": "New York", "country": "USA", "country_code": "US", "latitude": 40.7128, "longitude": -74.0060},
        {"city": "London", "country": "UK", "country_code": "GB", "latitude": 51.5074, "longitude": -0.1278},
        {"city": "Berlin", "country": "Germany", "country_code": "DE", "latitude": 52.5200, "longitude": 13.4050}
    ]
    
    producer = create_test_producer()
    
    print("🚀 Génération de données de test pour l'exercice 7...")
    
    for i, location in enumerate(test_locations):
        # Message geo_weather_stream format
        geo_message = {
            "location": location,
            "weather": {
                "temperature": 15.0 + (i * 2),
                "windspeed": 10.0 + (i * 3),
                "winddirection": 180 + (i * 20),
                "weathercode": 1 + (i % 4),
                "is_day": 1
            },
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test-generator",
                "geocoded": True
            }
        }
        
        key = f"{location['country_code']}_{location['city']}"
        
        # Envoyer vers geo_weather_stream
        future = producer.send('geo_weather_stream', key=key, value=geo_message)
        result = future.get(timeout=10)
        
        print(f"✅ Message envoyé: {location['city']}, {location['country']} "
              f"→ partition {result.partition}, offset {result.offset}")
        
        time.sleep(1)
    
    producer.flush()
    producer.close()
    
    print(f"\n🎉 {len(test_locations)} messages de test envoyés vers geo_weather_stream")
    print("💡 Vous pouvez maintenant lancer le consommateur HDFS")

if __name__ == "__main__":
    generate_test_data()