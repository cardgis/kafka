# Exercise 6: Geographic Weather Streaming

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
