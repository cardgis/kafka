# Exercice 1 - Création du topic weather_stream
param(
    [string]$TopicName = "weather_stream",
    [int]$Partitions = 1,
    [int]$ReplicationFactor = 1
)

Write-Host "=== CRÉATION TOPIC POUR EXERCICE 1 ===" -ForegroundColor Green
Write-Host "Topic: $TopicName" -ForegroundColor Yellow
Write-Host "Partitions: $Partitions" -ForegroundColor Yellow
Write-Host "Replication Factor: $ReplicationFactor" -ForegroundColor Yellow

$kafkaDir = "..\..\kafka_2.13-3.9.1"

try {
    Write-Host "`nCréation du topic..." -ForegroundColor Cyan
    
    & java -cp "$kafkaDir\libs\*" kafka.admin.TopicCommand `
        --create `
        --topic $TopicName `
        --bootstrap-server localhost:9092 `
        --partitions $Partitions `
        --replication-factor $ReplicationFactor
    
    Write-Host "✅ Topic '$TopicName' créé avec succès!" -ForegroundColor Green
    
    # Vérification
    Write-Host "`nVérification du topic..." -ForegroundColor Cyan
    & java -cp "$kafkaDir\libs\*" kafka.admin.TopicCommand `
        --describe `
        --topic $TopicName `
        --bootstrap-server localhost:9092
        
} catch {
    Write-Host "❌ Erreur lors de la création du topic: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== TOPIC PRÊT POUR L'EXERCICE 1 ===" -ForegroundColor Green