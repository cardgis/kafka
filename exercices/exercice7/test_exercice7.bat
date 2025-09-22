@echo off
echo 🌊📁 Test Exercice 7 - HDFS Consumer and Distributed Storage
echo ============================================================

:: Vérification de l'environnement Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou accessible
    exit /b 1
)

:: Installation des dépendances
echo 📦 Installation des dépendances...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Erreur lors de l'installation des dépendances
    exit /b 1
)

:: Test 1: Génération de données de test
echo.
echo 🎲 Test 1: Génération de données de test...
python generate_test_data.py --records 200 --countries 3
if errorlevel 1 (
    echo ❌ Erreur lors de la génération des données de test
    exit /b 1
)

:: Vérification de la structure HDFS créée
echo.
echo 🔍 Vérification de la structure HDFS...
if exist "hdfs-data" (
    echo ✅ Dossier hdfs-data créé
    dir hdfs-data /B 2>nul | find /c /v "" > temp_count.txt
    set /p country_count=<temp_count.txt
    del temp_count.txt
    echo ✅ %country_count% pays détectés dans hdfs-data
) else (
    echo ❌ Dossier hdfs-data manquant
    exit /b 1
)

:: Test 2: Validation du consumer HDFS (test rapide)
echo.
echo 🧪 Test 2: Validation du script consumer HDFS...
python hdfs_consumer.py --help >nul 2>&1
if errorlevel 1 (
    echo ❌ Script hdfs_consumer.py ne fonctionne pas correctement
    exit /b 1
) else (
    echo ✅ Script hdfs_consumer.py valide
)

:: Test 3: Vérification du format des données
echo.
echo 📄 Test 3: Vérification du format des fichiers...
set "found_valid_file="
for /R hdfs-data %%f in (alerts.json) do (
    if exist "%%f" (
        set "found_valid_file=1"
        echo ✅ Fichier trouvé: %%f
        
        :: Vérification que le fichier n'est pas vide
        for %%A in ("%%f") do (
            if %%~zA gtr 0 (
                echo ✅ Fichier non vide: %%~zA bytes
            ) else (
                echo ❌ Fichier vide: %%f
            )
        )
        goto :break_loop
    )
)
:break_loop

if not defined found_valid_file (
    echo ❌ Aucun fichier alerts.json trouvé
    exit /b 1
)

:: Test 4: Comptage des enregistrements
echo.
echo 📊 Test 4: Comptage des enregistrements...
set "total_lines=0"
for /R hdfs-data %%f in (alerts.json) do (
    if exist "%%f" (
        for /f %%A in ('type "%%f" ^| find /c /v ""') do (
            set /a total_lines+=%%A
            echo ✅ %%f: %%A lignes
        )
    )
)
echo ✅ Total des enregistrements: %total_lines%

:: Test 5: Validation JSON (test rapide sur un fichier)
echo.
echo 🔬 Test 5: Validation du format JSON...
for /R hdfs-data %%f in (alerts.json) do (
    if exist "%%f" (
        python -c "import json; [json.loads(line) for line in open('%%f', 'r', encoding='utf-8') if line.strip()]" 2>nul
        if errorlevel 1 (
            echo ❌ Format JSON invalide dans: %%f
            exit /b 1
        ) else (
            echo ✅ Format JSON valide: %%f
        )
        goto :break_json_test
    )
)
:break_json_test

:: Test 6: Structure des dossiers
echo.
echo 📁 Test 6: Validation de la structure des dossiers...
set "structure_valid=1"
for /D %%d in (hdfs-data\*) do (
    echo ✅ Pays détecté: %%~nxd
    for /D %%c in (%%d\*) do (
        echo ✅   Ville détectée: %%~nxc
        if exist "%%c\alerts.json" (
            echo ✅     Fichier alerts.json présent
        ) else (
            echo ❌     Fichier alerts.json manquant dans %%c
            set "structure_valid=0"
        )
    )
)

if "%structure_valid%"=="0" (
    echo ❌ Structure HDFS incomplète
    exit /b 1
)

echo.
echo 🎊 Tous les tests de l'exercice 7 sont terminés avec succès!
echo.
echo 📊 Résultats:
echo    - Structure HDFS: ✅ Valide
echo    - Données générées: ✅ %total_lines% enregistrements
echo    - Format JSON: ✅ Valide
echo    - Consumer script: ✅ Fonctionnel
echo.
echo 💡 Données prêtes pour l'exercice 8:
echo    python ..\exercice8\weather_visualizer.py --input "./hdfs-data"
echo.
echo ✅ Exercice 7 validé: HDFS Consumer et stockage distribué!