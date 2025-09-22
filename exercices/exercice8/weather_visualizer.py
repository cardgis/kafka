#!/usr/bin/env python3
"""
🌊📊 Kafka Weather Analytics - Exercice 8: Advanced BI Visualizations
=====================================================================

Système de visualisation et d'analyse BI avancée pour les données météorologiques
stockées dans la structure HDFS générée par l'exercice 7.

Fonctionnalités:
- Dashboards interactifs avec Plotly/Dash
- Analyses temporelles et géographiques
- Alertes prédictives et détection d'anomalies
- Export multi-format (PNG, HTML, CSV, JSON)
- Agrégations multi-dimensionnelles

Usage:
    python weather_visualizer.py --input "./hdfs-data"
    python weather_visualizer.py --input "./hdfs-data" --dashboard
    python weather_visualizer.py --input "./hdfs-data" --export-data
"""

import json
import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Analytics and Visualization Stack
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.gridspec import GridSpec
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

# Scientific Computing
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# ==================================================================================
# CONFIGURATION & CONSTANTS
# ==================================================================================

# Visualization Configuration
VISUALIZATION_CONFIG = {
    'figure_size': (20, 12),
    'dpi': 300,
    'style': 'seaborn-v0_8-darkgrid',
    'color_palette': 'viridis',
    'export_formats': ['png', 'html'],
    'interactive': True,
    'font_size': 12,
    'title_size': 16
}

# Alert Thresholds
ALERT_THRESHOLDS = {
    'wind': {'level_1': 10, 'level_2': 20},  # m/s
    'heat': {'level_1': 25, 'level_2': 35}   # °C
}

# Color Schemes
COUNTRY_COLORS = {
    'FR': '#FF6B6B', 'DE': '#4ECDC4', 'GB': '#45B7D1', 
    'US': '#96CEB4', 'JP': '#FFEAA7', 'UNKNOWN': '#DDA0DD'
}

ALERT_COLORS = {
    'wind_alert_0': '#2ECC71', 'wind_alert_1': '#F39C12', 'wind_alert_2': '#E74C3C',
    'heat_alert_0': '#3498DB', 'heat_alert_1': '#E67E22', 'heat_alert_2': '#C0392B'
}

# ==================================================================================
# DATA PROCESSING ENGINE
# ==================================================================================

