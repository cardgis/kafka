# Test du producteur géolocalisé - Exercice 6
# Test producer for geo-weather streaming with city/country resolution

# Installer les dépendances
pip install -r requirements.txt

# Démarrer Kafka (si pas encore fait)
Write-Host "Démarrage de Kafka si nécessaire..." -ForegroundColor Green
cd ..\..\
.\start-kafka.bat

Start-Sleep -Seconds 5

# Créer le topic geo_weather_stream
Write-Host "Création du topic geo_weather_stream..." -ForegroundColor Yellow
.\kafka_2.13-3.9.1\bin\windows\kafka-topics.bat --create --topic geo_weather_stream --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

cd exercices\exercice6

# Test 1: Données météo pour Paris, France
Write-Host "`nTest 1: Données météo pour Paris, France" -ForegroundColor Cyan
python geo_weather.py "Paris" "France" --topic geo_weather_stream --interval 10 --count 3

Start-Sleep -Seconds 2

# Test 2: Données météo pour Tokyo, Japon  
Write-Host "`nTest 2: Données météo pour Tokyo, Japon" -ForegroundColor Cyan
python geo_weather.py "Tokyo" "Japan" --topic geo_weather_stream --interval 10 --count 3

Start-Sleep -Seconds 2

# Test 3: Données météo pour New York, USA
Write-Host "`nTest 3: Données météo pour New York, USA" -ForegroundColor Cyan
python geo_weather.py "New York" "USA" --topic geo_weather_stream --interval 10 --count 3

# Lire les messages pour vérification
Write-Host "`nLecture des messages du topic geo_weather_stream:" -ForegroundColor Green
cd ..\..\
.\kafka_2.13-3.9.1\bin\windows\kafka-console-consumer.bat --topic geo_weather_stream --from-beginning --bootstrap-server localhost:9092 --max-messages 9

Write-Host "`nTest terminé. Vérifiez que les données incluent les informations de géolocalisation." -ForegroundColor Green