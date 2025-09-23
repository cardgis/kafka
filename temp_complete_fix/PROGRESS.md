# Kafka Weather Streaming Exercises

## Setup Status ✅
- **Docker Kafka & ZooKeeper**: Running on ports 9092 & 2181
- **Python Environment**: Configured with kafka-python and requests
- **Topic Created**: `weather_stream`

## Completed Exercises

### Exercise 1: Simple Kafka Producer ✅
**Goal**: Create topic and send static message
```bash
# Topic created successfully
docker exec kafka-broker kafka-topics --bootstrap-server localhost:9092 --list

# Static message sent
echo '{"msg": "Hello Kafka"}' | docker exec -i kafka-broker kafka-console-producer --bootstrap-server localhost:9092 --topic weather_stream
```

### Exercise 2: Python Kafka Consumer ✅
**Goal**: Create Python consumer script
```bash
# Run the consumer
C:/Big_data/.venv/Scripts/python.exe C:\Big_data\kafka\consumer.py weather_stream

# Features:
- Accepts topic name as argument
- Real-time message display
- JSON formatting
- Error handling
```

### Exercise 3: Weather Data Streaming ✅
**Goal**: Stream real weather data from Open-Meteo API
```bash
# Send single weather message for Paris
C:/Big_data/.venv/Scripts/python.exe C:\Big_data\kafka\current_weather.py 48.8566 2.3522

# Stream continuously (optional)
C:/Big_data/.venv/Scripts/python.exe C:\Big_data\kafka\current_weather.py 48.8566 2.3522 --stream --interval 30

# Features:
- Fetches real weather data from Open-Meteo API
- Structured JSON with temperature, wind, humidity
- Single message or continuous streaming modes
- Proper error handling
```

## Verification Commands

### Check all messages in topic:
```bash
docker exec kafka-broker kafka-console-consumer --bootstrap-server localhost:9092 --topic weather_stream --from-beginning --max-messages 10
```

### Check Docker services status:
```bash
docker-compose ps
```

### Test network connectivity:
```bash
netstat -an | findstr ":9092"
netstat -an | findstr ":2181"
```

## Next Steps (Remaining Exercises)

### Exercise 4: Data Transformation with Spark
- Process weather_stream with Spark
- Create weather_transformed topic
- Implement wind and heat alerts
- Add event_time, alert levels

### Exercise 5: Real-time Aggregates
- Sliding window analysis (1-5 minutes)
- Calculate alert counts, temperature stats
- Group by location/region

### Exercise 6: Extended Producer
- Accept city/country as arguments
- Use geocoding API for coordinates
- Include location metadata

### Exercise 7: HDFS Storage
- Save alerts to HDFS structure
- Partition by country/city
- JSON format storage

### Exercise 8: Visualization
- Temperature/wind evolution charts
- Alert distribution analysis
- Most frequent weather codes by country

## Current Status
✅ **3/8 exercises completed**
🟨 **Docker setup working perfectly**
🟨 **Ready for Spark integration (Exercise 4)**