@echo off
REM Script pour demarrer Kafka Server
echo Demarrage de Kafka Server...
cd /d "%~dp0kafka_2.13-3.9.1"
bin\windows\kafka-server-start.bat config\server.properties
pause