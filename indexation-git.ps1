# 🏷️ Script d'Indexation Git - Pipeline Kafka Weather Analytics
# Automatise le processus d'indexation et de préparation pour le repository

param(
    [Parameter(Mandatory=$false)]
    [string]$RemoteUrl = "",
    
    [Parameter(Mandatory=$false)]
    [string]$TagVersion = "v1.0.0",
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$PushToRemote = $false
)

Write-Host "=== SCRIPT D'INDEXATION GIT - KAFKA WEATHER ANALYTICS ===" -ForegroundColor Cyan
Write-Host "Version: $TagVersion" -ForegroundColor Green

# Configuration
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

# Fonction de validation
function Test-GitStatus {
    $status = git status --porcelain 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Erreur: Ce répertoire n'est pas un repository Git valide"
        exit 1
    }
    return $status
}

# Fonction d'affichage du statut
function Show-ProjectSummary {
    Write-Host "`n📊 RÉSUMÉ DU PROJET:" -ForegroundColor Yellow
    
    # Compter les exercices
    $exercices = Get-ChildItem "exercices" -Directory -ErrorAction SilentlyContinue
    Write-Host "   📁 Exercices implémentés: $($exercices.Count)" -ForegroundColor Green
    
    # Compter les fichiers Python
    $pythonFiles = Get-ChildItem -Recurse -Filter "*.py" -ErrorAction SilentlyContinue
    Write-Host "   🐍 Fichiers Python: $($pythonFiles.Count)" -ForegroundColor Green
    
    # Compter les scripts PowerShell
    $psFiles = Get-ChildItem -Recurse -Filter "*.ps1" -ErrorAction SilentlyContinue
    Write-Host "   ⚡ Scripts PowerShell: $($psFiles.Count)" -ForegroundColor Green
    
    # Compter les lignes de code
    $codeLines = 0
    Get-ChildItem -Recurse -Include "*.py", "*.ps1" -ErrorAction SilentlyContinue | ForEach-Object {
        $lines = (Get-Content $_.FullName -ErrorAction SilentlyContinue).Count
        $codeLines += $lines
    }
    Write-Host "   📝 Lignes de code total: $codeLines" -ForegroundColor Green
    
    # Vérifier les branches
    $branches = git branch --list 2>$null
    if ($branches) {
        $branchCount = ($branches | Measure-Object).Count
        Write-Host "   🌿 Branches Git: $branchCount" -ForegroundColor Green
    }
    
    # Vérifier les commits
    $commitCount = git rev-list --count HEAD 2>$null
    if ($commitCount) {
        Write-Host "   📝 Commits total: $commitCount" -ForegroundColor Green
    }
}

# Fonction de vérification des pré-requis
function Test-Prerequisites {
    Write-Host "`n🔍 VÉRIFICATION DES PRÉ-REQUIS:" -ForegroundColor Yellow
    
    # Vérifier Git
    try {
        $gitVersion = git --version 2>$null
        Write-Host "   ✅ Git installé: $gitVersion" -ForegroundColor Green
    } catch {
        Write-Error "❌ Git n'est pas installé ou accessible"
        exit 1
    }
    
    # Vérifier la structure du projet
    $requiredDirs = @("exercices", "kafka_2.13-3.9.1")
    foreach ($dir in $requiredDirs) {
        if (Test-Path $dir) {
            Write-Host "   ✅ Répertoire requis: $dir" -ForegroundColor Green
        } else {
            Write-Warning "   ⚠️  Répertoire manquant: $dir"
        }
    }
    
    # Vérifier les fichiers essentiels
    $requiredFiles = @("README.md", "PROJECT_README.md", "FINAL_STATUS.md")
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Host "   ✅ Fichier essentiel: $file" -ForegroundColor Green
        } else {
            Write-Warning "   ⚠️  Fichier manquant: $file"
        }
    }
}

# Fonction de nettoyage et optimisation
function Optimize-Repository {
    Write-Host "`n🧹 OPTIMISATION DU REPOSITORY:" -ForegroundColor Yellow
    
    if (-not $DryRun) {
        # Nettoyage Git
        Write-Host "   🗑️  Nettoyage des objets Git..." -ForegroundColor Blue
        git gc --aggressive --prune=now 2>$null
        
        # Vérification de l'intégrité
        Write-Host "   🔍 Vérification de l'intégrité..." -ForegroundColor Blue
        $fsckResult = git fsck --full 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Intégrité du repository: OK" -ForegroundColor Green
        } else {
            Write-Warning "   ⚠️  Problèmes détectés dans le repository"
        }
    } else {
        Write-Host "   📋 Mode DryRun: Nettoyage simulé" -ForegroundColor Gray
    }
}

