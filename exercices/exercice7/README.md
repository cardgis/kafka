# Exercice 7: Consommateur Kafka vers HDFS

## 🗄️ Objectif
Créer un consommateur Kafka qui lit les données météo et les organise dans une structure HDFS hiérarchique par pays et ville.

## 🏗️ Architecture
```
hdfs_consumer.py
├── HDFSWeatherConsumer
│   ├── _extract_location_info() → Extraction pays/ville des messages
│   ├── _get_hdfs_path() → Génération chemins HDFS structurés
│   ├── _append_to_hdfs_file() → Sauvegarde JSON Lines
│   └── start_consuming() → Boucle de consommation Kafka
└── Structure HDFS → /hdfs-data/{country}/{city}/alerts.json
```

## 📁 Structure HDFS Générée
```
hdfs-data/
├── FR/
│   └── Paris/
│       └── alerts.json
├── JP/
│   └── Tokyo/
│       └── alerts.json
├── US/
│   └── New_York/
│       └── alerts.json
└── UNKNOWN/
    └── fallback_cities/
        └── alerts.json
```

## 🔧 Installation

### Prérequis
- Apache Kafka en cours d'exécution
- Topics avec données météo géolocalisées
- Python 3.7+
- Accès en écriture au système de fichiers

### Dépendances
```bash
pip install -r requirements.txt
```

## 🚀 Utilisation

### Démarrage rapide
```bash
# Lancer le test complet avec génération de données
.\test-hdfs.ps1

# Ou manuellement:
python hdfs_consumer.py --hdfs-path ./hdfs-data
```

### Options avancées
```bash
# Topics spécifiques
python hdfs_consumer.py --topics geo_weather_stream --hdfs-path ./my-hdfs

# Serveur Kafka personnalisé
python hdfs_consumer.py --server my-kafka:9092 --hdfs-path /hdfs/weather
```

## 📊 Format des Données

### Topics consommés
- **geo_weather_stream**: Données enrichies avec géolocalisation
- **weather_transformed**: Données transformées avec alertes
- Compatible avec tous les topics des exercices précédents

### Format de sauvegarde (JSON Lines)
```json
{
  "location": {
    "city": "Paris",
    "country": "France",
    "country_code": "FR",
    "latitude": 48.8566,
    "longitude": 2.3522
  },
  "weather": {
    "temperature": 15.2,
    "windspeed": 12.5,
    "weathercode": 3
  },
  "hdfs_metadata": {
    "processed_at": "2024-01-15T14:30:00Z",
    "consumer_id": "hdfs-weather-consumer",
    "file_path": "./hdfs-data/FR/Paris/alerts.json"
  }
}
```

## 🔄 Gestion des Données

### Extraction de localisation
1. **geo_weather_stream**: Utilise `location.country_code` et `location.city`
2. **weather_transformed**: Déduit depuis `location_data` ou coordonnées
3. **Fallback**: Génère codes depuis latitude/longitude
4. **Défaut**: Place dans `UNKNOWN/UNKNOWN` si pas de géolocalisation

### Organisation HDFS
- **Partitioning géographique**: Un répertoire par pays
- **Sous-partitioning**: Un répertoire par ville
- **Fichier unique**: `alerts.json` en format JSON Lines
- **Métadonnées**: Timestamp et informations de traitement

## 🛠️ Fonctionnalités

### Robustesse
- **Signal handling**: Arrêt propre avec Ctrl+C
- **Gestion d'erreurs**: Retry automatique et logging
- **Consumer groups**: Évite la duplication de messages
- **Auto-commit**: Sauvegarde automatique des offsets

### Performance
- **Polling efficace**: Batch processing des messages
- **Création lazy**: Répertoires créés à la demande
- **JSON Lines**: Format optimisé pour l'append
- **Statistiques**: Suivi en temps réel du traitement

### Monitoring
- **Compteurs**: Messages traités, erreurs, pays/villes
- **Affichage périodique**: Progrès toutes les 10 messages
- **Structure finale**: Visualisation HDFS à l'arrêt
- **Logging détaillé**: Debug et troubleshooting

## 🧪 Tests

### Validation complète
```bash
# Test avec génération automatique de données
.\test-hdfs.ps1
```

### Vérification manuelle
```bash
# Lancer le consommateur
python hdfs_consumer.py

# Dans un autre terminal, générer des données
python ..\exercice6\geo_weather.py "London" "UK" --topic geo_weather_stream --count 5

# Vérifier la structure créée
ls -R hdfs-data/
```

## 📈 Intégration Pipeline

### Compatibilité upstream
- **Exercice 3**: current_weather.py → weather_stream
- **Exercice 4**: weather_alerts.py → weather_transformed  
- **Exercice 5**: weather_aggregates.py → weather_aggregates
- **Exercice 6**: geo_weather.py → geo_weather_stream

### Préparation downstream
- **Exercice 8**: Fichiers HDFS prêts pour visualisation
- **Analytics**: Structure optimisée pour requêtes géographiques
- **Backup**: Persistence des données météo historiques

## 📋 Métriques

### Performance typique
- **Throughput**: ~100 messages/sec pour données météo
- **Latence**: <10ms par message (I/O local)
- **Stockage**: ~1KB par message météo enrichi
- **Scalabilité**: Limité par I/O disque local

### Ressources
- **RAM**: ~50MB base + cache messages
- **Disque**: Croissance linéaire avec les données
- **CPU**: Minimal, principalement I/O bound
- **Réseau**: Consommation Kafka standard

## 🔄 Extensions Futures
- [ ] Support HDFS réel (hdfs3, pydoop)
- [ ] Compression des fichiers JSON (gzip)
- [ ] Partitioning temporel (par jour/heure)
- [ ] Rotation automatique des fichiers
- [ ] Métriques Prometheus/Grafana
- [ ] Mode batch pour historical data