#!/usr/bin/env python3
"""
🌊📁 Kafka Weather Analytics - Exercice 7: Test Data Generator for HDFS
========================================================================

Générateur de données de test pour l'exercice 7, créant des données météorologiques
géolocalisées dans la structure HDFS pour tester les fonctionnalités de l'exercice 8.

Usage:
    python generate_test_data.py
    python generate_test_data.py --records 1000 --countries 5
"""

import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

# Configuration des données de test
COUNTRIES_DATA = {
    'FR': {
        'name': 'France',
        'cities': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg', 'Montpellier'],
        'temp_range': (5, 35),
        'wind_range': (2, 25)
    },
    'DE': {
        'name': 'Germany', 
        'cities': ['Berlin', 'Munich', 'Hamburg', 'Cologne', 'Frankfurt', 'Stuttgart', 'Dusseldorf'],
        'temp_range': (0, 30),
        'wind_range': (3, 20)
    },
    'US': {
        'name': 'United States',
        'cities': ['New-York', 'Los-Angeles', 'Chicago', 'Houston', 'Philadelphia', 'Phoenix', 'San-Antonio'],
        'temp_range': (-10, 45),
        'wind_range': (1, 35)
    },
    'GB': {
        'name': 'United Kingdom',
        'cities': ['London', 'Birmingham', 'Manchester', 'Glasgow', 'Liverpool', 'Leeds', 'Sheffield'],
        'temp_range': (2, 25),
        'wind_range': (5, 30)
    },
    'JP': {
        'name': 'Japan',
        'cities': ['Tokyo', 'Osaka', 'Yokohama', 'Nagoya', 'Sapporo', 'Kobe', 'Kyoto'],
        'temp_range': (-5, 40),
        'wind_range': (2, 25)
    }
}

WEATHER_CODES = [
    200, 201, 202, 210, 211, 212, 221, 230, 231, 232,  # Thunderstorm
    300, 301, 302, 310, 311, 312, 313, 314, 321,       # Drizzle
    500, 501, 502, 503, 504, 511, 520, 521, 522, 531,  # Rain
    600, 601, 602, 611, 612, 613, 615, 616, 620, 621, 622,  # Snow
    701, 711, 721, 731, 741, 751, 761, 762, 771, 781,  # Atmosphere
    800, 801, 802, 803, 804                            # Clear/Clouds
]

def calculate_alert_levels(temperature: float, windspeed: float) -> Tuple[int, int]:
    """Calcule les niveaux d'alerte basés sur température et vitesse du vent"""
    # Alerte vent
    if windspeed >= 20:
        wind_alert = 2
    elif windspeed >= 10:
        wind_alert = 1
    else:
        wind_alert = 0
    
    # Alerte chaleur
    if temperature >= 35:
        heat_alert = 2
    elif temperature >= 25:
        heat_alert = 1
    else:
        heat_alert = 0
    
    return wind_alert, heat_alert

def generate_weather_record(country_code: str, city: str, timestamp: datetime) -> Dict:
    """Génère un enregistrement météorologique"""
    country_info = COUNTRIES_DATA[country_code]
    
    # Génération des valeurs météo
    temp_min, temp_max = country_info['temp_range']
    wind_min, wind_max = country_info['wind_range']
    
    temperature = round(random.uniform(temp_min, temp_max), 1)
    windspeed = round(random.uniform(wind_min, wind_max), 1)
    weather_code = random.choice(WEATHER_CODES)
    
    # Calcul des alertes
    wind_alert_level, heat_alert_level = calculate_alert_levels(temperature, windspeed)
    
    # Construction de l'enregistrement
    record = {
        'timestamp': timestamp.isoformat(),
        'city': city,
        'country': country_info['name'],
        'temperature': temperature,
        'windspeed': windspeed,
        'weather_code': weather_code,
        'wind_alert_level': wind_alert_level,
        'heat_alert_level': heat_alert_level,
        'location': f"{city}, {country_info['name']}",
        'generated_at': datetime.utcnow().isoformat(),
        'source': 'test_data_generator'
    }
    
    return record

