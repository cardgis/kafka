# Script de test pour l'exercice 3
# Lance le producteur météo pour Paris

Write-Host "=== TEST EXERCICE 3 - PRODUCTEUR MÉTÉO ===" -ForegroundColor Green

# Coordonnées de test
$locations = @{
    "Paris" = @{lat=48.8566; lon=2.3522}
    "Lyon" = @{lat=45.764; lon=4.8357}
    "Marseille" = @{lat=43.2965; lon=5.3698}
    "Nice" = @{lat=43.7102; lon=7.2620}
}

# Vérification de Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python non trouvé. Installez Python 3.x" -ForegroundColor Red
    exit 1
}

# Installation des dépendances
Write-Host "`nInstallation des dépendances..." -ForegroundColor Cyan
pip install -r requirements.txt

# Test de l'API Open-Meteo
Write-Host "`nTest de l'API Open-Meteo..." -ForegroundColor Cyan
try {
    $testApi = Invoke-RestMethod -Uri "https://api.open-meteo.com/v1/forecast?latitude=48.8566&longitude=2.3522&current=temperature_2m" -TimeoutSec 10
    Write-Host "✅ API Open-Meteo accessible" -ForegroundColor Green
} catch {
    Write-Host "❌ Problème d'accès à l'API Open-Meteo: $_" -ForegroundColor Red
    Write-Host "Vérifiez votre connexion internet" -ForegroundColor Yellow
}

# Menu de sélection
Write-Host "`n🌍 Choisissez une ville pour le test:" -ForegroundColor Cyan
$i = 1
foreach ($city in $locations.Keys) {
    $coords = $locations[$city]
    Write-Host "$i. $city (${coords.lat}, ${coords.lon})" -ForegroundColor White
    $i++
}

$choice = Read-Host "`nEntrez le numéro de votre choix (1-$($locations.Count))"

$cityNames = @($locations.Keys)
if ($choice -match '^\d+$' -and [int]$choice -ge 1 -and [int]$choice -le $locations.Count) {
    $selectedCity = $cityNames[[int]$choice - 1]
    $coords = $locations[$selectedCity]
    
    Write-Host "`n🎯 Test avec $selectedCity (${coords.lat}, ${coords.lon})" -ForegroundColor Yellow
    Write-Host "📊 Envoi de 3 messages avec intervalle de 10 secondes" -ForegroundColor Yellow
    Write-Host "`n💡 Pendant le test, ouvrez un autre terminal et lancez:" -ForegroundColor Cyan
    Write-Host "   cd ..\exercice2" -ForegroundColor White
    Write-Host "   python consumer.py weather_stream --from-beginning" -ForegroundColor White
    Write-Host "`n🚀 Lancement du producteur..." -ForegroundColor Green
    
    # Lancement du producteur météo
    python current_weather.py $coords.lat $coords.lon --interval 10 --count 3
    
} else {
    Write-Host "❌ Choix invalide" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Test terminé!" -ForegroundColor Green