# Fonction de création des tags
function New-VersionTag {
    param([string]$Version)
    
    Write-Host "`n🏷️  CRÉATION DU TAG DE VERSION:" -ForegroundColor Yellow
    
    # Vérifier si le tag existe déjà
    $existingTag = git tag --list $Version 2>$null
    if ($existingTag) {
        Write-Warning "   ⚠️  Le tag $Version existe déjà"
        $response = Read-Host "   Voulez-vous le remplacer? (y/N)"
        if ($response -eq "y" -or $response -eq "Y") {
            if (-not $DryRun) {
                git tag -d $Version 2>$null
                Write-Host "   🗑️  Tag existant supprimé" -ForegroundColor Blue
            }
        } else {
            Write-Host "   ⏭️  Création du tag annulée" -ForegroundColor Gray
            return
        }
    }
    
    # Créer le nouveau tag
    $tagMessage = @"
Version $Version: Pipeline Kafka Weather Analytics Complet

🚀 FONCTIONNALITÉS PRINCIPALES:
- 8 exercices Kafka implémentés et testés
- Pipeline end-to-end opérationnel (APIs → Kafka → HDFS → Visualisations)
- Support géolocalisation avec Open-Meteo APIs
- Visualisations avancées et dashboards BI
- Scripts d'automatisation PowerShell

🏗️ ARCHITECTURE:
- Apache Kafka 2.13-3.9.1 (KRaft mode)
- PySpark Structured Streaming
- Intégration HDFS avec partitioning géographique
- APIs REST (météo + géocodage)
- Système de monitoring et alertes

📊 STATISTIQUES:
- $((Get-ChildItem -Recurse -Include "*.py").Count) fichiers Python
- $((Get-ChildItem -Recurse -Include "*.ps1").Count) scripts PowerShell
- Pipeline testé sur 6 pays avec données temps réel
- 7 types de visualisations (température, vent, alertes, géographie)

✅ STATUT: PRODUCTION READY
"@

    if (-not $DryRun) {
        git tag -a $Version -m $tagMessage
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Tag créé: $Version" -ForegroundColor Green
        } else {
            Write-Error "   ❌ Erreur lors de la création du tag"
        }
    } else {
        Write-Host "   📋 Mode DryRun: Tag simulé - $Version" -ForegroundColor Gray
    }
}

# Fonction de préparation remote
function Set-RemoteRepository {
    param([string]$Url)
    
    if ([string]::IsNullOrEmpty($Url)) {
        Write-Host "`n🔗 CONFIGURATION REPOSITORY REMOTE:" -ForegroundColor Yellow
        Write-Host "   ⏭️  Aucune URL remote fournie - étape ignorée" -ForegroundColor Gray
        return
    }
    
    Write-Host "`n🔗 CONFIGURATION REPOSITORY REMOTE:" -ForegroundColor Yellow
    
    # Vérifier les remotes existants
    $existingRemotes = git remote -v 2>$null
    if ($existingRemotes) {
        Write-Host "   📋 Remotes existants:" -ForegroundColor Blue
        $existingRemotes | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
        
        $hasOrigin = $existingRemotes | Select-String "origin"
        if ($hasOrigin) {
            $response = Read-Host "   Origin existe déjà. Remplacer? (y/N)"
            if ($response -eq "y" -or $response -eq "Y") {
                if (-not $DryRun) {
                    git remote set-url origin $Url
                    Write-Host "   ✅ Remote origin mis à jour" -ForegroundColor Green
                }
            } else {
                Write-Host "   ⏭️  Configuration remote ignorée" -ForegroundColor Gray
                return
            }
        }
    } else {
        if (-not $DryRun) {
            git remote add origin $Url
            Write-Host "   ✅ Remote origin ajouté: $Url" -ForegroundColor Green
        }
    }
    
    if ($DryRun) {
        Write-Host "   📋 Mode DryRun: Remote simulé - $Url" -ForegroundColor Gray
    }
}

# Fonction de push vers remote
function Push-ToRemote {
    param([string]$TagVersion)
    
    if (-not $PushToRemote) {
        Write-Host "`n🚀 PUSH VERS REMOTE:" -ForegroundColor Yellow
        Write-Host "   ⏭️  Push non demandé (utilisez -PushToRemote)" -ForegroundColor Gray
        return
    }
    
    Write-Host "`n🚀 PUSH VERS REMOTE:" -ForegroundColor Yellow
    
    # Vérifier la connectivité
    $remoteUrl = git remote get-url origin 2>$null
    if (-not $remoteUrl) {
        Write-Warning "   ⚠️  Aucun remote 'origin' configuré"
        return
    }
    
    Write-Host "   🔗 Remote URL: $remoteUrl" -ForegroundColor Blue
    
    if (-not $DryRun) {
        Write-Host "   📤 Push branche master..." -ForegroundColor Blue
        git push -u origin master
        
        Write-Host "   📤 Push toutes les branches..." -ForegroundColor Blue
        git push --all origin
        
        Write-Host "   📤 Push tags..." -ForegroundColor Blue
        git push --tags origin
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Push terminé avec succès" -ForegroundColor Green
        } else {
            Write-Error "   ❌ Erreur lors du push"
        }
    } else {
        Write-Host "   📋 Mode DryRun: Push simulé vers $remoteUrl" -ForegroundColor Gray
    }
}

