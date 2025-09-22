# Script de test pour l'exercice 5
# Test des agrégats temps réel avec fenêtres glissantes

Write-Host "=== TEST EXERCICE 5 - AGRÉGATS SPARK TEMPS RÉEL ===" -ForegroundColor Green

# Vérification de Java et Python
Write-Host "`n1. Vérifications techniques..." -ForegroundColor Cyan
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Write-Host "✅ Java: $javaVersion" -ForegroundColor Green
    
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Java ou Python manquant" -ForegroundColor Red
    exit 1
}

# Installation des dépendances
Write-Host "`n2. Installation dépendances Spark..." -ForegroundColor Cyan
pip install -r requirements.txt

# Création du topic de sortie weather_aggregates
Write-Host "`n3. Création du topic weather_aggregates..." -ForegroundColor Cyan
$kafkaDir = "..\..\kafka_2.13-3.9.1"

try {
    & java -cp "$kafkaDir\libs\*" kafka.admin.TopicCommand `
        --create `
        --topic "weather_aggregates" `
        --bootstrap-server localhost:9092 `
        --partitions 2 `
        --replication-factor 1 2>$null
    
    Write-Host "✅ Topic weather_aggregates créé" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Topic weather_aggregates existe peut-être déjà" -ForegroundColor Yellow
}

# Vérification des topics requis
Write-Host "`n4. Vérification des topics..." -ForegroundColor Cyan
$topics = & java -cp "$kafkaDir\libs\*" kafka.admin.TopicCommand `
    --list `
    --bootstrap-server localhost:9092

Write-Host "Topics disponibles:" -ForegroundColor White
$topics | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }

# Vérification topics requis
$requiredTopics = @("weather_stream", "weather_transformed", "weather_aggregates")
$missingTopics = @()

foreach ($topic in $requiredTopics) {
    if ($topics -notcontains $topic) {
        $missingTopics += $topic
    }
}

if ($missingTopics.Count -gt 0) {
    Write-Host "`n⚠️  Topics manquants: $($missingTopics -join ', ')" -ForegroundColor Yellow
    Write-Host "💡 Lancez d'abord les exercices 1, 3 et 4 pour créer la chaîne complète" -ForegroundColor Yellow
} else {
    Write-Host "`n✅ Tous les topics requis sont présents" -ForegroundColor Green
}

Write-Host "`n=== SETUP TERMINÉ ===" -ForegroundColor Green
Write-Host "🚀 Pour tester l'exercice 5, lancez dans l'ordre:" -ForegroundColor Cyan

Write-Host "`n1️⃣  Terminal 1 - Producteur météo (génère des données):" -ForegroundColor White
Write-Host "   cd ..\exercice3" -ForegroundColor Gray
Write-Host "   python current_weather.py 48.8566 2.3522 --interval 10" -ForegroundColor Gray

Write-Host "`n2️⃣  Terminal 2 - Transformateur Spark (calcule alertes):" -ForegroundColor White
Write-Host "   cd ..\exercice4" -ForegroundColor Gray
Write-Host "   python weather_alerts.py" -ForegroundColor Gray

Write-Host "`n3️⃣  Terminal 3 - Agrégateur Spark (ce terminal):" -ForegroundColor White
Write-Host "   python weather_aggregates.py" -ForegroundColor Gray

Write-Host "`n4️⃣  Terminal 4 - Consommateur agrégats:" -ForegroundColor White
Write-Host "   cd ..\exercice2" -ForegroundColor Gray
Write-Host "   python consumer.py weather_aggregates" -ForegroundColor Gray

Write-Host "`n🔍 Métriques calculées:" -ForegroundColor Cyan
Write-Host "   • Moyennes/min/max température par fenêtre 5 min" -ForegroundColor White
Write-Host "   • Comptages alertes level_1/level_2 par type" -ForegroundColor White
Write-Host "   • Agrégats régionaux par zone géographique" -ForegroundColor White
Write-Host "   • Densité d'alertes et codes météo dominants" -ForegroundColor White

$response = Read-Host "`n❓ Voulez-vous lancer le processeur d'agrégats maintenant? (o/N)"
if ($response -eq "o" -or $response -eq "O" -or $response -eq "oui") {
    Write-Host "`n🚀 Lancement du processeur d'agrégats Spark..." -ForegroundColor Yellow
    Write-Host "💡 Assurez-vous que les exercices 3 et 4 tournent dans d'autres terminaux" -ForegroundColor Cyan
    Write-Host "🛑 Ctrl+C pour arrêter" -ForegroundColor Yellow
    
    # Lancement du processeur d'agrégats
    python weather_aggregates.py --window "1 minute" --slide "30 seconds"
} else {
    Write-Host "`n✅ Setup terminé. Lancez manuellement avec python weather_aggregates.py" -ForegroundColor Green
}