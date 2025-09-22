@echo off
echo 🌊📊 Test Exercice 8 - Weather Data Visualization and BI Analytics
echo ================================================================

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

:: Vérification de la présence des données HDFS
if not exist "hdfs-data" (
    echo ❌ Dossier hdfs-data introuvable
    echo ℹ️  Veuillez d'abord exécuter l'exercice 7 pour générer les données HDFS
    exit /b 1
)

:: Test 1: Génération des visualisations complètes
echo.
echo 🎨 Test 1: Génération des visualisations complètes...
python weather_visualizer.py --input "./hdfs-data" --verbose
if errorlevel 1 (
    echo ❌ Erreur lors de la génération des visualisations complètes
    exit /b 1
)

:: Test 2: Dashboard interactif seulement
echo.
echo 🎛️ Test 2: Génération du dashboard interactif...
python weather_visualizer.py --input "./hdfs-data" --dashboard --verbose
if errorlevel 1 (
    echo ❌ Erreur lors de la génération du dashboard interactif
    exit /b 1
)

:: Test 3: Export des données agrégées
echo.
echo 📊 Test 3: Export des données agrégées...
python weather_visualizer.py --input "./hdfs-data" --export-data --verbose
if errorlevel 1 (
    echo ❌ Erreur lors de l'export des données agrégées
    exit /b 1
)

:: Vérification des fichiers générés
echo.
echo 🔍 Vérification des fichiers générés...

set "visualizations_dir=visualizations"
if exist "%visualizations_dir%" (
    echo ✅ Dossier visualizations créé
    
    if exist "%visualizations_dir%\01_temporal_overview.png" (
        echo ✅ Analyse temporelle générée
    ) else (
        echo ❌ Analyse temporelle manquante
    )
    
    if exist "%visualizations_dir%\02_geographical_analysis.png" (
        echo ✅ Analyse géographique générée
    ) else (
        echo ❌ Analyse géographique manquante
    )
    
    if exist "%visualizations_dir%\03_alert_analysis.png" (
        echo ✅ Analyse des alertes générée
    ) else (
        echo ❌ Analyse des alertes manquante
    )
    
    if exist "%visualizations_dir%\04_correlation_analysis.png" (
        echo ✅ Analyse des corrélations générée
    ) else (
        echo ❌ Analyse des corrélations manquante
    )
    
    if exist "%visualizations_dir%\05_interactive_dashboard.html" (
        echo ✅ Dashboard interactif généré
    ) else (
        echo ❌ Dashboard interactif manquant
    )
    
    if exist "%visualizations_dir%\exports" (
        echo ✅ Dossier exports créé
        
        if exist "%visualizations_dir%\exports\daily_aggregated_data.csv" (
            echo ✅ Données journalières exportées
        ) else (
            echo ❌ Données journalières manquantes
        )
        
        if exist "%visualizations_dir%\exports\country_statistics.csv" (
            echo ✅ Statistiques par pays exportées
        ) else (
            echo ❌ Statistiques par pays manquantes
        )
        
        if exist "%visualizations_dir%\exports\complete_statistics.json" (
            echo ✅ Statistiques complètes exportées
        ) else (
            echo ❌ Statistiques complètes manquantes
        )
    ) else (
        echo ❌ Dossier exports manquant
    )
) else (
    echo ❌ Dossier visualizations manquant
)

:: Test avec filtrage par pays
echo.
echo 🌍 Test 4: Filtrage par pays (France)...
python weather_visualizer.py --input "./hdfs-data" --country FR --type geographical --verbose
if errorlevel 1 (
    echo ❌ Erreur lors du filtrage par pays
    exit /b 1
)

echo.
echo 🎊 Tous les tests de l'exercice 8 sont terminés avec succès!
echo.
echo 📊 Résultats disponibles dans:
echo    - ./visualizations/ : Graphiques et analyses
echo    - ./visualizations/exports/ : Données agrégées
echo    - ./visualizations/05_interactive_dashboard.html : Dashboard interactif
echo.
echo 💡 Pour ouvrir le dashboard interactif:
echo    - Double-cliquez sur ./visualizations/05_interactive_dashboard.html
echo    - Ou ouvrez-le dans votre navigateur web
echo.
echo ✅ Exercice 8 validé: Advanced BI Visualizations pour données météorologiques Kafka!