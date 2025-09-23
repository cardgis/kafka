# Exercise 3: Weather Data Streaming

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
