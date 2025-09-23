@echo off
REM Script de test pour Kafka
echo Test de Kafka - Creation d'un topic et envoi de messages
cd /d "%~dp0kafka_2.13-3.9.1"

echo.
echo 1. Creation du topic 'test-topic'...
bin\windows\kafka-topics.bat --create --topic test-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

echo.
echo 2. Liste des topics disponibles:
bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092

echo.
echo 3. Pour tester l'envoi de messages, utilisez:
echo    bin\windows\kafka-console-producer.bat --topic test-topic --bootstrap-server localhost:9092
echo.
echo 4. Pour tester la reception de messages, utilisez (dans une autre console):
echo    bin\windows\kafka-console-consumer.bat --topic test-topic --from-beginning --bootstrap-server localhost:9092

pause
