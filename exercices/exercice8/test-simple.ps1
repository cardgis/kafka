# Test simple pour exercice 8
Write-Host "Installation des dependances..." -ForegroundColor Green
pip install -r requirements.txt

# Copier donnees HDFS depuis exercice 7
$exercice7Path = "..\exercice7\hdfs-data"
$localHdfsPath = ".\hdfs-data"

if (Test-Path $exercice7Path) {
    Write-Host "Copie des donnees HDFS..." -ForegroundColor Yellow
    Copy-Item -Path $exercice7Path -Destination $localHdfsPath -Recurse -Force
    Write-Host "Donnees copiees avec succes" -ForegroundColor Green
} else {
    Write-Host "Creation de donnees de test..." -ForegroundColor Yellow
    # Code Python pour creer donnees test
    python -c "
import json
import os
from pathlib import Path

base_path = Path('./hdfs-data')
test_data = [
    ('FR', 'Paris', {'temperature': 18.5, 'windspeed': 15.2, 'weathercode': 2}),
    ('JP', 'Tokyo', {'temperature': 22.1, 'windspeed': 8.7, 'weathercode': 1}),
    ('US', 'New_York', {'temperature': 16.8, 'windspeed': 12.4, 'weathercode': 3}),
    ('GB', 'London', {'temperature': 14.2, 'windspeed': 18.9, 'weathercode': 61}),
    ('DE', 'Berlin', {'temperature': 19.3, 'windspeed': 11.1, 'weathercode': 2})
]

for country, city, weather in test_data:
    city_path = base_path / country / city
    city_path.mkdir(parents=True, exist_ok=True)
    
    alert_file = city_path / 'alerts.json'
    
    record = {
        'location': {
            'city': city.replace('_', ' '),
            'country_code': country,
            'latitude': 48.8566 if country == 'FR' else 35.6762,
            'longitude': 2.3522 if country == 'FR' else 139.6503
        },
        'weather': weather,
        'metadata': {
            'timestamp': '2024-01-15T14:30:00Z',
            'source': 'test-data'
        },
        'hdfs_metadata': {
            'processed_at': '2024-01-15T14:30:00Z',
            'consumer_id': 'test-consumer'
        }
    }
    
    with open(alert_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')

print('Donnees de test creees')
"
}

# Generer visualisations
Write-Host "Generation des visualisations..." -ForegroundColor Green
python weather_visualizer.py --hdfs-path "./hdfs-data" --output-dir "./visualizations" --report

# Afficher resultats
Write-Host "Visualisations generees dans ./visualizations/" -ForegroundColor Green