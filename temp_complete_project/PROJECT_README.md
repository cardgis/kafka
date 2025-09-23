# 🌍 Kafka Streaming Weather Analytics Pipeline

## 📋 Vue d'Ensemble

Ce projet implémente un pipeline complet d'analyse de données météo en temps réel utilisant Apache Kafka, Spark Structured Streaming, et des technologies de Big Data. Le système couvre toute la chaîne de traitement depuis l'ingestion des données jusqu'à la visualisation business intelligence.

## 🏗️ Architecture Globale

```
📡 APIs Météo (Open-Meteo)
    ↓
🔄 Kafka Producers (Python)
    ↓
📊 Kafka Topics (weather_stream, geo_weather_stream, etc.)
    ↓
⚡ Spark Structured Streaming (Transformations)
    ↓
📈 Aggregations temps réel (Windows, Watermarks)
    ↓
🗄️ HDFS Storage (Structure géographique)
    ↓
📊 Visualisations & Analytics (Dashboard BI)
```

## 📂 Structure du Projet

```
kafka/
├── exercices/
│   ├── exercice1/     # 🔧 Kafka Setup & Topics
│   ├── exercice2/     # 🐍 Python Consumer
│   ├── exercice3/     # 🌤️ Weather API Producer  
│   ├── exercice4/     # ⚡ Spark Transformations
│   ├── exercice5/     # 📈 Real-time Aggregations
│   ├── exercice6/     # 🗺️ Geo-Weather Producer
│   ├── exercice7/     # 🗄️ HDFS Consumer
│   └── exercice8/     # 📊 Data Visualizations
├── kafka_2.13-3.9.1/  # Apache Kafka Installation
└── README.md          # Ce fichier
```

## 🚀 Exercices Implémentés

### 1️⃣ Exercice 1: Kafka Foundation
**Objectif**: Configuration Kafka et manipulation topics
- ✅ Scripts PowerShell pour Windows
- ✅ Création topics automatisée
- ✅ Envoi/lecture messages CLI
- ✅ Configuration KRaft mode

**Technologies**: Apache Kafka 2.13-3.9.1, PowerShell
**Fichiers clés**: `start-kafka-exercice1.ps1`, `create-topic.ps1`

### 2️⃣ Exercice 2: Python Consumer
**Objectif**: Consommateur Python avec CLI interactive
- ✅ KafkaConsumerApp class avec argparse
- ✅ Gestion signaux (Ctrl+C) propre
- ✅ Formatting emojis et JSON pretty-print
- ✅ Consumer groups et offset management

**Technologies**: kafka-python, argparse, signal handling
**Fichiers clés**: `consumer.py`

### 3️⃣ Exercice 3: Weather API Producer
**Objectif**: Producteur météo temps réel avec API externe
- ✅ WeatherProducer class avec Open-Meteo API
- ✅ Streaming continu avec intervalle configurable
- ✅ Gestion erreurs et retry automatique
- ✅ Coordonnées Bordeaux et données enrichies

**Technologies**: Open-Meteo API, requests, JSON streaming
**Fichiers clés**: `current_weather.py`

### 4️⃣ Exercice 4: Spark Transformations
**Objectif**: Transformations Spark avec calculs d'alertes
- ✅ WeatherAlertProcessor avec Structured Streaming
- ✅ Calculs niveaux alerte (vent/chaleur) automatiques
- ✅ Schema JSON complexe et transformation colonnes
- ✅ Topic sortie `weather_transformed`

**Technologies**: PySpark, Structured Streaming, Complex JSON
**Fichiers clés**: `weather_alerts.py`

### 5️⃣ Exercice 5: Real-time Aggregations
**Objectif**: Agrégations temps réel avec fenêtres glissantes
- ✅ WeatherAggregatesProcessor avec dual streams
- ✅ Sliding windows 5 minutes avec watermark 2 minutes
- ✅ Agrégations temporelles ET régionales parallèles
- ✅ Métriques avancées (avg, max, min, count distinct)

