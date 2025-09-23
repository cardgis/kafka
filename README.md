# Exercise 1: Kafka & ZooKeeper Setup

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
