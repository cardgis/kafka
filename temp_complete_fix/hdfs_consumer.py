#!/usr/bin/env python3
"""
HDFS Consumer for Exercise 7
Consumes weather alert data and saves to HDFS structure organized by country/city
"""

import json
import os
import argparse
from datetime import datetime
from kafka import KafkaConsumer
from pathlib import Path

class HDFSConsumer:
    def __init__(self, kafka_servers='localhost:9092', hdfs_root='hdfs-data'):
        """Initialize HDFS consumer"""
        self.consumer = KafkaConsumer(
            'weather_transformed',
            bootstrap_servers=[kafka_servers],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=10000,  # 10 second timeout
            group_id='hdfs-consumer-v2',
            auto_offset_reset='earliest'
        )
        self.hdfs_root = Path(hdfs_root)
        self.message_count = 0
        self.alert_count = 0
        
        # Create root HDFS directory if it doesn't exist
        self.hdfs_root.mkdir(exist_ok=True)
        print(f"HDFS Consumer initialized - Root directory: {self.hdfs_root.absolute()}")
    
    def should_store_message(self, message):
        """Check if message contains alerts worth storing"""
        try:
            # Check for wind alerts level 1 or 2 (new format)
            wind_alert_level = message.get('wind_alert_level', 'level_0')
            if wind_alert_level in ['level_1', 'level_2']:
                return True
            
            # Check for heat alerts level 1 or 2 (new format)
            heat_alert_level = message.get('heat_alert_level', 'level_0')
            if heat_alert_level in ['level_1', 'level_2']:
                return True
            
            # Fallback: Check for wind alerts level 1 or 2 (old format)
            wind_alert = message.get('wind_alert', {})
            if isinstance(wind_alert, dict) and wind_alert.get('level', 0) >= 1:
                return True
            
            # Fallback: Check for heat alerts level 1 or 2 (old format)
            heat_alert = message.get('heat_alert', {})
            if isinstance(heat_alert, dict) and heat_alert.get('level', 0) >= 1:
                return True
            
            return False
        except Exception as e:
            print(f"Error checking message alerts: {e}")
            return False
    
    def get_storage_path(self, message):
        """Generate HDFS storage path from message location data"""
        try:
            # Try to extract location information from message
            location = message.get('location', {})
            country = location.get('country', None)
            city = location.get('city', None)
            
            # Fallback: use coordinates if no location info
            if not city or not country:
                lat = message.get('latitude', 0)
                lon = message.get('longitude', 0)
                city = f"coord_{lat:.2f}_{lon:.2f}"
                country = "unknown"
            
            # Clean country and city names for filesystem
            country_clean = self.clean_filename(country)
            city_clean = self.clean_filename(city)
            
            # Create directory structure: hdfs-data/{country}/{city}/
            storage_dir = self.hdfs_root / country_clean / city_clean
            storage_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"alerts_{timestamp}.json"
            
            return storage_dir / filename
            
        except Exception as e:
            print(f"Error generating storage path: {e}")
            # Fallback path
            fallback_dir = self.hdfs_root / "unknown" / "unknown"
            fallback_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return fallback_dir / f"alerts_{timestamp}.json"
    
    def clean_filename(self, name):
        """Clean filename for filesystem compatibility"""
        if not name or name == 'unknown':
            return 'unknown'
        
        # Replace spaces and special characters
        cleaned = str(name).replace(' ', '_').replace('/', '_').replace('\\', '_')
        # Remove other problematic characters
        import re
        cleaned = re.sub(r'[<>:"|?*]', '_', cleaned)
        return cleaned.lower()
    
    def save_to_hdfs(self, message, file_path):
        """Save message to HDFS file"""
        try:
            # Add storage metadata
            storage_record = {
                'stored_at': datetime.now().isoformat(),
                'storage_path': str(file_path),
                'message': message
            }
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(storage_record, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving to HDFS: {e}")
            return False
    
    def print_message_summary(self, message):
        """Print summary of stored message"""
        try:
            # Try to get location from message
            location = message.get('location', {})
            city = location.get('city') or f"coord_{message.get('latitude', 'N/A'):.2f}"
            country = location.get('country', 'Unknown')
            
            # Get weather data
            temperature = message.get('temperature', 'N/A')
            wind_speed = message.get('windspeed', message.get('wind_speed', 'N/A'))
            
            # Get alert levels (new format)
            wind_alert_level = message.get('wind_alert_level', 'level_0')
            heat_alert_level = message.get('heat_alert_level', 'level_0')
            
            # Fallback to old format
            wind_alert = message.get('wind_alert', {})
            heat_alert = message.get('heat_alert', {})
            
            alerts = []
            if wind_alert_level in ['level_1', 'level_2']:
                alerts.append(f"Wind {wind_alert_level}")
            elif isinstance(wind_alert, dict) and wind_alert.get('level', 0) >= 1:
                alerts.append(f"Wind Level {wind_alert['level']}")
                
            if heat_alert_level in ['level_1', 'level_2']:
                alerts.append(f"Heat {heat_alert_level}")
            elif isinstance(heat_alert, dict) and heat_alert.get('level', 0) >= 1:
                alerts.append(f"Heat Level {heat_alert['level']}")
            
            print(f"  -> {city}, {country}: {temperature}°C, {wind_speed} m/s - Alerts: {', '.join(alerts)}")
            
        except Exception as e:
            print(f"  -> Error printing summary: {e}")
    
    def run(self):
        """Run the HDFS consumer"""
        print("Starting HDFS Consumer...")
        print("Consuming from 'weather_transformed' topic")
        print("Storing alert messages (level 1+ wind/heat alerts)")
        print("-" * 60)
        
        try:
            for message in self.consumer:
                self.message_count += 1
                data = message.value
                
                print(f"Message {self.message_count}: Processing...")
                
                # Check if message should be stored
                if self.should_store_message(data):
                    # Generate storage path
                    file_path = self.get_storage_path(data)
                    
                    # Save to HDFS
                    if self.save_to_hdfs(data, file_path):
                        self.alert_count += 1
                        print(f"  ✓ STORED: {file_path}")
                        self.print_message_summary(data)
                    else:
                        print(f"  ✗ FAILED to store message")
                else:
                    print(f"  - Skipped (no significant alerts)")
                
                print()
                
        except KeyboardInterrupt:
            print(f"\nStopping consumer...")
        except Exception as e:
            print(f"Error in consumer: {e}")
        finally:
            self.consumer.close()
            print(f"\nConsumer stopped. Processed {self.message_count} messages, stored {self.alert_count} alerts.")
    
    def list_stored_data(self):
        """List all stored data in HDFS structure"""
        print(f"HDFS Data Structure in {self.hdfs_root.absolute()}:")
        print("=" * 50)
        
        if not self.hdfs_root.exists():
            print("No data stored yet.")
            return
        
        total_files = 0
        for country_dir in sorted(self.hdfs_root.iterdir()):
            if country_dir.is_dir():
                print(f"\n📍 {country_dir.name.upper()}")
                
                for city_dir in sorted(country_dir.iterdir()):
                    if city_dir.is_dir():
                        files = list(city_dir.glob('*.json'))
                        total_files += len(files)
                        print(f"  └── {city_dir.name}: {len(files)} alert files")
                        
                        # Show recent files
                        if files:
                            recent_files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
                            for f in recent_files:
                                size = f.stat().st_size
                                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                                print(f"      • {f.name} ({size} bytes, {mtime})")
        
        print(f"\nTotal: {total_files} alert files stored")

def main():
    parser = argparse.ArgumentParser(description='HDFS Consumer for Kafka Weather Alerts')
    parser.add_argument('--kafka-servers', default='localhost:9092', 
                       help='Kafka bootstrap servers')
    parser.add_argument('--hdfs-root', default='hdfs-data',
                       help='HDFS root directory')
    parser.add_argument('--list', action='store_true',
                       help='List stored data structure')
    
    args = parser.parse_args()
    
    consumer = HDFSConsumer(args.kafka_servers, args.hdfs_root)
    
    if args.list:
        consumer.list_stored_data()
    else:
        consumer.run()

if __name__ == "__main__":
    main()