**Technologies**: Spark Windows, Watermarking, approx_count_distinct
**Fichiers clés**: `weather_aggregates.py`

### 6️⃣ Exercice 6: Geo-Weather Producer
**Objectif**: Producteur géolocalisé avec API géocodage
- ✅ GeoWeatherProducer avec geocoding API Open-Meteo
- ✅ Arguments ville/pays CLI intuitifs
- ✅ Enrichissement données géographiques (timezone, population)
- ✅ Clés Kafka structurées pour partitioning géographique

**Technologies**: Open-Meteo Geocoding API, Enhanced JSON
**Fichiers clés**: `geo_weather.py`

### 7️⃣ Exercice 7: HDFS Consumer
**Objectif**: Sauvegarde organisée par structure géographique
- ✅ HDFSWeatherConsumer avec partitioning automatique
- ✅ Structure `/hdfs-data/{country}/{city}/alerts.json`
- ✅ JSON Lines format pour append efficient
- ✅ Métadonnées traçabilité et consumer groups

**Technologies**: Kafka Consumer, File I/O, Geographic partitioning
**Fichiers clés**: `hdfs_consumer.py`

### 8️⃣ Exercice 8: Data Visualizations
**Objectif**: Dashboard analytics et business intelligence
- ✅ HDFSWeatherAnalyzer avec 7 types visualisations
- ✅ Dashboard complet: température, vent, alertes, géographie
- ✅ Rapport HTML interactif responsive
- ✅ Métriques automatisées et codes météo WMO

**Technologies**: pandas, matplotlib, seaborn, HTML dashboard
**Fichiers clés**: `weather_visualizer.py`, rapport HTML

## 📊 Pipeline de Données Complet

### 1. Ingestion
```bash
# Démarrer Kafka
./start-kafka.bat

# Générer données géolocalisées
python exercice6/geo_weather.py "Paris" "France" --topic geo_weather_stream
```

### 2. Transformation
```bash
# Lancer transformations Spark
python exercice4/weather_alerts.py
python exercice5/weather_aggregates.py
```

### 3. Storage
```bash
# Sauvegarder en HDFS
python exercice7/hdfs_consumer.py --hdfs-path ./hdfs-data
```

### 4. Analytics
```bash
# Générer visualisations
python exercice8/weather_visualizer.py --hdfs-path ./hdfs-data --report
```

## 🛠️ Installation & Configuration

### Prérequis
- **Java 8+** (pour Kafka)
- **Python 3.7+** avec pip
- **Windows PowerShell** (scripts optimisés)
- **Accès Internet** (APIs Open-Meteo)

### Setup Rapide
```powershell
# 1. Cloner le projet
git clone <repository>
cd kafka

# 2. Démarrer Kafka
.\start-kafka.bat

# 3. Installer dépendances Python par exercice
cd exercices\exercice2
pip install -r requirements.txt

# 4. Tester un exercice
python consumer.py weather_stream
```

### Configuration Kafka
- **Mode**: KRaft (pas de ZooKeeper)
- **Port**: 9092
- **Logs**: `C:\tmp\kraft-combined-logs`
- **Topics**: Auto-création activée

## 📈 Métriques & Performance

### Throughput Typique
- **Producteur météo**: ~1 message/seconde/ville
- **Consommateur**: ~100 messages/seconde
- **Spark Streaming**: ~50 messages/seconde transformés
- **HDFS Writer**: ~10MB/heure pour 10 villes

### Resources
- **Kafka**: ~200MB RAM, 1 CPU core
- **Spark**: ~512MB RAM, 2 CPU cores
- **Python apps**: ~50MB RAM chacune
- **Stockage**: ~1KB par message météo

## 🌐 APIs Externes

### Open-Meteo Weather API
- **Endpoint**: `https://api.open-meteo.com/v1/forecast`
- **Rate Limit**: Gratuit illimité
- **Données**: Température, vent, codes météo WMO

