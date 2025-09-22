# Exercice 1 - Démarrage Kafka pour tests basiques
# Script optimisé pour Windows PowerShell

Write-Host "=== EXERCICE 1 - DÉMARRAGE KAFKA ===" -ForegroundColor Green
Write-Host "Date: $(Get-Date)" -ForegroundColor Yellow

# Configuration des chemins
$kafkaDir = "..\..\kafka_2.13-3.9.1"
$logsDir = "C:\tmp\kraft-combined-logs"

# Vérification Java
Write-Host "`n1. Vérification Java..." -ForegroundColor Cyan
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Write-Host "✅ Java trouvé: $javaVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Java non trouvé. Installez Java 8 ou plus récent." -ForegroundColor Red
    exit 1
}

# Génération d'un cluster-id si nécessaire
$clusterIdFile = "$kafkaDir\cluster-id.txt"
if (!(Test-Path $clusterIdFile)) {
    Write-Host "`n2. Génération Cluster ID..." -ForegroundColor Cyan
    $clusterId = & java -cp "$kafkaDir\libs\*" kafka.tools.StorageTool random-uuid
    $clusterId | Out-File -FilePath $clusterIdFile -Encoding UTF8
    Write-Host "✅ Cluster ID généré: $clusterId" -ForegroundColor Green
} else {
    $clusterId = Get-Content $clusterIdFile
    Write-Host "`n2. Cluster ID existant: $clusterId" -ForegroundColor Green
}

# Format du stockage (si nécessaire)
if (!(Test-Path $logsDir)) {
    Write-Host "`n3. Formatage du stockage..." -ForegroundColor Cyan
    & java -Dkafka.logs.dir=$logsDir -cp "$kafkaDir\libs\*" kafka.tools.StorageTool format -t $clusterId -c "$kafkaDir\config\kraft\server.properties"
    Write-Host "✅ Stockage formaté" -ForegroundColor Green
} else {
    Write-Host "`n3. Stockage déjà formaté" -ForegroundColor Green
}

# Démarrage Kafka
Write-Host "`n4. Démarrage du serveur Kafka..." -ForegroundColor Cyan
Write-Host "🚀 Kafka démarre en arrière-plan..." -ForegroundColor Yellow

# Démarrage en arrière-plan avec redirection des logs
Start-Process -FilePath "java" -ArgumentList @(
    "-Dkafka.logs.dir=$logsDir",
    "-cp", "$kafkaDir\libs\*",
    "kafka.Kafka",
    "$kafkaDir\config\kraft\server.properties"
) -WindowStyle Hidden

# Attendre le démarrage
Write-Host "⏳ Attente du démarrage (15 secondes)..."
Start-Sleep -Seconds 15

# Test de connexion
Write-Host "`n5. Test de connexion..." -ForegroundColor Cyan
try {
    $testResult = & java -cp "$kafkaDir\libs\*" kafka.tools.ConsoleProducer --broker-list localhost:9092 --topic test-connection --timeout 5000 2>&1
    Write-Host "✅ Kafka server opérationnel sur port 9092" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Vérifiez que Kafka démarre correctement" -ForegroundColor Yellow
}

Write-Host "`n=== KAFKA PRÊT POUR EXERCICE 1 ===" -ForegroundColor Green
Write-Host "Commandes utiles:" -ForegroundColor Cyan
Write-Host "- Créer topic: .\create-topic.ps1 weather_stream" -ForegroundColor White
Write-Host "- Envoyer message: .\send-message.ps1" -ForegroundColor White
Write-Host "- Lire messages: .\read-messages.ps1 weather_stream" -ForegroundColor White