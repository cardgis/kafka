# 🌟 Stratégie des Branches par Exercice - Guide Complet

## 🎯 Architecture des Branches

Voici comment organiser votre repository avec une branche dédiée pour chaque exercice :

### **Structure des Branches**

```
kafka/
├── main                 # Documentation générale + setup global
├── exercice1           # Setup Kafka & Zookeeper uniquement
├── exercice2           # Basic Producer/Consumer uniquement  
├── exercice3           # Weather Data Streaming uniquement
├── exercice4           # Multi-City Weather Networks uniquement
├── exercice5           # Real-time Weather Alerts uniquement
├── exercice6           # Geographic Weather Streaming uniquement
├── exercice7           # HDFS Consumer & Storage uniquement
└── exercice8           # BI Visualizations & Analytics uniquement
```

## 🚀 Commandes pour Créer les Branches

### **1. Script PowerShell Automatisé**

```powershell
# Script create-all-branches.ps1
$exercices = 2..8

foreach ($ex in $exercices) {
    Write-Host "Traitement exercice$ex..." -ForegroundColor Yellow
    
    # Checkout et merge
    git checkout main
    git checkout exercice$ex
    git merge main --no-edit
    
    # Copier contenu spécifique
    Copy-Item -Path "exercices\exercice$ex\*" -Destination "." -Recurse -Force
    Remove-Item -Path "exercices" -Recurse -Force
    
    # Créer README de branche
    @"
# 🚀 Exercice $ex - Branch Dédiée

Cette branche contient uniquement l'exercice $ex.

## Navigation
- exercice1: ``git checkout exercice1``
- exercice2: ``git checkout exercice2``
- exercice3: ``git checkout exercice3``
- exercice4: ``git checkout exercice4``
- exercice5: ``git checkout exercice5``
- exercice6: ``git checkout exercice6``
- exercice7: ``git checkout exercice7``
- exercice8: ``git checkout exercice8``
"@ | Out-File -FilePath "EXERCICE${ex}_BRANCH.md" -Encoding UTF8
    
    # Commit
    git add -A
    git commit -m "Exercice $ex: Dedicated branch content"
}
```

### **2. Commandes Manuelles (Alternative)**

```bash
# Pour chaque exercice (2 à 8), répéter :
git checkout main
git checkout exercice2  # Remplacer par exercice3, exercice4, etc.
git merge main --no-edit
cp -r exercices/exercice2/* .  # Adapter le numéro
rm -rf exercices/
git add -A
git commit -m "Exercice 2: Dedicated branch content"
```

## 📤 Push des Branches vers GitHub

### **Push Toutes les Branches**
```bash
# Push exercice1 (déjà fait)
git push origin exercice1

# Push exercices 2-8
for i in {2..8}; do
    git push origin exercice$i
done
```

### **Ou individuellement**
```bash
git push origin exercice2
git push origin exercice3
git push origin exercice4
git push origin exercice5
git push origin exercice6
git push origin exercice7
git push origin exercice8
```

## 🧹 Nettoyage de la Branche Main

```bash
git checkout main

# Supprimer le dossier exercices/
rm -rf exercices/

# Garder seulement :
# - README.md général
# - Documentation globale
# - Scripts de setup globaux
# - Infrastructure Kafka

git add -A
git commit -m "Clean main branch: Keep only global documentation and setup"
git push origin main
```

## 📋 Structure Finale

### **Branche `main`**
```
kafka/
├── README.md                    # Vue d'ensemble du projet
├── DEVELOPMENT_ROADMAP.md       # Roadmap de développement
├── setup-environment.ps1       # Setup global
├── requirements.txt             # Dépendances globales
├── kafka_2.13-3.9.1/          # Installation Kafka
├── docs/                       # Documentation technique
└── .github/workflows/          # CI/CD
```

### **Chaque Branche `exerciceX`**
```
kafka/
├── README.md                    # Spécifique à l'exercice
├── EXERCICEX_BRANCH.md         # Guide de navigation
├── [fichiers spécifiques]      # Code de l'exercice uniquement
├── requirements.txt            # Dépendances de l'exercice
├── test-exerciceX.ps1          # Tests spécifiques
└── [autres fichiers]          # Infrastructure nécessaire
```

## 🎯 Avantages de cette Structure

### **✅ Avantages**
1. **Isolation parfaite** - Chaque exercice est indépendant
2. **Navigation facile** - `git checkout exerciceX` pour switcher
3. **Développement propre** - Pas de pollution entre exercices
4. **Clone spécifique** - Possibilité de cloner une branche uniquement
5. **Tests séparés** - Tests unitaires par exercice
6. **Documentation ciblée** - Docs spécifiques par exercice

### **🔄 Workflow de Développement**
```bash
# Développer exercice 3
git checkout exercice3
# Modifier, tester, commiter
git add .
git commit -m "Fix: amélioration weather API"
git push origin exercice3

# Passer à exercice 5
git checkout exercice5
# Continuer le développement...
```

### **📚 Navigation pour les Utilisateurs**
```bash
# Débutant : commencer par exercice 1
git clone https://github.com/cardgis/kafka.git
cd kafka
git checkout exercice1

# Continuer progressivement
git checkout exercice2
git checkout exercice3
# etc.
```

## 🎊 Résultat Final

Votre repository GitHub aura :
- **9 branches** (main + 8 exercices)
- **Navigation claire** entre exercices
- **Développement isolé** pour chaque étape
- **Documentation spécialisée** par exercice
- **Clone sélectif** possible

---

**🎯 Cette structure permet un apprentissage progressif et un développement structuré de votre pipeline Kafka weather analytics !**