### Open-Meteo Geocoding API
- **Endpoint**: `https://geocoding-api.open-meteo.com/v1/search`
- **Fonctionnalité**: Résolution ville/pays → coordonnées
- **Enrichissement**: Timezone, population, régions

## 🔄 Workflow Git

Le projet utilise une stratégie de branches par exercice:

```bash
# Structure branches
master              # Branch principale avec README
├── exercice1       # Kafka setup
├── exercice2       # Python consumer
├── exercice3       # Weather producer
├── exercice4       # Spark transformations
├── exercice5       # Aggregations
├── exercice6       # Geo-producer
├── exercice7       # HDFS consumer
└── exercice8       # Visualizations
```

### Commandes Git Utiles
```bash
# Voir toutes les branches
git branch -a

# Basculer vers un exercice spécifique
git checkout exercice3

# Voir l'historique d'un exercice
git log --oneline exercice6

# Merger exercice vers master
git checkout master
git merge exercice8 --no-ff
```

## 🧪 Tests & Validation

### Tests Automatisés
Chaque exercice inclut des scripts de test:
- `test-*.ps1` pour validation fonctionnelle
- Génération automatique de données test
- Vérification end-to-end du pipeline

### Validation Manuelle
```bash
# Test exercice 3 (weather producer)
cd exercices\exercice3
.\test-weather.ps1

# Test exercice 8 (visualizations)
cd exercices\exercice8
.\test-simple.ps1
```

## 📋 Troubleshooting

### Problèmes Fréquents

**Kafka ne démarre pas**
```bash
# Nettoyer les logs
rmdir /S C:\tmp\kraft-combined-logs
.\start-kafka.bat
```

**Erreur Python dependencies**
```bash
# Réinstaller dans environnement propre
python -m venv kafka-env
kafka-env\Scripts\activate
pip install -r requirements.txt
```

**Spark timeout/memory**
```bash
# Ajuster configuration Spark
export SPARK_CONF_DIR=./spark-conf
# Éditer spark-defaults.conf
```

### Logs Utiles
- **Kafka**: `./kafka_2.13-3.9.1/logs/server.log`
- **Spark**: Console output avec niveau INFO
- **Python**: Logs configurés par module

## 🚀 Extensions Futures

### Améliorations Techniques
- [ ] **Kubernetes deployment** avec Helm charts
- [ ] **Schema Registry** pour évolution schemas
- [ ] **Kafka Streams** pour processing natif
- [ ] **Monitoring** Prometheus + Grafana

### Fonctionnalités Business
- [ ] **Machine Learning** prédictions météo
- [ ] **Alertes temps réel** (webhooks, email)
- [ ] **APIs REST** pour accès données
- [ ] **Interface web** React/Vue.js

### Scalabilité
- [ ] **Multi-datacenter** replication
- [ ] **Auto-scaling** basé sur charge
- [ ] **Data partitioning** avancé
- [ ] **Compression** et archivage automatique

## 👥 Contribution

### Standards Code
- **Python**: PEP 8, type hints
- **PowerShell**: Verb-Noun naming
- **Git**: Conventional commits
- **Documentation**: README par exercice

### Structure Commits
```
type(scope): description

✨ feat(exercice6): géocodage API Open-Meteo
🐛 fix(exercice4): schema Spark nullable fields
📚 docs(README): installation Windows
♻️ refactor(exercice3): error handling retry
```

## 📄 Licence

MIT License - Libre d'utilisation pour projets éducatifs et commerciaux.

## 🆘 Support

Pour questions ou problèmes:
1. Vérifier la documentation exercice spécifique
2. Consulter les logs Kafka/Spark
3. Tester avec données exemples fournies
4. Ouvrir issue avec contexte détaillé

---

**🎉 Projet terminé avec succès!**
*Pipeline complet Kafka → Spark → HDFS → Analytics opérationnel*