# Exercice 3 - Streaming de données météo en direct

## 🎯 Objectif
Écrire un producteur `current_weather` qui interroge l'API Open-Meteo pour une latitude/longitude passée en argument et envoie les données reçues dans le topic Kafka `weather_stream`.

## 📋 Spécifications
- Script Python prenant latitude/longitude en arguments
- Interrogation de l'API Open-Meteo
- Envoi des données météo vers Kafka
- Support du streaming en temps réel
- Gestion des erreurs API et réseau

## 🛠️ Implementation

### Structure du projet
```
exercice3/
├── current_weather.py      # Producteur principal (✅ TERMINÉ)
├── requirements.txt        # Dépendances Python
├── test-weather.ps1        # Script de test
└── README.md              # Cette documentation
```

### Fonctionnalités implémentées

#### ✅ Producteur météo complet (`current_weather.py`)
- **Arguments latitude/longitude** obligatoires
- **API Open-Meteo** intégration complète
- **Données météo riches** (température, vent, humidité, pression, etc.)
- **Streaming temps réel** avec intervalle configurable
- **Clés Kafka** basées sur coordonnées
- **Gestion d'erreurs** robuste
- **Formatage JSON** structuré

#### API Open-Meteo - Données récupérées:
- **Température actuelle** et ressentie
- **Humidité relative**
- **Précipitations** (pluie, averses, neige)
- **Vitesse et direction du vent**
- **Rafales de vent**
- **Couverture nuageuse**
- **Pression atmosphérique**
- **Code météo** et statut jour/nuit
- **Informations géographiques** (timezone, élévation)

#### Options de ligne de commande:
```bash
python current_weather.py 48.8566 2.3522                    # Paris
python current_weather.py 45.764 4.8357 --interval 30       # Lyon, toutes les 30s
python current_weather.py 43.2965 5.3698 --count 5          # Marseille, 5 messages
python current_weather.py 48.8566 2.3522 --topic weather_live
python current_weather.py 48.8566 2.3522 --server localhost:9092
```

## 🚀 Tests et utilisation

### 1. Installation des dépendances
```powershell
pip install -r requirements.txt
```

### 2. Test rapide avec script automatisé
```powershell
.\test-weather.ps1
```

### 3. Test manuel

#### Terminal 1 - Démarrer le consommateur (exercice 2)
```powershell
cd ..\exercice2
python consumer.py weather_stream --from-beginning
```

#### Terminal 2 - Lancer le producteur météo
```powershell
# Paris - 3 messages toutes les 10 secondes
python current_weather.py 48.8566 2.3522 --interval 10 --count 3

# Lyon - mode continu toutes les 60 secondes
python current_weather.py 45.764 4.8357

# Marseille - 5 messages personnalisés
python current_weather.py 43.2965 5.3698 --interval 30 --count 5
```

### 4. Villes principales françaises

| Ville | Latitude | Longitude | Commande |
|-------|----------|-----------|----------|
| Paris | 48.8566 | 2.3522 | `python current_weather.py 48.8566 2.3522` |
| Lyon | 45.764 | 4.8357 | `python current_weather.py 45.764 4.8357` |
| Marseille | 43.2965 | 5.3698 | `python current_weather.py 43.2965 5.3698` |
| Nice | 43.7102 | 7.2620 | `python current_weather.py 43.7102 7.2620` |
| Toulouse | 43.6045 | 1.4440 | `python current_weather.py 43.6045 1.4440` |

## 📊 Format des données envoyées

Exemple de message JSON envoyé vers Kafka :

```json
{
  "timestamp": "2025-09-22T14:30:45.123456",
  "api_timestamp": "2025-09-22T14:30",
  "location": {
    "latitude": 48.8566,
    "longitude": 2.3522,
    "timezone": "Europe/Paris",
    "timezone_abbreviation": "CEST",
    "elevation": 42.0
  },
  "current_weather": {
    "temperature": 22.5,
    "temperature_unit": "°C",
    "apparent_temperature": 24.1,
    "humidity": 65,
    "humidity_unit": "%",
    "precipitation": 0.0,
    "precipitation_unit": "mm",
    "rain": 0.0,
    "showers": 0.0,
    "snowfall": 0.0,
    "weather_code": 3,
    "cloud_cover": 75,
    "cloud_cover_unit": "%",
    "pressure_msl": 1013.2,
    "pressure_unit": "hPa",
    "wind_speed": 12.5,
    "wind_speed_unit": "km/h",
    "wind_direction": 240,
    "wind_direction_unit": "°",
    "wind_gusts": 18.2,
    "is_day": true
  },
  "producer_info": {
    "source": "open-meteo-api",
    "producer_id": "current_weather",
    "version": "1.0"
  }
}
```

## 🔧 Architecture technique

### Classe `WeatherProducer`
- **Configuration Kafka** optimisée pour la fiabilité
- **Gestion des timeouts** et retry automatique
- **Sérialisation JSON** automatique
- **Clés de partitioning** basées sur coordonnées

### Intégration API Open-Meteo
- **Endpoint officiel** : `https://api.open-meteo.com/v1/forecast`
- **Paramètres riches** pour données météo complètes
- **Timezone automatique** selon les coordonnées
- **Gestion d'erreurs** HTTP et parsing

### Caractéristiques Kafka
- **Acknowledgment complet** (`acks='all'`)
- **Retry automatique** (3 tentatives)
- **Batching optimisé** pour performance
- **Compression** et buffering intelligent

## ✅ Validation de l'exercice

- [x] Script Python `current_weather` fonctionnel
- [x] Arguments latitude/longitude supportés
- [x] Intégration API Open-Meteo complète
- [x] Envoi vers topic `weather_stream`
- [x] Streaming temps réel avec intervalle
- [x] Gestion d'erreurs robuste
- [x] Format de données riche et structuré

## 📈 Tests effectués

### API Open-Meteo
1. **Connectivité** ✅ (timeout 10s)
2. **Parsing JSON** ✅ (données complètes)
3. **Gestion timezone** ✅ (automatique)
4. **Erreurs réseau** ✅ (retry et timeout)

### Production Kafka
1. **Messages envoyés** ✅ (confirmation d'offset)
2. **Clés de partition** ✅ (latitude,longitude)
3. **Sérialisation JSON** ✅ (UTF-8)
4. **Gestion erreurs** ✅ (retry et rollback)

### Données météo
1. **Paris** ✅ (48.8566, 2.3522)
2. **Lyon** ✅ (45.764, 4.8357)
3. **Marseille** ✅ (43.2965, 5.3698)
4. **Nice** ✅ (43.7102, 7.2620)

## 🌍 Cas d'usage avancés

### Monitoring météo multi-villes
```bash
# Terminal 1 - Paris
python current_weather.py 48.8566 2.3522 --interval 60

# Terminal 2 - Lyon  
python current_weather.py 45.764 4.8357 --interval 60

# Terminal 3 - Marseille
python current_weather.py 43.2965 5.3698 --interval 60
```

### Test de charge
```bash
# Envoi rapide pour tests
python current_weather.py 48.8566 2.3522 --interval 5 --count 20
```

### Topic personnalisé
```bash
# Topic spécialisé par région
python current_weather.py 48.8566 2.3522 --topic weather_paris
python current_weather.py 45.764 4.8357 --topic weather_lyon
```

---

**Status:** ✅ **EXERCICE 3 TERMINÉ AVEC SUCCÈS**  
**Date:** 22 septembre 2025  
**Prochaine étape:** Exercice 4 - Transformation Spark et alertes