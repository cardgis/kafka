@echo off
echo Test rapide Kafka sans ZooKeeper (mode KRaft)
echo.

REM Initialiser le stockage Kafka en mode KRaft
echo Initialisation du stockage...
bin\windows\kafka-storage.bat random-uuid > cluster-id.txt
set /p CLUSTER_ID=<cluster-id.txt

bin\windows\kafka-storage.bat format -t %CLUSTER_ID% -c config\kraft\server.properties

echo.
echo Demarrage de Kafka en mode KRaft...
start "Kafka KRaft" bin\windows\kafka-server-start.bat config\kraft\server.properties

echo.
echo Attendre 10 secondes pour le demarrage...
timeout /t 10 /nobreak > nul

echo.
echo Creation du topic hello-world...
bin\windows\kafka-topics.bat --create --topic hello-world --bootstrap-server localhost:9092

echo.
echo Test termine ! Topic cree.
pause
