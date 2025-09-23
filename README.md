# Exercise 5: Real-time Aggregates

## Objective
Implement sliding window aggregation for weather metrics.

## Files
- `weather_aggregator.py` - Sliding window processor
- `weather_transformer_simple.py` - Alert generator
- `current_weather.py` - Weather producer

## Metrics Calculated
- Temperature statistics (min, max, avg)
- Wind speed metrics
- Alert counts by level and type
- Time-based sliding windows

## Usage
```bash
# Start aggregator
python weather_aggregator.py --window-minutes 5

# Generate weather data
python current_weather.py 48.8566 2.3522

# Check aggregates
python consumer.py weather_aggregates
```
