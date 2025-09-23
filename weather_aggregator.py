#!/usr/bin/env python3
"""
Exercise 5: Real-time Aggregates with Sliding Windows
Calculate real-time metrics on weather_transformed data using time windows.

Features:
- Sliding window aggregation (1 or 5 minutes)
- Alert counts by level and type
- Temperature statistics (avg, min, max)
- Alert counts by location/region

Usage: python weather_aggregator.py [--window-minutes 1]
"""

import json
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import argparse
import threading
from statistics import mean

class SlidingWindowAggregator:
    def __init__(self, kafka_servers='localhost:9092', input_topic='weather_transformed', 
                 output_topic='weather_aggregates', window_minutes=1):
        self.kafka_servers = kafka_servers
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.window_size = timedelta(minutes=window_minutes)
        
        # Data storage for sliding windows
        self.data_window = deque()  # Store (timestamp, data) tuples
        self.lock = threading.Lock()
        
        # Initialize Kafka connections
        self._init_kafka()
        
        # Start background window cleanup
        self.running = True
        self.cleanup_thread = threading.Thread(target=self._cleanup_old_data, daemon=True)
        self.cleanup_thread.start()
    
    def _init_kafka(self):
        """Initialize Kafka consumer and producer"""
        try:
            self.consumer = KafkaConsumer(
                self.input_topic,
                bootstrap_servers=self.kafka_servers,
                auto_offset_reset='latest',  # Start from latest for real-time
                enable_auto_commit=True,
                group_id='weather-aggregator-group',
                value_deserializer=lambda x: x.decode('utf-8') if x else None
            )
            
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                acks='all'
            )
            
            print("✅ Kafka connections initialized successfully")
            
        except KafkaError as e:
            print(f"❌ Failed to initialize Kafka: {e}")
            raise
    
    def _cleanup_old_data(self):
        """Background thread to remove data older than window size"""
        while self.running:
            try:
                time.sleep(10)  # Check every 10 seconds
                cutoff_time = datetime.utcnow() - self.window_size
                
                with self.lock:
                    # Remove old data points
                    while (self.data_window and 
                           self.data_window[0][0] < cutoff_time):
                        self.data_window.popleft()
                        
            except Exception as e:
                print(f"⚠️ Error in cleanup thread: {e}")
    
    def add_data_point(self, data):
        """Add a new data point to the sliding window"""
        try:
            timestamp = datetime.utcnow()
            
            with self.lock:
                self.data_window.append((timestamp, data))
                
                # Also remove very old data (beyond 2x window size)
                cutoff_time = timestamp - (self.window_size * 2)
                while (self.data_window and 
                       self.data_window[0][0] < cutoff_time):
                    self.data_window.popleft()
                    
        except Exception as e:
            print(f"⚠️ Error adding data point: {e}")
    
    def calculate_aggregates(self):
        """Calculate aggregates for the current window"""
        try:
            current_time = datetime.utcnow()
            cutoff_time = current_time - self.window_size
            
            with self.lock:
                # Get data within the window
                window_data = [
                    data for timestamp, data in self.data_window
                    if timestamp >= cutoff_time
                ]
            
            if not window_data:
                return None
            
            # Initialize counters
            wind_alerts = defaultdict(int)  # level -> count
            heat_alerts = defaultdict(int)  # level -> count
            temperatures = []
            wind_speeds = []
            location_alerts = defaultdict(lambda: defaultdict(int))  # location -> alert_type -> count
            
            # Process each data point
            for data in window_data:
                # Alert counts
                wind_level = data.get('wind_alert_level')
                heat_level = data.get('heat_alert_level')
                
                if wind_level:
                    wind_alerts[wind_level] += 1
                if heat_level:
                    heat_alerts[heat_level] += 1
                
                # Temperature and wind data
                temp = data.get('temperature')
                wind = data.get('windspeed')
                
                if temp is not None:
                    temperatures.append(temp)
                if wind is not None:
                    wind_speeds.append(wind)
                
                # Location-based alerts
                lat = data.get('latitude')
                lon = data.get('longitude')
                if lat is not None and lon is not None:
                    location_key = f"{lat:.2f},{lon:.2f}"
                    
                    if wind_level and wind_level != 'level_0':
                        location_alerts[location_key]['wind_alerts'] += 1
                    if heat_level and heat_level != 'level_0':
                        location_alerts[location_key]['heat_alerts'] += 1
            
            # Calculate temperature statistics
            temp_stats = {}
            if temperatures:
                temp_stats = {
                    'avg': round(mean(temperatures), 2),
                    'min': min(temperatures),
                    'max': max(temperatures),
                    'count': len(temperatures)
                }
            
            # Calculate wind statistics
            wind_stats = {}
            if wind_speeds:
                wind_stats = {
                    'avg': round(mean(wind_speeds), 2),
                    'min': min(wind_speeds),
                    'max': max(wind_speeds),
                    'count': len(wind_speeds)
                }
            
            # Count significant alerts (level_1 and level_2)
            significant_wind_alerts = wind_alerts.get('level_1', 0) + wind_alerts.get('level_2', 0)
            significant_heat_alerts = heat_alerts.get('level_1', 0) + heat_alerts.get('level_2', 0)
            
            # Build aggregation result
            aggregates = {
                'window_info': {
                    'start_time': (current_time - self.window_size).isoformat() + 'Z',
                    'end_time': current_time.isoformat() + 'Z',
                    'window_size_minutes': self.window_size.total_seconds() / 60,
                    'data_points_count': len(window_data)
                },
                'alert_counts': {
                    'wind_alerts': dict(wind_alerts),
                    'heat_alerts': dict(heat_alerts),
                    'significant_alerts': {
                        'wind': significant_wind_alerts,
                        'heat': significant_heat_alerts,
                        'total': significant_wind_alerts + significant_heat_alerts
                    }
                },
                'temperature_stats': temp_stats,
                'wind_stats': wind_stats,
                'location_alerts': dict(location_alerts),
                'generated_at': current_time.isoformat() + 'Z'
            }
            
            return aggregates
            
        except Exception as e:
            print(f"❌ Error calculating aggregates: {e}")
            return None
    
    def send_aggregates(self, aggregates):
        """Send aggregates to output topic"""
        try:
            future = self.producer.send(self.output_topic, value=aggregates)
            future.get(timeout=10)
            
            print(f"📊 Aggregates sent successfully!")
            print(f"   📈 Data points: {aggregates['window_info']['data_points_count']}")
            print(f"   🚨 Significant alerts: {aggregates['alert_counts']['significant_alerts']['total']}")
            if aggregates['temperature_stats']:
                print(f"   🌡️  Temp range: {aggregates['temperature_stats']['min']}°C - {aggregates['temperature_stats']['max']}°C")
            
            return True
            
        except KafkaError as e:
            print(f"❌ Failed to send aggregates: {e}")
            return False
    
    def display_aggregates(self, aggregates):
        """Display aggregates in console"""
        print("\n" + "="*80)
        print(f"📊 SLIDING WINDOW AGGREGATES")
        print(f"🕒 Window: {aggregates['window_info']['window_size_minutes']} minutes")
        print(f"📍 Time: {aggregates['window_info']['start_time']} → {aggregates['window_info']['end_time']}")
        print(f"📦 Data points: {aggregates['window_info']['data_points_count']}")
        print("-"*80)
        
        # Alert summary
        sig_alerts = aggregates['alert_counts']['significant_alerts']
        print(f"🚨 SIGNIFICANT ALERTS (level_1 + level_2):")
        print(f"   💨 Wind alerts: {sig_alerts['wind']}")
        print(f"   🔥 Heat alerts: {sig_alerts['heat']}")
        print(f"   📊 Total: {sig_alerts['total']}")
        
        # Detailed alert breakdown
        wind_alerts = aggregates['alert_counts']['wind_alerts']
        heat_alerts = aggregates['alert_counts']['heat_alerts']
        
        if wind_alerts:
            print(f"\n💨 WIND ALERT BREAKDOWN:")
            for level, count in wind_alerts.items():
                print(f"   {level}: {count}")
        
        if heat_alerts:
            print(f"\n🔥 HEAT ALERT BREAKDOWN:")
            for level, count in heat_alerts.items():
                print(f"   {level}: {count}")
        
        # Temperature statistics
        temp_stats = aggregates.get('temperature_stats', {})
        if temp_stats:
            print(f"\n🌡️  TEMPERATURE STATISTICS:")
            print(f"   Average: {temp_stats['avg']}°C")
            print(f"   Range: {temp_stats['min']}°C - {temp_stats['max']}°C")
            print(f"   Samples: {temp_stats['count']}")
        
        # Wind statistics
        wind_stats = aggregates.get('wind_stats', {})
        if wind_stats:
            print(f"\n💨 WIND STATISTICS:")
            print(f"   Average: {wind_stats['avg']} m/s")
            print(f"   Range: {wind_stats['min']} - {wind_stats['max']} m/s")
            print(f"   Samples: {wind_stats['count']}")
        
        # Location alerts
        location_alerts = aggregates.get('location_alerts', {})
        if location_alerts:
            print(f"\n📍 ALERTS BY LOCATION:")
            for location, alerts in location_alerts.items():
                print(f"   {location}: Wind={alerts.get('wind_alerts', 0)}, Heat={alerts.get('heat_alerts', 0)}")
        
        print("="*80)
    
    def start_aggregation(self, output_to_kafka=True, display_in_console=True):
        """Start the real-time aggregation process"""
        print(f"🚀 Starting real-time aggregation...")
        print(f"📥 Input topic: {self.input_topic}")
        print(f"📤 Output topic: {self.output_topic}")
        print(f"⏱️  Window size: {self.window_size.total_seconds() / 60} minutes")
        print(f"📊 Output to Kafka: {output_to_kafka}")
        print(f"🖥️  Display in console: {display_in_console}")
        print("Press Ctrl+C to stop...")
        print("-" * 80)
        
        message_count = 0
        last_aggregate_time = datetime.utcnow()
        aggregate_interval = timedelta(seconds=30)  # Generate aggregates every 30 seconds
        
        try:
            for message in self.consumer:
                try:
                    # Parse the transformed weather data
                    data = json.loads(message.value)
                    self.add_data_point(data)
                    message_count += 1
                    
                    print(f"📩 Processed message #{message_count} - Temp: {data.get('temperature')}°C, Wind: {data.get('windspeed')} m/s")
                    
                    # Generate aggregates periodically
                    current_time = datetime.utcnow()
                    if current_time - last_aggregate_time >= aggregate_interval:
                        aggregates = self.calculate_aggregates()
                        
                        if aggregates and aggregates['window_info']['data_points_count'] > 0:
                            if display_in_console:
                                self.display_aggregates(aggregates)
                            
                            if output_to_kafka:
                                self.send_aggregates(aggregates)
                        
                        last_aggregate_time = current_time
                    
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"⚠️ Error processing message: {e}")
                    continue
                
        except KeyboardInterrupt:
            print(f"\n🛑 Aggregation stopped. Processed {message_count} messages.")
        except Exception as e:
            print(f"❌ Aggregation error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the aggregator"""
        self.running = False
        if hasattr(self, 'consumer'):
            self.consumer.close()
        if hasattr(self, 'producer'):
            self.producer.flush()
            self.producer.close()
        print("🔌 Aggregator connections closed")

def main():
    parser = argparse.ArgumentParser(description='Weather Data Sliding Window Aggregator')
    parser.add_argument('--kafka-servers', default='localhost:9092', help='Kafka bootstrap servers')
    parser.add_argument('--input-topic', default='weather_transformed', help='Input topic name')
    parser.add_argument('--output-topic', default='weather_aggregates', help='Output topic name')
    parser.add_argument('--window-minutes', type=int, default=1, help='Sliding window size in minutes')
    parser.add_argument('--no-kafka-output', action='store_true', help='Disable Kafka output (console only)')
    parser.add_argument('--no-console', action='store_true', help='Disable console display')
    
    args = parser.parse_args()
    
    print(f"🌍 Weather Sliding Window Aggregator Starting...")
    print(f"⏱️  Window: {args.window_minutes} minute(s)")
    print(f"📥 Input: {args.input_topic}")
    print(f"📤 Output: {args.output_topic}")
    print("="*80)
    
    # Create aggregator
    aggregator = SlidingWindowAggregator(
        kafka_servers=args.kafka_servers,
        input_topic=args.input_topic,
        output_topic=args.output_topic,
        window_minutes=args.window_minutes
    )
    
    # Start aggregation
    aggregator.start_aggregation(
        output_to_kafka=not args.no_kafka_output,
        display_in_console=not args.no_console
    )

if __name__ == "__main__":
    main()