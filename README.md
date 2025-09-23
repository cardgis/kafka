# Exercise 4: Data Transformation & Alerts

## Objective
Transform weather data and generate alerts based on thresholds.

## Files
- `weather_transformer_simple.py` - Data transformer with alerts
- `current_weather.py` - Weather data producer

## Alert Levels
- **Wind**: Level 1 (10-20 m/s), Level 2 (≥20 m/s)
- **Heat**: Level 1 (25-35°C), Level 2 (≥35°C)

## Usage
```bash
# Start transformer
python weather_transformer_simple.py --mode stream

# Generate weather data
python current_weather.py 48.8566 2.3522

# Check transformed data
python consumer.py weather_transformed
```
