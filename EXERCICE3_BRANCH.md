# 🚀 Exercice 3 - Weather Data Streaming - Branch Dédiée

## 🎯 Bienvenue sur la branche `exercice3`

Cette branche contient **uniquement** le contenu de l'exercice 3 : Weather Data Streaming.

## 🌦️ Contenu de l'exercice 3

- `current_weather.py` - Producteur de données météorologiques en temps réel
- `requirements.txt` - Dépendances Python (requests)
- `test-weather.ps1` - Tests automatisés
- `README.md` - Documentation complète de l'exercice

## 🛠️ Fonctionnalités

- **API météo temps réel** avec OpenWeatherMap
- **Producer Kafka** pour streaming de données
- **Gestion d'erreurs** robuste
- **Configuration flexible** ville/pays
- **Mode continu** pour simulation temps réel

## 🚀 Démarrage rapide

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le producteur météo
python current_weather.py Paris France

# Mode continu
python current_weather.py Paris France --continuous
```

## 🌟 Navigation entre exercices

- **Exercice 1** - `git checkout exercice1` - Setup Kafka & Zookeeper
- **Exercice 2** - `git checkout exercice2` - Basic Producer/Consumer
- **Exercice 3** - `git checkout exercice3` - Weather Data Streaming (vous êtes ici)
- **Exercice 4** - `git checkout exercice4` - Multi-City Weather Networks
- **Exercice 5** - `git checkout exercice5` - Real-time Weather Alerts
- **Exercice 6** - `git checkout exercice6` - Geographic Weather Streaming
- **Exercice 7** - `git checkout exercice7` - HDFS Consumer & Storage
- **Exercice 8** - `git checkout exercice8` - BI Visualizations & Analytics

## 📚 Documentation complète

Consultez le [README principal](https://github.com/cardgis/kafka/blob/main/README.md) pour la vue d'ensemble du projet.

---
**🎯 Cette branche est dédiée exclusivement à l'exercice 3 : Weather Data Streaming.**