# Exercice 1 - Mise en place de Kafka et d'un producteur simple

## ✅ EXERCICE TERMINÉ AVEC SUCCÈS

### 🎯 Objectifs
- [x] Créer un topic Kafka nommé `weather_stream`
- [x] Envoyer un message statique : `{"msg": "Hello Kafka"}`

### 🔧 Configuration réalisée

#### 1. Installation et configuration Kafka
- **Mode utilisé:** KRaft (sans ZooKeeper)
- **Version:** Apache Kafka 2.13-3.9.1
- **Port:** 9092
- **Cluster ID:** 7HB1jQrgR1iR37Aol7uu5Q

#### 2. Topic créé
```bash
Topic: weather_stream
├── Partitions: 1
├── Facteur de réplication: 1
├── ID du topic: jBJlog8kQRaGmHJLXZ1Mhw
└── Status: ACTIF
```

#### 3. Emplacement physique des données
```
C:\tmp\kraft-combined-logs\weather_stream-0\
├── 00000000000000000000.log      # Messages stockés ici
├── 00000000000000000000.index    # Index des messages
├── 00000000000000000000.timeindex
├── leader-epoch-checkpoint
└── partition.metadata
```

### 📝 Commandes utilisées

#### Démarrage de Kafka
```powershell
& "C:\Big_data\kafka\start-kafka-simple.ps1"
```

#### Création du topic
```bash
java -cp "libs/*" org.apache.kafka.tools.TopicCommand --create --topic weather_stream --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

#### Envoi du message
```bash
echo '{"msg": "Hello Kafka"}' | java -cp "libs/*" kafka.tools.ConsoleProducer --topic weather_stream --bootstrap-server localhost:9092
```

#### Vérification du topic
```bash
java -cp "libs/*" org.apache.kafka.tools.TopicCommand --list --bootstrap-server localhost:9092
java -cp "libs/*" org.apache.kafka.tools.TopicCommand --describe --topic weather_stream --bootstrap-server localhost:9092
```

### 🧪 Tests réalisés

#### Messages envoyés avec succès :
1. `{"msg": "Hello Kafka"}`
2. `{"msg": "Hello Kafka", "timestamp": "2025-09-22 12:45:00"}`
3. `{"msg": "Test message 2", "weather": "sunny", "temp": 25}`
4. `{"msg": "Test message 3", "weather": "rainy", "temp": 18, "humidity": 85}`

### 📁 Fichiers créés pour cet exercice

#### Scripts principaux
- **`start-kafka-simple.ps1`** - Script optimisé pour démarrer Kafka
- **`test-interactif.ps1`** - Interface de test interactive

#### Scripts de configuration (corrigés)
- **`start-zookeeper.bat`** - Chemins corrigés
- **`start-kafka.bat`** - Chemins corrigés

#### Documentation
- **`README.md`** - Documentation complète du projet
- **`.gitignore`** - Configuration Git

### 🎉 Résultats

✅ **Environment Kafka** : Configuré et fonctionnel  
✅ **Topic weather_stream** : Créé et testé  
✅ **Messages** : Envoyés et stockés avec succès  
✅ **Producteur** : Fonctionnel  
✅ **Architecture** : Mode KRaft (moderne, sans ZooKeeper)  

### 🚀 Prêt pour l'exercice 2

L'exercice 1 est terminé avec succès. L'environment est maintenant prêt pour développer un consommateur Python dans l'exercice 2.

---

**Date de completion :** 22 septembre 2025  
**Durée :** ~2 heures (incluant débogage et optimisation)  
**Status :** ✅ TERMINÉ