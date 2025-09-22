#!/usr/bin/env python3
"""
Exercice 6 - Extension du producteur avec géolocalisation
Producteur météo qui accepte ville et pays comme arguments via l'API Geocoding Open-Meteo
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

class GeoWeatherProducer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='weather_stream'):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        self.running = True
        
        # URLs des APIs Open-Meteo
        self.geocoding_api_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.weather_api_url = "https://api.open-meteo.com/v1/forecast"
        
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
                acks='all',
                retries=3,
                batch_size=16384,
                linger_ms=10,
                buffer_memory=33554432
            )
            
            print(f"✅ Producteur géolocalisé créé pour le topic '{self.topic}'")
            print(f"📍 Serveur: {self.bootstrap_servers}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création du producteur: {e}")
            return False
    
    def geocode_location(self, city, country=None, language="fr"):
        """Géocoder une ville/pays vers coordonnées via l'API Open-Meteo"""
        try:
            # Paramètres pour l'API de géocodage
            params = {
                'name': city,
                'count': 5,  # Récupérer plusieurs résultats
                'language': language,
                'format': 'json'
            }
            
            if country:
                params['name'] = f"{city}, {country}"
            
            # Requête à l'API de géocodage
            response = requests.get(self.geocoding_api_url, params=params, timeout=10)
            response.raise_for_status()
            
            geocoding_data = response.json()
            
            if 'results' not in geocoding_data or not geocoding_data['results']:
                print(f"❌ Aucun résultat trouvé pour '{city}'" + (f", {country}" if country else ""))
                return None
            
            # Prendre le premier résultat (le plus pertinent)
            best_result = geocoding_data['results'][0]
            
            location_info = {
                'name': best_result.get('name'),
                'latitude': best_result.get('latitude'),
                'longitude': best_result.get('longitude'),
                'country': best_result.get('country'),
                'country_code': best_result.get('country_code'),
                'admin1': best_result.get('admin1'),  # Région/État
                'admin2': best_result.get('admin2'),  # Département/Comté
                'admin3': best_result.get('admin3'),  # Commune/District
                'admin4': best_result.get('admin4'),  # Quartier
                'population': best_result.get('population'),
                'elevation': best_result.get('elevation'),
                'feature_code': best_result.get('feature_code'),
                'timezone': best_result.get('timezone'),
                'postcodes': best_result.get('postcodes', [])
            }
            
            print(f"🌍 Géolocalisation trouvée:")
            print(f"   📍 {location_info['name']}, {location_info['country']}")
            print(f"   🌐 Coordonnées: {location_info['latitude']}, {location_info['longitude']}")
            if location_info['admin1']:
                print(f"   🏛️  Région: {location_info['admin1']}")
            if location_info['population']:
                print(f"   👥 Population: {location_info['population']:,}")
            
            return location_info
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors de la géolocalisation: {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur lors du traitement de géolocalisation: {e}")
            return None
    
    def get_weather_data(self, location_info):
        """Récupérer les données météo pour une localisation géocodée"""
        try:
            latitude = location_info['latitude']
            longitude = location_info['longitude']
            
            # Paramètres pour l'API météo Open-Meteo
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
            
            # Requête à l'API météo
            response = requests.get(self.weather_api_url, params=params, timeout=10)
            response.raise_for_status()
            
            api_data = response.json()
            
            # Extraction et formatage des données
            current = api_data.get('current', {})
            current_units = api_data.get('current_units', {})
            
            weather_data = {
                'timestamp': datetime.now().isoformat(),
                'api_timestamp': current.get('time'),
                'location': {
                    'coordinates': {
                        'latitude': latitude,
                        'longitude': longitude
                    },
                    'geography': {
                        'name': location_info['name'],
                        'country': location_info['country'],
                        'country_code': location_info['country_code'],
                        'admin1': location_info.get('admin1'),  # Région
                        'admin2': location_info.get('admin2'),  # Département
                        'admin3': location_info.get('admin3'),  # Commune
                        'population': location_info.get('population'),
                        'elevation': location_info.get('elevation'),
                        'feature_code': location_info.get('feature_code')
                    },
                    'timezone': api_data.get('timezone'),
                    'timezone_abbreviation': api_data.get('timezone_abbreviation'),
                    'elevation_api': api_data.get('elevation')
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
                    'source': 'open-meteo-geocoded',
                    'producer_id': 'geo_weather_producer',
                    'version': '1.0',
                    'geocoded': True,
                    'original_query': {
                        'city': location_info.get('original_city'),
                        'country': location_info.get('original_country')
                    }
                }
            }
            
            return weather_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors de la requête météo: {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur lors du traitement des données météo: {e}")
            return None
    
    def send_weather_message(self, weather_data, key=None):
        """Envoyer un message météo géolocalisé vers Kafka"""
        if not self.producer or not weather_data:
            return False
        
        try:
            # Clé basée sur la géographie complète
            if not key:
                geo = weather_data['location']['geography']
                key = f"{geo['country_code']}-{geo['name']}"
            
            # Envoi du message
            future = self.producer.send(
                self.topic, 
                value=weather_data,
                key=key
            )
            
            # Attendre la confirmation
            record_metadata = future.get(timeout=10)
            
            location = weather_data['location']
            geo = location['geography']
            weather = weather_data['current_weather']
            
            print(f"✅ Message géolocalisé envoyé:")
            print(f"   🏙️  Ville: {geo['name']}, {geo['country']}")
            if geo['admin1']:
                print(f"   🏛️  Région: {geo['admin1']}")
            print(f"   📍 Coordonnées: {location['coordinates']['latitude']}, {location['coordinates']['longitude']}")
            print(f"   🌡️  Température: {weather['temperature']}°C")
            print(f"   💨 Vent: {weather['wind_speed']} km/h")
            if geo['population']:
                print(f"   👥 Population: {geo['population']:,}")
            print(f"   📊 Topic: {record_metadata.topic} | Partition: {record_metadata.partition} | Offset: {record_metadata.offset}")
            
            return True
            
        except KafkaError as e:
            print(f"❌ Erreur Kafka: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi: {e}")
            return False
    
    def start_streaming(self, city, country=None, interval=60, count=None):
        """Démarrer le streaming météo géolocalisé"""
        if not self.producer:
            print("❌ Producteur non initialisé")
            return False
        
        # Géolocalisation initiale
        print(f"🔍 Géolocalisation de '{city}'" + (f", {country}" if country else "") + "...")
        location_info = self.geocode_location(city, country)
        
        if not location_info:
            print("❌ Impossible de géolocaliser la ville")
            return False
        
        # Sauvegarder la requête originale
        location_info['original_city'] = city
        location_info['original_country'] = country
        
        print(f"\n🌍 Démarrage du streaming météo géolocalisé:")
        print(f"🏙️  Ville: {location_info['name']}, {location_info['country']}")
        print(f"📍 Coordonnées: {location_info['latitude']}, {location_info['longitude']}")
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
                
                print(f"📡 Requête météo géolocalisée #{message_count}...")
                
                # Récupération des données météo
                weather_data = self.get_weather_data(location_info)
                
                if weather_data:
                    # Envoi vers Kafka
                    if self.send_weather_message(weather_data):
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
        description="Exercice 6 - Producteur météo géolocalisé",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python geo_weather.py Paris                        # Paris, France
  python geo_weather.py Lyon France                  # Lyon, France explicite  
  python geo_weather.py "New York" USA               # New York, États-Unis
  python geo_weather.py London "United Kingdom"      # Londres, Royaume-Uni
  python geo_weather.py Tokyo --interval 30          # Tokyo avec intervalle
  python geo_weather.py Berlin --count 10            # Berlin, 10 messages
  python geo_weather.py Madrid --topic weather_geo   # Topic personnalisé
        """
    )
    
    parser.add_argument('city', 
                       help='Nom de la ville à géolocaliser')
    parser.add_argument('country', 
                       nargs='?',
                       help='Pays (optionnel, améliore la précision)')
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
    parser.add_argument('--language', 
                       default='fr',
                       help='Langue pour la géolocalisation (défaut: fr)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🌍 EXERCICE 6 - PRODUCTEUR MÉTÉO GÉOLOCALISÉ")
    print("="*60)
    
    # Création et démarrage du producteur géolocalisé
    producer = GeoWeatherProducer(
        bootstrap_servers=args.server,
        topic=args.topic
    )
    
    if producer.create_producer():
        success = producer.start_streaming(
            city=args.city,
            country=args.country,
            interval=args.interval,
            count=args.count
        )
        sys.exit(0 if success else 1)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()