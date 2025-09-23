# Exercise 7: HDFS Storage - COMPLETED ✅

## Objectif
Créer un consumer Kafka qui lit les messages d'alerte du topic `weather_transformed` et les stocke dans une structure HDFS organisée par localisation géographique.

## Implementation

### 1. Consumer HDFS (`hdfs_consumer.py`)
- **Topic source** : `weather_transformed`
- **Filtrage** : Messages avec alertes niveau 1+ (vent ou chaleur)
- **Structure de stockage** : `/hdfs-data/{country}/{city}/alerts_*.json`
- **Format** : Fichiers JSON avec métadonnées de stockage

### 2. Structure des données stockées
```json
{
  "stored_at": "2025-09-23T10:25:47.375047",
  "storage_path": "hdfs-data\\test_data\\coord_48_86_2_35\\alert_*.json",
  "message": {
    "latitude": 48.8566,
    "longitude": 2.3522,
    "temperature": 10.7,
    "windspeed": 15.0,
    "wind_alert_level": "level_1",
    "heat_alert_level": "level_0",
    "event_time": "2025-09-23T07:45:41.886594Z",
    ...
  }
}
```

### 3. Analyseur HDFS (`hdfs_analyzer.py`)
- Analyse statistique des données stockées
- Structure de répertoires hiérarchique
- Comptage des alertes par type et localisation
- Nettoyage des anciens fichiers

## Tests réalisés

### Test rapide (`quick_hdfs_test.py`)
- ✅ **15 messages traités**
- ✅ **7 alertes stockées** 
- ✅ **4 localisations distinctes** organisées par coordonnées

### Structure HDFS créée
```
hdfs-data/
├── test_data/
│   ├── coord_48_86_2_35/     # Paris (vent level_1)
│   ├── coord_40_71_-74_01/   # New York (chaleur level_1)
│   ├── coord_51_51_-0_13/    # Londres (chaleur level_1)
│   └── coord_0_00_0_00/      # Test data (multi-alertes)
└── unknown/
    ├── coord_35.68_139.65/   # Tokyo (16 fichiers d'alerte)
    ├── coord_48.86_2.35/     # Paris variations (21 fichiers)
    └── ...
```

## Résultats

### Performances
- **95 fichiers d'alerte** stockés au total
- **7 localisations géographiques** distinctes  
- **Stockage organisé** par coordonnées géographiques
- **Temps de traitement** optimisé avec timeouts

### Types d'alertes stockées
- **Alertes vent** : niveau 1 (10-20 m/s), niveau 2 (≥20 m/s)
- **Alertes chaleur** : niveau 1 (25-35°C), niveau 2 (≥35°C)
- **Messages filtrés** : Seuls les niveau 1+ sont stockés

### Avantages de la structure
1. **Partitioning géographique** : Facile de trouver alertes par région
2. **Horodatage** : Chaque fichier a un timestamp unique
3. **Métadonnées** : Informations de stockage incluses
4. **Format JSON** : Facile à lire et analyser
5. **Scalabilité** : Structure extensible pour plus de données

## Commandes utiles

```bash
# Démarrer le consumer HDFS
python hdfs_consumer.py

# Test rapide limité
python quick_hdfs_test.py

# Analyser les données stockées
python hdfs_analyzer.py

# Lister la structure
python hdfs_consumer.py --list

# Nettoyer les anciens fichiers
python hdfs_analyzer.py --clean 7
```

## État des services
- ✅ **Docker Kafka/ZooKeeper** : Opérationnels
- ✅ **Topics** : weather_stream, weather_transformed, weather_aggregates
- ✅ **Transformer** : Génère les alertes correctement
- ✅ **Consumer HDFS** : Stocke les alertes automatiquement
- ✅ **Structure de données** : Organisée et consultable

---

## ➡️ Prêt pour Exercise 8: Visualisation des données
L'exercice 7 fournit maintenant une base de données d'alertes structurée parfaite pour créer des visualisations et analyses dans l'exercice 8.