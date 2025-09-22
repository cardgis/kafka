# 📊 Exercice 8: Visualisation et Agrégation des Logs Météo

## 🎯 Objectif
Créer des visualisations avancées des données météorologiques stockées dans HDFS et implémenter des dashboards BI pour l'analyse des tendances et alertes.

## 📋 Spécifications

### **Visualisations Requises**
1. **Évolution de la température** au fil du temps
2. **Évolution de la vitesse du vent** 
3. **Nombre d'alertes vent et chaleur** par niveau
4. **Code météo le plus fréquent** par pays
5. **Distribution géographique** des alertes
6. **Tendances saisonnières** et patterns
7. **Dashboard interactif** pour exploration

### **Fonctionnalités Avancées**
- Export multi-format (PNG, HTML, CSV)
- Filtrage par date, pays, type d'alerte
- Agrégations temporelles (horaire, journalière, hebdomadaire)
- Alertes prédictives basées sur les tendances
- Rapports automatisés

## 🚀 Utilisation

### **Génération de Toutes les Visualisations**
```bash
python weather_visualizer.py --input "./hdfs-data"
```

### **Visualisation Spécifique**
```bash
# Température seulement
python weather_visualizer.py --input "./hdfs-data" --type temperature

# Alertes par pays
python weather_visualizer.py --input "./hdfs-data" --type alerts --country FR

# Dashboard interactif
python weather_visualizer.py --input "./hdfs-data" --dashboard
```

### **Export Personnalisé**
```bash
# Export HTML interactif
python weather_visualizer.py --input "./hdfs-data" --output "./reports" --format html

# Export CSV pour analyse
python weather_visualizer.py --input "./hdfs-data" --export-data
```

## 📊 Types de Visualisations

### 1. **Analyse Temporelle**
- Séries temporelles température/vent
- Tendances et saisonnalité
- Patterns journaliers/hebdomadaires

### 2. **Analyse Géographique**
- Heatmaps par pays/ville
- Distribution géographique des alertes
- Comparaisons régionales

### 3. **Analyse des Alertes**
- Distribution par niveau (0, 1, 2)
- Évolution des alertes dans le temps
- Corrélations vent/température

### 4. **Analytics Avancées**
- Clustering des patterns météo
- Prédictions de tendances
- Détection d'anomalies

## 🛠️ Architecture Technique

### **Input Data**
- Source: HDFS structure `/hdfs-data/{country}/{city}/alerts.json`
- Format: JSON Lines avec weather_transformed data
- Colonnes: timestamp, temperature, windspeed, wind_alert_level, heat_alert_level

### **Processing Pipeline**
1. **Data Loading**: Lecture récursive HDFS structure
2. **Data Cleaning**: Validation et nettoyage des données
3. **Aggregation**: Calculs statistiques et groupements
4. **Visualization**: Génération graphiques avec matplotlib/seaborn
5. **Export**: Sauvegarde multi-format

### **Output Formats**
- **PNG**: Graphiques haute résolution
- **HTML**: Dashboards interactifs
- **CSV**: Données agrégées pour analyse
- **JSON**: Métadonnées et statistiques

## 📈 Métriques Calculées

### **Statistiques Temporelles**
- Moyenne, min, max température par période
- Évolution vitesse du vent
- Fréquence des alertes par type

### **Statistiques Géographiques**
- Température moyenne par pays/ville
- Distribution des codes météo
- Hotspots d'alertes climatiques

### **Indicateurs de Performance**
- Précision des prédictions d'alertes
- Trends accuracy sur 7/30 jours
- Coverage géographique des données

## 🔧 Configuration

### **Paramètres de Visualisation**
```python
# Configuration dans weather_visualizer.py
VISUALIZATION_CONFIG = {
    'figure_size': (15, 10),
    'dpi': 300,
    'style': 'seaborn-v0_8',
    'color_palette': 'viridis',
    'export_formats': ['png', 'html'],
    'interactive': True
}
```

### **Alertes et Seuils**
```python
# Seuils d'alertes configurables
ALERT_THRESHOLDS = {
    'wind': {'level_1': 10, 'level_2': 20},  # m/s
    'heat': {'level_1': 25, 'level_2': 35}   # °C
}
```

## 🎯 Résultats Attendus

Après exécution, vous obtiendrez :

1. **Dossier `visualizations/`** avec tous les graphiques
2. **Rapport HTML interactif** avec dashboard complet
3. **Fichiers CSV** avec données agrégées
4. **Statistiques JSON** avec métriques détaillées

## 📊 Exemples de Visualisations

### **1. Évolution Température**
- Line chart avec tendances
- Heatmap par pays/mois
- Box plots pour distribution

### **2. Analyse du Vent**
- Séries temporelles vitesse
- Rose des vents par région
- Corrélation vent/température

### **3. Dashboard Alertes**
- Barres par niveau d'alerte
- Évolution temporelle des alertes
- Geographic scatter plot

### **4. Analytics Avancées**
- Clustering analysis
- Prediction models
- Anomaly detection

## 🚀 Intégration

### **Avec Exercice 7 (HDFS Consumer)**
```bash
# 1. Produire des données (Exercice 6)
cd ../exercice6
python geo_weather.py Paris France --continuous

# 2. Consumer vers HDFS (Exercice 7)
cd ../exercice7
python hdfs_consumer.py --hdfs-path "./hdfs-data" --topics geo_weather_stream

# 3. Visualisation (Exercice 8)
cd ../exercice8
python weather_visualizer.py --input "./hdfs-data"
```

### **Pipeline Complet**
1. **Production**: Données météo temps réel
2. **Streaming**: Kafka + Spark transformations
3. **Storage**: HDFS partitioning géographique
4. **Analytics**: Visualisations et BI dashboards

## 📚 Dépendances

```bash
pip install pandas matplotlib seaborn plotly dash streamlit
pip install numpy scipy scikit-learn
```

## 🎊 Validation

Pour valider l'exercice :
1. Générer visualisations complètes
2. Vérifier exports multi-format
3. Tester filtres et agrégations
4. Valider dashboard interactif

---

**🎯 Cet exercice démontre la capacité à créer des dashboards BI professionnels et des analytics avancées sur des données de streaming en temps réel.**