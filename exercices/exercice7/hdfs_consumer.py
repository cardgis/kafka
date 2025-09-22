#!/usr/bin/env python3
"""
🌊📁 Kafka Weather Analytics - Exercice 7: HDFS Consumer & Distributed Storage
===============================================================================

Consumer Kafka avancé qui stocke les données météorologiques dans une structure
HDFS (Hadoop Distributed File System) organisée géographiquement pour faciliter
les analyses ultérieures et le traitement Big Data.

Fonctionnalités:
- Consumer multi-topics avec auto-partitioning géographique
- Stockage HDFS optimisé en format JSONL
- Batch processing pour optimiser les performances I/O
- Monitoring en temps réel avec métriques détaillées
- Gestion d'erreurs robuste avec retry automatique
- Support pour millions de messages par heure

Architecture:
    hdfs-data/
    ├── FR/Paris/alerts.json
    ├── DE/Berlin/alerts.json  
    ├── US/New-York/alerts.json
    └── UNKNOWN/Unknown-City/alerts.json

Usage:
    python hdfs_consumer.py --hdfs-path "./hdfs-data" --topics geo_weather_stream
    python hdfs_consumer.py --hdfs-path "./hdfs-data" --topics "weather_stream,geo_weather_stream" --monitoring
"""

import json
import os
import sys
import time
import argparse
import logging
import signal
import threading
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
import re

# Kafka Client
try:
    from kafka import KafkaConsumer
    from kafka.errors import KafkaError, KafkaTimeoutError
except ImportError:
    print("❌ kafka-python not installed. Run: pip install kafka-python")
    sys.exit(1)

# Data Processing
try:
    import pandas as pd
except ImportError:
    print("⚠️ pandas not installed. Some features may be limited. Run: pip install pandas")
    pd = None

# ==================================================================================
# CONFIGURATION & CONSTANTS
# ==================================================================================

# Default Configuration
DEFAULT_CONFIG = {
    'kafka': {
        'bootstrap_servers': ['localhost:9092'],
        'group_id': 'hdfs_consumer_group',
        'auto_offset_reset': 'earliest',
        'enable_auto_commit': True,
        'auto_commit_interval_ms': 1000,
        'consumer_timeout_ms': 5000,
        'max_poll_records': 500,
        'value_deserializer': lambda x: json.loads(x.decode('utf-8')) if x else None
    },
    'hdfs': {
        'base_path': './hdfs-data',
        'batch_size': 100,
        'flush_interval': 30,  # seconds
        'max_file_size': 100 * 1024 * 1024,  # 100MB
        'file_format': 'jsonl',
        'create_directories': True
    },
    'monitoring': {
        'enabled': False,
        'stats_interval': 60,  # seconds
        'log_level': 'INFO',
        'performance_tracking': True
    }
}

# Country Code Mapping
COUNTRY_MAPPING = {
    'france': 'FR', 'fr': 'FR', 'french': 'FR',
    'germany': 'DE', 'de': 'DE', 'deutschland': 'DE', 'german': 'DE',
    'united states': 'US', 'usa': 'US', 'us': 'US', 'america': 'US',
    'united kingdom': 'GB', 'uk': 'GB', 'gb': 'GB', 'britain': 'GB',
    'japan': 'JP', 'jp': 'JP', 'japanese': 'JP',
    'spain': 'ES', 'es': 'ES', 'spanish': 'ES',
    'italy': 'IT', 'it': 'IT', 'italian': 'IT',
    'canada': 'CA', 'ca': 'CA', 'canadian': 'CA',
    'australia': 'AU', 'au': 'AU', 'australian': 'AU'
}

# ==================================================================================
# UTILITIES & HELPERS
# ==================================================================================

