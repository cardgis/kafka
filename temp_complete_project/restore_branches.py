#!/usr/bin/env python3
"""
Restore Branch Content Script
Properly restores the correct files to each exercise branch
"""

import subprocess
import os
import shutil
from pathlib import Path

def run_git_command(command, description):
    """Execute git command and print results"""
    print(f"🔧 {description}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("✅", result.stdout.strip())
    if result.stderr and "Already on" not in result.stderr:
        print("⚠️", result.stderr.strip())
    
    return result.returncode == 0

def restore_branch_content():
    """Restore correct content to each branch"""
    
    # Map exercises to their required files from the complete project
    exercise_files = {
        'exercice1': [
            'docker-compose.yml',
            'requirements.txt'
        ],
        'exercice2': [
            'docker-compose.yml',
            'requirements.txt',
            'consumer.py'
        ],
        'exercice3': [
            'docker-compose.yml',
            'requirements.txt',
            'consumer.py',
            'current_weather.py'
        ],
        'exercice4': [
            'docker-compose.yml',
            'requirements.txt',
            'consumer.py',
            'current_weather.py',
            'weather_transformer_simple.py'
        ],
        'exercice5': [
            'docker-compose.yml',
            'requirements.txt',
            'consumer.py',
            'current_weather.py',
            'weather_transformer_simple.py',
            'weather_aggregator.py'
        ],
        'exercice6': [
            'docker-compose.yml',
            'requirements.txt',
            'consumer.py',
            'extended_weather_producer.py',
            'weather_transformer_simple.py',
            'EXERCISE6_SUMMARY.md'
        ],
        'exercice7': [
            'docker-compose.yml',
            'requirements.txt',
            'consumer.py',
            'extended_weather_producer.py',
            'weather_transformer_simple.py',
            'hdfs_consumer.py',
            'hdfs_analyzer.py',
            'hdfs_health_check.py',
            'EXERCISE7_SUMMARY.md'
        ],
        'exercice8': [
            'docker-compose.yml',
            'requirements.txt',
            'consumer.py',
            'extended_weather_producer.py',
            'hdfs_consumer.py',
            'hdfs_analyzer.py'
        ]
    }
    
    print("🔄 Restoring correct content to each exercise branch")
    print("=" * 60)
    
    # First, go to main branch to get all files
    run_git_command('git checkout main', 'Switching to main branch with all files')
    
    # Store all files in temp directory
    temp_dir = Path('temp_complete_project')
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # Copy all current files to temp
    for item in Path('.').iterdir():
        if item.name not in ['.git', 'temp_complete_project', '__pycache__']:
            if item.is_file():
                shutil.copy2(item, temp_dir / item.name)
            elif item.is_dir():
                shutil.copytree(item, temp_dir / item.name)
    
    print(f"📦 Stored complete project in {temp_dir}")
    
    # Now restore each branch
    for exercise, required_files in exercise_files.items():
        print(f"\n🔧 Restoring {exercise}")
        
        # Switch to exercise branch
        run_git_command(f'git checkout {exercise}', f'Switching to {exercise}')
        
        # Clear current directory (except .git and temp)
        for item in Path('.').iterdir():
            if item.name not in ['.git', 'temp_complete_project', '__pycache__']:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        
        # Copy required files from temp
        for filename in required_files:
            src_file = temp_dir / filename
            if src_file.exists():
                if src_file.is_file():
                    shutil.copy2(src_file, filename)
                    print(f"   ✅ Restored: {filename}")
                elif src_file.is_dir():
                    shutil.copytree(src_file, filename)
                    print(f"   ✅ Restored directory: {filename}")
            else:
                print(f"   ⚠️ Missing: {filename}")
        
        # Create exercise-specific README
        readme_content = create_exercise_readme(exercise)
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"   ✅ Created: README.md")
        
        # Add and commit changes
        run_git_command('git add .', f'Adding {exercise} content')
        run_git_command(f'git commit -m "Restore complete {exercise} content"', 
                       f'Committing {exercise} restoration')
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    # Return to exercice1
    run_git_command('git checkout exercice1', 'Returning to exercice1')
    
    print("\n" + "=" * 60)
    print("✅ BRANCH CONTENT RESTORATION COMPLETE!")
    print("=" * 60)

