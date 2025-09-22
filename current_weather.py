#!/usr/bin/env python3
"""
Exercice 3 - Producteur météo en direct
Interroge l'API Open-Meteo pour une latitude/longitude et envoie les données dans Kafka
"""

import argparse
import json
import time
import sys
import requests
from kafka import KafkaProducer
from kafka.errors import KafkaError
from datetime import datetime
import signal

class WeatherProducer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='weather_stream'):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        self.running = True
        
        # URL de base de l'API Open-Meteo
        self.api_base_url = "https://api.open-meteo.com/v1/forecast"
        
        # Configuration du gestionnaire de signaux
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Gestionnaire pour arrêt propre avec Ctrl+C"""
        print(f"\n🛑 Signal {signum} reçu, arrêt du producteur...")
        self.running = False
        if self.producer:
            self.producer.close()
    
    def create_producer(self):
        """Créer et configurer le producteur Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[self.bootstrap_servers],
                value_serializer=lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8') if x else None,
                acks='all',  # Attendre confirmation de tous les brokers
                retries=3,   # Retry en cas d'erreur
                batch_size=16384,
                linger_ms=10,
                buffer_memory=33554432
            )
            
            print(f"✅ Producteur créé pour le topic '{self.topic}'")
            print(f"📍 Serveur: {self.bootstrap_servers}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création du producteur: {e}")
            return False
    
    def get_weather_data(self, latitude, longitude):
        """Récupérer les données météo depuis l'API Open-Meteo"""
        try:
            # Paramètres pour l'API Open-Meteo
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current': [
                    'temperature_2m',
                    'relative_humidity_2m', 
                    'apparent_temperature',
                    'is_day',
                    'precipitation',
                    'rain',
                    'showers',
                    'snowfall',
                    'weather_code',
                    'cloud_cover',
                    'pressure_msl',
                    'surface_pressure',
                    'wind_speed_10m',
                    'wind_direction_10m',
                    'wind_gusts_10m'
                ],
                'timezone': 'auto'
            }
            
            # Requête à l'API
            response = requests.get(self.api_base_url, params=params, timeout=10)
            response.raise_for_status()
            
            api_data = response.json()
            
            # Extraction et formatage des données
            current = api_data.get('current', {})
            current_units = api_data.get('current_units', {})
            
            weather_data = {
                'timestamp': datetime.now().isoformat(),
                'api_timestamp': current.get('time'),
                'location': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'timezone': api_data.get('timezone'),
                    'timezone_abbreviation': api_data.get('timezone_abbreviation'),
                    'elevation': api_data.get('elevation')
                },
                'current_weather': {
                    'temperature': current.get('temperature_2m'),
                    'temperature_unit': current_units.get('temperature_2m', '°C'),
                    'apparent_temperature': current.get('apparent_temperature'),
                    'humidity': current.get('relative_humidity_2m'),
                    'humidity_unit': current_units.get('relative_humidity_2m', '%'),
                    'precipitation': current.get('precipitation'),
                    'precipitation_unit': current_units.get('precipitation', 'mm'),
                    'rain': current.get('rain'),
                    'showers': current.get('showers'),
                    'snowfall': current.get('snowfall'),
                    'weather_code': current.get('weather_code'),
                    'cloud_cover': current.get('cloud_cover'),
                    'cloud_cover_unit': current_units.get('cloud_cover', '%'),
                    'pressure_msl': current.get('pressure_msl'),
                    'pressure_unit': current_units.get('pressure_msl', 'hPa'),
                    'wind_speed': current.get('wind_speed_10m'),
                    'wind_speed_unit': current_units.get('wind_speed_10m', 'km/h'),
                    'wind_direction': current.get('wind_direction_10m'),
                    'wind_direction_unit': current_units.get('wind_direction_10m', '°'),
                    'wind_gusts': current.get('wind_gusts_10m'),
                    'is_day': bool(current.get('is_day', 0))
                },
                'producer_info': {
                    'source': 'open-meteo-api',
                    'producer_id': 'current_weather',
                    'version': '1.0'
                }
            }
            
            return weather_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors de la requête API: {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur lors du traitement des données météo: {e}")
            return None
    
    def send_weather_message(self, weather_data, key=None):
        """Envoyer un message météo vers Kafka"""
        if not self.producer or not weather_data:
            return False
        
        try:
            # Envoi du message
            future = self.producer.send(
                self.topic, 
                value=weather_data,
                key=key
            )
            
            # Attendre la confirmation
            record_metadata = future.get(timeout=10)
            
            print(f"✅ Message envoyé:")
            print(f"   📍 Location: {weather_data['location']['latitude']}, {weather_data['location']['longitude']}")
            print(f"   🌡️  Température: {weather_data['current_weather']['temperature']}°C")
            print(f"   💨 Vent: {weather_data['current_weather']['wind_speed']} km/h")
            print(f"   📊 Topic: {record_metadata.topic}")
            print(f"   📊 Partition: {record_metadata.partition}")
            print(f"   📊 Offset: {record_metadata.offset}")
            
            return True
            
        except KafkaError as e:
            print(f"❌ Erreur Kafka: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi: {e}")
            return False
    
    def start_streaming(self, latitude, longitude, interval=60, count=None):
        """Démarrer le streaming de données météo"""
        if not self.producer:
            print("❌ Producteur non initialisé")
            return False
        
        print(f"\n🌍 Démarrage du streaming météo:")
        print(f"📍 Coordonnées: {latitude}, {longitude}")
        print(f"⏱️  Intervalle: {interval} secondes")
        if count:
            print(f"🔢 Nombre de messages: {count}")
        else:
            print(f"🔄 Mode continu (Ctrl+C pour arrêter)")
        print()
        
        message_count = 0
        
        try:
            while self.running:
                message_count += 1
                
                print(f"📡 Requête météo #{message_count}...")
                
                # Récupération des données météo
                weather_data = self.get_weather_data(latitude, longitude)
                
                if weather_data:
                    # Clé basée sur les coordonnées
                    key = f"{latitude},{longitude}"
                    
                    # Envoi vers Kafka
                    if self.send_weather_message(weather_data, key):
                        print(f"🎉 Message #{message_count} envoyé avec succès!")
                    else:
                        print(f"❌ Échec envoi message #{message_count}")
                else:
                    print(f"❌ Échec récupération données météo #{message_count}")
                
                # Vérifier si on a atteint le nombre demandé
                if count and message_count >= count:
                    print(f"\n✅ {count} messages envoyés, arrêt du streaming")
                    break
                
                # Attendre avant la prochaine itération
                if self.running and (not count or message_count < count):
                    print(f"⏳ Attente {interval} secondes...\n")
                    time.sleep(interval)
                    
        except KeyboardInterrupt:
            print(f"\n🛑 Interruption utilisateur")
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")
        finally:
            if self.producer:
                self.producer.close()
                print(f"\n✅ Producteur fermé. Total messages envoyés: {message_count}")
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description="Exercice 3 - Producteur météo en temps réel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python current_weather.py 48.8566 2.3522                    # Paris
  python current_weather.py 45.764 4.8357 --interval 30       # Lyon, toutes les 30s
  python current_weather.py 43.2965 5.3698 --count 5          # Marseille, 5 messages
  python current_weather.py 48.8566 2.3522 --topic weather_live
        """
    )
    
    parser.add_argument('latitude', 
                       type=float,
                       help='Latitude de la localisation')
    parser.add_argument('longitude', 
                       type=float,
                       help='Longitude de la localisation')
    parser.add_argument('--server', 
                       default='localhost:9092',
                       help='Adresse du serveur Kafka (défaut: localhost:9092)')
    parser.add_argument('--topic', 
                       default='weather_stream',
                       help='Topic Kafka de destination (défaut: weather_stream)')
    parser.add_argument('--interval', 
                       type=int, 
                       default=60,
                       help='Intervalle entre les requêtes en secondes (défaut: 60)')
    parser.add_argument('--count', 
                       type=int,
                       help='Nombre de messages à envoyer (défaut: illimité)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🌤️  EXERCICE 3 - PRODUCTEUR MÉTÉO EN TEMPS RÉEL")
    print("="*60)
    
    # Création et démarrage du producteur
    producer = WeatherProducer(
        bootstrap_servers=args.server,
        topic=args.topic
    )
    
    if producer.create_producer():
        success = producer.start_streaming(
            latitude=args.latitude,
            longitude=args.longitude,
            interval=args.interval,
            count=args.count
        )
        sys.exit(0 if success else 1)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()