class PerformanceMonitor:
    """Moniteur de performance pour tracking des métriques"""
    
    def __init__(self, stats_interval: int = 60):
        self.stats_interval = stats_interval
        self.reset_stats()
        self.start_time = time.time()
        self.last_stats_time = self.start_time
        
    def reset_stats(self):
        """Reset des statistiques"""
        self.messages_processed = 0
        self.batches_written = 0
        self.total_bytes = 0
        self.error_count = 0
        self.location_counter = Counter()
        self.topic_counter = Counter()
        
    def record_message(self, topic: str, message_size: int, location: str):
        """Enregistre une métrique de message"""
        self.messages_processed += 1
        self.total_bytes += message_size
        self.location_counter[location] += 1
        self.topic_counter[topic] += 1
        
    def record_batch(self, batch_size: int):
        """Enregistre une métrique de batch"""
        self.batches_written += 1
        
    def record_error(self):
        """Enregistre une erreur"""
        self.error_count += 1
        
    def get_current_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques actuelles"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        stats = {
            'runtime_seconds': elapsed_time,
            'messages_processed': self.messages_processed,
            'batches_written': self.batches_written,
            'total_bytes': self.total_bytes,
            'error_count': self.error_count,
            'messages_per_second': self.messages_processed / elapsed_time if elapsed_time > 0 else 0,
            'bytes_per_second': self.total_bytes / elapsed_time if elapsed_time > 0 else 0,
            'avg_batch_size': self.messages_processed / self.batches_written if self.batches_written > 0 else 0,
            'top_locations': dict(self.location_counter.most_common(10)),
            'topics_distribution': dict(self.topic_counter)
        }
        
        return stats
    
    def should_print_stats(self) -> bool:
        """Vérifie si il faut imprimer les stats"""
        current_time = time.time()
        if current_time - self.last_stats_time >= self.stats_interval:
            self.last_stats_time = current_time
            return True
        return False

def normalize_country_name(country: str) -> str:
    """Normalise le nom de pays vers un code ISO"""
    if not country:
        return 'UNKNOWN'
        
    country_clean = re.sub(r'[^a-zA-Z\s]', '', country.lower().strip())
    
    # Lookup direct
    if country_clean in COUNTRY_MAPPING:
        return COUNTRY_MAPPING[country_clean]
    
    # Lookup par mots-clés
    for key, code in COUNTRY_MAPPING.items():
        if key in country_clean or country_clean in key:
            return code
    
    # Code ISO direct (2-3 lettres majuscules)
    if len(country) <= 3 and country.isalpha():
        return country.upper()
    
    return 'UNKNOWN'

def normalize_city_name(city: str) -> str:
    """Normalise le nom de ville pour le filesystem"""
    if not city:
        return 'Unknown-City'
        
    # Nettoyage et normalisation
    city_clean = re.sub(r'[^\w\s-]', '', city.strip())
    city_clean = re.sub(r'\s+', '-', city_clean)
    city_clean = city_clean.title()
    
    return city_clean if city_clean else 'Unknown-City'

def create_safe_path(base_path: str, *parts) -> Path:
    """Crée un chemin filesystem sécurisé"""
    path_parts = [base_path]
    
    for part in parts:
        if part:
            # Suppression des caractères dangereux
            safe_part = re.sub(r'[<>:"|?*]', '', str(part))
            safe_part = safe_part.replace('..', '')  # Prévention path traversal
            path_parts.append(safe_part)
    
    return Path(*path_parts)

# ==================================================================================
# HDFS CONSUMER CORE
# ==================================================================================

