@echo off
REM Test Hello World pour Kafka
echo ========================================
echo Test Hello World - Apache Kafka 3.9.1
echo ========================================

cd /d "C:\kafka\kafka_2.13-3.9.1"

echo.
echo 1. Creation du topic 'hello-world'...
bin\windows\kafka-topics.bat --create --topic hello-world --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

echo.
echo 2. Verification du topic cree:
bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092

echo.
echo 3. Test termine ! Topic hello-world cree.
echo.
echo Pour tester l'envoi/reception de messages:
echo - Producteur: bin\windows\kafka-console-producer.bat --topic hello-world --bootstrap-server localhost:9092
echo - Consommateur: bin\windows\kafka-console-consumer.bat --topic hello-world --from-beginning --bootstrap-server localhost:9092

pause