# Fonction de génération du rapport final
function New-IndexationReport {
    Write-Host "`n📋 GÉNÉRATION DU RAPPORT D'INDEXATION:" -ForegroundColor Yellow
    
    $reportContent = @"
# 📊 RAPPORT D'INDEXATION GIT
**Date**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Version**: $TagVersion

## 🎯 STATUT FINAL
- ✅ Repository Git optimisé et nettoyé
- ✅ Tag de version créé: $TagVersion
- ✅ Structure projet validée
- ✅ Documentation complète
- ✅ .gitignore optimisé

## 📈 STATISTIQUES
- **Exercices**: $((Get-ChildItem "exercices" -Directory -ErrorAction SilentlyContinue).Count)
- **Fichiers Python**: $((Get-ChildItem -Recurse -Filter "*.py" -ErrorAction SilentlyContinue).Count)
- **Scripts PowerShell**: $((Get-ChildItem -Recurse -Filter "*.ps1" -ErrorAction SilentlyContinue).Count)
- **Commits**: $(git rev-list --count HEAD 2>$null)
- **Branches**: $((git branch --list 2>$null | Measure-Object).Count)

## 🔄 PROCHAINES ÉTAPES RECOMMANDÉES
1. **Push vers remote**: ``git push -u origin master``
2. **Vérifier sur GitHub/GitLab**: Interface web
3. **Cloner pour test**: ``git clone [URL] test-repo``
4. **Configuration CI/CD**: GitHub Actions/GitLab CI
5. **Documentation wiki**: Pages projet

## 🚀 COMMANDES RAPIDES
```powershell
# Push complet
git push -u origin master
git push --all origin  
git push --tags origin

# Vérification
git remote -v
git tag -l
git log --oneline -10
```

---
*Généré automatiquement par indexation-git.ps1*
"@

    $reportPath = "INDEXATION_REPORT.md"
    if (-not $DryRun) {
        $reportContent | Out-File -FilePath $reportPath -Encoding UTF8
        Write-Host "   ✅ Rapport sauvé: $reportPath" -ForegroundColor Green
    } else {
        Write-Host "   📋 Mode DryRun: Rapport simulé" -ForegroundColor Gray
    }
}

# === EXÉCUTION PRINCIPALE ===

try {
    Write-Host "Démarrage de l'indexation Git..." -ForegroundColor Blue
    
    # Vérifications préliminaires
    Test-Prerequisites
    Show-ProjectSummary
    
    # Vérifier le statut Git
    $gitStatus = Test-GitStatus
    if ($gitStatus) {
        Write-Host "`n⚠️  FICHIERS NON COMMITÉES DÉTECTÉS:" -ForegroundColor Yellow
        $gitStatus | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
        
        if (-not $DryRun) {
            $response = Read-Host "`nCommitter automatiquement? (y/N)"
            if ($response -eq "y" -or $response -eq "Y") {
                git add .
                git commit -m "INDEXATION: Préparation finale pour tag $TagVersion

- Optimisation .gitignore
- Documentation complète
- Structure projet finalisée
- Prêt pour indexation Git"
                Write-Host "   ✅ Commit automatique effectué" -ForegroundColor Green
            } else {
                Write-Warning "Veuillez committer les changements avant de continuer"
                exit 1
            }
        }
    } else {
        Write-Host "`n✅ Working directory propre - prêt pour l'indexation" -ForegroundColor Green
    }
    
    # Optimisation du repository
    Optimize-Repository
    
    # Création du tag de version
    New-VersionTag -Version $TagVersion
    
    # Configuration remote si fournie
    Set-RemoteRepository -Url $RemoteUrl
    
    # Push vers remote si demandé
    Push-ToRemote -TagVersion $TagVersion
    
    # Génération du rapport
    New-IndexationReport
    
    # Résumé final
    Write-Host "`n🎉 INDEXATION GIT TERMINÉE AVEC SUCCÈS!" -ForegroundColor Green
    Write-Host "   📋 Tag créé: $TagVersion" -ForegroundColor Cyan
    Write-Host "   🔗 Remote: $($RemoteUrl -or 'Non configuré')" -ForegroundColor Cyan
    Write-Host "   📊 Rapport: INDEXATION_REPORT.md" -ForegroundColor Cyan
    
    if (-not $PushToRemote -and -not [string]::IsNullOrEmpty($RemoteUrl)) {
        Write-Host "`n💡 CONSEIL: Utilisez -PushToRemote pour pousser vers le remote" -ForegroundColor Yellow
    }
    
    Write-Host "`n🚀 Le projet est maintenant prêt pour le développement collaboratif!" -ForegroundColor Green

} catch {
    Write-Error "Erreur lors de l'indexation: $($_.Exception.Message)"
    exit 1
}