def create_exercise_readme(exercise):
    """Create README content for each exercise"""
    readmes = {
        'exercice1': """# Exercise 1: Kafka & ZooKeeper Setup

## Objective
Set up a Kafka cluster with ZooKeeper using Docker for local development.

## Files
- `docker-compose.yml` - Docker services configuration
- `requirements.txt` - Python dependencies

## Quick Start
```bash
# Start services
docker-compose up -d

# Check services
docker ps

# View logs
docker-compose logs kafka-broker
docker-compose logs kafka-zookeeper
```

## Services
- **Kafka Broker**: localhost:9092
- **ZooKeeper**: localhost:2181

## Next Steps
Continue with Exercise 2: Basic Producer/Consumer
""",

        'exercice2': """# Exercise 2: Basic Producer/Consumer

## Objective
Create basic Kafka producer and consumer scripts in Python.

## Files
- `consumer.py` - Generic Kafka consumer
- `docker-compose.yml` - Kafka infrastructure

## Usage
```bash
# Start consumer (in one terminal)
python consumer.py weather_stream

# Create a simple producer to test
# (See Exercise 3 for weather producer)
```

## Key Concepts
- Kafka Consumer API
- Topic subscription
- Message consumption patterns
""",

        'exercice3': """# Exercise 3: Weather Data Streaming

## Objective
Stream real weather data from Open-Meteo API to Kafka.

## Files
- `current_weather.py` - Weather data producer
- `consumer.py` - Message consumer

## Usage
```bash
# Stream weather data (coordinates: latitude longitude)
python current_weather.py 48.8566 2.3522  # Paris
python current_weather.py 40.7128 -74.0060  # New York

# Consume weather stream
python consumer.py weather_stream
```

## Data Source
- Open-Meteo Weather API
- Real-time weather conditions
- Coordinates-based location
""",

        'exercice4': """# Exercise 4: Data Transformation & Alerts

## Objective
Transform weather data and generate alerts based on thresholds.

## Files
- `weather_transformer_simple.py` - Data transformer with alerts
- `current_weather.py` - Weather data producer
- `consumer.py` - Message consumer

## Alert System
- **Wind Alerts**: 
  - Level 1: 10-20 m/s
  - Level 2: ≥20 m/s
- **Heat Alerts**: 
  - Level 1: 25-35°C
  - Level 2: ≥35°C

## Usage
```bash
# Start transformer
python weather_transformer_simple.py --mode stream

# Generate weather data
python current_weather.py 48.8566 2.3522

# Check transformed data
python consumer.py weather_transformed
```
""",

        'exercice5': """# Exercise 5: Real-time Aggregates

## Objective
Implement sliding window aggregation for weather metrics.

## Files
- `weather_aggregator.py` - Sliding window processor
- `weather_transformer_simple.py` - Alert generator
- `current_weather.py` - Weather producer

## Metrics Calculated
- Temperature statistics (min, max, avg)
- Wind speed metrics
- Alert counts by level and type
- Time-based sliding windows

## Usage
```bash
# Start aggregator
python weather_aggregator.py --window-minutes 5

# Generate weather data
python current_weather.py 48.8566 2.3522

# Check aggregates
python consumer.py weather_aggregates
```
""",

        'exercice6': """# Exercise 6: Geographic Weather Streaming

## Objective
Enhance producers with geocoding to accept city/country input.

## Files
- `extended_weather_producer.py` - City/country weather producer
- `weather_transformer_simple.py` - Alert processor
- `EXERCISE6_SUMMARY.md` - Detailed implementation notes

## Enhanced Features
- City/country input instead of coordinates
- Geocoding via Open-Meteo API
- Complete location metadata
- Unicode support for international cities

## Usage
```bash
# Generate weather for cities
python extended_weather_producer.py Paris France
python extended_weather_producer.py "New York" "United States"
python extended_weather_producer.py Tokyo Japan
python extended_weather_producer.py Москва Россия  # Moscow, Russia
```

## Data Format
Messages now include complete location metadata for downstream processing.
""",

        'exercice7': """# Exercise 7: HDFS Consumer & Storage

## Objective
Store weather alerts in organized HDFS structure with geographic partitioning.

## Files
- `hdfs_consumer.py` - HDFS storage consumer
- `hdfs_analyzer.py` - Storage analytics
- `hdfs_health_check.py` - System diagnostics
- `EXERCISE7_SUMMARY.md` - Implementation details

## Storage Structure
```
hdfs-data/
├── {country}/
│   └── {city}/
│       └── alerts_YYYYMMDD_HHMMSS.json
```

## Features
- Geographic partitioning by country/city
- Alert filtering (level 1+ only)
- JSON storage with metadata
- Comprehensive health monitoring

## Usage
```bash
# Start HDFS consumer
python hdfs_consumer.py

# Check storage health
python hdfs_health_check.py

# Analyze stored data
python hdfs_analyzer.py

# Generate test data
python extended_weather_producer.py Paris France
```

## Monitoring
The health check system provides 6-level diagnostics for HDFS operations.
""",

        'exercice8': """# Exercise 8: BI Visualizations & Analytics

## Objective
Create data visualizations and business intelligence dashboards.

## Files
- `weather_dashboard.py` - Streamlit dashboard (to be implemented)
- `weather_analytics.py` - Analysis scripts (to be implemented)
- Complete pipeline infrastructure

## Planned Features
- 📊 Temperature evolution charts
- 🚨 Alert distribution analysis
- 🗺️ Geographic heat maps
- ⏰ Real-time dashboards
- 📈 Historical trend analysis

## Technology Stack
- Matplotlib/Plotly for charts
- Streamlit for web dashboard
- Pandas for data analysis
- HDFS stored data as source

## Usage (Future)
```bash
# Start visualization dashboard
streamlit run weather_dashboard.py

# Generate analysis reports
python weather_analytics.py
```

## Data Sources
- HDFS stored alerts from Exercise 7
- Real-time Kafka streams
- Aggregated metrics from Exercise 5

## Implementation Status
🚧 **Exercise 8 is prepared for implementation** 
The infrastructure is ready, visualization components can be built on top of the established data pipeline.
"""
    }
    
    return readmes.get(exercise, f"# {exercise}\n\nExercise content here.")

if __name__ == "__main__":
    restore_branch_content()