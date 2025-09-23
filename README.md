# Exercise 7: HDFS Consumer & Storage

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
