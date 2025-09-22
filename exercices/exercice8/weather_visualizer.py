#!/usr/bin/env python3
"""
Exercice 8: Visualisations des logs HDFS
=========================================

Dashboard de visualisation des données météo stockées dans HDFS.
Analyse des températures, vents, alertes par niveau et codes météo par pays.

Fonctionnalités:
- Analyse des données HDFS par pays/ville
- Graphiques température et vent
- Distribution des alertes par niveau
- Codes météo par pays
- Dashboard interactif

Author: Assistant
Date: 2024
"""

import json
import os
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from collections import defaultdict, Counter

# Configuration matplotlib pour de beaux graphiques
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class HDFSWeatherAnalyzer:
    """Analyseur et visualiseur de données météo HDFS"""
    
    def __init__(self, hdfs_path: str = "./hdfs-data"):
        """
        Initialise l'analyseur HDFS
        
        Args:
            hdfs_path: Chemin vers la structure HDFS
        """
        self.hdfs_path = Path(hdfs_path)
        self.data = []
        self.countries_data = defaultdict(list)
        self.cities_data = defaultdict(list)
        
        print("📊 EXERCICE 8 - VISUALISATIONS DONNÉES MÉTÉO HDFS")
        print("=" * 60)
        
        if not self.hdfs_path.exists():
            raise FileNotFoundError(f"❌ Répertoire HDFS non trouvé: {hdfs_path}")
            
        print(f"📁 Répertoire HDFS: {self.hdfs_path.absolute()}")
        
    def load_hdfs_data(self):
        """Charge toutes les données depuis la structure HDFS"""
        print("\n🔄 Chargement des données HDFS...")
        
        total_files = 0
        total_records = 0
        
        for country_dir in self.hdfs_path.iterdir():
            if not country_dir.is_dir():
                continue
                
            country_code = country_dir.name
            print(f"🌍 Traitement pays: {country_code}")
            
            for city_dir in country_dir.iterdir():
                if not city_dir.is_dir():
                    continue
                    
                city_name = city_dir.name
                alerts_file = city_dir / "alerts.json"
                
                if not alerts_file.exists():
                    continue
                    
                try:
                    with open(alerts_file, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            try:
                                record = json.loads(line.strip())
                                
                                # Enrichir avec métadonnées géographiques
                                record['country_code'] = country_code
                                record['city_name'] = city_name
                                record['file_path'] = str(alerts_file)
                                
                                self.data.append(record)
                                self.countries_data[country_code].append(record)
                                self.cities_data[f"{country_code}_{city_name}"].append(record)
                                
                                total_records += 1
                                
                            except json.JSONDecodeError as e:
                                print(f"⚠️  Erreur JSON ligne {line_num} dans {alerts_file}: {e}")
                                
                    total_files += 1
                    print(f"   🏙️  {city_name}: {sum(1 for _ in open(alerts_file))} entrées")
                    
                except Exception as e:
                    print(f"❌ Erreur lecture {alerts_file}: {e}")
                    
        print(f"\n✅ Chargement terminé:")
        print(f"   📄 Fichiers traités: {total_files}")
        print(f"   📊 Enregistrements: {total_records}")
        print(f"   🌍 Pays: {len(self.countries_data)}")
        print(f"   🏙️  Villes: {len(self.cities_data)}")
        
        return total_records > 0
        
    def create_dataframe(self) -> pd.DataFrame:
        """Convertit les données en DataFrame pandas pour l'analyse"""
        if not self.data:
            raise ValueError("❌ Aucune donnée chargée. Appelez load_hdfs_data() d'abord.")
            
        records = []
        
        for item in self.data:
            try:
                # Extraire les données météo
                weather = item.get('weather', {})
                location = item.get('location', {})
                metadata = item.get('metadata', {})
                hdfs_meta = item.get('hdfs_metadata', {})
                
                record = {
                    'country_code': item.get('country_code', 'UNKNOWN'),
                    'city_name': item.get('city_name', 'UNKNOWN'),
                    'country': location.get('country', 'Unknown'),
                    'city': location.get('city', 'Unknown'),
                    'latitude': location.get('latitude', 0.0),
                    'longitude': location.get('longitude', 0.0),
                    'temperature': weather.get('temperature', 0.0),
                    'windspeed': weather.get('windspeed', 0.0),
                    'winddirection': weather.get('winddirection', 0),
                    'weathercode': weather.get('weathercode', 0),
                    'is_day': weather.get('is_day', 1),
                    'timestamp': metadata.get('timestamp', ''),
                    'processed_at': hdfs_meta.get('processed_at', ''),
                    'source': metadata.get('source', 'unknown')
                }
                
                # Calculer niveau d'alerte (comme dans exercice 4)
                alert_level = self._calculate_alert_level(
                    record['temperature'], 
                    record['windspeed']
                )
                record['alert_level'] = alert_level
                
                records.append(record)
                
            except Exception as e:
                print(f"⚠️  Erreur traitement enregistrement: {e}")
                continue
                
        df = pd.DataFrame(records)
        
        # Convertir les timestamps
        for col in ['timestamp', 'processed_at']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                
        print(f"📊 DataFrame créé: {len(df)} lignes, {len(df.columns)} colonnes")
        return df
        
    def _calculate_alert_level(self, temperature: float, windspeed: float) -> str:
        """Calcule le niveau d'alerte basé sur température et vent"""
        # Logique identique à l'exercice 4
        temp_alert = 0
        wind_alert = 0
        
        # Alerte température
        if temperature >= 35:
            temp_alert = 3  # Critique
        elif temperature >= 30:
            temp_alert = 2  # Élevée
        elif temperature >= 25:
            temp_alert = 1  # Modérée
        elif temperature <= -10:
            temp_alert = 3  # Critique (froid)
        elif temperature <= 0:
            temp_alert = 2  # Élevée (froid)
        elif temperature <= 5:
            temp_alert = 1  # Modérée (froid)
            
        # Alerte vent
        if windspeed >= 100:
            wind_alert = 3  # Critique
        elif windspeed >= 70:
            wind_alert = 2  # Élevée
        elif windspeed >= 40:
            wind_alert = 1  # Modérée
            
        # Niveau final (maximum des deux)
        max_alert = max(temp_alert, wind_alert)
        
        if max_alert == 3:
            return "CRITIQUE"
        elif max_alert == 2:
            return "ÉLEVÉE"
        elif max_alert == 1:
            return "MODÉRÉE"
        else:
            return "NORMALE"
            
    def generate_visualizations(self, output_dir: str = "./visualizations"):
        """Génère toutes les visualisations"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        if not self.data:
            print("❌ Aucune donnée à visualiser")
            return
            
        df = self.create_dataframe()
        
        print(f"\n🎨 Génération des visualisations dans {output_path}...")
        
        # 1. Analyse température par pays
        self._plot_temperature_by_country(df, output_path)
        
        # 2. Analyse vent par pays
        self._plot_wind_by_country(df, output_path)
        
        # 3. Distribution des alertes
        self._plot_alert_distribution(df, output_path)
        
        # 4. Codes météo par pays
        self._plot_weather_codes(df, output_path)
        
        # 5. Vue d'ensemble géographique
        self._plot_geographic_overview(df, output_path)
        
        # 6. Analyse temporelle
        self._plot_temporal_analysis(df, output_path)
        
        # 7. Dashboard récapitulatif
        self._create_dashboard(df, output_path)
        
        print(f"✅ Visualisations générées dans {output_path}")
        
    def _plot_temperature_by_country(self, df: pd.DataFrame, output_path: Path):
        """Graphique température par pays"""
        plt.figure(figsize=(12, 8))
        
        # Box plot des températures par pays
        countries = df['country_code'].value_counts().head(10).index
        df_filtered = df[df['country_code'].isin(countries)]
        
        sns.boxplot(data=df_filtered, x='country_code', y='temperature')
        plt.title('🌡️ Distribution des Températures par Pays', fontsize=16, fontweight='bold')
        plt.xlabel('Code Pays', fontsize=12)
        plt.ylabel('Température (°C)', fontsize=12)
        plt.xticks(rotation=45)
        
        # Ajouter ligne température moyenne globale
        mean_temp = df['temperature'].mean()
        plt.axhline(y=mean_temp, color='red', linestyle='--', alpha=0.7, 
                   label=f'Moyenne globale: {mean_temp:.1f}°C')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(output_path / "temperature_by_country.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   ✅ temperature_by_country.png")
        
    def _plot_wind_by_country(self, df: pd.DataFrame, output_path: Path):
        """Graphique vent par pays"""
        plt.figure(figsize=(12, 8))
        
        # Graphique barres vitesse moyenne du vent par pays
        wind_by_country = df.groupby('country_code')['windspeed'].agg(['mean', 'max']).reset_index()
        wind_by_country = wind_by_country.sort_values('mean', ascending=False).head(10)
        
        x = range(len(wind_by_country))
        width = 0.35
        
        plt.bar([i - width/2 for i in x], wind_by_country['mean'], width, 
               label='Vitesse moyenne', alpha=0.8)
        plt.bar([i + width/2 for i in x], wind_by_country['max'], width, 
               label='Vitesse maximale', alpha=0.8)
        
        plt.title('💨 Vitesse du Vent par Pays', fontsize=16, fontweight='bold')
        plt.xlabel('Code Pays', fontsize=12)
        plt.ylabel('Vitesse du Vent (km/h)', fontsize=12)
        plt.xticks(x, wind_by_country['country_code'], rotation=45)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(output_path / "wind_by_country.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   ✅ wind_by_country.png")
        
    def _plot_alert_distribution(self, df: pd.DataFrame, output_path: Path):
        """Distribution des niveaux d'alerte"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Graphique en camembert global
        alert_counts = df['alert_level'].value_counts()
        colors = ['green', 'yellow', 'orange', 'red'][:len(alert_counts)]
        
        ax1.pie(alert_counts.values, labels=alert_counts.index, autopct='%1.1f%%',
               colors=colors, startangle=90)
        ax1.set_title('🚨 Distribution Globale des Alertes', fontsize=14, fontweight='bold')
        
        # Graphique barres par pays
        alert_by_country = pd.crosstab(df['country_code'], df['alert_level'])
        alert_by_country.plot(kind='bar', stacked=True, ax=ax2, 
                             color=colors[:len(alert_by_country.columns)])
        ax2.set_title('🚨 Alertes par Pays', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Code Pays')
        ax2.set_ylabel('Nombre d\'Alertes')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend(title='Niveau d\'Alerte')
        
        plt.tight_layout()
        plt.savefig(output_path / "alert_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   ✅ alert_distribution.png")
        
    def _plot_weather_codes(self, df: pd.DataFrame, output_path: Path):
        """Codes météo par pays"""
        plt.figure(figsize=(14, 8))
        
        # Mapping des codes météo WMO
        weather_code_mapping = {
            0: "Ciel dégagé",
            1: "Principalement dégagé", 
            2: "Partiellement nuageux",
            3: "Couvert",
            45: "Brouillard",
            48: "Brouillard givrant",
            51: "Bruine légère",
            53: "Bruine modérée",
            55: "Bruine forte",
            61: "Pluie légère",
            63: "Pluie modérée",
            65: "Pluie forte",
            71: "Neige légère",
            73: "Neige modérée",
            75: "Neige forte",
            95: "Orage"
        }
        
        # Créer heatmap des codes météo par pays
        weather_by_country = pd.crosstab(df['country_code'], df['weathercode'])
        
        # Renommer les colonnes avec les descriptions
        weather_by_country.columns = [
            weather_code_mapping.get(code, f"Code {code}") 
            for code in weather_by_country.columns
        ]
        
        sns.heatmap(weather_by_country, annot=True, fmt='d', cmap='YlOrRd', 
                   cbar_kws={'label': 'Nombre d\'observations'})
        
        plt.title('🌤️ Codes Météo par Pays', fontsize=16, fontweight='bold')
        plt.xlabel('Code Météo', fontsize=12)
        plt.ylabel('Code Pays', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig(output_path / "weather_codes_by_country.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   ✅ weather_codes_by_country.png")
        
    def _plot_geographic_overview(self, df: pd.DataFrame, output_path: Path):
        """Vue d'ensemble géographique"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Scatter plot latitude/longitude avec température
        scatter = ax1.scatter(df['longitude'], df['latitude'], 
                            c=df['temperature'], s=df['windspeed']*2, 
                            cmap='coolwarm', alpha=0.7)
        ax1.set_title('🗺️ Localisation avec Température/Vent', fontweight='bold')
        ax1.set_xlabel('Longitude')
        ax1.set_ylabel('Latitude')
        plt.colorbar(scatter, ax=ax1, label='Température (°C)')
        
        # 2. Nombre de villes par pays
        cities_by_country = df.groupby('country_code')['city_name'].nunique().sort_values(ascending=False)
        cities_by_country.head(10).plot(kind='bar', ax=ax2, color='skyblue')
        ax2.set_title('🏙️ Nombre de Villes par Pays', fontweight='bold')
        ax2.set_ylabel('Nombre de Villes')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Température moyenne par pays
        temp_by_country = df.groupby('country_code')['temperature'].mean().sort_values(ascending=False)
        temp_by_country.head(10).plot(kind='bar', ax=ax3, color='coral')
        ax3.set_title('🌡️ Température Moyenne par Pays', fontweight='bold')
        ax3.set_ylabel('Température (°C)')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Distribution des directions du vent
        wind_directions = df['winddirection'].value_counts().head(8)
        wind_directions.plot(kind='bar', ax=ax4, color='lightgreen')
        ax4.set_title('🧭 Distribution des Directions du Vent', fontweight='bold')
        ax4.set_ylabel('Nombre d\'observations')
        ax4.set_xlabel('Direction (degrés)')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path / "geographic_overview.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   ✅ geographic_overview.png")
        
    def _plot_temporal_analysis(self, df: pd.DataFrame, output_path: Path):
        """Analyse temporelle des données"""
        if df['processed_at'].isna().all():
            print("   ⚠️ Pas de données temporelles pour l'analyse")
            return
            
        plt.figure(figsize=(14, 8))
        
        # Filtrer les données avec timestamps valides
        df_time = df.dropna(subset=['processed_at'])
        
        if len(df_time) == 0:
            print("   ⚠️ Aucune donnée temporelle valide")
            return
            
        # Température au fil du temps
        df_time = df_time.sort_values('processed_at')
        
        plt.subplot(2, 1, 1)
        for country in df_time['country_code'].unique()[:5]:  # Top 5 pays
            country_data = df_time[df_time['country_code'] == country]
            plt.plot(country_data['processed_at'], country_data['temperature'], 
                    marker='o', label=country, alpha=0.7)
                    
        plt.title('📈 Évolution Temporelle des Températures', fontsize=14, fontweight='bold')
        plt.ylabel('Température (°C)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Vitesse du vent au fil du temps
        plt.subplot(2, 1, 2)
        for country in df_time['country_code'].unique()[:5]:
            country_data = df_time[df_time['country_code'] == country]
            plt.plot(country_data['processed_at'], country_data['windspeed'], 
                    marker='s', label=country, alpha=0.7)
                    
        plt.title('💨 Évolution Temporelle du Vent', fontsize=14, fontweight='bold')
        plt.ylabel('Vitesse du Vent (km/h)')
        plt.xlabel('Temps de Traitement')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / "temporal_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   ✅ temporal_analysis.png")
        
    def _create_dashboard(self, df: pd.DataFrame, output_path: Path):
        """Dashboard récapitulatif avec statistiques clés"""
        fig = plt.figure(figsize=(20, 12))
        
        # Créer une grille de sous-graphiques
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # Statistiques générales (texte)
        ax_stats = fig.add_subplot(gs[0, :2])
        ax_stats.axis('off')
        
        stats_text = f"""
📊 STATISTIQUES GÉNÉRALES HDFS
═══════════════════════════════════
📄 Total enregistrements: {len(df):,}
🌍 Pays analysés: {df['country_code'].nunique()}
🏙️ Villes analysées: {df['city_name'].nunique()}

🌡️ TEMPÉRATURE
• Moyenne: {df['temperature'].mean():.1f}°C
• Min: {df['temperature'].min():.1f}°C  
• Max: {df['temperature'].max():.1f}°C

💨 VENT  
• Vitesse moyenne: {df['windspeed'].mean():.1f} km/h
• Vitesse max: {df['windspeed'].max():.1f} km/h

🚨 ALERTES
• Critiques: {len(df[df['alert_level'] == 'CRITIQUE'])}
• Élevées: {len(df[df['alert_level'] == 'ÉLEVÉE'])}
• Modérées: {len(df[df['alert_level'] == 'MODÉRÉE'])}
• Normales: {len(df[df['alert_level'] == 'NORMALE'])}
        """
        
        ax_stats.text(0.05, 0.95, stats_text, transform=ax_stats.transAxes, 
                     fontsize=12, verticalalignment='top', fontfamily='monospace',
                     bbox=dict(boxstyle="round,pad=1", facecolor="lightblue", alpha=0.7))
        
        # Top 5 pays par température
        ax1 = fig.add_subplot(gs[0, 2])
        top_temp = df.groupby('country_code')['temperature'].mean().sort_values(ascending=False).head(5)
        top_temp.plot(kind='bar', ax=ax1, color='red', alpha=0.7)
        ax1.set_title('🌡️ Top 5 Pays - Température', fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)
        
        # Top 5 pays par vent
        ax2 = fig.add_subplot(gs[0, 3])
        top_wind = df.groupby('country_code')['windspeed'].mean().sort_values(ascending=False).head(5)
        top_wind.plot(kind='bar', ax=ax2, color='blue', alpha=0.7)
        ax2.set_title('💨 Top 5 Pays - Vent', fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        
        # Distribution alertes (pie)
        ax3 = fig.add_subplot(gs[1, 0])
        alert_counts = df['alert_level'].value_counts()
        colors = ['green', 'yellow', 'orange', 'red'][:len(alert_counts)]
        ax3.pie(alert_counts.values, labels=alert_counts.index, autopct='%1.1f%%',
               colors=colors, startangle=90)
        ax3.set_title('🚨 Distribution Alertes', fontweight='bold')
        
        # Codes météo les plus fréquents
        ax4 = fig.add_subplot(gs[1, 1])
        top_weather = df['weathercode'].value_counts().head(5)
        top_weather.plot(kind='bar', ax=ax4, color='orange', alpha=0.7)
        ax4.set_title('🌤️ Top 5 Codes Météo', fontweight='bold')
        ax4.tick_params(axis='x', rotation=45)
        
        # Heatmap température vs vent par pays
        ax5 = fig.add_subplot(gs[1, 2:])
        temp_wind_by_country = df.groupby('country_code')[['temperature', 'windspeed']].mean()
        sns.scatterplot(data=temp_wind_by_country, x='temperature', y='windspeed', 
                       s=100, alpha=0.7, ax=ax5)
        
        # Annoter les points avec les codes pays
        for idx, row in temp_wind_by_country.iterrows():
            ax5.annotate(idx, (row['temperature'], row['windspeed']), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
                        
        ax5.set_title('🌡️💨 Température vs Vent par Pays', fontweight='bold')
        ax5.set_xlabel('Température Moyenne (°C)')
        ax5.set_ylabel('Vitesse Vent Moyenne (km/h)')
        
        # Historique par pays (ligne du temps simplifiée)
        ax6 = fig.add_subplot(gs[2, :])
        
        # Simulation d'une timeline avec index
        df_sample = df.head(50)  # Échantillon pour la lisibilité
        
        for i, country in enumerate(df_sample['country_code'].unique()[:5]):
            country_data = df_sample[df_sample['country_code'] == country]
            indices = country_data.index
            temperatures = country_data['temperature']
            
            ax6.plot(indices, temperatures, marker='o', label=country, alpha=0.7)
            
        ax6.set_title('📈 Échantillon Évolution Températures par Index', fontweight='bold')
        ax6.set_xlabel('Index d\'enregistrement')
        ax6.set_ylabel('Température (°C)')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        plt.suptitle('🌍 DASHBOARD MÉTÉO HDFS - VUE D\'ENSEMBLE COMPLÈTE', 
                    fontsize=20, fontweight='bold', y=0.98)
        
        plt.savefig(output_path / "dashboard_overview.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   ✅ dashboard_overview.png")
        
    def generate_report(self, output_dir: str = "./visualizations"):
        """Génère un rapport HTML avec toutes les visualisations"""
        output_path = Path(output_dir)
        
        if not self.data:
            print("❌ Aucune donnée pour le rapport")
            return
            
        df = self.create_dataframe()
        
        # Template HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌍 Rapport Analyse Météo HDFS</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1, h2 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 5px solid #3498db;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2980b9;
        }}
        .chart {{
            text-align: center;
            margin: 30px 0;
        }}
        .chart img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            background: #34495e;
            color: white;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 Rapport d'Analyse Météo HDFS</h1>
        <p><strong>Généré le:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
        
        <h2>📊 Statistiques Générales</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{len(df):,}</div>
                <div>Enregistrements Totaux</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{df['country_code'].nunique()}</div>
                <div>Pays Analysés</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{df['city_name'].nunique()}</div>
                <div>Villes Analysées</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{df['temperature'].mean():.1f}°C</div>
                <div>Température Moyenne</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{df['windspeed'].mean():.1f}</div>
                <div>Vent Moyen (km/h)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(df[df['alert_level'] != 'NORMALE'])}</div>
                <div>Alertes Météo</div>
            </div>
        </div>
        
        <h2>📈 Dashboard Complet</h2>
        <div class="chart">
            <img src="dashboard_overview.png" alt="Dashboard Complet">
        </div>
        
        <h2>🌡️ Analyse des Températures</h2>
        <div class="chart">
            <img src="temperature_by_country.png" alt="Températures par Pays">
        </div>
        
        <h2>💨 Analyse du Vent</h2>
        <div class="chart">
            <img src="wind_by_country.png" alt="Vent par Pays">
        </div>
        
        <h2>🚨 Distribution des Alertes</h2>
        <div class="chart">
            <img src="alert_distribution.png" alt="Distribution des Alertes">
        </div>
        
        <h2>🌤️ Codes Météo par Pays</h2>
        <div class="chart">
            <img src="weather_codes_by_country.png" alt="Codes Météo">
        </div>
        
        <h2>🗺️ Vue Géographique</h2>
        <div class="chart">
            <img src="geographic_overview.png" alt="Vue Géographique">
        </div>
        
        <h2>📈 Analyse Temporelle</h2>
        <div class="chart">
            <img src="temporal_analysis.png" alt="Analyse Temporelle">
        </div>
        
        <div class="footer">
            <p>🌍 Rapport généré par l'Exercice 8 - Visualisations HDFS</p>
            <p>Données source: Structure HDFS {self.hdfs_path}</p>
        </div>
    </div>
</body>
</html>
        """
        
        report_path = output_path / "rapport_meteo_hdfs.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"✅ Rapport HTML généré: {report_path}")
        return report_path


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Visualisations des données météo HDFS"
    )
    
    parser.add_argument('--hdfs-path', 
                        default='./hdfs-data',
                        help='Chemin vers la structure HDFS (défaut: ./hdfs-data)')
    
    parser.add_argument('--output-dir', 
                        default='./visualizations',
                        help='Répertoire de sortie pour les visualisations (défaut: ./visualizations)')
    
    parser.add_argument('--report', 
                        action='store_true',
                        help='Générer aussi un rapport HTML')
    
    args = parser.parse_args()
    
    try:
        # Créer l'analyseur
        analyzer = HDFSWeatherAnalyzer(args.hdfs_path)
        
        # Charger les données
        if not analyzer.load_hdfs_data():
            print("❌ Aucune donnée trouvée dans la structure HDFS")
            return
            
        # Générer les visualisations
        analyzer.generate_visualizations(args.output_dir)
        
        # Générer le rapport HTML si demandé
        if args.report:
            analyzer.generate_report(args.output_dir)
            
        print(f"\n🎉 Analyse terminée avec succès!")
        print(f"📁 Visualisations disponibles dans: {args.output_dir}")
        
    except Exception as e:
        print(f"❌ Erreur durant l'analyse: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()