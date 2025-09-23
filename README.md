# Exercise 6: Geographic Weather Streaming

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
