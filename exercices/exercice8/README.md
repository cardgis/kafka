# Exercice 8: Visualisations des Logs HDFS

## 📊 Objectif
Créer un système de visualisation et d'analyse des données météo stockées dans la structure HDFS pour générer des dashboards interactifs et des rapports d'analyse.

## 🏗️ Architecture
```
weather_visualizer.py
├── HDFSWeatherAnalyzer
│   ├── load_hdfs_data() → Lecture structure HDFS complète
│   ├── create_dataframe() → Conversion pandas pour analyse
│   ├── generate_visualizations() → Création graphiques
│   └── generate_report() → Rapport HTML interactif
└── Visualisations
    ├── Température par pays
    ├── Vitesse du vent par pays  
    ├── Distribution des alertes
    ├── Codes météo par pays
    ├── Vue géographique
    ├── Analyse temporelle
    └── Dashboard récapitulatif
```

## 📈 Types de Visualisations

### 1. Analyse des Températures
- **Box plots** par pays avec quartiles et outliers
- **Ligne de moyenne globale** pour comparaison
- **Top 5 pays** les plus chauds/froids

### 2. Analyse du Vent
- **Graphiques en barres** vitesse moyenne vs maximale
- **Distribution des directions** du vent (rose des vents)
- **Corrélation** température-vent par pays

### 3. Distribution des Alertes
- **Graphique en camembert** global des niveaux d'alerte
- **Barres empilées** par pays
- **Heatmap** alertes par région géographique

### 4. Codes Météo WMO
- **Heatmap** codes météo par pays
- **Mapping complet** des descriptions WMO
- **Fréquence** des phénomènes météo

### 5. Vue Géographique
- **Scatter plot** latitude/longitude avec température
- **Bulles proportionnelles** à la vitesse du vent
- **Nombre de villes** par pays

### 6. Analyse Temporelle
- **Séries temporelles** température/vent
- **Évolution** par pays sur la timeline
- **Tendances** et patterns temporels

## 🔧 Installation

### Prérequis
- Données HDFS de l'exercice 7
- Python 3.7+ avec packages scientifiques
- Structure HDFS: `/hdfs-data/{country}/{city}/alerts.json`

### Dépendances
```bash
pip install -r requirements.txt
```

## 🚀 Utilisation

### Démarrage rapide
```bash
# Lancer le test complet avec copie données + visualisations
.\test-visualizations.ps1

# Ou manuellement:
python weather_visualizer.py --hdfs-path ./hdfs-data --report
```

### Options avancées
```bash
# Répertoire HDFS personnalisé
python weather_visualizer.py --hdfs-path /path/to/hdfs --output-dir ./my-charts

# Générer seulement les graphiques (sans rapport HTML)
python weather_visualizer.py --hdfs-path ./hdfs-data --output-dir ./charts

# Avec rapport HTML complet
python weather_visualizer.py --hdfs-path ./hdfs-data --report
```

## 📊 Sorties Générées

### Visualisations PNG (300 DPI)
- `temperature_by_country.png` - Distribution températures par pays
- `wind_by_country.png` - Vitesse du vent par pays
- `alert_distribution.png` - Niveaux d'alerte global + par pays
- `weather_codes_by_country.png` - Heatmap codes météo WMO
- `geographic_overview.png` - 4 vues géographiques combinées
- `temporal_analysis.png` - Évolution temporelle
- `dashboard_overview.png` - Dashboard complet récapitulatif

### Rapport HTML Interactif
- `rapport_meteo_hdfs.html` - Rapport complet avec:
  - Statistiques générales automatisées
  - Toutes les visualisations intégrées
  - Design responsive et professionnel
  - Navigation fluide entre sections

## 📋 Métriques Calculées

### Statistiques Générales
- **Total enregistrements** traités
- **Nombre de pays/villes** uniques
- **Température**: moyenne, min, max globales
- **Vent**: vitesse moyenne et maximale
- **Distribution des alertes** par niveau

### Analyses Géographiques
- **Top 5 pays** par température moyenne
- **Top 5 pays** par vitesse du vent
- **Correlation** température-vent par localisation
- **Density mapping** des observations

### Analyses Météorologiques
- **Codes WMO** les plus fréquents
- **Patterns saisonniers** (si données temporelles)
- **Alertes critiques** par région
- **Phénomènes extrêmes** identifiés

## 🎨 Personnalisation

### Styles Graphiques
- **Palette de couleurs** Seaborn husl
- **Style** seaborn-v0_8 moderne
- **Résolution** 300 DPI pour impression
- **Format** PNG optimisé

### Template HTML
- **Design responsive** compatible mobile
- **CSS moderne** avec animations
- **Grid layout** pour statistiques
- **Cards design** pour métriques clés

## 🔄 Intégration Pipeline

### Sources de données
- **Exercice 7**: Structure HDFS `/hdfs-data/{country}/{city}/alerts.json`
- **Format**: JSON Lines avec métadonnées enrichies
- **Compatibilité**: Tous les topics précédents via HDFS consumer

### Architecture complète
```
Exercice 3: WeatherProducer → weather_stream
Exercice 4: Spark Transform → weather_transformed  
Exercice 5: Aggregations → weather_aggregates
Exercice 6: Geo Producer → geo_weather_stream
Exercice 7: HDFS Consumer → /hdfs-data/{country}/{city}/
Exercice 8: Visualizer → 📊 Dashboard Analytics
```

## 📈 Cas d'Usage

### Monitoring Opérationnel
- **Surveillance temps réel** des alertes météo
- **Détection anomalies** par région
- **Reporting automatisé** pour décideurs

### Analyse Historique
- **Trends climatiques** par pays/ville
- **Comparaisons géographiques** détaillées
- **Patterns temporels** et saisonnalité

### Recherche & Développement
- **Validation des modèles** météo
- **Analyse de corrélations** complexes
- **Benchmarking international** des conditions

## 🛠️ Extensions Possibles

### Visualisations Avancées
- [ ] Cartes géographiques interactives (Folium)
- [ ] Animations temporelles (matplotlib.animation)
- [ ] 3D scatter plots pour corrélations multiples
- [ ] Heatmaps temporelles (calendrier)

### Analyses Statistiques
- [ ] Régression linéaire température-vent
- [ ] Clustering géographique K-means
- [ ] Détection d'outliers statistiques
- [ ] Prédictions court-terme

### Dashboard Interactif
- [ ] Interface web Streamlit/Dash
- [ ] Filtres dynamiques par pays/période
- [ ] Exports PDF automatisés
- [ ] Alertes en temps réel

### Intégration Business Intelligence
- [ ] Connecteurs Tableau/Power BI
- [ ] APIs REST pour données
- [ ] Webhooks pour notifications
- [ ] Intégration bases de données

## 📊 Performance

### Métriques typiques
- **Chargement données**: ~100ms pour 1000 enregistrements
- **Génération graphiques**: ~5-10s pour 7 visualisations
- **Rapport HTML**: ~1-2s pour génération template
- **Mémoire**: ~100-200MB pour datasets moyens

### Optimisations
- **Lazy loading** des données par chunks
- **Caching** pandas DataFrames
- **Vectorisation** numpy pour calculs
- **Compression** PNG avec optimisation