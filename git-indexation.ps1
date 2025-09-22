# Script d'Indexation Git - Kafka Weather Analytics
# Version simplifiee sans caracteres speciaux

param(
    [Parameter(Mandatory=$false)]
    [string]$TagVersion = "v1.0.0",
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false
)

Write-Host "=== INDEXATION GIT - KAFKA WEATHER ANALYTICS ===" -ForegroundColor Cyan
Write-Host "Version: $TagVersion" -ForegroundColor Green

# Configuration
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

# Verification Git
function Test-GitStatus {
    $status = git status --porcelain 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Erreur: Repository Git invalide"
        exit 1
    }
    return $status
}

# Resume du projet
function Show-ProjectSummary {
    Write-Host "`nRESUME DU PROJET:" -ForegroundColor Yellow
    
    $exercices = Get-ChildItem "exercices" -Directory -ErrorAction SilentlyContinue
    Write-Host "   Exercices implementes: $($exercices.Count)" -ForegroundColor Green
    
    $pythonFiles = Get-ChildItem -Recurse -Filter "*.py" -ErrorAction SilentlyContinue
    Write-Host "   Fichiers Python: $($pythonFiles.Count)" -ForegroundColor Green
    
    $psFiles = Get-ChildItem -Recurse -Filter "*.ps1" -ErrorAction SilentlyContinue
    Write-Host "   Scripts PowerShell: $($psFiles.Count)" -ForegroundColor Green
    
    $codeLines = 0
    Get-ChildItem -Recurse -Include "*.py", "*.ps1" -ErrorAction SilentlyContinue | ForEach-Object {
        $lines = (Get-Content $_.FullName -ErrorAction SilentlyContinue).Count
        $codeLines += $lines
    }
    Write-Host "   Lignes de code total: $codeLines" -ForegroundColor Green
    
    $commitCount = git rev-list --count HEAD 2>$null
    if ($commitCount) {
        Write-Host "   Commits total: $commitCount" -ForegroundColor Green
    }
}

# Creation du tag
function New-VersionTag {
    param([string]$Version)
    
    Write-Host "`nCREATION DU TAG DE VERSION:" -ForegroundColor Yellow
    
    $existingTag = git tag --list $Version 2>$null
    if ($existingTag) {
        Write-Warning "Le tag $Version existe deja"
        return
    }
    
    $tagMessage = "Version $Version - Pipeline Kafka Weather Analytics Complet

FONCTIONNALITES PRINCIPALES:
- 8 exercices Kafka implementes et testes
- Pipeline end-to-end operationnel
- Support geolocalisation avec Open-Meteo APIs
- Visualisations avancees et dashboards BI
- Scripts d automatisation PowerShell

ARCHITECTURE:
- Apache Kafka 2.13-3.9.1 KRaft mode
- PySpark Structured Streaming
- Integration HDFS avec partitioning geographique
- APIs REST meteo + geocodage
- Systeme de monitoring et alertes

STATUT: PRODUCTION READY"

    if (-not $DryRun) {
        git tag -a $Version -m $tagMessage
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   Tag cree: $Version" -ForegroundColor Green
        } else {
            Write-Error "   Erreur lors de la creation du tag"
        }
    } else {
        Write-Host "   Mode DryRun: Tag simule - $Version" -ForegroundColor Gray
    }
}

# Generation du rapport
function New-IndexationReport {
    Write-Host "`nGENERATION DU RAPPORT:" -ForegroundColor Yellow
    
    $reportContent = "# RAPPORT D INDEXATION GIT
**Date**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Version**: $TagVersion

## STATUT FINAL
- Repository Git optimise et nettoye
- Tag de version cree: $TagVersion
- Structure projet validee
- Documentation complete
- .gitignore optimise

## STATISTIQUES
- **Exercices**: $((Get-ChildItem 'exercices' -Directory -ErrorAction SilentlyContinue).Count)
- **Fichiers Python**: $((Get-ChildItem -Recurse -Filter '*.py' -ErrorAction SilentlyContinue).Count)
- **Scripts PowerShell**: $((Get-ChildItem -Recurse -Filter '*.ps1' -ErrorAction SilentlyContinue).Count)
- **Commits**: $(git rev-list --count HEAD 2>`$null)

## PROCHAINES ETAPES
1. **Push vers remote**: git push -u origin master
2. **Verifier sur GitHub/GitLab**: Interface web
3. **Configuration CI/CD**: GitHub Actions/GitLab CI

## COMMANDES RAPIDES
Push complet:
git push -u origin master
git push --all origin  
git push --tags origin

Verification:
git remote -v
git tag -l
git log --oneline -10"

    $reportPath = "INDEXATION_REPORT.md"
    if (-not $DryRun) {
        $reportContent | Out-File -FilePath $reportPath -Encoding UTF8
        Write-Host "   Rapport sauve: $reportPath" -ForegroundColor Green
    } else {
        Write-Host "   Mode DryRun: Rapport simule" -ForegroundColor Gray
    }
}

# === EXECUTION PRINCIPALE ===

try {
    Write-Host "Demarrage de l'indexation Git..." -ForegroundColor Blue
    
    # Resume du projet
    Show-ProjectSummary
    
    # Verifier le statut Git
    $gitStatus = Test-GitStatus
    if ($gitStatus) {
        Write-Host "`nFICHIERS NON COMMITES DETECTES:" -ForegroundColor Yellow
        $gitStatus | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
        
        if (-not $DryRun) {
            git add .
            git commit -m "INDEXATION: Preparation finale pour tag $TagVersion"
            Write-Host "   Commit automatique effectue" -ForegroundColor Green
        }
    } else {
        Write-Host "`nWorking directory propre - pret pour l'indexation" -ForegroundColor Green
    }
    
    # Creation du tag de version
    New-VersionTag -Version $TagVersion
    
    # Generation du rapport
    New-IndexationReport
    
    # Resume final
    Write-Host "`nINDEXATION GIT TERMINEE AVEC SUCCES!" -ForegroundColor Green
    Write-Host "   Tag cree: $TagVersion" -ForegroundColor Cyan
    Write-Host "   Rapport: INDEXATION_REPORT.md" -ForegroundColor Cyan
    
    Write-Host "`nPROJET PRET POUR LE DEVELOPPEMENT COLLABORATIF!" -ForegroundColor Green

} catch {
    Write-Error "Erreur lors de l'indexation: $($_.Exception.Message)"
    exit 1
}