# Guide Git pour le Projet Kafka

## 🌳 Structure des Branches

```
master (main)
├── exercice1 ✅ TERMINÉ
├── exercice2 🔄 En cours
├── exercice3 📋 Préparé
├── exercice4 📋 Préparé
├── exercice5 📋 Préparé
├── exercice6 📋 Préparé
├── exercice7 📋 Préparé
└── exercice8 📋 Préparé
```

## 🚀 Workflow Git

### Commandes de base
```bash
# Voir toutes les branches
git branch -a

# Basculer vers un exercice
git checkout exercice2

# Voir l'état actuel
git status

# Ajouter et commiter des changements
git add .
git commit -m "Exercice 2: Description des changements"

# Pousser vers le repository distant
git push origin exercice2
```

### Workflow type pour un exercice
```bash
# 1. Basculer vers la branche de l'exercice
git checkout exercice3

# 2. Développer l'exercice
# ... coder, tester, débugger ...

# 3. Ajouter les fichiers
git add .

# 4. Commiter avec un message descriptif
git commit -m "Exercice 3: Producteur API météo Open-Meteo terminé"

# 5. Pousser vers le repository distant
git push origin exercice3

# 6. Mettre à jour le README principal si nécessaire
git checkout master
# ... modifier README.md ...
git add README.md
git commit -m "Update: Exercice 3 terminé"
git push origin master
```

## 📊 Suivi des Exercices

### Status actuel
| Exercice | Status | Branche | Commit |
|----------|--------|---------|--------|
| 1 | ✅ TERMINÉ | `exercice1` | `a882ac6` |
| 2 | 🔄 Template créé | `exercice2` | - |
| 3-8 | 📋 Préparé | `exercice3-8` | - |

### Convention de nommage des commits
```bash
# Exercice en cours
"Exercice X: Description du travail effectué"
"Exercice X: Fix bug dans le consommateur"
"Exercice X: Ajout tests unitaires"

# Exercice terminé
"Exercice X TERMINÉ: Description complète"

# Documentation
"Update: README exercice X"
"Add: Documentation exercice X"
```

## 🔄 Synchronisation avec Repository Distant

### Première fois (setup)
```bash
# Ajouter le repository distant
git remote add origin https://github.com/username/kafka-streaming-exercises.git

# Pousser toutes les branches
git push -u origin master
git push -u origin exercice1
git push -u origin exercice2
# ... etc pour toutes les branches
```

### Mise à jour régulière
```bash
# Pousser la branche courante
git push

# Pousser toutes les branches
git push --all origin

# Récupérer les changements distants
git pull origin master
```

## 🛠️ Commandes Utiles

### Navigation
```bash
# Historique des commits
git log --oneline --graph --all

# Différences entre branches
git diff exercice1 exercice2

# Voir les fichiers modifiés
git diff --name-only
```

### Debugging
```bash
# Annuler le dernier commit (garde les fichiers)
git reset --soft HEAD~1

# Annuler les modifications non commitées
git checkout -- <fichier>

# Voir l'historique d'un fichier
git log --follow -- <fichier>
```

### Nettoyage
```bash
# Voir les fichiers non suivis
git status --porcelain

# Nettoyer les fichiers non suivis
git clean -f -d

# Voir la taille du repository
git count-objects -vH
```

## 📝 Templates de Messages

### Commit d'exercice terminé
```
Exercice X TERMINÉ: [Titre de l'exercice]

✅ Objectifs atteints:
- [Objectif 1]
- [Objectif 2]

📁 Fichiers ajoutés:
- exercices/exerciceX/script.py
- exercices/exerciceX/README.md

🧪 Tests réalisés:
- [Test 1]
- [Test 2]
```

### Commit de travail en cours
```
Exercice X: [Description du travail]

🔧 Modifications:
- [Modification 1]
- [Modification 2]

📋 TODO:
- [Tâche restante 1]
- [Tâche restante 2]
```

---

**Dernière mise à jour:** 22 septembre 2025  
**Repository status:** Local (prêt pour push distant)