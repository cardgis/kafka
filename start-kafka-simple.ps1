# Script PowerShell pour Kafka KRaft
$kafkaHome = "C:\Big_data\kafka\kafka_2.13-3.9.1"
Set-Location $kafkaHome

Write-Host "=== Configuration Kafka KRaft ===" -ForegroundColor Green

# Génération du cluster ID
Write-Host "1. Generation du cluster ID..." -ForegroundColor Yellow
$clusterId = & java -cp "libs/*" kafka.tools.StorageTool random-uuid 2>$null
$clusterId = $clusterId | Where-Object { $_ -match "^[a-zA-Z0-9]" } | Select-Object -First 1
Write-Host "Cluster ID: $clusterId" -ForegroundColor Cyan

# Sauvegarde du cluster ID
$clusterId | Out-File -FilePath "cluster-id.txt" -Encoding ASCII -NoNewline

# Formatage du stockage
Write-Host "2. Formatage du stockage..." -ForegroundColor Yellow
& java -cp "libs/*" kafka.tools.StorageTool format -t $clusterId -c "config/kraft/server.properties" --ignore-formatted 2>$null

Write-Host "3. Demarrage de Kafka..." -ForegroundColor Yellow
Write-Host "Kafka sera demarre en arriere-plan. Attendez 20 secondes..." -ForegroundColor Yellow

# Démarrage de Kafka en arrière-plan
$kafkaProcess = Start-Process -FilePath "java" -ArgumentList "-cp", "libs/*", "kafka.Kafka", "config/kraft/server.properties" -PassThru -WindowStyle Hidden

Start-Sleep -Seconds 20

# Vérification
$port9092 = netstat -an | Select-String ":9092"
if ($port9092) {
    Write-Host "SUCCESS: Kafka est demarre sur le port 9092!" -ForegroundColor Green
    Write-Host "Kafka PID: $($kafkaProcess.Id)" -ForegroundColor Cyan
} else {
    Write-Host "ECHEC: Kafka ne semble pas demarre" -ForegroundColor Red
}

Write-Host "=== Pret pour les tests ===" -ForegroundColor Green