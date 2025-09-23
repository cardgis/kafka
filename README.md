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

# Check services
docker ps

# View logs
docker-compose logs kafka-broker
docker-compose logs kafka-zookeeper
```

## Services
- **Kafka Broker**: localhost:9092
- **ZooKeeper**: localhost:2181

## Test
```bash
# Create topic
docker exec kafka-broker kafka-topics --create --topic test --bootstrap-server localhost:9092

# Send message
echo "Hello Kafka" | docker exec -i kafka-broker kafka-console-producer --bootstrap-server localhost:9092 --topic test

# Read messages
docker exec kafka-broker kafka-console-consumer --bootstrap-server localhost:9092 --topic test --from-beginning
```

## Next Steps
Continue with Exercise 2: Basic Producer/Consumer