class WeatherDataProcessor:
    """Engine de traitement des données météorologiques HDFS"""
    
    def __init__(self, hdfs_path: str):
        self.hdfs_path = Path(hdfs_path)
        self.logger = self._setup_logging()
        self.data = pd.DataFrame()
        self.stats = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration du système de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('weather_analytics.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    def load_hdfs_data(self) -> pd.DataFrame:
        """Charge toutes les données HDFS dans un DataFrame unifié"""
        self.logger.info(f"🔍 Scanning HDFS structure: {self.hdfs_path}")
        
        all_data = []
        countries_found = []
        cities_found = []
        
        # Parcours récursif de la structure HDFS
        for country_dir in self.hdfs_path.iterdir():
            if not country_dir.is_dir():
                continue
                
            country_code = country_dir.name
            countries_found.append(country_code)
            
            for city_dir in country_dir.iterdir():
                if not city_dir.is_dir():
                    continue
                    
                city_name = city_dir.name
                cities_found.append(f"{city_name}, {country_code}")
                
                # Lecture du fichier alerts.json
                alerts_file = city_dir / "alerts.json"
                if alerts_file.exists():
                    try:
                        with open(alerts_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                if line.strip():
                                    record = json.loads(line.strip())
                                    # Enrichissement avec métadonnées géographiques
                                    record['country'] = country_code
                                    record['city'] = city_name
                                    record['location'] = f"{city_name}, {country_code}"
                                    all_data.append(record)
                                    
                    except Exception as e:
                        self.logger.warning(f"⚠️ Erreur lecture {alerts_file}: {e}")
        
        # Conversion en DataFrame
        if all_data:
            self.data = pd.DataFrame(all_data)
            self._process_dataframe()
            
            self.logger.info(f"✅ Données chargées: {len(self.data)} records")
            self.logger.info(f"🌍 Pays: {sorted(set(countries_found))}")
            self.logger.info(f"🏙️ Villes: {len(set(cities_found))} villes")
            
        else:
            self.logger.error("❌ Aucune donnée trouvée dans la structure HDFS")
            self.data = pd.DataFrame()
            
        return self.data
    
    def _process_dataframe(self):
        """Traitement et nettoyage du DataFrame"""
        if self.data.empty:
            return
            
        # Conversion des types
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        self.data['temperature'] = pd.to_numeric(self.data['temperature'], errors='coerce')
        self.data['windspeed'] = pd.to_numeric(self.data['windspeed'], errors='coerce')
        self.data['wind_alert_level'] = pd.to_numeric(self.data['wind_alert_level'], errors='coerce')
        self.data['heat_alert_level'] = pd.to_numeric(self.data['heat_alert_level'], errors='coerce')
        
        # Création de colonnes dérivées
        self.data['date'] = self.data['timestamp'].dt.date
        self.data['hour'] = self.data['timestamp'].dt.hour
        self.data['day_of_week'] = self.data['timestamp'].dt.day_name()
        self.data['month'] = self.data['timestamp'].dt.month_name()
        
        # Calcul d'indicateurs composites
        self.data['total_alert_level'] = self.data['wind_alert_level'] + self.data['heat_alert_level']
        self.data['has_alert'] = (self.data['wind_alert_level'] > 0) | (self.data['heat_alert_level'] > 0)
        
        # Suppression des valeurs aberrantes
        initial_count = len(self.data)
        self.data = self.data.dropna(subset=['temperature', 'windspeed'])
        self.data = self.data[
            (self.data['temperature'] >= -50) & (self.data['temperature'] <= 60) &
            (self.data['windspeed'] >= 0) & (self.data['windspeed'] <= 200)
        ]
        final_count = len(self.data)
        
        if initial_count > final_count:
            self.logger.info(f"🧹 Nettoyage: {initial_count - final_count} records supprimés")
    
    def compute_statistics(self) -> Dict[str, Any]:
        """Calcule des statistiques descriptives complètes"""
        if self.data.empty:
            return {}
            
        stats = {
            'general': {
                'total_records': len(self.data),
                'date_range': {
                    'start': self.data['timestamp'].min().isoformat(),
                    'end': self.data['timestamp'].max().isoformat(),
                    'duration_days': (self.data['timestamp'].max() - self.data['timestamp'].min()).days
                },
                'countries': sorted(self.data['country'].unique().tolist()),
                'cities': sorted(self.data['location'].unique().tolist()),
                'unique_locations': self.data['location'].nunique()
            },
            
            'temperature': {
                'mean': float(self.data['temperature'].mean()),
                'std': float(self.data['temperature'].std()),
                'min': float(self.data['temperature'].min()),
                'max': float(self.data['temperature'].max()),
                'median': float(self.data['temperature'].median()),
                'q25': float(self.data['temperature'].quantile(0.25)),
                'q75': float(self.data['temperature'].quantile(0.75))
            },
            
            'windspeed': {
                'mean': float(self.data['windspeed'].mean()),
                'std': float(self.data['windspeed'].std()),
                'min': float(self.data['windspeed'].min()),
                'max': float(self.data['windspeed'].max()),
                'median': float(self.data['windspeed'].median()),
                'q25': float(self.data['windspeed'].quantile(0.25)),
                'q75': float(self.data['windspeed'].quantile(0.75))
            },
            
            'alerts': {
                'total_alerts': int(self.data['has_alert'].sum()),
                'alert_percentage': float(self.data['has_alert'].mean() * 100),
                'wind_alerts': {
                    'level_0': int((self.data['wind_alert_level'] == 0).sum()),
                    'level_1': int((self.data['wind_alert_level'] == 1).sum()),
                    'level_2': int((self.data['wind_alert_level'] == 2).sum())
                },
                'heat_alerts': {
                    'level_0': int((self.data['heat_alert_level'] == 0).sum()),
                    'level_1': int((self.data['heat_alert_level'] == 1).sum()),
                    'level_2': int((self.data['heat_alert_level'] == 2).sum())
                }
            },
            
            'geographical': {
                'by_country': self.data.groupby('country').agg({
                    'temperature': ['mean', 'std', 'count'],
                    'windspeed': ['mean', 'std'],
                    'has_alert': 'mean'
                }).round(2).to_dict(),
                
                'most_active_cities': self.data['location'].value_counts().head(10).to_dict()
            },
            
            'temporal': {
                'by_hour': self.data.groupby('hour')['temperature'].mean().round(2).to_dict(),
                'by_month': self.data.groupby('month')['temperature'].mean().round(2).to_dict(),
                'daily_records': self.data.groupby('date').size().describe().to_dict()
            }
        }
        
        self.stats = stats
        return stats

# ==================================================================================
# VISUALIZATION ENGINE
# ==================================================================================

class WeatherVisualizer:
    """Engine de visualisation avancée pour analytics météorologiques"""
    
    def __init__(self, data_processor: WeatherDataProcessor, output_dir: str = "./visualizations"):
        self.processor = data_processor
        self.data = data_processor.data
        self.stats = data_processor.stats
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = data_processor.logger
        
        # Configuration matplotlib
        plt.style.use(VISUALIZATION_CONFIG['style'])
        plt.rcParams['figure.figsize'] = VISUALIZATION_CONFIG['figure_size']
        plt.rcParams['figure.dpi'] = VISUALIZATION_CONFIG['dpi']
        plt.rcParams['font.size'] = VISUALIZATION_CONFIG['font_size']
        
    def create_comprehensive_dashboard(self):
        """Crée un dashboard complet avec toutes les visualisations"""
        self.logger.info("🎨 Génération du dashboard complet")
        
        if self.data.empty:
            self.logger.error("❌ Aucune donnée à visualiser")
            return
            
        # 1. Overview temporel
        self._create_temporal_overview()
        
        # 2. Analyses géographiques
        self._create_geographical_analysis()
        
        # 3. Analyse des alertes
        self._create_alert_analysis()
        
        # 4. Corrélations et patterns
        self._create_correlation_analysis()
        
        # 5. Dashboard interactif
        self._create_interactive_dashboard()
        
        # 6. Export des données agrégées
        self._export_aggregated_data()
        
        self.logger.info(f"✅ Dashboard complet généré dans: {self.output_dir}")
    
    def _create_temporal_overview(self):
        """Crée les visualisations temporelles"""
        self.logger.info("📈 Génération des analyses temporelles")
        
        fig = plt.figure(figsize=(20, 16))
        gs = GridSpec(4, 2, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. Évolution température dans le temps
        ax1 = fig.add_subplot(gs[0, :])
        if not self.data.empty:
            daily_temp = self.data.groupby('date')['temperature'].agg(['mean', 'min', 'max']).reset_index()
            daily_temp['date'] = pd.to_datetime(daily_temp['date'])
            
            ax1.plot(daily_temp['date'], daily_temp['mean'], label='Température moyenne', color='red', linewidth=2)
            ax1.fill_between(daily_temp['date'], daily_temp['min'], daily_temp['max'], 
                           alpha=0.3, color='red', label='Min-Max range')
            
            ax1.set_title('🌡️ Évolution de la Température dans le Temps', fontsize=16, fontweight='bold')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Température (°C)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(daily_temp)//10)))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # 2. Évolution vitesse du vent
        ax2 = fig.add_subplot(gs[1, :])
        if not self.data.empty:
            daily_wind = self.data.groupby('date')['windspeed'].agg(['mean', 'min', 'max']).reset_index()
            daily_wind['date'] = pd.to_datetime(daily_wind['date'])
            
            ax2.plot(daily_wind['date'], daily_wind['mean'], label='Vitesse moyenne', color='blue', linewidth=2)
            ax2.fill_between(daily_wind['date'], daily_wind['min'], daily_wind['max'], 
                           alpha=0.3, color='blue', label='Min-Max range')
            
            ax2.set_title('💨 Évolution de la Vitesse du Vent dans le Temps', fontsize=16, fontweight='bold')
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Vitesse du vent (m/s)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax2.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(daily_wind)//10)))
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        # 3. Distribution par heure
        ax3 = fig.add_subplot(gs[2, 0])
        if not self.data.empty:
            hourly_temp = self.data.groupby('hour')['temperature'].mean()
            ax3.bar(hourly_temp.index, hourly_temp.values, color='orange', alpha=0.7)
            ax3.set_title('🕐 Température Moyenne par Heure', fontweight='bold')
            ax3.set_xlabel('Heure')
            ax3.set_ylabel('Température (°C)')
            ax3.grid(True, alpha=0.3)
        
        # 4. Distribution par pays
        ax4 = fig.add_subplot(gs[2, 1])
        if not self.data.empty:
            country_temp = self.data.groupby('country')['temperature'].mean().sort_values(ascending=False)
            colors = [COUNTRY_COLORS.get(country, '#888888') for country in country_temp.index]
            ax4.bar(country_temp.index, country_temp.values, color=colors, alpha=0.8)
            ax4.set_title('🌍 Température Moyenne par Pays', fontweight='bold')
            ax4.set_xlabel('Pays')
            ax4.set_ylabel('Température (°C)')
            ax4.grid(True, alpha=0.3)
        
        # 5. Heatmap correlation
        ax5 = fig.add_subplot(gs[3, :])
        if not self.data.empty:
            numeric_cols = ['temperature', 'windspeed', 'wind_alert_level', 'heat_alert_level', 'total_alert_level']
            correlation_matrix = self.data[numeric_cols].corr()
            
            im = ax5.imshow(correlation_matrix, cmap='RdYlBu_r', aspect='auto', vmin=-1, vmax=1)
            ax5.set_xticks(range(len(numeric_cols)))
            ax5.set_yticks(range(len(numeric_cols)))
            ax5.set_xticklabels(numeric_cols, rotation=45, ha='right')
            ax5.set_yticklabels(numeric_cols)
            ax5.set_title('🔗 Matrice de Corrélation des Variables Météorologiques', fontweight='bold')
            
            # Annotations des valeurs
            for i in range(len(numeric_cols)):
                for j in range(len(numeric_cols)):
                    text = ax5.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                                   ha="center", va="center", color="black", fontweight='bold')
            
            plt.colorbar(im, ax=ax5, fraction=0.046, pad=0.04)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "01_temporal_overview.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_geographical_analysis(self):
        """Crée les analyses géographiques"""
        self.logger.info("🗺️ Génération des analyses géographiques")
        
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle('🌍 Analyse Géographique des Données Météorologiques', fontsize=20, fontweight='bold')
        
        if self.data.empty:
            return
            
        # 1. Température moyenne par pays
        ax1 = axes[0, 0]
        country_stats = self.data.groupby('country').agg({
            'temperature': 'mean',
            'windspeed': 'mean',
            'has_alert': 'mean'
        }).round(2)
        
        colors = [COUNTRY_COLORS.get(country, '#888888') for country in country_stats.index]
        bars = ax1.bar(country_stats.index, country_stats['temperature'], color=colors, alpha=0.8)
        ax1.set_title('🌡️ Température Moyenne par Pays', fontweight='bold')
        ax1.set_ylabel('Température (°C)')
        ax1.grid(True, alpha=0.3)
        
        # Annotations
        for bar, temp in zip(bars, country_stats['temperature']):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    f'{temp:.1f}°C', ha='center', va='bottom', fontweight='bold')
        
        # 2. Vitesse du vent par pays
        ax2 = axes[0, 1]
        bars = ax2.bar(country_stats.index, country_stats['windspeed'], color=colors, alpha=0.8)
        ax2.set_title('💨 Vitesse du Vent Moyenne par Pays', fontweight='bold')
        ax2.set_ylabel('Vitesse (m/s)')
        ax2.grid(True, alpha=0.3)
        
        for bar, wind in zip(bars, country_stats['windspeed']):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
                    f'{wind:.1f}m/s', ha='center', va='bottom', fontweight='bold')
        
        # 3. Pourcentage d'alertes par pays
        ax3 = axes[1, 0]
        alert_percentage = country_stats['has_alert'] * 100
        bars = ax3.bar(country_stats.index, alert_percentage, color=colors, alpha=0.8)
        ax3.set_title('⚠️ Pourcentage d\'Alertes par Pays', fontweight='bold')
        ax3.set_ylabel('Pourcentage (%)')
        ax3.grid(True, alpha=0.3)
        
        for bar, pct in zip(bars, alert_percentage):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 4. Top 10 villes les plus actives
        ax4 = axes[1, 1]
        top_cities = self.data['location'].value_counts().head(10)
        ax4.barh(range(len(top_cities)), top_cities.values, color='skyblue', alpha=0.8)
        ax4.set_yticks(range(len(top_cities)))
        ax4.set_yticklabels(top_cities.index)
        ax4.set_title('🏙️ Top 10 Villes les Plus Actives', fontweight='bold')
        ax4.set_xlabel('Nombre de mesures')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "02_geographical_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_alert_analysis(self):
        """Crée l'analyse des alertes"""
        self.logger.info("🚨 Génération de l'analyse des alertes")
        
        fig, axes = plt.subplots(2, 3, figsize=(24, 16))
        fig.suptitle('🚨 Analyse Complète des Alertes Météorologiques', fontsize=20, fontweight='bold')
        
        if self.data.empty:
            return
        
        # 1. Distribution des alertes vent
        ax1 = axes[0, 0]
        wind_alert_counts = self.data['wind_alert_level'].value_counts().sort_index()
        colors_wind = ['#2ECC71', '#F39C12', '#E74C3C']
        bars = ax1.bar(wind_alert_counts.index, wind_alert_counts.values, 
                      color=colors_wind[:len(wind_alert_counts)], alpha=0.8)
        ax1.set_title('💨 Distribution des Alertes Vent', fontweight='bold')
        ax1.set_xlabel('Niveau d\'alerte')
        ax1.set_ylabel('Nombre de mesures')
        ax1.grid(True, alpha=0.3)
        
        for bar, count in zip(bars, wind_alert_counts.values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, 
                    f'{count:,}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Distribution des alertes chaleur
        ax2 = axes[0, 1]
        heat_alert_counts = self.data['heat_alert_level'].value_counts().sort_index()
        colors_heat = ['#3498DB', '#E67E22', '#C0392B']
        bars = ax2.bar(heat_alert_counts.index, heat_alert_counts.values, 
                      color=colors_heat[:len(heat_alert_counts)], alpha=0.8)
        ax2.set_title('🌡️ Distribution des Alertes Chaleur', fontweight='bold')
        ax2.set_xlabel('Niveau d\'alerte')
        ax2.set_ylabel('Nombre de mesures')
        ax2.grid(True, alpha=0.3)
        
        for bar, count in zip(bars, heat_alert_counts.values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, 
                    f'{count:,}', ha='center', va='bottom', fontweight='bold')
        
        # 3. Évolution des alertes dans le temps
        ax3 = axes[0, 2]
        daily_alerts = self.data.groupby('date')['has_alert'].sum().reset_index()
        daily_alerts['date'] = pd.to_datetime(daily_alerts['date'])
        
        ax3.plot(daily_alerts['date'], daily_alerts['has_alert'], 
                color='red', linewidth=2, marker='o', markersize=4)
        ax3.set_title('📈 Évolution des Alertes par Jour', fontweight='bold')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Nombre d\'alertes')
        ax3.grid(True, alpha=0.3)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        
        # 4. Alertes par pays
        ax4 = axes[1, 0]
        alert_by_country = self.data.groupby('country')['has_alert'].sum().sort_values(ascending=False)
        colors = [COUNTRY_COLORS.get(country, '#888888') for country in alert_by_country.index]
        bars = ax4.bar(alert_by_country.index, alert_by_country.values, color=colors, alpha=0.8)
        ax4.set_title('🌍 Nombre d\'Alertes par Pays', fontweight='bold')
        ax4.set_ylabel('Nombre d\'alertes')
        ax4.grid(True, alpha=0.3)
        
        for bar, count in zip(bars, alert_by_country.values):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                    f'{count:,}', ha='center', va='bottom', fontweight='bold')
        
        # 5. Heatmap alertes par heure et jour de la semaine
        ax5 = axes[1, 1]
        if not self.data.empty:
            hourly_dow_alerts = self.data.groupby(['day_of_week', 'hour'])['has_alert'].sum().unstack(fill_value=0)
            
            # Réorganiser les jours de la semaine
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            hourly_dow_alerts = hourly_dow_alerts.reindex(day_order)
            
            im = ax5.imshow(hourly_dow_alerts.values, aspect='auto', cmap='Reds')
            ax5.set_xticks(range(24))
            ax5.set_xticklabels(range(24))
            ax5.set_yticks(range(len(day_order)))
            ax5.set_yticklabels([day[:3] for day in day_order])
            ax5.set_title('🕐 Heatmap Alertes par Heure et Jour', fontweight='bold')
            ax5.set_xlabel('Heure')
            ax5.set_ylabel('Jour de la semaine')
            plt.colorbar(im, ax=ax5, fraction=0.046, pad=0.04)
        
        # 6. Corrélation température vs vitesse du vent avec alertes
        ax6 = axes[1, 2]
        if not self.data.empty:
            # Scatter plot avec couleurs par niveau d'alerte
            scatter_data = self.data.sample(min(1000, len(self.data)))  # Échantillonnage pour performance
            colors = []
            for _, row in scatter_data.iterrows():
                if row['wind_alert_level'] >= 2 or row['heat_alert_level'] >= 2:
                    colors.append('#E74C3C')  # Rouge pour alertes niveau 2
                elif row['wind_alert_level'] >= 1 or row['heat_alert_level'] >= 1:
                    colors.append('#F39C12')  # Orange pour alertes niveau 1
                else:
                    colors.append('#2ECC71')  # Vert pour pas d'alerte
            
            ax6.scatter(scatter_data['temperature'], scatter_data['windspeed'], 
                       c=colors, alpha=0.6, s=20)
            ax6.set_title('🌡️💨 Température vs Vitesse du Vent\n(Couleur = Niveau d\'alerte)', fontweight='bold')
            ax6.set_xlabel('Température (°C)')
            ax6.set_ylabel('Vitesse du vent (m/s)')
            ax6.grid(True, alpha=0.3)
            
            # Légende
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ECC71', markersize=8, label='Pas d\'alerte'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='#F39C12', markersize=8, label='Alerte niveau 1'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='#E74C3C', markersize=8, label='Alerte niveau 2')
            ]
            ax6.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "03_alert_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_correlation_analysis(self):
        """Crée l'analyse des corrélations et patterns"""
        self.logger.info("🔗 Génération de l'analyse des corrélations")
        
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle('🔗 Analyse des Corrélations et Patterns Météorologiques', fontsize=20, fontweight='bold')
        
        if self.data.empty:
            return
        
        # 1. Matrice de corrélation détaillée
        ax1 = axes[0, 0]
        numeric_cols = ['temperature', 'windspeed', 'wind_alert_level', 'heat_alert_level', 'hour']
        correlation_matrix = self.data[numeric_cols].corr()
        
        im = ax1.imshow(correlation_matrix, cmap='RdYlBu_r', aspect='auto', vmin=-1, vmax=1)
        ax1.set_xticks(range(len(numeric_cols)))
        ax1.set_yticks(range(len(numeric_cols)))
        ax1.set_xticklabels(['Température', 'Vitesse vent', 'Alerte vent', 'Alerte chaleur', 'Heure'], 
                           rotation=45, ha='right')
        ax1.set_yticklabels(['Température', 'Vitesse vent', 'Alerte vent', 'Alerte chaleur', 'Heure'])
        ax1.set_title('🔗 Matrice de Corrélation Détaillée', fontweight='bold')
        
        # Annotations
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                text = ax1.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                               ha="center", va="center", color="black", fontweight='bold')
        
        plt.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
        
        # 2. Distribution température par niveau d'alerte vent
        ax2 = axes[0, 1]
        wind_levels = sorted(self.data['wind_alert_level'].unique())
        temp_by_wind = [self.data[self.data['wind_alert_level'] == level]['temperature'].values 
                       for level in wind_levels]
        
        bp = ax2.boxplot(temp_by_wind, labels=[f'Niveau {level}' for level in wind_levels], 
                        patch_artist=True)
        colors = ['#2ECC71', '#F39C12', '#E74C3C']
        for patch, color in zip(bp['boxes'], colors[:len(bp['boxes'])]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax2.set_title('🌡️ Distribution de la Température\npar Niveau d\'Alerte Vent', fontweight='bold')
        ax2.set_ylabel('Température (°C)')
        ax2.grid(True, alpha=0.3)
        
        # 3. Patterns temporels - température moyenne par heure
        ax3 = axes[1, 0]
        hourly_patterns = self.data.groupby('hour').agg({
            'temperature': 'mean',
            'windspeed': 'mean',
            'has_alert': 'mean'
        })
        
        ax3_twin = ax3.twinx()
        
        line1 = ax3.plot(hourly_patterns.index, hourly_patterns['temperature'], 
                        'r-', linewidth=2, label='Température', marker='o')
        line2 = ax3_twin.plot(hourly_patterns.index, hourly_patterns['windspeed'], 
                             'b-', linewidth=2, label='Vitesse vent', marker='s')
        
        ax3.set_xlabel('Heure')
        ax3.set_ylabel('Température (°C)', color='red')
        ax3_twin.set_ylabel('Vitesse du vent (m/s)', color='blue')
        ax3.set_title('🕐 Patterns Horaires - Température et Vent', fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # Légende combinée
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, loc='upper left')
        
        # 4. Clustering analysis
        ax4 = axes[1, 1]
        if len(self.data) > 100:  # Clustering seulement si suffisamment de données
            # Préparation des données pour clustering
            cluster_data = self.data[['temperature', 'windspeed']].dropna()
            if len(cluster_data) > 100:
                # Échantillonnage pour performance
                cluster_sample = cluster_data.sample(min(1000, len(cluster_data)))
                
                # Normalisation
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(cluster_sample)
                
                # K-means clustering
                kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(scaled_data)
                
                # Visualisation
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
                for i in range(3):
                    mask = cluster_labels == i
                    ax4.scatter(cluster_sample.iloc[mask]['temperature'], 
                               cluster_sample.iloc[mask]['windspeed'],
                               c=colors[i], alpha=0.6, s=20, label=f'Cluster {i+1}')
                
                # Centres des clusters
                centers = scaler.inverse_transform(kmeans.cluster_centers_)
                ax4.scatter(centers[:, 0], centers[:, 1], c='black', marker='x', s=200, linewidths=3)
                
                ax4.set_title('🎯 Clustering K-means\n(Température vs Vitesse du vent)', fontweight='bold')
                ax4.set_xlabel('Température (°C)')
                ax4.set_ylabel('Vitesse du vent (m/s)')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "04_correlation_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_interactive_dashboard(self):
        """Crée un dashboard interactif avec Plotly"""
        self.logger.info("🎛️ Génération du dashboard interactif")
        
        if self.data.empty:
            return
        
        # Création du dashboard avec subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                '🌡️ Évolution de la Température',
                '💨 Évolution de la Vitesse du Vent',
                '🚨 Distribution des Alertes',
                '🌍 Analyse Géographique',
                '🕐 Patterns Horaires',
                '🔗 Corrélation Temp vs Vent'
            ),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": True}, {"secondary_y": False}]]
        )
        
        # 1. Évolution température
        daily_temp = self.data.groupby('date')['temperature'].agg(['mean', 'min', 'max']).reset_index()
        fig.add_trace(
            go.Scatter(x=daily_temp['date'], y=daily_temp['mean'], 
                      mode='lines+markers', name='Temp moyenne',
                      line=dict(color='red', width=2)),
            row=1, col=1
        )
        
        # 2. Évolution vitesse du vent
        daily_wind = self.data.groupby('date')['windspeed'].agg(['mean', 'min', 'max']).reset_index()
        fig.add_trace(
            go.Scatter(x=daily_wind['date'], y=daily_wind['mean'], 
                      mode='lines+markers', name='Vent moyen',
                      line=dict(color='blue', width=2)),
            row=1, col=2
        )
        
        # 3. Distribution des alertes
        alert_counts = pd.concat([
            self.data['wind_alert_level'].value_counts().rename('Wind'),
            self.data['heat_alert_level'].value_counts().rename('Heat')
        ], axis=1).fillna(0)
        
        fig.add_trace(
            go.Bar(x=alert_counts.index, y=alert_counts['Wind'], 
                  name='Alertes Vent', marker_color='lightblue'),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(x=alert_counts.index, y=alert_counts['Heat'], 
                  name='Alertes Chaleur', marker_color='orange'),
            row=2, col=1
        )
        
        # 4. Analyse géographique
        country_stats = self.data.groupby('country')['temperature'].mean().sort_values(ascending=False)
        fig.add_trace(
            go.Bar(x=country_stats.index, y=country_stats.values, 
                  name='Temp par pays', marker_color='green'),
            row=2, col=2
        )
        
        # 5. Patterns horaires
        hourly_temp = self.data.groupby('hour')['temperature'].mean()
        hourly_wind = self.data.groupby('hour')['windspeed'].mean()
        
        fig.add_trace(
            go.Scatter(x=hourly_temp.index, y=hourly_temp.values, 
                      mode='lines+markers', name='Temp horaire',
                      line=dict(color='red')),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=hourly_wind.index, y=hourly_wind.values, 
                      mode='lines+markers', name='Vent horaire',
                      line=dict(color='blue'), yaxis='y2'),
            row=3, col=1, secondary_y=True
        )
        
        # 6. Scatter plot température vs vent
        sample_data = self.data.sample(min(500, len(self.data)))
        fig.add_trace(
            go.Scatter(x=sample_data['temperature'], y=sample_data['windspeed'],
                      mode='markers', name='Temp vs Vent',
                      marker=dict(color=sample_data['total_alert_level'], 
                                colorscale='Reds', showscale=True)),
            row=3, col=2
        )
        
        # Configuration du layout
        fig.update_layout(
            title_text="🌊📊 Dashboard Interactif - Analyse Météorologique Complète",
            title_x=0.5,
            title_font_size=20,
            height=1200,
            showlegend=True
        )
        
        # Sauvegarde du dashboard interactif
        output_html = self.output_dir / "05_interactive_dashboard.html"
        pyo.plot(fig, filename=str(output_html), auto_open=False)
        
        self.logger.info(f"✅ Dashboard interactif sauvegardé: {output_html}")
    
    def _export_aggregated_data(self):
        """Exporte les données agrégées dans différents formats"""
        self.logger.info("📊 Export des données agrégées")
        
        if self.data.empty:
            return
        
        exports_dir = self.output_dir / "exports"
        exports_dir.mkdir(exist_ok=True)
        
        # 1. Données journalières agrégées
        daily_agg = self.data.groupby(['date', 'country']).agg({
            'temperature': ['mean', 'min', 'max', 'std'],
            'windspeed': ['mean', 'min', 'max', 'std'],
            'wind_alert_level': ['mean', 'max'],
            'heat_alert_level': ['mean', 'max'],
            'has_alert': ['sum', 'mean'],
            'location': 'count'
        }).round(2)
        
        daily_agg.columns = ['_'.join(col).strip() for col in daily_agg.columns.values]
        daily_agg.reset_index().to_csv(exports_dir / "daily_aggregated_data.csv", index=False)
        
        # 2. Statistiques par pays
        country_stats = self.data.groupby('country').agg({
            'temperature': ['count', 'mean', 'std', 'min', 'max'],
            'windspeed': ['mean', 'std', 'min', 'max'],
            'wind_alert_level': lambda x: (x > 0).sum(),
            'heat_alert_level': lambda x: (x > 0).sum(),
            'has_alert': ['sum', 'mean'],
            'location': 'nunique'
        }).round(2)
        
        country_stats.columns = ['_'.join(col).strip() for col in country_stats.columns.values]
        country_stats.to_csv(exports_dir / "country_statistics.csv")
        
        # 3. Top villes avec le plus d'alertes
        city_alerts = self.data.groupby('location').agg({
            'has_alert': 'sum',
            'temperature': 'mean',
            'windspeed': 'mean',
            'wind_alert_level': 'max',
            'heat_alert_level': 'max'
        }).sort_values('has_alert', ascending=False).head(20)
        
        city_alerts.to_csv(exports_dir / "top_alert_cities.csv")
        
        # 4. Patterns temporels
        temporal_patterns = self.data.groupby(['hour', 'day_of_week']).agg({
            'temperature': 'mean',
            'windspeed': 'mean',
            'has_alert': 'mean'
        }).round(2)
        
        temporal_patterns.to_csv(exports_dir / "temporal_patterns.csv")
        
        # 5. Export des statistiques complètes en JSON
        with open(exports_dir / "complete_statistics.json", 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"✅ Données exportées dans: {exports_dir}")

