#!/usr/bin/env python3
"""
Exercice 7: Consommateur Kafka vers HDFS
==========================================

Consommateur qui lit les données météo depuis Kafka et les organise
dans une structure HDFS hiérarchique par pays et ville.

Structure HDFS: /hdfs-data/{country}/{city}/alerts.json

Fonctionnalités:
- Lecture des topics weather_transformed et geo_weather_stream
- Organisation géographique des données
- Sauvegarde JSON structurée
- Gestion des partitions et du parallélisme

Author: Assistant
Date: 2024
"""

import json
import os
import argparse
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set
import time

from kafka import KafkaConsumer
from kafka.errors import KafkaError
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HDFSWeatherConsumer:
    """Consommateur Kafka vers HDFS pour données météo géolocalisées"""
    
    def __init__(self, kafka_server: str = "localhost:9092", 
                 hdfs_base_path: str = "./hdfs-data",
                 topics: List[str] = None):
        """
        Initialise le consommateur HDFS
        
        Args:
            kafka_server: Serveur Kafka (host:port)
            hdfs_base_path: Chemin de base pour la structure HDFS
            topics: Liste des topics à consommer
        """
        self.kafka_server = kafka_server
        self.hdfs_base_path = Path(hdfs_base_path)
        self.topics = topics or ['weather_transformed', 'geo_weather_stream']
        self.consumer = None
        self.running = False
        self.processed_count = 0
        self.error_count = 0
        self.countries_seen: Set[str] = set()
        self.cities_seen: Set[str] = set()
        
        # Créer la structure de base HDFS
        self._ensure_hdfs_structure()
        
        print("🗄️  EXERCICE 7 - CONSOMMATEUR KAFKA VERS HDFS")
        print("=" * 60)
        
    def _ensure_hdfs_structure(self):
        """Crée la structure de base HDFS si elle n'existe pas"""
        try:
            self.hdfs_base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Structure HDFS créée: {self.hdfs_base_path}")
            print(f"📁 Répertoire HDFS: {self.hdfs_base_path.absolute()}")
        except Exception as e:
            logger.error(f"❌ Erreur création structure HDFS: {e}")
            raise
            
    def _setup_consumer(self):
        """Configure et initialise le consommateur Kafka"""
        try:
            self.consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=self.kafka_server,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                key_deserializer=lambda x: x.decode('utf-8') if x else None,
                group_id='hdfs-weather-consumer',
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                consumer_timeout_ms=1000,  # Timeout pour permettre les arrêts propres
            )
            
            print(f"✅ Consommateur HDFS créé:")
            print(f"   📍 Serveur: {self.kafka_server}")
            print(f"   📊 Topics: {', '.join(self.topics)}")
            print(f"   👥 Groupe: hdfs-weather-consumer")
            print(f"   🗄️  HDFS: {self.hdfs_base_path.absolute()}")
            
            logger.info(f"Consommateur créé pour topics: {self.topics}")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration consommateur: {e}")
            raise
            
    def _extract_location_info(self, message: Dict) -> tuple[str, str]:
        """
        Extrait les informations de localisation du message
        
        Args:
            message: Message JSON Kafka
            
        Returns:
            tuple: (country_code, city_name)
        """
        try:
            # Tentative d'extraction depuis geo_weather_stream (format enrichi)
            if 'location' in message:
                location = message['location']
                country_code = location.get('country_code', 'UNKNOWN')
                city = location.get('city', 'UNKNOWN')
                return country_code, city
                
            # Tentative d'extraction depuis weather_transformed (format alerte)
            if 'location_data' in message:
                location = message['location_data']
                # Essayer de déduire le pays depuis latitude/longitude ou utiliser défaut
                country_code = location.get('country_code', 'FR')  # Défaut France
                city = location.get('city', f"LAT_{location.get('latitude', 0)}")
                return country_code, city
                
            # Format basique avec latitude/longitude seulement
            if 'latitude' in message and 'longitude' in message:
                lat = message['latitude']
                lon = message['longitude']
                return 'UNKNOWN', f"LAT_{lat}_LON_{lon}"
                
            # Fallback par défaut
            return 'UNKNOWN', 'UNKNOWN'
            
        except Exception as e:
            logger.warning(f"⚠️  Erreur extraction localisation: {e}")
            return 'UNKNOWN', 'UNKNOWN'
            
    def _get_hdfs_path(self, country_code: str, city: str) -> Path:
        """
        Génère le chemin HDFS pour un pays/ville donnés
        
        Args:
            country_code: Code pays (ex: FR, JP, US)
            city: Nom de la ville
            
        Returns:
            Path: Chemin complet vers le fichier alerts.json
        """
        # Nettoyer les noms pour le système de fichiers
        safe_country = self._sanitize_filename(country_code)
        safe_city = self._sanitize_filename(city)
        
        country_dir = self.hdfs_base_path / safe_country
        city_dir = country_dir / safe_city
        
        # Créer les répertoires si nécessaire
        city_dir.mkdir(parents=True, exist_ok=True)
        
        return city_dir / "alerts.json"
        
    def _sanitize_filename(self, name: str) -> str:
        """Nettoie un nom pour qu'il soit compatible système de fichiers"""
        # Remplacer les caractères problématiques
        import re
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', str(name))
        sanitized = sanitized.replace(' ', '_')
        return sanitized[:50]  # Limiter la longueur
        
    def _append_to_hdfs_file(self, file_path: Path, message: Dict):
        """
        Ajoute un message au fichier HDFS en format JSON Lines
        
        Args:
            file_path: Chemin vers le fichier alerts.json
            message: Message à ajouter
        """
        try:
            # Ajouter timestamp de traitement
            enriched_message = {
                **message,
                'hdfs_metadata': {
                    'processed_at': datetime.now(timezone.utc).isoformat(),
                    'consumer_id': 'hdfs-weather-consumer',
                    'file_path': str(file_path)
                }
            }
            
            # Écrire en mode append (une ligne JSON par message)
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(enriched_message, ensure_ascii=False) + '\n')
                
            logger.debug(f"📝 Message ajouté à {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Erreur écriture HDFS {file_path}: {e}")
            self.error_count += 1
            raise
            
    def _process_message(self, message):
        """
        Traite un message Kafka et l'enregistre dans HDFS
        
        Args:
            message: Message Kafka ConsumerRecord
        """
        try:
            topic = message.topic
            partition = message.partition
            offset = message.offset
            key = message.key
            value = message.value
            
            if not value:
                logger.warning("⚠️  Message vide ignoré")
                return
                
            # Extraire les informations de localisation
            country_code, city = self._extract_location_info(value)
            
            # Générer le chemin HDFS
            hdfs_path = self._get_hdfs_path(country_code, city)
            
            # Sauvegarder dans HDFS
            self._append_to_hdfs_file(hdfs_path, value)
            
            # Mise à jour des statistiques
            self.processed_count += 1
            self.countries_seen.add(country_code)
            self.cities_seen.add(city)
            
            # Affichage périodique des progrès
            if self.processed_count % 10 == 0:
                print(f"📊 Traité: {self.processed_count} messages | "
                      f"Pays: {len(self.countries_seen)} | "
                      f"Villes: {len(self.cities_seen)}")
                      
            logger.debug(
                f"✅ Message traité: {topic}[{partition}]@{offset} "
                f"→ {country_code}/{city}"
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement message: {e}")
            self.error_count += 1
            
    def _setup_signal_handlers(self):
        """Configure les gestionnaires de signaux pour arrêt propre"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Signal {signum} reçu, arrêt du consommateur...")
            self.stop()
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def start_consuming(self):
        """Démarre la consommation des messages Kafka"""
        try:
            self._setup_consumer()
            self._setup_signal_handlers()
            
            print("\n🚀 Démarrage de la consommation Kafka vers HDFS...")
            print("💡 Appuyez sur Ctrl+C pour arrêter proprement")
            print("-" * 60)
            
            self.running = True
            
            while self.running:
                try:
                    # Consommer les messages avec timeout
                    message_batch = self.consumer.poll(timeout_ms=1000)
                    
                    if not message_batch:
                        continue
                        
                    for topic_partition, messages in message_batch.items():
                        for message in messages:
                            if not self.running:
                                break
                            self._process_message(message)
                            
                except Exception as e:
                    logger.error(f"❌ Erreur consommation: {e}")
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Interruption utilisateur détectée")
            self.stop()
        except Exception as e:
            logger.error(f"❌ Erreur fatale: {e}")
            self.stop()
            
    def stop(self):
        """Arrête le consommateur proprement"""
        print("\n📊 STATISTIQUES FINALES:")
        print(f"   📝 Messages traités: {self.processed_count}")
        print(f"   ❌ Erreurs: {self.error_count}")
        print(f"   🌍 Pays découverts: {len(self.countries_seen)}")
        print(f"   🏙️  Villes découvertes: {len(self.cities_seen)}")
        
        if self.countries_seen:
            print(f"   📍 Pays: {', '.join(sorted(self.countries_seen))}")
            
        self.running = False
        
        if self.consumer:
            try:
                self.consumer.close()
                print("✅ Consommateur fermé proprement")
            except Exception as e:
                logger.error(f"❌ Erreur fermeture: {e}")
                
        print("🗄️  Structure HDFS créée avec succès!")
        self._display_hdfs_structure()
        
    def _display_hdfs_structure(self):
        """Affiche la structure HDFS créée"""
        print(f"\n📁 STRUCTURE HDFS GÉNÉRÉE ({self.hdfs_base_path}):")
        print("-" * 50)
        
        try:
            for country_dir in sorted(self.hdfs_base_path.iterdir()):
                if country_dir.is_dir():
                    print(f"🌍 {country_dir.name}/")
                    for city_dir in sorted(country_dir.iterdir()):
                        if city_dir.is_dir():
                            alerts_file = city_dir / "alerts.json"
                            if alerts_file.exists():
                                size = alerts_file.stat().st_size
                                lines = sum(1 for _ in open(alerts_file, 'r'))
                                print(f"   🏙️  {city_dir.name}/")
                                print(f"      📄 alerts.json ({lines} entrées, {size} bytes)")
                                
        except Exception as e:
            logger.error(f"❌ Erreur affichage structure: {e}")


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Consommateur Kafka vers HDFS pour données météo"
    )
    
    parser.add_argument('--server', 
                        default='localhost:9092',
                        help='Serveur Kafka (défaut: localhost:9092)')
    
    parser.add_argument('--hdfs-path', 
                        default='./hdfs-data',
                        help='Chemin de base HDFS (défaut: ./hdfs-data)')
    
    parser.add_argument('--topics', 
                        nargs='+',
                        default=['weather_transformed', 'geo_weather_stream'],
                        help='Topics à consommer (défaut: weather_transformed geo_weather_stream)')
    
    args = parser.parse_args()
    
    # Créer et démarrer le consommateur
    consumer = HDFSWeatherConsumer(
        kafka_server=args.server,
        hdfs_base_path=args.hdfs_path,
        topics=args.topics
    )
    
    try:
        consumer.start_consuming()
    except Exception as e:
        logger.error(f"❌ Erreur démarrage: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()