# Setup Environment - Kafka Weather Analytics Pipeline
# Configuration automatique de l'environnement de developpement

param(
    [Parameter(Mandatory=$false)]
    [switch]$SkipPythonSetup = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipKafkaSetup = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$InstallDev = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$QuickSetup = $false
)

Write-Host "=== CONFIGURATION ENVIRONNEMENT KAFKA WEATHER ANALYTICS ===" -ForegroundColor Cyan
Write-Host "Version: 1.0.0" -ForegroundColor Green

# Configuration
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

# Fonctions utilitaires
function Write-Step {
    param([string]$Message, [string]$Color = "Yellow")
    Write-Host "`n$Message" -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Host "   ✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "   ⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "   ❌ $Message" -ForegroundColor Red
}

# Verification des prerequis
function Test-Prerequisites {
    Write-Step "🔍 VERIFICATION DES PREREQUIS"
    
    # Verifier Python
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion -match "Python 3\.([8-9]|1[0-9])") {
            Write-Success "Python installé: $pythonVersion"
        } else {
            Write-Warning "Version Python non optimale: $pythonVersion"
            Write-Host "      Recommandé: Python 3.8+" -ForegroundColor Gray
        }
    } catch {
        Write-Error "Python non installé ou non accessible"
        Write-Host "      Installer Python 3.8+ depuis https://python.org" -ForegroundColor Gray
        return $false
    }
    
    # Verifier pip
    try {
        pip --version | Out-Null
        Write-Success "pip installé et accessible"
    } catch {
        Write-Error "pip non accessible"
        return $false
    }
    
    # Verifier Git
    try {
        $gitVersion = git --version 2>$null
        Write-Success "Git installé: $gitVersion"
    } catch {
        Write-Error "Git non installé"
        return $false
    }
    
    # Verifier Java pour Kafka
    if (-not $SkipKafkaSetup) {
        try {
            $javaVersion = java -version 2>&1 | Select-String "version"
            Write-Success "Java installé pour Kafka"
        } catch {
            Write-Warning "Java non détecté - nécessaire pour Kafka"
            Write-Host "      Installer OpenJDK 11+ ou Oracle JDK" -ForegroundColor Gray
        }
    }
    
    return $true
}

# Configuration Python
function Set-PythonEnvironment {
    if ($SkipPythonSetup) {
        Write-Step "⏭️  Configuration Python ignorée"
        return
    }
    
    Write-Step "🐍 CONFIGURATION ENVIRONNEMENT PYTHON"
    
    # Créer environnement virtuel si nécessaire
    if (-not (Test-Path "venv")) {
        Write-Host "   📦 Création environnement virtuel..." -ForegroundColor Blue
        python -m venv venv
        Write-Success "Environnement virtuel créé"
    } else {
        Write-Success "Environnement virtuel existant"
    }
    
    # Activer environnement virtuel
    Write-Host "   🔌 Activation environnement virtuel..." -ForegroundColor Blue
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
        Write-Success "Environnement virtuel activé"
    } else {
        Write-Warning "Script d'activation non trouvé"
    }
    
    # Mettre à jour pip
    Write-Host "   📈 Mise à jour pip..." -ForegroundColor Blue
    python -m pip install --upgrade pip
    Write-Success "pip mis à jour"
    
    # Installer dépendances principales
    Write-Host "   📦 Installation dépendances principales..." -ForegroundColor Blue
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Dépendances principales installées"
    } else {
        Write-Warning "Problèmes lors de l'installation des dépendances"
    }
    
    # Installer dépendances de développement
    if ($InstallDev) {
        Write-Host "   🛠️  Installation outils de développement..." -ForegroundColor Blue
        pip install pytest black flake8 isort mypy pre-commit
        Write-Success "Outils de développement installés"
    }
}

# Configuration Kafka
function Set-KafkaEnvironment {
    if ($SkipKafkaSetup) {
        Write-Step "⏭️  Configuration Kafka ignorée"
        return
    }
    
    Write-Step "📨 CONFIGURATION APACHE KAFKA"
    
    # Vérifier présence Kafka
    if (Test-Path "kafka_2.13-3.9.1") {
        Write-Success "Apache Kafka 2.13-3.9.1 détecté"
        
        # Vérifier scripts PowerShell
        $scripts = @("start-kafka.ps1", "start-zookeeper.ps1", "stop-kafka.ps1", "test-kafka.ps1")
        foreach ($script in $scripts) {
            if (Test-Path $script) {
                Write-Success "Script disponible: $script"
            } else {
                Write-Warning "Script manquant: $script"
            }
        }
        
        # Test de connectivité Kafka (rapide)
        if (-not $QuickSetup) {
            Write-Host "   🔍 Test rapide de connectivité..." -ForegroundColor Blue
            try {
                # Tenter de lister les topics existants
                $kafkaTest = & "kafka_2.13-3.9.1\bin\windows\kafka-topics.bat" --bootstrap-server localhost:9092 --list 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Kafka accessible sur localhost:9092"
                } else {
                    Write-Warning "Kafka non démarré (normal au premier setup)"
                    Write-Host "      Utiliser: .\start-kafka.ps1" -ForegroundColor Gray
                }
            } catch {
                Write-Warning "Test Kafka échoué (Kafka non démarré)"
            }
        }
    } else {
        Write-Error "Apache Kafka non trouvé dans le répertoire"
        Write-Host "      Vérifier l'installation Kafka" -ForegroundColor Gray
    }
}

