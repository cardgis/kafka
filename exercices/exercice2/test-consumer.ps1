# Script de test pour l'exercice 2
# Lance le consommateur Python sur le topic weather_stream

Write-Host "=== TEST EXERCICE 2 - CONSOMMATEUR PYTHON ===" -ForegroundColor Green

# Vérification de Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python non trouvé. Installez Python 3.x" -ForegroundColor Red
    exit 1
}

# Vérification des dépendances
Write-Host "`nVérification des dépendances..." -ForegroundColor Cyan
$packages = @("kafka-python")

foreach ($package in $packages) {
    try {
        python -c "import $($package.Replace('-', '_'))" 2>$null
        Write-Host "✅ $package installé" -ForegroundColor Green
    } catch {
        Write-Host "❌ $package manquant. Installation..." -ForegroundColor Yellow
        pip install $package
    }
}

# Test de démarrage du consommateur
Write-Host "`n🚀 Démarrage du consommateur sur weather_stream..." -ForegroundColor Yellow
Write-Host "💡 Ouvrez un autre terminal et envoyez des messages avec:" -ForegroundColor Cyan
Write-Host "   cd ..\exercice1" -ForegroundColor White
Write-Host "   .\send-message.ps1" -ForegroundColor White
Write-Host "`n🛑 Appuyez sur Ctrl+C pour arrêter le consommateur" -ForegroundColor Yellow

# Lancement du consommateur
python consumer.py weather_stream --from-beginning