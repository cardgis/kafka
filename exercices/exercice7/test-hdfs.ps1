# Test du consommateur HDFS - Exercice 7
# Test consumer for Kafka to HDFS with geographical organization

# Installer les dépendances
pip install -r requirements.txt

# Démarrer Kafka (si pas encore fait)
Write-Host "Démarrage de Kafka si nécessaire..." -ForegroundColor Green
Set-Location ..\..\
.\start-kafka.bat

Start-Sleep -Seconds 5

# Retourner au répertoire exercice7
Set-Location exercices\exercice7

# Générer quelques données de test dans les topics
Write-Host "`nGénération de données de test..." -ForegroundColor Yellow

# Générer des données geo_weather_stream avec différentes villes
Start-Process -FilePath "python" -ArgumentList "..\exercice6\geo_weather.py", "Paris", "France", "--topic", "geo_weather_stream", "--interval", "2", "--count", "3" -NoNewWindow
Start-Sleep -Seconds 1

Start-Process -FilePath "python" -ArgumentList "..\exercice6\geo_weather.py", "Tokyo", "Japan", "--topic", "geo_weather_stream", "--interval", "2", "--count", "3" -NoNewWindow  
Start-Sleep -Seconds 1

Start-Process -FilePath "python" -ArgumentList "..\exercice6\geo_weather.py", "New York", "USA", "--topic", "geo_weather_stream", "--interval", "2", "--count", "3" -NoNewWindow

Write-Host "Attente génération des données..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Démarrer le consommateur HDFS
Write-Host "`nDémarrage du consommateur HDFS..." -ForegroundColor Green
Write-Host "💡 Le consommateur va lire les topics et organiser les données par pays/ville" -ForegroundColor Cyan
Write-Host "📁 Structure HDFS: ./hdfs-data/{country}/{city}/alerts.json" -ForegroundColor Cyan
Write-Host "🛑 Appuyez sur Ctrl+C pour arrêter après quelques secondes" -ForegroundColor Yellow

# Lancer le consommateur HDFS en mode interactif
python hdfs_consumer.py --hdfs-path ".\hdfs-data" --topics geo_weather_stream weather_transformed

Write-Host "`nTest terminé. Vérifiez la structure HDFS créée dans ./hdfs-data/" -ForegroundColor Green