# Configuration des exercices
function Test-Exercices {
    Write-Step "🧪 VALIDATION DES EXERCICES"
    
    if (Test-Path "exercices") {
        $exercices = Get-ChildItem "exercices" -Directory
        Write-Success "$($exercices.Count) exercices détectés"
        
        foreach ($exercice in $exercices) {
            $readmePath = Join-Path $exercice.FullName "README.md"
            $pythonFiles = Get-ChildItem $exercice.FullName -Filter "*.py" -ErrorAction SilentlyContinue
            
            if (Test-Path $readmePath) {
                Write-Success "$($exercice.Name): Documentation OK"
            } else {
                Write-Warning "$($exercice.Name): README.md manquant"
            }
            
            if ($pythonFiles.Count -gt 0) {
                Write-Success "$($exercice.Name): $($pythonFiles.Count) fichiers Python"
            } else {
                Write-Warning "$($exercice.Name): Aucun fichier Python"
            }
        }
    } else {
        Write-Error "Répertoire exercices non trouvé"
    }
}

# Configuration de développement
function Set-DevelopmentTools {
    Write-Step "🛠️  CONFIGURATION OUTILS DE DEVELOPPEMENT"
    
    # Configuration Git hooks si demandé
    if ($InstallDev -and (Test-Path ".git")) {
        Write-Host "   🪝 Configuration Git hooks..." -ForegroundColor Blue
        try {
            pre-commit install 2>$null
            Write-Success "Pre-commit hooks configurés"
        } catch {
            Write-Warning "Pre-commit non configuré (optionnel)"
        }
    }
    
    # Vérifier structure projet
    $requiredDirs = @("exercices", "kafka_2.13-3.9.1")
    $requiredFiles = @("README.md", "requirements.txt", "PROJECT_README.md")
    
    foreach ($dir in $requiredDirs) {
        if (Test-Path $dir) {
            Write-Success "Répertoire requis: $dir"
        } else {
            Write-Warning "Répertoire manquant: $dir"
        }
    }
    
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Success "Fichier essentiel: $file"
        } else {
            Write-Warning "Fichier manquant: $file"
        }
    }
}

# Instructions finales
function Show-FinalInstructions {
    Write-Step "🎯 INSTRUCTIONS FINALES" "Green"
    
    Write-Host "   📋 Environnement configuré avec succès!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   🚀 PROCHAINES ETAPES:" -ForegroundColor Cyan
    Write-Host "   1. Démarrer Kafka: .\start-kafka.ps1" -ForegroundColor White
    Write-Host "   2. Tester connexion: .\test-kafka.ps1" -ForegroundColor White
    Write-Host "   3. Exécuter exercice: cd exercices\exercice1" -ForegroundColor White
    Write-Host "   4. Lancer tests: pytest tests/" -ForegroundColor White
    Write-Host ""
    Write-Host "   📚 DOCUMENTATION:" -ForegroundColor Cyan
    Write-Host "   - README.md: Guide principal" -ForegroundColor White
    Write-Host "   - PROJECT_README.md: Documentation technique" -ForegroundColor White
    Write-Host "   - GUIDE_CONTINUITE.md: Suite du développement" -ForegroundColor White
    Write-Host ""
    Write-Host "   🌐 INTERFACES WEB (après démarrage Docker):" -ForegroundColor Cyan
    Write-Host "   - Kafka UI: http://localhost:8080" -ForegroundColor White
    Write-Host "   - Grafana: http://localhost:3000" -ForegroundColor White
    Write-Host "   - Dashboard: http://localhost:8501" -ForegroundColor White
}

# === EXECUTION PRINCIPALE ===

try {
    Write-Host "Démarrage configuration environnement..." -ForegroundColor Blue
    
    # Mode setup rapide
    if ($QuickSetup) {
        Write-Step "⚡ MODE SETUP RAPIDE ACTIVE" "Magenta"
    }
    
    # Vérifications préliminaires
    if (-not (Test-Prerequisites)) {
        Write-Error "Prérequis non satisfaits. Arrêt du setup."
        exit 1
    }
    
    # Configuration Python
    Set-PythonEnvironment
    
    # Configuration Kafka
    Set-KafkaEnvironment
    
    # Validation exercices
    Test-Exercices
    
    # Outils de développement
    Set-DevelopmentTools
    
    # Instructions finales
    Show-FinalInstructions
    
    Write-Host "`n🎉 CONFIGURATION TERMINEE AVEC SUCCES!" -ForegroundColor Green
    Write-Host "   L'environnement Kafka Weather Analytics est prêt!" -ForegroundColor Green

} catch {
    Write-Error "Erreur lors de la configuration: $($_.Exception.Message)"
    exit 1
}