def generate_test_data(base_path: str, num_records: int, num_countries: int):
    """Génère les données de test dans la structure HDFS"""
    print(f"🌊📁 Génération de {num_records} enregistrements de test")
    print(f"📁 Chemin de base: {base_path}")
    
    base_dir = Path(base_path)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Sélection des pays
    selected_countries = list(COUNTRIES_DATA.keys())[:num_countries]
    print(f"🌍 Pays sélectionnés: {selected_countries}")
    
    # Génération des timestamps
    start_time = datetime.utcnow() - timedelta(days=7)
    
    records_generated = 0
    stats = {country: {city: 0 for city in COUNTRIES_DATA[country]['cities']} 
             for country in selected_countries}
    
    for i in range(num_records):
        # Sélection aléatoire pays/ville
        country_code = random.choice(selected_countries)
        city = random.choice(COUNTRIES_DATA[country_code]['cities'])
        
        # Timestamp aléatoire dans les 7 derniers jours
        random_offset = timedelta(
            days=random.randint(0, 6),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        timestamp = start_time + random_offset
        
        # Génération de l'enregistrement
        record = generate_weather_record(country_code, city, timestamp)
        
        # Création du chemin de fichier
        country_dir = base_dir / country_code
        city_dir = country_dir / city
        city_dir.mkdir(parents=True, exist_ok=True)
        
        alerts_file = city_dir / 'alerts.json'
        
        # Écriture en mode append (JSONL)
        with open(alerts_file, 'a', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, separators=(',', ':'))
            f.write('\n')
        
        records_generated += 1
        stats[country_code][city] += 1
        
        # Affichage du progrès
        if records_generated % (num_records // 10) == 0:
            progress = (records_generated / num_records) * 100
            print(f"📊 Progrès: {progress:.0f}% ({records_generated}/{num_records})")
    
    print(f"\n✅ Génération terminée: {records_generated} enregistrements")
    
    # Affichage des statistiques
    print("\n📊 Répartition par localisation:")
    total_cities = 0
    for country_code in selected_countries:
        country_total = sum(stats[country_code].values())
        active_cities = sum(1 for count in stats[country_code].values() if count > 0)
        total_cities += active_cities
        print(f"  🌍 {country_code}: {country_total} records, {active_cities} villes")
        
        for city, count in stats[country_code].items():
            if count > 0:
                print(f"    🏙️  {city}: {count} records")
    
    print(f"\n📈 Résumé:")
    print(f"  • Total records: {records_generated:,}")
    print(f"  • Pays: {len(selected_countries)}")
    print(f"  • Villes actives: {total_cities}")
    print(f"  • Période: 7 derniers jours")
    
    # Vérification de la structure créée
    print(f"\n🔍 Structure HDFS créée dans: {base_dir}")
    for country_dir in base_dir.iterdir():
        if country_dir.is_dir():
            city_count = len([d for d in country_dir.iterdir() if d.is_dir()])
            print(f"  📁 {country_dir.name}/: {city_count} villes")

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="🌊📁 Générateur de données de test pour l'exercice 7",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--path',
        type=str,
        default='./hdfs-data',
        help='Chemin de base pour les données HDFS (défaut: ./hdfs-data)'
    )
    
    parser.add_argument(
        '--records',
        type=int,
        default=500,
        help='Nombre d\'enregistrements à générer (défaut: 500)'
    )
    
    parser.add_argument(
        '--countries',
        type=int,
        default=5,
        choices=range(1, 6),
        help='Nombre de pays à inclure (1-5, défaut: 5)'
    )
    
    args = parser.parse_args()
    
    try:
        print("🌊📁 Kafka Weather Analytics - Exercice 7: Test Data Generator")
        print("=" * 70)
        
        generate_test_data(args.path, args.records, args.countries)
        
        print("\n🎊 Données de test générées avec succès!")
        print(f"💡 Vous pouvez maintenant tester l'exercice 8 avec: python weather_visualizer.py --input \"{args.path}\"")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())