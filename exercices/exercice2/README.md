# Exercice 2 - Consommateur Kafka en Python

## 🎯 Objectif
Créer un script Python consommateur qui lit les messages depuis un topic Kafka passé en argument et affiche les messages reçus en temps réel.

## 📋 Spécifications
- **Langage:** Python
- **Paramètre d'entrée:** Nom du topic Kafka
- **Fonctionnalité:** Affichage des messages en temps réel
- **Topic de test:** `weather_stream` (créé dans l'exercice 1)

## 🛠️ Prérequis
```bash
pip install kafka-python
```

## 📁 Structure attendue
```
exercices/exercice2/
├── consumer.py              # Script principal du consommateur
├── requirements.txt         # Dépendances Python
├── README.md               # Ce fichier
└── test_consumer.py        # Script de test
```

## 🚀 Usage attendu
```bash
python consumer.py weather_stream
python consumer.py <topic_name>
```

## ✅ Critères de validation
- [ ] Script accepte le nom du topic en argument
- [ ] Connexion réussie à Kafka (localhost:9092)
- [ ] Affichage des messages en temps réel
- [ ] Gestion gracieuse des erreurs
- [ ] Code bien documenté

## 🧪 Test
```bash
# Terminal 1: Démarrer le consommateur
python consumer.py weather_stream

# Terminal 2: Envoyer un message test
echo '{"test": "message from exercice2"}' | java -cp "libs/*" kafka.tools.ConsoleProducer --topic weather_stream --bootstrap-server localhost:9092
```

---

**Status:** 🔄 TODO  
**Branche:** exercice2