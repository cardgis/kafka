#!/usr/bin/env powershell
# Script pour créer les branches dédiées pour chaque exercice

Write-Host "🌟 Création des branches dédiées pour chaque exercice" -ForegroundColor Green

# Array des exercices
$exercices = @(2, 3, 4, 5, 6, 7, 8)

foreach ($ex in $exercices) {
    Write-Host "📝 Traitement exercice$ex..." -ForegroundColor Yellow
    
    # Checkout vers main pour récupérer le contenu complet
    git checkout main
    
    # Checkout vers la branche exercice
    git checkout exercice$ex
    
    # Merge le contenu de main
    git merge main --no-edit
    
    # Copier le contenu spécifique de l'exercice vers la racine
    if (Test-Path "exercices\exercice$ex") {
        Copy-Item -Path "exercices\exercice$ex\*" -Destination "." -Recurse -Force
        Write-Host "  ✅ Contenu exercice$ex copié" -ForegroundColor Green
    }
    
    # Supprimer le dossier exercices
    if (Test-Path "exercices") {
        Remove-Item -Path "exercices" -Recurse -Force
        Write-Host "  ✅ Dossier exercices supprimé" -ForegroundColor Green
    }
    
    # Créer un README spécifique à la branche
    $branchReadme = @"
# 🚀 Exercice $ex - Branch Dédiée

## 🎯 Bienvenue sur la branche `exercice$ex`

Cette branche contient **uniquement** le contenu de l'exercice $ex.

## 🌟 Navigation entre exercices

- **Exercice 1** - ``git checkout exercice1`` - Setup Kafka & Zookeeper
- **Exercice 2** - ``git checkout exercice2`` - Basic Producer/Consumer  
- **Exercice 3** - ``git checkout exercice3`` - Weather Data Streaming
- **Exercice 4** - ``git checkout exercice4`` - Multi-City Weather Networks
- **Exercice 5** - ``git checkout exercice5`` - Real-time Weather Alerts
- **Exercice 6** - ``git checkout exercice6`` - Geographic Weather Streaming
- **Exercice 7** - ``git checkout exercice7`` - HDFS Consumer & Storage
- **Exercice 8** - ``git checkout exercice8`` - BI Visualizations & Analytics

## 📚 Documentation complète

Consultez le [README principal](https://github.com/cardgis/kafka/blob/main/README.md) pour la vue d'ensemble du projet.

---
**🎯 Cette branche est dédiée exclusivement à l'exercice $ex. Chaque exercice a sa propre branche pour un développement isolé et structuré.**
"@
    
    $branchReadme | Out-File -FilePath "EXERCICE${ex}_BRANCH.md" -Encoding UTF8
    
    # Ajouter et commiter les changements
    git add -A
    git commit -m "🚀 Exercice $ex Branch: Dedicated branch with only exercice $ex content"
    
    Write-Host "  ✅ Exercice$ex branch configured" -ForegroundColor Green
}

Write-Host "🎊 Toutes les branches d'exercices ont été créées!" -ForegroundColor Green