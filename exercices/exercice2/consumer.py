#!/usr/bin/env python3
"""
Exercice 2 - Consommateur Kafka Python
Lit les messages depuis un topic Kafka passé en argument et les affiche en temps réel
"""

import argparse
import json
import sys
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from datetime import datetime
import signal

class KafkaConsumerApp:
    def __init__(self, topic, bootstrap_servers='localhost:9092', group_id='python-consumer-group'):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer = None
        self.running = True
        
        # Configuration du gestionnaire de signaux pour arrêt propre
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Gestionnaire pour arrêt propre avec Ctrl+C"""
        print(f"\n🛑 Signal {signum} reçu, arrêt du consommateur...")
        self.running = False
        if self.consumer:
            self.consumer.close()
    
    def create_consumer(self, from_beginning=False):
        """Créer et configurer le consommateur Kafka"""
        try:
            # Configuration du consommateur
            consumer_config = {
                'bootstrap_servers': [self.bootstrap_servers],
                'group_id': self.group_id,
                'value_deserializer': lambda m: m.decode('utf-8'),
                'key_deserializer': lambda m: m.decode('utf-8') if m else None,
                'enable_auto_commit': True,
                'auto_commit_interval_ms': 1000,
                'session_timeout_ms': 30000,
                'heartbeat_interval_ms': 10000
            }
            
            if from_beginning:
                consumer_config['auto_offset_reset'] = 'earliest'
            else:
                consumer_config['auto_offset_reset'] = 'latest'
            
            self.consumer = KafkaConsumer(**consumer_config)
            self.consumer.subscribe([self.topic])
            
            print(f"✅ Consommateur créé pour le topic '{self.topic}'")
            print(f"📍 Serveur: {self.bootstrap_servers}")
            print(f"👥 Groupe: {self.group_id}")
            print(f"⏰ Mode: {'Depuis le début' if from_beginning else 'Nouveaux messages uniquement'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création du consommateur: {e}")
            return False
    
    def format_message(self, message):
        """Formater un message pour l'affichage"""
        timestamp = datetime.fromtimestamp(message.timestamp / 1000)
        
        # Tentative de parsing JSON pour un affichage plus joli
        try:
            value_json = json.loads(message.value)
            value_str = json.dumps(value_json, indent=2, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            value_str = message.value
        
        return f"""
📨 Message reçu:
   🕐 Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
   🏷️  Topic: {message.topic}
   📊 Partition: {message.partition}
   🔢 Offset: {message.offset}
   🔑 Key: {message.key}
   📝 Value:
{value_str}
{"="*60}"""
    
    def consume_messages(self, timeout_ms=1000):
        """Consommer les messages en continu"""
        if not self.consumer:
            print("❌ Consommateur non initialisé")
            return False
        
        print(f"\n🔍 Écoute des messages sur '{self.topic}'...")
        print("💡 Appuyez sur Ctrl+C pour arrêter\n")
        
        message_count = 0
        
        try:
            while self.running:
                # Poll pour les nouveaux messages
                message_batch = self.consumer.poll(timeout_ms=timeout_ms)
                
                if message_batch:
                    for topic_partition, messages in message_batch.items():
                        for message in messages:
                            message_count += 1
                            print(self.format_message(message))
                            
                            # Affichage du compteur
                            print(f"📊 Messages reçus: {message_count}")
                
                # Petit délai pour éviter de surcharger le CPU
                if not message_batch:
                    continue
                    
        except KafkaError as e:
            print(f"❌ Erreur Kafka: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return False
        finally:
            if self.consumer:
                self.consumer.close()
                print(f"\n✅ Consommateur fermé. Total messages traités: {message_count}")
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description="Exercice 2 - Consommateur Kafka Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python consumer.py weather_stream
  python consumer.py weather_stream --from-beginning
  python consumer.py weather_stream --server localhost:9092 --group my-group
  python consumer.py weather_stream --timeout 5000
        """
    )
    
    parser.add_argument('topic', 
                       help='Nom du topic Kafka à consommer')
    parser.add_argument('--server', 
                       default='localhost:9092',
                       help='Adresse du serveur Kafka (défaut: localhost:9092)')
    parser.add_argument('--group', 
                       default='python-consumer-group',
                       help='ID du groupe de consommateurs (défaut: python-consumer-group)')
    parser.add_argument('--from-beginning', 
                       action='store_true',
                       help='Lire les messages depuis le début du topic')
    parser.add_argument('--timeout', 
                       type=int, 
                       default=1000,
                       help='Timeout en millisecondes pour poll (défaut: 1000)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🐍 EXERCICE 2 - CONSOMMATEUR KAFKA PYTHON")
    print("="*60)
    
    # Création et démarrage du consommateur
    consumer_app = KafkaConsumerApp(
        topic=args.topic,
        bootstrap_servers=args.server,
        group_id=args.group
    )
    
    if consumer_app.create_consumer(from_beginning=args.from_beginning):
        success = consumer_app.consume_messages(timeout_ms=args.timeout)
        sys.exit(0 if success else 1)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()