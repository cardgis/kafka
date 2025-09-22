"""
Exercice 2 - Consommateur Kafka en Python
Consommateur qui lit les messages depuis un topic Kafka passé en argument
"""

import sys
import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import argparse
import logging

def setup_logging():
    """Configure le logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def create_consumer(topic_name, bootstrap_servers='localhost:9092'):
    """
    Crée un consommateur Kafka
    
    Args:
        topic_name (str): Nom du topic Kafka
        bootstrap_servers (str): Serveurs Kafka
        
    Returns:
        KafkaConsumer: Instance du consommateur
    """
    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=[bootstrap_servers],
            auto_offset_reset='latest',  # Commence par les nouveaux messages
            enable_auto_commit=True,
            group_id='exercice2-consumer-group',
            value_deserializer=lambda x: x.decode('utf-8') if x else None,
            consumer_timeout_ms=1000  # Timeout d'1 seconde
        )
        logging.info(f"Consommateur créé pour le topic '{topic_name}'")
        return consumer
    except Exception as e:
        logging.error(f"Erreur lors de la création du consommateur: {e}")
        return None

def consume_messages(consumer, topic_name):
    """
    Consomme les messages du topic
    
    Args:
        consumer (KafkaConsumer): Instance du consommateur
        topic_name (str): Nom du topic
    """
    logging.info(f"🎧 Écoute du topic '{topic_name}' en cours...")
    logging.info("Appuyez sur Ctrl+C pour arrêter")
    
    try:
        message_count = 0
        for message in consumer:
            message_count += 1
            
            # Affichage du message
            print(f"\n📨 Message #{message_count}")
            print(f"   Topic: {message.topic}")
            print(f"   Partition: {message.partition}")
            print(f"   Offset: {message.offset}")
            print(f"   Timestamp: {message.timestamp}")
            print(f"   Value: {message.value}")
            
            # Tentative de parsing JSON
            try:
                json_data = json.loads(message.value)
                print(f"   JSON: {json.dumps(json_data, indent=2)}")
            except (json.JSONDecodeError, TypeError):
                print(f"   Raw: {message.value}")
                
    except KeyboardInterrupt:
        logging.info("🛑 Arrêt du consommateur demandé par l'utilisateur")
    except KafkaError as e:
        logging.error(f"Erreur Kafka: {e}")
    except Exception as e:
        logging.error(f"Erreur inattendue: {e}")
    finally:
        consumer.close()
        logging.info("Consommateur fermé")

def main():
    """Fonction principale"""
    # Configuration des arguments
    parser = argparse.ArgumentParser(description='Consommateur Kafka pour l\'exercice 2')
    parser.add_argument('topic', help='Nom du topic Kafka à consommer')
    parser.add_argument('--server', default='localhost:9092', 
                       help='Serveur Kafka (défaut: localhost:9092)')
    
    args = parser.parse_args()
    
    # Configuration du logging
    setup_logging()
    
    # Création et lancement du consommateur
    consumer = create_consumer(args.topic, args.server)
    if consumer:
        consume_messages(consumer, args.topic)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()