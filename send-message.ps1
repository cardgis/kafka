# Exercice 1 - Envoi de messages vers weather_stream
param(
    [string]$TopicName = "weather_stream",
    [string]$Message = ""
)

Write-Host "=== ENVOI MESSAGE EXERCICE 1 ===" -ForegroundColor Green
Write-Host "Topic: $TopicName" -ForegroundColor Yellow

$kafkaDir = "..\..\kafka_2.13-3.9.1"

# Messages prédéfinis pour l'exercice 1
$messages = @(
    '{"msg": "Hello Kafka"}',
    '{"temperature": 22.5, "city": "Paris", "timestamp": "' + (Get-Date -Format "yyyy-MM-ddTHH:mm:ss") + '"}',
    '{"temperature": 18.3, "city": "Lyon", "timestamp": "' + (Get-Date -Format "yyyy-MM-ddTHH:mm:ss") + '"}',
    '{"temperature": 25.1, "city": "Marseille", "timestamp": "' + (Get-Date -Format "yyyy-MM-ddTHH:mm:ss") + '"}'
)

if ($Message -eq "") {
    Write-Host "`nMessages disponibles pour l'exercice 1:" -ForegroundColor Cyan
    for ($i = 0; $i -lt $messages.Length; $i++) {
        Write-Host "$($i+1). $($messages[$i])" -ForegroundColor White
    }
    
    $choice = Read-Host "`nChoisissez un message (1-$($messages.Length)) ou tapez votre message"
    
    if ($choice -match '^\d+$' -and [int]$choice -ge 1 -and [int]$choice -le $messages.Length) {
        $Message = $messages[[int]$choice - 1]
    } else {
        $Message = $choice
    }
}

Write-Host "`nEnvoi du message: $Message" -ForegroundColor Yellow

try {
    # Création d'un fichier temporaire pour le message
    $tempFile = [System.IO.Path]::GetTempFileName()
    $Message | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline
    
    # Envoi du message
    Get-Content $tempFile | & java -cp "$kafkaDir\libs\*" kafka.tools.ConsoleProducer `
        --broker-list localhost:9092 `
        --topic $TopicName
    
    # Nettoyage
    Remove-Item $tempFile -Force
    
    Write-Host "✅ Message envoyé avec succès!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Erreur lors de l'envoi: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== MESSAGE ENVOYÉ POUR EXERCICE 1 ===" -ForegroundColor Green