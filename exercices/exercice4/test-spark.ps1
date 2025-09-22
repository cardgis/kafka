# Script de test pour l'exercice 4
# Test de la transformation Spark avec alertes

Write-Host "=== TEST EXERCICE 4 - TRANSFORMATION SPARK ===" -ForegroundColor Green

# Vérification de Java (requis pour Spark)
Write-Host "`n1. Vérification de Java..." -ForegroundColor Cyan
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Write-Host "✅ Java trouvé: $javaVersion" -ForegroundColor Green
    
    # Vérification version Java (Spark nécessite Java 8+)
    if ($javaVersion -match "1\.8\.|11\.|17\.|21\.|") {
        Write-Host "✅ Version Java compatible avec Spark" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Version Java possiblement incompatible avec Spark" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Java non trouvé. Installez Java 8+ pour Spark" -ForegroundColor Red
    Write-Host "💡 Téléchargez depuis: https://adoptium.net/" -ForegroundColor Yellow
    exit 1
}

# Vérification de Python
Write-Host "`n2. Vérification de Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python non trouvé. Installez Python 3.8+" -ForegroundColor Red
    exit 1
}

# Installation des dépendances
Write-Host "`n3. Installation des dépendances Spark..." -ForegroundColor Cyan
Write-Host "⏳ Installation en cours (peut prendre plusieurs minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt

# Vérification de l'installation Spark
Write-Host "`n4. Test de Spark..." -ForegroundColor Cyan
try {
    python -c "from pyspark.sql import SparkSession; print('✅ PySpark importé avec succès')" 2>$null
    Write-Host "✅ PySpark opérationnel" -ForegroundColor Green
} catch {
    Write-Host "❌ Problème avec PySpark: $_" -ForegroundColor Red
    Write-Host "💡 Vérifiez l'installation Java et les variables d'environnement" -ForegroundColor Yellow
}

# Création du topic de sortie weather_transformed
Write-Host "`n5. Création du topic weather_transformed..." -ForegroundColor Cyan
$kafkaDir = "..\..\kafka_2.13-3.9.1"

try {
    & java -cp "$kafkaDir\libs\*" kafka.admin.TopicCommand `
        --create `
        --topic "weather_transformed" `
        --bootstrap-server localhost:9092 `
        --partitions 3 `
        --replication-factor 1 2>$null
    
    Write-Host "✅ Topic weather_transformed créé" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Topic weather_transformed existe peut-être déjà" -ForegroundColor Yellow
}

# Vérification des topics
Write-Host "`n6. Vérification des topics..." -ForegroundColor Cyan
& java -cp "$kafkaDir\libs\*" kafka.admin.TopicCommand `
    --list `
    --bootstrap-server localhost:9092

Write-Host "`n=== SETUP TERMINÉ ===" -ForegroundColor Green
Write-Host "🚀 Pour tester l'exercice 4:" -ForegroundColor Cyan
Write-Host "1. Terminal 1 - Producteur météo:" -ForegroundColor White
Write-Host "   cd ..\exercice3" -ForegroundColor Gray
Write-Host "   python current_weather.py 48.8566 2.3522 --interval 15" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Terminal 2 - Processeur Spark:" -ForegroundColor White  
Write-Host "   python weather_alerts.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Terminal 3 - Consommateur alertes:" -ForegroundColor White
Write-Host "   cd ..\exercice2" -ForegroundColor Gray
Write-Host "   python consumer.py weather_transformed" -ForegroundColor Gray

$response = Read-Host "`n❓ Voulez-vous lancer le test complet maintenant? (o/N)"
if ($response -eq "o" -or $response -eq "O" -or $response -eq "oui") {
    Write-Host "`n🚀 Lancement du processeur Spark..." -ForegroundColor Yellow
    Write-Host "💡 Ouvrez d'autres terminaux pour le producteur et consommateur" -ForegroundColor Cyan
    Write-Host "🛑 Ctrl+C pour arrêter" -ForegroundColor Yellow
    
    # Lancement du processeur
    python weather_alerts.py
} else {
    Write-Host "`n✅ Setup terminé. Lancez manuellement quand vous êtes prêt." -ForegroundColor Green
}