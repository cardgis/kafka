# Projet KAFKA - Exercices de Streaming de Données Météo

## 📖 Description du Projet

Ce projet contient 8 exercices progressifs sur Apache Kafka, le streaming de données, et l'analyse en temps réel de données météorologiques.

## 🏗️ Structure du Repository

- **main** : Branche principale avec la documentation
- **exercice1** : Mise en place de Kafka et producteur simple
- **exercice2** : Consommateur Kafka en Python
- **exercice3** : Streaming de données météo en direct
- **exercice4** : Transformation des données et détection d'alertes
- **exercice5** : Agrégats en temps réel avec Spark
- **exercice6** : Extension du producteur (géolocalisation)
- **exercice7** : Stockage dans HDFS organisé
- **exercice8** : Visualisation et agrégation des logs météo

## 📋 Exercices Détaillés

### Exercice 1 : Mise en place de Kafka et d'un producteur simple ✅
**Status:** TERMINÉ

- [x] Créer un topic Kafka nommé `weather_stream`
- [x] Envoyer un message statique : `{"msg": "Hello Kafka"}`

**Branche:** `exercice1`

### Exercice 2 : Écriture d'un consommateur Kafka
**Objectif:** Créer un script Python consommateur qui lit les messages depuis un topic Kafka passé en argument.

**Livrables:**
- Script Python consommateur
- Affichage des messages reçus en temps réel

**Branche:** `exercice2`

### Exercice 3 : Streaming de données météo en direct
**Objectif:** Écrire un producteur `current_weather` qui interroge l'API Open-Meteo.

**Spécifications:**
- Interroger l'API Open-Meteo pour une latitude/longitude passée en argument
- Envoyer les données reçues dans le topic Kafka `weather_stream`

**Branche:** `exercice3`

### Exercice 4 : Transformation des données et détection d'alertes
**Objectif:** Traiter le flux `weather_stream` en temps réel avec Spark.

**Spécifications:**
- Produire un topic Kafka `weather_transformed`
- **Alertes de vent:**
  - Vent faible (< 10 m/s) → `level_0`
  - Vent modéré (10-20 m/s) → `level_1`
  - Vent fort (> 20 m/s) → `level_2`
- **Alertes de chaleur:**
  - Température normale (< 25°C) → `level_0`
  - Chaleur modérée (25-35°C) → `level_1`
  - Canicule (> 35°C) → `level_2`
- **Colonnes ajoutées:**
  - `event_time` (timestamp)
  - `temperature` et `windspeed` transformés
  - `wind_alert_level` et `heat_alert_level`

**Branche:** `exercice4`

### Exercice 5 : Agrégats en temps réel avec Spark
**Objectif:** Calculer des agrégats en temps réel sur des fenêtres glissantes.

**Spécifications:**
- Implémenter un sliding window (1 ou 5 minutes) sur le flux `weather_transformed`
- **Métriques à calculer:**
  - Nombre d'alertes `level_1` ou `level_2` par type d'alerte (vent/chaleur)
  - Moyenne, min, max de la température
  - Nombre total d'alertes par ville ou pays

**Branche:** `exercice5`

### Exercice 6 : Extension du producteur
**Objectif:** Modifier les producteurs pour accepter ville et pays comme arguments.

**API à utiliser:** https://open-meteo.com/en/docs/geocoding-api?name=paris

**Spécifications:**
- Chaque message produit doit inclure ville et pays
- Permettre le partitionnement par HDFS et les agrégats par région

**Branche:** `exercice6`

### Exercice 7 : Stockage dans HDFS organisé
**Objectif:** Écrire un consommateur Kafka qui lit `weather_transformed`.

**Spécifications:**
- Sauvegarder les alertes dans HDFS
- **Structure:** `/hdfs-data/{country}/{city}/alerts.json`

**Branche:** `exercice7`

### Exercice 8 : Visualisation et agrégation des logs météo
**Objectif:** Consommer les logs HDFS et implémenter des visualisations.

**Visualisations à implémenter:**
- Évolution de la température au fil du temps
- Évolution de la vitesse du vent
- Nombre d'alertes vent et chaleur par niveau
- Code météo le plus fréquent par pays

**Branche:** `exercice8`

## 🛠️ Technologies Utilisées

- **Apache Kafka** : Streaming de données
- **Python** : Scripts de production/consommation
- **Apache Spark** : Traitement en temps réel
- **HDFS** : Stockage distribué
- **Open-Meteo API** : Données météorologiques
- **Git** : Gestion de versions

## 🚀 Démarrage Rapide

### Prérequis
- Java 11+
- Python 3.8+
- Apache Kafka
- Apache Spark (pour exercices 4-5)
- HDFS (pour exercices 7-8)

### Démarrer Kafka
```powershell
& "C:\Big_data\kafka\start-kafka-simple.ps1"
```

### Naviguer entre les exercices
```bash
# Changer vers un exercice spécifique
git checkout exercice1

# Voir toutes les branches
git branch -a

# Créer et pousser vers une nouvelle branche exercice
git checkout -b exercice2
git add .
git commit -m "Exercice 2: Consommateur Python terminé"
git push origin exercice2
```

## 📁 Arborescence

```
kafka/
├── .git/
├── .gitignore
├── README.md
├── start-kafka-simple.ps1
├── test-interactif.ps1
├── kafka_2.13-3.9.1/          # Installation Kafka
├── exercices/
│   ├── exercice2/              # Scripts Python consommateur
│   ├── exercice3/              # Producteur API météo
│   ├── exercice4/              # Spark transformation
│   ├── exercice5/              # Spark agrégats
│   ├── exercice6/              # Extension géolocalisation
│   ├── exercice7/              # HDFS storage
│   └── exercice8/              # Visualisations
└── docs/                       # Documentation supplémentaire
```

## 📊 Suivi des Exercices

| Exercice | Status | Branche | Description |
|----------|--------|---------|-------------|
| 1 | ✅ TERMINÉ | `exercice1` | Setup Kafka + Topic + Message |
| 2 | 🔄 TODO | `exercice2` | Consommateur Python |
| 3 | 🔄 TODO | `exercice3` | API Open-Meteo |
| 4 | 🔄 TODO | `exercice4` | Spark Transformation |
| 5 | 🔄 TODO | `exercice5` | Spark Agrégats |
| 6 | 🔄 TODO | `exercice6` | Géolocalisation |
| 7 | 🔄 TODO | `exercice7` | HDFS Storage |
| 8 | 🔄 TODO | `exercice8` | Visualisations |

---

## 👨‍💻 Auteur
Projet d'apprentissage Apache Kafka et streaming de données

## 📅 Dates
- **Début:** 22 septembre 2025
- **Exercice 1 terminé:** 22 septembre 2025