# ==================================================================================
# CLI INTERFACE
# ==================================================================================

def create_argparser() -> argparse.ArgumentParser:
    """Crée le parser d'arguments CLI"""
    parser = argparse.ArgumentParser(
        description="🌊📊 Kafka Weather Analytics - Exercice 8: Advanced BI Visualizations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python weather_visualizer.py --input "./hdfs-data"
  python weather_visualizer.py --input "./hdfs-data" --dashboard
  python weather_visualizer.py --input "./hdfs-data" --export-data
  python weather_visualizer.py --input "./hdfs-data" --output "./custom_reports"
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        default="./hdfs-data",
        help="Chemin vers les données HDFS (défaut: ./hdfs-data)"
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default="./visualizations",
        help="Dossier de sortie pour les visualisations (défaut: ./visualizations)"
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help="Génère seulement le dashboard interactif"
    )
    
    parser.add_argument(
        '--export-data',
        action='store_true',
        help="Exporte seulement les données agrégées"
    )
    
    parser.add_argument(
        '--type',
        choices=['temperature', 'wind', 'alerts', 'geographical', 'temporal', 'all'],
        default='all',
        help="Type de visualisation à générer (défaut: all)"
    )
    
    parser.add_argument(
        '--country',
        type=str,
        help="Filtrer par pays spécifique (ex: FR, DE, US)"
    )
    
    parser.add_argument(
        '--format',
        choices=['png', 'html', 'both'],
        default='both',
        help="Format de sortie (défaut: both)"
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Mode verbeux"
    )
    
    return parser

