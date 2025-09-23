#!/usr/bin/env python3
"""
HDFS Data Analyzer for Exercise 7
Analyzes stored alert data and provides statistics
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

class HDFSAnalyzer:
    def __init__(self, hdfs_root='hdfs-data'):
        self.hdfs_root = Path(hdfs_root)
        self.stats = defaultdict(int)
        self.alerts_by_location = defaultdict(list)
        self.alerts_by_type = defaultdict(int)
    
    def analyze_all_data(self):
        """Analyze all stored HDFS data"""
        if not self.hdfs_root.exists():
            print(f"HDFS directory {self.hdfs_root} does not exist")
            return
        
        json_files = list(self.hdfs_root.rglob("*.json"))
        if not json_files:
            print("No alert files found in HDFS structure")
            return
        
        print(f"Analyzing {len(json_files)} alert files...")
        print("-" * 50)
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.analyze_file_data(file_path, data)
                
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        self.print_statistics()
    
    def analyze_file_data(self, file_path, data):
        """Analyze individual file data"""
        # Extract location from path
        parts = file_path.relative_to(self.hdfs_root).parts
        if len(parts) >= 2:
            country = parts[0]
            city = parts[1]
            location_key = f"{city}, {country}"
        else:
            location_key = "unknown"
        
        # Analyze message content
        message = data.get('message', {})
        
        # Count alerts
        wind_alert = message.get('wind_alert', {})
        heat_alert = message.get('heat_alert', {})
        
        if isinstance(wind_alert, dict) and wind_alert.get('level', 0) >= 1:
            alert_info = {
                'type': 'wind',
                'level': wind_alert['level'],
                'value': wind_alert.get('wind_speed', 'N/A'),
                'timestamp': message.get('timestamp'),
                'file': file_path.name
            }
            self.alerts_by_location[location_key].append(alert_info)
            self.alerts_by_type[f"wind_level_{wind_alert['level']}"] += 1
        
        if isinstance(heat_alert, dict) and heat_alert.get('level', 0) >= 1:
            alert_info = {
                'type': 'heat',
                'level': heat_alert['level'],
                'value': heat_alert.get('temperature', 'N/A'),
                'timestamp': message.get('timestamp'),
                'file': file_path.name
            }
            self.alerts_by_location[location_key].append(alert_info)
            self.alerts_by_type[f"heat_level_{heat_alert['level']}"] += 1
        
        self.stats['total_files'] += 1
    
    def print_statistics(self):
        """Print comprehensive statistics"""
        print("\n" + "=" * 60)
        print("HDFS ALERT DATA ANALYSIS")
        print("=" * 60)
        
        print(f"\n📊 OVERALL STATISTICS")
        print(f"Total alert files: {self.stats['total_files']}")
        print(f"Locations with alerts: {len(self.alerts_by_location)}")
        print(f"Total alert instances: {sum(self.alerts_by_type.values())}")
        
        print(f"\n🚨 ALERT BREAKDOWN BY TYPE")
        for alert_type, count in sorted(self.alerts_by_type.items()):
            print(f"  {alert_type.replace('_', ' ').title()}: {count}")
        
        print(f"\n🌍 ALERTS BY LOCATION")
        for location, alerts in sorted(self.alerts_by_location.items()):
            print(f"\n📍 {location.upper()}")
            
            # Group by alert type
            wind_alerts = [a for a in alerts if a['type'] == 'wind']
            heat_alerts = [a for a in alerts if a['type'] == 'heat']
            
            if wind_alerts:
                print(f"  💨 Wind Alerts: {len(wind_alerts)}")
                for alert in wind_alerts[-3:]:  # Show last 3
                    print(f"    - Level {alert['level']}: {alert['value']} m/s ({alert['file']})")
            
            if heat_alerts:
                print(f"  🌡️  Heat Alerts: {len(heat_alerts)}")
                for alert in heat_alerts[-3:]:  # Show last 3
                    print(f"    - Level {alert['level']}: {alert['value']}°C ({alert['file']})")
        
        print(f"\n📁 DIRECTORY STRUCTURE")
        self.print_directory_tree()
    
    def print_directory_tree(self):
        """Print directory tree structure"""
        if not self.hdfs_root.exists():
            print("No HDFS directory found")
            return
        
        def print_tree(path, indent=""):
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_indent = "└── " if is_last else "├── "
                
                if item.is_dir():
                    print(f"{indent}{current_indent}{item.name}/")
                    next_indent = indent + ("    " if is_last else "│   ")
                    print_tree(item, next_indent)
                else:
                    size = item.stat().st_size
                    print(f"{indent}{current_indent}{item.name} ({size} bytes)")
        
        print(f"{self.hdfs_root.name}/")
        print_tree(self.hdfs_root)
    
    def clean_old_files(self, days_old=7):
        """Clean files older than specified days"""
        if not self.hdfs_root.exists():
            print("No HDFS directory to clean")
            return
        
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(days=days_old)
        
        json_files = list(self.hdfs_root.rglob("*.json"))
        old_files = []
        
        for file_path in json_files:
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_time < cutoff_time:
                old_files.append(file_path)
        
        if not old_files:
            print(f"No files older than {days_old} days found")
            return
        
        print(f"Found {len(old_files)} files older than {days_old} days:")
        for file_path in old_files:
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            print(f"  - {file_path}: {file_time}")
        
        confirm = input(f"\nDelete these {len(old_files)} files? (y/N): ")
        if confirm.lower() == 'y':
            for file_path in old_files:
                try:
                    file_path.unlink()
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
            
            # Remove empty directories
            for root, dirs, files in self.hdfs_root.walk(top_down=False):
                if root != self.hdfs_root and not any(root.iterdir()):
                    try:
                        root.rmdir()
                        print(f"Removed empty directory: {root}")
                    except Exception:
                        pass

def main():
    parser = argparse.ArgumentParser(description='HDFS Data Analyzer')
    parser.add_argument('--hdfs-root', default='hdfs-data',
                       help='HDFS root directory')
    parser.add_argument('--clean', type=int, metavar='DAYS',
                       help='Clean files older than DAYS days')
    
    args = parser.parse_args()
    
    analyzer = HDFSAnalyzer(args.hdfs_root)
    
    if args.clean:
        analyzer.clean_old_files(args.clean)
    else:
        analyzer.analyze_all_data()

if __name__ == "__main__":
    main()