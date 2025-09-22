# Script de préparation et test pour l'exercice 8
# Copie des données HDFS et génération des visualisations

# Installer les dépendances
Write-Host "Installation des dépendances pour les visualisations..." -ForegroundColor Green
pip install -r requirements.txt

# Copier les données HDFS depuis l'exercice 7 si elles existent
$exercice7Path = "..\exercice7\hdfs-data"
$localHdfsPath = ".\hdfs-data"

if (Test-Path $exercice7Path) {
    Write-Host "Copie des données HDFS depuis l'exercice 7..." -ForegroundColor Yellow
    Copy-Item -Path $exercice7Path -Destination $localHdfsPath -Recurse -Force
    Write-Host "✅ Données HDFS copiées avec succès" -ForegroundColor Green
} else {
    Write-Host "⚠️ Données HDFS non trouvées, génération de données de test..." -ForegroundColor Yellow
    
    # Créer structure HDFS de test
    New-Item -Path $localHdfsPath -ItemType Directory -Force | Out-Null
    
    # Générer quelques données de test
    python -c "
import json
import os
from pathlib import Path

# Créer structure test
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
    
    # Créer fichier alerts.json
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

print('✅ Données de test créées')
"
}

# Vérifier la structure HDFS
Write-Host "`nStructure HDFS disponible:" -ForegroundColor Cyan
Get-ChildItem -Path $localHdfsPath -Recurse | ForEach-Object {
    $relativePath = $_.FullName.Replace((Get-Location).Path + "\hdfs-data\", "")
    if ($_.PSIsContainer) {
        Write-Host "📁 $relativePath/" -ForegroundColor Blue
    } else {
        $size = [math]::Round($_.Length / 1KB, 1)
        Write-Host "📄 $relativePath ($size KB)" -ForegroundColor Gray
    }
}

# Générer les visualisations
Write-Host "`nGénération des visualisations météo..." -ForegroundColor Green
python weather_visualizer.py --hdfs-path "./hdfs-data" --output-dir "./visualizations" --report

# Afficher les résultats
Write-Host "`n🎨 VISUALISATIONS GÉNÉRÉES:" -ForegroundColor Green
if (Test-Path ".\visualizations") {
    Get-ChildItem -Path ".\visualizations" | ForEach-Object {
        if ($_.Extension -eq ".png") {
            Write-Host "   🖼️  $($_.Name)" -ForegroundColor Cyan
        } elseif ($_.Extension -eq ".html") {
            Write-Host "   📄 $($_.Name)" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`n💡 Ouvrez le fichier 'rapport_meteo_hdfs.html' dans votre navigateur pour voir le rapport complet" -ForegroundColor Yellow
} else {
    Write-Host "❌ Erreur: Répertoire visualizations non créé" -ForegroundColor Red
}

Write-Host "`n✅ Test de l'exercice 8 terminé!" -ForegroundColor Green