def main():
    """Point d'entrée principal"""
    parser = create_argparser()
    args = parser.parse_args()
    
    # Configuration du logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.getLogger().setLevel(log_level)
    
    try:
        # Initialisation du processeur de données
        print("🌊📊 Kafka Weather Analytics - Exercice 8: Advanced BI Visualizations")
        print("=" * 80)
        
        processor = WeatherDataProcessor(args.input)
        
        # Chargement des données
        data = processor.load_hdfs_data()
        if data.empty:
            print("❌ Aucune donnée trouvée. Vérifiez le chemin HDFS.")
            return 1
        
        # Calcul des statistiques
        stats = processor.compute_statistics()
        
        # Filtrage par pays si spécifié
        if args.country:
            data = data[data['country'] == args.country.upper()]
            processor.data = data
            print(f"🔍 Filtrage par pays: {args.country.upper()} ({len(data)} records)")
        
        # Initialisation du visualiseur
        visualizer = WeatherVisualizer(processor, args.output)
        
        # Génération des visualisations selon les options
        if args.dashboard:
            visualizer._create_interactive_dashboard()
        elif args.export_data:
            visualizer._export_aggregated_data()
        elif args.type == 'temperature':
            visualizer._create_temporal_overview()
        elif args.type == 'alerts':
            visualizer._create_alert_analysis()
        elif args.type == 'geographical':
            visualizer._create_geographical_analysis()
        elif args.type == 'temporal':
            visualizer._create_correlation_analysis()
        else:
            # Génération complète
            visualizer.create_comprehensive_dashboard()
        
        # Affichage des statistiques clés
        print("\n📊 Statistiques Clés:")
        print(f"   • Total records: {stats['general']['total_records']:,}")
        print(f"   • Période: {stats['general']['date_range']['duration_days']} jours")
        print(f"   • Pays: {len(stats['general']['countries'])}")
        print(f"   • Villes: {stats['general']['unique_locations']}")
        print(f"   • Alertes: {stats['alerts']['total_alerts']:,} ({stats['alerts']['alert_percentage']:.1f}%)")
        print(f"   • Température moyenne: {stats['temperature']['mean']:.1f}°C")
        print(f"   • Vitesse vent moyenne: {stats['windspeed']['mean']:.1f} m/s")
        
        print(f"\n✅ Visualisations générées dans: {args.output}")
        print("🎊 Exercice 8 terminé avec succès!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())