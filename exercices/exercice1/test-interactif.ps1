# Script PowerShell interactif pour tester Kafka en direct
$kafkaHome = "C:\Big_data\kafka\kafka_2.13-3.9.1"
Set-Location $kafkaHome

Write-Host "=== TEST KAFKA EN DIRECT ===" -ForegroundColor Green
Write-Host "Topic: weather_stream" -ForegroundColor Cyan
Write-Host ""

# Vérification que Kafka fonctionne
$port9092 = netstat -an | Select-String ":9092"
if (-not $port9092) {
    Write-Host "ERREUR: Kafka n'est pas demarre!" -ForegroundColor Red
    exit 1
}

Write-Host "Kafka est actif! Vous pouvez maintenant envoyer des messages." -ForegroundColor Green
Write-Host ""
Write-Host "Instructions:" -ForegroundColor Yellow
Write-Host "1. Ouvrez une autre console PowerShell" -ForegroundColor White
Write-Host "2. Executez: cmd /c 'C:\Big_data\kafka\consumer-direct.bat'" -ForegroundColor White
Write-Host "3. Revenez ici pour envoyer des messages" -ForegroundColor White
Write-Host ""

# Boucle interactive
do {
    Write-Host "Entrez votre message JSON (ou 'quit' pour sortir):" -ForegroundColor Cyan
    $message = Read-Host "> "
    
    if ($message -eq "quit" -or $message -eq "exit") {
        break
    }
    
    if ($message.Trim() -ne "") {
        # Si ce n'est pas du JSON, on l'encapsule
        if (-not $message.StartsWith("{")) {
            $message = "{`"msg`": `"$message`", `"timestamp`": `"$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`"}"
        }
        
        Write-Host "Envoi du message: $message" -ForegroundColor Green
        $message | & java -cp "libs/*" kafka.tools.ConsoleProducer --topic weather_stream --bootstrap-server localhost:9092 2>$null
        Write-Host "Message envoye!" -ForegroundColor Green
        Write-Host ""
    }
} while ($true)

Write-Host "Test termine. Au revoir!" -ForegroundColor Green