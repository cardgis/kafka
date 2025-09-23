# Exercise 2: Basic Producer/Consumer

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
echo '{"test": "Hello from Python"}' | docker exec -i kafka-broker kafka-console-producer --bootstrap-server localhost:9092 --topic weather_stream
```

## Key Concepts
- Kafka Consumer API
- Topic subscription
- Message consumption patterns
