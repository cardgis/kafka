# Exercice 1 - Lecture des messages depuis weather_stream
param(
    [string]$TopicName = "weather_stream",
    [switch]$FromBeginning
)

Write-Host "=== LECTURE MESSAGES EXERCICE 1 ===" -ForegroundColor Green
Write-Host "Topic: $TopicName" -ForegroundColor Yellow

$kafkaDir = "..\..\kafka_2.13-3.9.1"

# Construction des arguments
$consumerArgs = @(
    "--bootstrap-server", "localhost:9092",
    "--topic", $TopicName,
    "--property", "print.key=true",
    "--property", "print.value=true",
    "--property", "print.timestamp=true"
)

if ($FromBeginning) {
    $consumerArgs += "--from-beginning"
    Write-Host "Mode: Lecture depuis le début" -ForegroundColor Cyan
} else {
    Write-Host "Mode: Lecture des nouveaux messages" -ForegroundColor Cyan
}

Write-Host "`n🔍 Lecture des messages en cours..." -ForegroundColor Yellow
Write-Host "Appuyez sur Ctrl+C pour arrêter`n" -ForegroundColor Gray

try {
    & java -cp "$kafkaDir\libs\*" kafka.tools.ConsoleConsumer @consumerArgs
    
} catch {
    Write-Host "`n❌ Erreur lors de la lecture: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== FIN LECTURE EXERCICE 1 ===" -ForegroundColor Green