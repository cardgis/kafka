# Exercise 3: Weather Data Streaming

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
