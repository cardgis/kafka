#!/usr/bin/env python3
"""
Git Branch Organization Script
Creates 8 specialized branches for each Kafka exercise
"""

import subprocess
import os
from pathlib import Path

def run_git_command(command, description):
    """Execute git command and print results"""
    print(f"🔧 {description}")
    print(f"Command: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("Output:", result.stdout.strip())
    if result.stderr:
        print("Error:", result.stderr.strip())
    
    return result.returncode == 0

def create_exercise_branches():
    """Create all exercise branches with appropriate content"""
    
    # Definition of exercises and their main files
    exercises = {
        'exercice1': {
            'description': 'Setup Kafka & ZooKeeper',
            'files': [
                'docker-compose.yml',
                'EXERCICE1_BRANCH.md',
                'requirements.txt'
            ],
            'new_files': {
                'README.md': """# Exercise 1: Kafka & ZooKeeper Setup

## Objective
Set up a Kafka cluster with ZooKeeper using Docker for local development.

## Files
- `docker-compose.yml` - Docker services configuration
- `requirements.txt` - Python dependencies

## Quick Start
```bash
# Start services
docker-compose up -d

# Verify services
docker ps
```

## Topics Created
- `weather_stream` - Raw weather data
- `weather_transformed` - Processed data with alerts
- `weather_aggregates` - Aggregated metrics

## Next Steps
Continue with Exercise 2: Basic Producer/Consumer
""",
                'test_exercise1.py': """#!/usr/bin/env python3
import subprocess
import time

def test_exercise1():
    print("Testing Exercise 1: Docker Kafka Setup")
    
    # Test Docker services
    result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\\t{{.Status}}'], 
                          capture_output=True, text=True)
    
    if 'kafka-broker' in result.stdout:
        print("✅ Kafka broker running")
    else:
        print("❌ Kafka broker not found")
    
    if 'kafka-zookeeper' in result.stdout:
        print("✅ ZooKeeper running")
    else:
        print("❌ ZooKeeper not found")

if __name__ == "__main__":
    test_exercise1()
"""
            }
        },
        
        'exercice2': {
            'description': 'Basic Producer/Consumer',
            'files': [
                'docker-compose.yml',
                'consumer.py',
                'requirements.txt'
            ],
            'new_files': {
                'README.md': """# Exercise 2: Basic Producer/Consumer

## Objective
Create basic Kafka producer and consumer scripts in Python.

## Files
- `consumer.py` - Generic Kafka consumer
- `simple_producer.py` - Basic message producer

## Usage
```bash
# Start consumer
python consumer.py weather_stream

# Send test message
python simple_producer.py
```
""",
                'simple_producer.py': """#!/usr/bin/env python3
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
"""
            }
        },
        
        'exercice3': {
            'description': 'Weather Data Streaming',
            'files': [
                'docker-compose.yml',
                'consumer.py',
                'current_weather.py',
                'requirements.txt'
            ],
            'new_files': {
                'README.md': """# Exercise 3: Weather Data Streaming

## Objective
Stream real weather data from Open-Meteo API to Kafka.

## Files
- `current_weather.py` - Weather data producer
- `consumer.py` - Message consumer

## Usage
```bash
# Stream weather data
python current_weather.py 48.8566 2.3522  # Paris coordinates

# Consume weather stream
python consumer.py weather_stream
```
"""
            }
        },
        
        'exercice4': {
            'description': 'Data Transformation & Alerts',
            'files': [
                'docker-compose.yml',
                'consumer.py',
                'current_weather.py',
                'weather_transformer_simple.py',
                'requirements.txt'
            ],
            'new_files': {
                'README.md': """# Exercise 4: Data Transformation & Alerts

## Objective
Transform weather data and generate alerts based on thresholds.

## Files
- `weather_transformer_simple.py` - Data transformer with alerts
- `current_weather.py` - Weather data producer

## Alert Levels
- **Wind**: Level 1 (10-20 m/s), Level 2 (≥20 m/s)
- **Heat**: Level 1 (25-35°C), Level 2 (≥35°C)

## Usage
```bash
# Start transformer
python weather_transformer_simple.py --mode stream

# Generate weather data
python current_weather.py 48.8566 2.3522

# Check transformed data
python consumer.py weather_transformed
```
"""
            }
        },
        
        'exercice5': {
            'description': 'Real-time Aggregates',
            'files': [
                'docker-compose.yml',
                'consumer.py',
                'current_weather.py',
                'weather_transformer_simple.py',
                'weather_aggregator.py',
                'requirements.txt'
            ],
            'new_files': {
                'README.md': """# Exercise 5: Real-time Aggregates

## Objective
Implement sliding window aggregation for weather metrics.

## Files
- `weather_aggregator.py` - Sliding window processor
- `weather_transformer_simple.py` - Alert generator

## Metrics Calculated
- Temperature statistics (min, max, avg)
- Wind speed metrics
- Alert counts by level and type
- Time-based windows

## Usage
```bash
# Start aggregator
python weather_aggregator.py --window-minutes 5

# Check aggregates
python consumer.py weather_aggregates
```
"""
            }
        },
        
        'exercice6': {
            'description': 'Geographic Weather Streaming',
            'files': [
                'docker-compose.yml',
                'consumer.py',
                'extended_weather_producer.py',
                'weather_transformer_simple.py',
                'requirements.txt',
                'EXERCISE6_SUMMARY.md'
            ],
            'new_files': {
                'README.md': """# Exercise 6: Geographic Weather Streaming

## Objective
Enhance producers with geocoding to accept city/country input.

## Files
- `extended_weather_producer.py` - City/country weather producer
- Geocoding integration with Open-Meteo API

## Usage
```bash
# Generate weather for cities
python extended_weather_producer.py Paris France
python extended_weather_producer.py "New York" "United States"
python extended_weather_producer.py Tokyo Japan
```

## Enhanced Data Format
Messages now include complete location metadata for HDFS partitioning.
"""
            }
        },
        
        'exercice7': {
            'description': 'HDFS Consumer & Storage',
            'files': [
                'docker-compose.yml',
                'consumer.py',
                'extended_weather_producer.py',
                'weather_transformer_simple.py',
                'hdfs_consumer.py',
                'hdfs_analyzer.py',
                'hdfs_health_check.py',
                'requirements.txt',
                'EXERCISE7_SUMMARY.md'
            ],
            'new_files': {
                'README.md': """# Exercise 7: HDFS Consumer & Storage

## Objective
Store weather alerts in organized HDFS structure.

## Files
- `hdfs_consumer.py` - HDFS storage consumer
- `hdfs_analyzer.py` - Storage analytics
- `hdfs_health_check.py` - System diagnostics

## Storage Structure
```
hdfs-data/
├── {country}/
│   └── {city}/
│       └── alerts_*.json
```

## Usage
```bash
# Start HDFS consumer
python hdfs_consumer.py

# Check storage health
python hdfs_health_check.py

# Analyze stored data
python hdfs_analyzer.py
```
"""
            }
        },
        
        'exercice8': {
            'description': 'BI Visualizations & Analytics',
            'files': [
                'docker-compose.yml',
                'consumer.py',
                'extended_weather_producer.py',
                'hdfs_consumer.py',
                'hdfs_analyzer.py',
                'requirements.txt'
            ],
            'new_files': {
                'README.md': """# Exercise 8: BI Visualizations & Analytics

## Objective
Create data visualizations and business intelligence dashboards.

## Planned Features
- Temperature evolution charts
- Alert distribution analysis
- Geographic heat maps
- Real-time dashboards
- Historical trend analysis

## Technology Stack
- Matplotlib/Plotly for charts
- Streamlit for web dashboard
- Pandas for data analysis

## Usage
```bash
# Start visualization dashboard
python weather_dashboard.py

# Generate analysis reports
python weather_analytics.py
```

## Data Sources
- HDFS stored alerts
- Real-time Kafka streams
- Aggregated metrics
""",
                'weather_dashboard.py': """#!/usr/bin/env python3
# Weather Dashboard - Exercise 8
# TODO: Implement visualization dashboard

import streamlit as st
import pandas as pd
import plotly.express as px

def main():
    st.title("🌤️ Weather Analytics Dashboard")
    st.write("Exercise 8: BI Visualizations & Analytics")
    
    st.info("Dashboard implementation coming soon!")
    
    # Placeholder for future charts
    st.subheader("📊 Temperature Trends")
    st.subheader("🚨 Alert Distribution")
    st.subheader("🗺️ Geographic Analysis")

if __name__ == "__main__":
    main()
""",
                'weather_analytics.py': """#!/usr/bin/env python3
# Weather Analytics - Exercise 8
# TODO: Implement data analysis

def analyze_weather_patterns():
    print("🔍 Weather Pattern Analysis")
    print("TODO: Implement analytics")

def generate_reports():
    print("📊 Generating Weather Reports")
    print("TODO: Implement reporting")

if __name__ == "__main__":
    analyze_weather_patterns()
    generate_reports()
"""
            }
        }
    }
    
    print("🚀 Creating Exercise Branches for Kafka Project")
    print("=" * 60)
    
    # Get current branch
    current_branch = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True).stdout.strip()
    print(f"Current branch: {current_branch}")
    
    # Store current state
    print("\n1. Storing current complete state...")
    run_git_command('git add .', 'Adding all changes')
    run_git_command('git commit -m "Complete project state before branch organization"', 
                   'Committing complete state')
    
    # Create and setup each exercise branch
    for exercise, config in exercises.items():
        print(f"\n2. Creating branch: {exercise}")
        print(f"   Description: {config['description']}")
        
        # Create branch from current state
        if exercise != current_branch:
            run_git_command(f'git checkout -b {exercise}', f'Creating branch {exercise}')
        
        # Remove files not needed for this exercise
        all_exercise_files = set()
        for ex_config in exercises.values():
            all_exercise_files.update(ex_config['files'])
            all_exercise_files.update(ex_config.get('new_files', {}).keys())
        
        current_files = set()
        for file_path in Path('.').rglob('*.py'):
            current_files.add(str(file_path))
        for file_path in Path('.').rglob('*.md'):
            current_files.add(str(file_path))
        for file_path in Path('.').rglob('*.yml'):
            current_files.add(str(file_path))
        for file_path in Path('.').rglob('*.txt'):
            current_files.add(str(file_path))
        
        # Keep only files needed for this exercise
        files_to_keep = set(config['files'])
        files_to_keep.update(config.get('new_files', {}).keys())
        
        # Remove unnecessary files
        for file_path in current_files:
            if os.path.basename(file_path) not in files_to_keep:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"   Removed: {file_path}")
        
        # Create new files for this exercise
        for filename, content in config.get('new_files', {}).items():
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   Created: {filename}")
        
        # Update EXERCICE1_BRANCH.md to reflect current exercise
        if exercise != 'exercice1' and 'EXERCICE1_BRANCH.md' in config['files']:
            # Replace with exercise-specific README
            if os.path.exists('EXERCICE1_BRANCH.md'):
                os.remove('EXERCICE1_BRANCH.md')
        
        # Commit changes for this exercise
        run_git_command('git add .', f'Adding {exercise} files')
        run_git_command(f'git commit -m "Setup {exercise}: {config["description"]}"', 
                       f'Committing {exercise} setup')
    
    # Return to original branch
    run_git_command(f'git checkout {current_branch}', f'Returning to {current_branch}')
    
    print("\n" + "=" * 60)
    print("✅ BRANCH ORGANIZATION COMPLETE!")
    print("=" * 60)
    
    # Show all branches
    print("\n📋 Created branches:")
    subprocess.run(['git', 'branch', '-a'], check=True)
    
    print(f"\n🎯 Navigation:")
    for exercise, config in exercises.items():
        print(f"  git checkout {exercise}  # {config['description']}")
    
    print(f"\n📚 To push all branches:")
    print(f"  git push origin --all")

if __name__ == "__main__":
    create_exercise_branches()