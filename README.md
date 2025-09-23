# Exercise 7: HDFS Consumer & Storage

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