class HDFSConsumer:
    """Consumer Kafka avancé avec stockage HDFS géographique"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.hdfs_path = Path(config['hdfs']['base_path'])
        self.batch_size = config['hdfs']['batch_size']
        self.flush_interval = config['hdfs']['flush_interval']
        
        # State management
        self.running = False
        self.consumer = None
        self.batches = defaultdict(list)  # location -> messages
        self.last_flush = time.time()
        
        # Monitoring
        self.monitor = PerformanceMonitor(config['monitoring']['stats_interval'])
        self.monitoring_enabled = config['monitoring']['enabled']
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Ensure HDFS directory exists
        self.hdfs_path.mkdir(parents=True, exist_ok=True)
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration du système de logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, self.config['monitoring']['log_level']))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = self.hdfs_path / 'hdfs_consumer.log'
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _signal_handler(self, signum, frame):
        """Handler pour arrêt gracieux"""
        self.logger.info(f"🛑 Signal reçu ({signum}), arrêt en cours...")
        self.stop()
    
    def connect_kafka(self, topics: List[str]) -> bool:
        """Connexion au cluster Kafka"""
        try:
            self.logger.info("🔌 Connexion à Kafka...")
            
            self.consumer = KafkaConsumer(
                *topics,
                **self.config['kafka']
            )
            
            self.logger.info(f"✅ Connecté aux topics: {', '.join(topics)}")
            
            # Test de connexion
            partitions = self.consumer.assignment()
            self.logger.info(f"📊 Partitions assignées: {len(partitions)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur connexion Kafka: {e}")
            return False
    
    def extract_location_info(self, message: Dict[str, Any]) -> tuple[str, str]:
        """Extrait les informations de localisation du message"""
        # Tentatives d'extraction de pays
        country = None
        city = None
        
        # Extraction directe
        if 'country' in message:
            country = message['country']
        elif 'location' in message and ',' in str(message['location']):
            parts = str(message['location']).split(',')
            if len(parts) >= 2:
                city = parts[0].strip()
                country = parts[1].strip()
        
        # Extraction de ville
        if not city and 'city' in message:
            city = message['city']
        elif not city and 'location' in message:
            city = str(message['location']).split(',')[0].strip()
        
        # Normalisation
        country_code = normalize_country_name(country)
        city_name = normalize_city_name(city)
        
        return country_code, city_name
    
    def process_message(self, topic: str, message: Dict[str, Any]) -> bool:
        """Traite un message et l'ajoute au batch approprié"""
        try:
            # Extraction de la localisation
            country, city = self.extract_location_info(message)
            location_key = f"{country}/{city}"
            
            # Enrichissement du message avec metadata
            enriched_message = {
                **message,
                'processed_at': datetime.utcnow().isoformat(),
                'topic': topic,
                'country_code': country,
                'city_normalized': city
            }
            
            # Ajout au batch
            self.batches[location_key].append(enriched_message)
            
            # Monitoring
            message_size = len(json.dumps(enriched_message))
            self.monitor.record_message(topic, message_size, location_key)
            
            self.logger.debug(f"📝 Message traité: {location_key}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement message: {e}")
            self.monitor.record_error()
            return False
    
    def flush_batches(self, force: bool = False) -> int:
        """Écrit les batches sur disque"""
        current_time = time.time()
        
        # Vérification si flush nécessaire
        should_flush = (
            force or 
            (current_time - self.last_flush) >= self.flush_interval or
            any(len(batch) >= self.batch_size for batch in self.batches.values())
        )
        
        if not should_flush:
            return 0
        
        total_written = 0
        
        try:
            for location_key, messages in list(self.batches.items()):
                if not messages:
                    continue
                
                # Création du chemin HDFS
                country, city = location_key.split('/')
                hdfs_file_path = create_safe_path(
                    str(self.hdfs_path), country, city, 'alerts.json'
                )
                
                # Création des dossiers
                hdfs_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Écriture en mode append (JSONL)
                with open(hdfs_file_path, 'a', encoding='utf-8') as f:
                    for message in messages:
                        json.dump(message, f, ensure_ascii=False, separators=(',', ':'))
                        f.write('\n')
                
                total_written += len(messages)
                self.monitor.record_batch(len(messages))
                
                self.logger.debug(f"💾 Batch écrit: {location_key} ({len(messages)} messages)")
                
                # Clear du batch
                self.batches[location_key].clear()
            
            self.last_flush = current_time
            
            if total_written > 0:
                self.logger.info(f"✅ Flush terminé: {total_written} messages écrits")
            
            return total_written
            
        except Exception as e:
            self.logger.error(f"❌ Erreur flush batches: {e}")
            self.monitor.record_error()
            return 0
    
    def print_monitoring_stats(self):
        """Affiche les statistiques de monitoring"""
        if not self.monitoring_enabled:
            return
            
        stats = self.monitor.get_current_stats()
        
        self.logger.info("📊 === STATISTIQUES PERFORMANCE ===")
        self.logger.info(f"⏱️  Runtime: {stats['runtime_seconds']:.1f}s")
        self.logger.info(f"📨 Messages traités: {stats['messages_processed']:,}")
        self.logger.info(f"📦 Batches écrits: {stats['batches_written']:,}")
        self.logger.info(f"💽 Données totales: {stats['total_bytes'] / 1024 / 1024:.1f} MB")
        self.logger.info(f"⚡ Performance: {stats['messages_per_second']:.1f} msg/sec")
        self.logger.info(f"🚨 Erreurs: {stats['error_count']}")
        
        if stats['top_locations']:
            self.logger.info("🌍 Top Locations:")
            for location, count in list(stats['top_locations'].items())[:5]:
                self.logger.info(f"   • {location}: {count:,} messages")
        
        self.logger.info("=" * 50)
    
    def consume_messages(self, topics: List[str]) -> bool:
        """Boucle principale de consommation des messages"""
        if not self.connect_kafka(topics):
            return False
        
        self.running = True
        self.logger.info("🚀 Démarrage de la consommation des messages...")
        
        try:
            while self.running:
                try:
                    # Poll des messages
                    message_batch = self.consumer.poll(
                        timeout_ms=self.config['kafka']['consumer_timeout_ms']
                    )
                    
                    if not message_batch:
                        # Pas de nouveaux messages, flush périodique
                        self.flush_batches()
                        
                        # Stats monitoring
                        if self.monitoring_enabled and self.monitor.should_print_stats():
                            self.print_monitoring_stats()
                        
                        continue
                    
                    # Traitement des messages
                    for topic_partition, messages in message_batch.items():
                        topic = topic_partition.topic
                        
                        for message in messages:
                            if not self.running:
                                break
                                
                            try:
                                if message.value:
                                    self.process_message(topic, message.value)
                            except Exception as e:
                                self.logger.error(f"❌ Erreur message: {e}")
                                self.monitor.record_error()
                    
                    # Flush périodique
                    self.flush_batches()
                    
                    # Stats monitoring
                    if self.monitoring_enabled and self.monitor.should_print_stats():
                        self.print_monitoring_stats()
                    
                except KafkaTimeoutError:
                    self.logger.debug("⏰ Timeout Kafka, continuing...")
                    continue
                except KafkaError as e:
                    self.logger.error(f"❌ Erreur Kafka: {e}")
                    time.sleep(5)  # Pause avant retry
                    continue
                    
        except Exception as e:
            self.logger.error(f"❌ Erreur fatale dans consume_messages: {e}")
            return False
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Arrêt gracieux du consumer"""
        if not self.running:
            return
            
        self.logger.info("🛑 Arrêt du consumer...")
        self.running = False
        
        # Flush final des batches
        final_count = self.flush_batches(force=True)
        if final_count > 0:
            self.logger.info(f"💾 Flush final: {final_count} messages")
        
        # Fermeture du consumer Kafka
        if self.consumer:
            try:
                self.consumer.close()
                self.logger.info("✅ Consumer Kafka fermé")
            except Exception as e:
                self.logger.error(f"⚠️ Erreur fermeture consumer: {e}")
        
        # Stats finales
        if self.monitoring_enabled:
            self.print_monitoring_stats()
        
        self.logger.info("✅ HDFS Consumer arrêté proprement")

# ==================================================================================
# CLI INTERFACE
# ==================================================================================

def create_argparser() -> argparse.ArgumentParser:
    """Crée le parser d'arguments CLI"""
    parser = argparse.ArgumentParser(
        description="🌊📁 Kafka Weather Analytics - Exercice 7: HDFS Consumer & Distributed Storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python hdfs_consumer.py --hdfs-path "./hdfs-data" --topics geo_weather_stream
  python hdfs_consumer.py --hdfs-path "./hdfs-data" --topics "weather_stream,geo_weather_stream" --monitoring
  python hdfs_consumer.py --hdfs-path "./data-lake" --topics geo_weather_stream --batch-size 500 --flush-interval 10
        """
    )
    
    parser.add_argument(
        '--hdfs-path',
        type=str,
        default='./hdfs-data',
        help='Chemin de base pour le stockage HDFS (défaut: ./hdfs-data)'
    )
    
    parser.add_argument(
        '--topics',
        type=str,
        required=True,
        help='Topics Kafka à consumer (séparés par des virgules)'
    )
    
    parser.add_argument(
        '--kafka-servers',
        type=str,
        default='localhost:9092',
        help='Serveurs Kafka bootstrap (défaut: localhost:9092)'
    )
    
    parser.add_argument(
        '--group-id',
        type=str,
        default='hdfs_consumer_group',
        help='Groupe de consumers Kafka (défaut: hdfs_consumer_group)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Taille des batches pour écriture (défaut: 100)'
    )
    
    parser.add_argument(
        '--flush-interval',
        type=int,
        default=30,
        help='Intervalle de flush en secondes (défaut: 30)'
    )
    
    parser.add_argument(
        '--monitoring',
        action='store_true',
        help='Active le monitoring de performance'
    )
    
    parser.add_argument(
        '--stats-interval',
        type=int,
        default=60,
        help='Intervalle des stats en secondes (défaut: 60)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Niveau de logging (défaut: INFO)'
    )
    
    parser.add_argument(
        '--offset-reset',
        choices=['earliest', 'latest'],
        default='earliest',
        help='Position de départ du consumer (défaut: earliest)'
    )
    
    return parser

def main():
    """Point d'entrée principal"""
    parser = create_argparser()
    args = parser.parse_args()
    
    # Parse topics
    topics = [topic.strip() for topic in args.topics.split(',') if topic.strip()]
    if not topics:
        print("❌ Aucun topic spécifié")
        return 1
    
    # Parse Kafka servers
    kafka_servers = [server.strip() for server in args.kafka_servers.split(',')]
    
    # Configuration
    config = {
        'kafka': {
            'bootstrap_servers': kafka_servers,
            'group_id': args.group_id,
            'auto_offset_reset': args.offset_reset,
            'enable_auto_commit': True,
            'auto_commit_interval_ms': 1000,
            'consumer_timeout_ms': 5000,
            'max_poll_records': 500,
            'value_deserializer': lambda x: json.loads(x.decode('utf-8')) if x else None
        },
        'hdfs': {
            'base_path': args.hdfs_path,
            'batch_size': args.batch_size,
            'flush_interval': args.flush_interval,
            'max_file_size': 100 * 1024 * 1024,
            'file_format': 'jsonl',
            'create_directories': True
        },
        'monitoring': {
            'enabled': args.monitoring,
            'stats_interval': args.stats_interval,
            'log_level': args.log_level,
            'performance_tracking': True
        }
    }
    
    try:
        # Affichage de la configuration
        print("🌊📁 Kafka Weather Analytics - Exercice 7: HDFS Consumer")
        print("=" * 70)
        print(f"📁 HDFS Path: {args.hdfs_path}")
        print(f"📊 Topics: {', '.join(topics)}")
        print(f"🔌 Kafka Servers: {', '.join(kafka_servers)}")
        print(f"👥 Consumer Group: {args.group_id}")
        print(f"📦 Batch Size: {args.batch_size}")
        print(f"⏰ Flush Interval: {args.flush_interval}s")
        print(f"📈 Monitoring: {'Activé' if args.monitoring else 'Désactivé'}")
        print("=" * 70)
        
        # Initialisation du consumer
        consumer = HDFSConsumer(config)
        
        # Démarrage de la consommation
        success = consumer.consume_messages(topics)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
        return 0
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())