#!/usr/bin/env python3
"""
Simple Branch Fix Script
Copy docker-compose.yml and essential files to all exercise branches
"""

import subprocess
import shutil
from pathlib import Path

def run_git_command(command, description):
    """Execute git command"""
    print(f"🔧 {description}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print("✅", result.stdout.strip())
    return result.returncode == 0

def copy_files_to_all_branches():
    """Copy essential files to all branches"""
    
    exercises = ['exercice2', 'exercice3', 'exercice4', 'exercice5', 'exercice6', 'exercice7', 'exercice8']
    
    # Store docker-compose.yml content
    docker_compose_content = """version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    hostname: zookeeper
    container_name: kafka-zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
      - zookeeper-logs:/var/lib/zookeeper/log

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    hostname: kafka
    container_name: kafka-broker
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "9101:9101"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_JMX_PORT: 9101
      KAFKA_JMX_HOSTNAME: localhost
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
    volumes:
      - kafka-data:/var/lib/kafka/data

volumes:
  zookeeper-data:
  zookeeper-logs:
  kafka-data:"""

    requirements_content = """kafka-python==2.0.2
requests==2.31.0
pyspark==3.5.0
plotly==5.17.0
streamlit==1.29.0
pandas==2.1.4
matplotlib==3.8.2
numpy==1.25.2"""

    for exercise in exercises:
        print(f"\\n📁 Fixing {exercise}...")
        
        # Switch to branch
        run_git_command(f'git checkout {exercise}', f'Switching to {exercise}')
        
        # Create docker-compose.yml
        with open('docker-compose.yml', 'w', encoding='utf-8') as f:
            f.write(docker_compose_content)
        print("   ✅ Created docker-compose.yml")
        
        # Create requirements.txt
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        print("   ✅ Created requirements.txt")
        
        # Commit changes
        run_git_command('git add .', 'Adding files')
        run_git_command(f'git commit -m "Add Docker setup to {exercise}"', f'Committing {exercise}')

    # Return to exercice1
    run_git_command('git checkout exercice1', 'Returning to exercice1')
    
    print("\\n🚀 Pushing all branches...")
    run_git_command('git push origin --all --force', 'Pushing all branches')
    
    print("\\n✅ All branches now have Docker setup!")

if __name__ == "__main__":
    copy_files_to_all_branches()