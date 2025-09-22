# Script PowerShell pour setup du repository distant
# Usage: .\setup-remote.ps1 "https://github.com/username/kafka-streaming-exercises.git"

param(
    [Parameter(Mandatory=$true)]
    [string]$RemoteUrl
)

Write-Host "=== Setup Repository Distant ===" -ForegroundColor Green

# Vérifier si on est dans le bon répertoire
if (-not (Test-Path ".git")) {
    Write-Host "ERREUR: Pas dans un repository Git" -ForegroundColor Red
    exit 1
}

# Ajouter le remote origin
Write-Host "1. Ajout du repository distant..." -ForegroundColor Yellow
try {
    git remote add origin $RemoteUrl
    Write-Host "✓ Remote origin ajouté: $RemoteUrl" -ForegroundColor Green
} catch {
    Write-Host "⚠ Remote origin existe déjà ou erreur" -ForegroundColor Yellow
    git remote set-url origin $RemoteUrl
    Write-Host "✓ Remote origin mis à jour: $RemoteUrl" -ForegroundColor Green
}

# Pousser toutes les branches
Write-Host "`n2. Push de toutes les branches..." -ForegroundColor Yellow

$branches = @("master", "exercice1", "exercice2", "exercice3", "exercice4", "exercice5", "exercice6", "exercice7", "exercice8")

foreach ($branch in $branches) {
    Write-Host "Pushing $branch..." -ForegroundColor Cyan
    try {
        git push -u origin $branch
        Write-Host "✓ $branch poussée avec succès" -ForegroundColor Green
    } catch {
        Write-Host "✗ Erreur lors du push de $branch" -ForegroundColor Red
    }
}

Write-Host "`n3. Vérification..." -ForegroundColor Yellow
git remote -v
git branch -a

Write-Host "`n=== Setup terminé ===" -ForegroundColor Green
Write-Host "Repository configuré avec:" -ForegroundColor Cyan
Write-Host "- Remote: $RemoteUrl" -ForegroundColor White
Write-Host "- Branches: 9 (master + 8 exercices)" -ForegroundColor White
Write-Host "- Status: Prêt pour le développement" -ForegroundColor White

Write-Host "`nCommandes utiles:" -ForegroundColor Yellow
Write-Host "git status                    # Voir l'état" -ForegroundColor White
Write-Host "git checkout exercice2        # Basculer vers exercice 2" -ForegroundColor White
Write-Host "git push origin exercice2     # Pousser exercice 2" -ForegroundColor White