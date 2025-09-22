# 🐳 CONTAINERISATION - Kafka Weather Analytics

## 📦 Images Docker Disponibles

### 1️⃣ **Producer Image (Geo Weather)**
```dockerfile
FROM python:3.9-slim

LABEL maintainer="Kafka Weather Analytics Team"
LABEL version="1.0.0"
LABEL description="Geo-enabled weather data producer for Kafka"

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY exercices/exercice6/ .

# Variables d'environnement
ENV KAFKA_BOOTSTRAP_SERVERS=localhost:9092
ENV OPEN_METEO_API_TIMEOUT=30
ENV PYTHONUNBUFFERED=1

# Santé du container
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://api.open-meteo.com')" || exit 1

# Utilisateur non-root pour sécurité
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

EXPOSE 8080

ENTRYPOINT ["python", "geo_weather.py"]
CMD ["--help"]
```

### 2️⃣ **Consumer Image (HDFS Consumer)**
```dockerfile
FROM python:3.9-slim

LABEL maintainer="Kafka Weather Analytics Team"
LABEL version="1.0.0"
LABEL description="HDFS consumer for geographical weather data"

WORKDIR /app

# Installation Java pour HDFS
RUN apt-get update && apt-get install -y \
    openjdk-11-jre-headless \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Variables d'environnement Java
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Installation dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installation dépendances HDFS
RUN pip install hdfs3 pyarrow

# Copie du code source
COPY exercices/exercice7/ .

# Configuration
ENV KAFKA_BOOTSTRAP_SERVERS=localhost:9092
ENV HDFS_URL=hdfs://localhost:9000
ENV PYTHONUNBUFFERED=1

# Santé du container
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from kafka import KafkaConsumer; KafkaConsumer(bootstrap_servers=['${KAFKA_BOOTSTRAP_SERVERS}'])" || exit 1

# Volume pour données HDFS
VOLUME ["/data"]

RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

ENTRYPOINT ["python", "hdfs_consumer.py"]
CMD ["--help"]
```

### 3️⃣ **Visualizer Image (Analytics & BI)**
```dockerfile
FROM python:3.9-slim

LABEL maintainer="Kafka Weather Analytics Team"
LABEL version="1.0.0"
LABEL description="Weather data visualization and BI dashboard"

WORKDIR /app

# Installation des dépendances système pour matplotlib
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installation dépendances visualisation
RUN pip install plotly dash streamlit

# Copie du code source
COPY exercices/exercice8/ .

# Configuration
ENV PYTHONUNBUFFERED=1
ENV MPLBACKEND=Agg

# Port pour dashboard web
EXPOSE 8501

# Santé du container
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/health || exit 1

# Volume pour visualisations
VOLUME ["/output"]

RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

ENTRYPOINT ["python", "weather_visualizer.py"]
CMD ["--help"]
```

## 🔧 Docker Compose - Environnement Complet

### **docker-compose.yml**
```yaml
version: '3.8'

services:
  # ==================== INFRASTRUCTURE ====================
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    hostname: zookeeper
    container_name: kafka-weather-zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
      - zookeeper-logs:/var/lib/zookeeper/log
    networks:
      - kafka-weather-network

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    hostname: kafka
    container_name: kafka-weather-broker
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_JMX_PORT: 9101
      KAFKA_JMX_HOSTNAME: localhost
    ports:
      - "9092:9092"
      - "9101:9101"
    volumes:
      - kafka-data:/var/lib/kafka/data
    networks:
      - kafka-weather-network

  # ==================== APPLICATION ====================
  geo-weather-producer:
    build:
      context: .
      dockerfile: docker/Dockerfile.producer
    container_name: kafka-weather-producer
    depends_on:
      - kafka
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:29092
      OPEN_METEO_API_TIMEOUT: 30
      PRODUCER_INTERVAL: 60
    command: ["Paris", "France", "--interval", "60"]
    restart: unless-stopped
    networks:
      - kafka-weather-network

  hdfs-consumer:
    build:
      context: .
      dockerfile: docker/Dockerfile.consumer
    container_name: kafka-weather-consumer
    depends_on:
      - kafka
      - geo-weather-producer
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:29092
      HDFS_BASE_PATH: /data/weather
    volumes:
      - weather-data:/data
    command: ["--hdfs-path", "/data/weather", "--topics", "geo_weather_stream"]
    restart: unless-stopped
    networks:
      - kafka-weather-network

  weather-visualizer:
    build:
      context: .
      dockerfile: docker/Dockerfile.visualizer
    container_name: kafka-weather-visualizer
    depends_on:
      - hdfs-consumer
    environment:
      DATA_INPUT_PATH: /data/weather
      OUTPUT_PATH: /output
    volumes:
      - weather-data:/data:ro
      - visualizations:/output
    ports:
      - "8501:8501"
    command: ["--input", "/data/weather", "--output", "/output", "--web"]
    restart: unless-stopped
    networks:
      - kafka-weather-network

  # ==================== MONITORING ====================
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-weather-ui
    depends_on:
      - kafka
    environment:
      KAFKA_CLUSTERS_0_NAME: kafka-weather-cluster
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:29092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
    ports:
      - "8080:8080"
    networks:
      - kafka-weather-network

  prometheus:
    image: prom/prometheus:latest
    container_name: kafka-weather-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - kafka-weather-network

  grafana:
    image: grafana/grafana:latest
    container_name: kafka-weather-grafana
    depends_on:
      - prometheus
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin123
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana-dashboards:/etc/grafana/provisioning/dashboards
    networks:
      - kafka-weather-network

# ==================== VOLUMES ====================
volumes:
  zookeeper-data:
    driver: local
  zookeeper-logs:
    driver: local
  kafka-data:
    driver: local
  weather-data:
    driver: local
  visualizations:
    driver: local
  prometheus-data:
    driver: local
  grafana-data:
    driver: local

# ==================== NETWORKS ====================
networks:
  kafka-weather-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 🚀 Scripts de Déploiement

### **deploy.sh**
```bash
#!/bin/bash
# 🚀 Script de déploiement Docker - Kafka Weather Analytics

set -e

# Configuration
PROJECT_NAME="kafka-weather-analytics"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Fonction de vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    log_success "Prérequis validés"
}

# Fonction de build des images
build_images() {
    log_info "Construction des images Docker..."
    
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    log_success "Images construites avec succès"
}

# Fonction de déploiement
deploy() {
    log_info "Déploiement de l'environnement..."
    
    # Arrêter les services existants
    docker-compose -f $COMPOSE_FILE down -v
    
    # Démarrer les services
    docker-compose -f $COMPOSE_FILE up -d
    
    log_success "Déploiement terminé"
}

# Fonction de test des services
test_services() {
    log_info "Test des services déployés..."
    
    # Attendre que Kafka soit prêt
    log_info "Attente de Kafka..."
    sleep 30
    
    # Test de connectivité Kafka
    if docker exec kafka-weather-broker kafka-topics --bootstrap-server localhost:9092 --list; then
        log_success "Kafka opérationnel"
    else
        log_error "Problème avec Kafka"
        return 1
    fi
    
    # Test du producer
    log_info "Test du producer..."
    if docker logs kafka-weather-producer | grep -q "Successfully sent"; then
        log_success "Producer opérationnel"
    else
        log_warning "Producer en cours de démarrage..."
    fi
    
    # Test des interfaces web
    log_info "Test des interfaces web..."
    
    if curl -f http://localhost:8080 &> /dev/null; then
        log_success "Kafka UI accessible sur http://localhost:8080"
    else
        log_warning "Kafka UI en cours de démarrage"
    fi
    
    if curl -f http://localhost:3000 &> /dev/null; then
        log_success "Grafana accessible sur http://localhost:3000"
    else
        log_warning "Grafana en cours de démarrage"
    fi
    
    if curl -f http://localhost:8501 &> /dev/null; then
        log_success "Dashboard visualisation accessible sur http://localhost:8501"
    else
        log_warning "Dashboard en cours de démarrage"
    fi
}

# Fonction d'affichage du statut
show_status() {
    log_info "Statut des services:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    log_info "URLs d'accès:"
    echo "  🌐 Kafka UI: http://localhost:8080"
    echo "  📊 Grafana: http://localhost:3000 (admin/admin123)"
    echo "  📈 Prometheus: http://localhost:9090"
    echo "  📋 Dashboard Visualisations: http://localhost:8501"
    
    echo ""
    log_info "Commandes utiles:"
    echo "  docker-compose logs [service]  # Voir les logs"
    echo "  docker-compose exec [service] bash  # Accéder au container"
    echo "  docker-compose down  # Arrêter tous les services"
}

# Menu principal
case "${1:-deploy}" in
    "check")
        check_prerequisites
        ;;
    "build")
        check_prerequisites
        build_images
        ;;
    "deploy")
        check_prerequisites
        build_images
        deploy
        test_services
        show_status
        ;;
    "test")
        test_services
        ;;
    "status")
        show_status
        ;;
    "stop")
        log_info "Arrêt des services..."
        docker-compose -f $COMPOSE_FILE down
        log_success "Services arrêtés"
        ;;
    "clean")
        log_info "Nettoyage complet..."
        docker-compose -f $COMPOSE_FILE down -v --rmi all
        docker system prune -f
        log_success "Nettoyage terminé"
        ;;
    *)
        echo "Usage: $0 {check|build|deploy|test|status|stop|clean}"
        echo ""
        echo "  check   - Vérifier les prérequis"
        echo "  build   - Construire les images Docker"
        echo "  deploy  - Déploiement complet (défaut)"
        echo "  test    - Tester les services"
        echo "  status  - Afficher le statut"
        echo "  stop    - Arrêter les services"
        echo "  clean   - Nettoyage complet"
        exit 1
        ;;
esac
```

### **deploy.ps1** (Version Windows)
```powershell
# 🚀 Script de déploiement Docker - Kafka Weather Analytics (Windows)

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("check", "build", "deploy", "test", "status", "stop", "clean")]
    [string]$Action = "deploy"
)

# Configuration
$ProjectName = "kafka-weather-analytics"
$ComposeFile = "docker-compose.yml"

# Fonctions utilitaires
function Write-ColoredOutput {
    param([string]$Message, [string]$Color = "White")
    
    $colorMap = @{
        "Red" = "Red"
        "Green" = "Green"
        "Yellow" = "Yellow"
        "Blue" = "Blue"
        "White" = "White"
    }
    
    Write-Host $Message -ForegroundColor $colorMap[$Color]
}

function Test-Prerequisites {
    Write-ColoredOutput "🔍 Vérification des prérequis..." "Blue"
    
    try {
        docker --version | Out-Null
        Write-ColoredOutput "✅ Docker installé" "Green"
    } catch {
        Write-ColoredOutput "❌ Docker n'est pas installé ou accessible" "Red"
        exit 1
    }
    
    try {
        docker-compose --version | Out-Null
        Write-ColoredOutput "✅ Docker Compose installé" "Green"
    } catch {
        Write-ColoredOutput "❌ Docker Compose n'est pas installé ou accessible" "Red"
        exit 1
    }
    
    Write-ColoredOutput "✅ Prérequis validés" "Green"
}

function Build-Images {
    Write-ColoredOutput "🏗️ Construction des images Docker..." "Blue"
    
    & docker-compose -f $ComposeFile build --no-cache
    if ($LASTEXITCODE -eq 0) {
        Write-ColoredOutput "✅ Images construites avec succès" "Green"
    } else {
        Write-ColoredOutput "❌ Erreur lors de la construction" "Red"
        exit 1
    }
}

function Deploy-Services {
    Write-ColoredOutput "🚀 Déploiement de l'environnement..." "Blue"
    
    # Arrêter les services existants
    & docker-compose -f $ComposeFile down -v
    
    # Démarrer les services
    & docker-compose -f $ComposeFile up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColoredOutput "✅ Déploiement terminé" "Green"
    } else {
        Write-ColoredOutput "❌ Erreur lors du déploiement" "Red"
        exit 1
    }
}

function Test-Services {
    Write-ColoredOutput "🧪 Test des services déployés..." "Blue"
    
    # Attendre que Kafka soit prêt
    Write-ColoredOutput "⏳ Attente de Kafka..." "Yellow"
    Start-Sleep -Seconds 30
    
    # Test de connectivité Kafka
    $kafkaTest = & docker exec kafka-weather-broker kafka-topics --bootstrap-server localhost:9092 --list 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-ColoredOutput "✅ Kafka opérationnel" "Green"
    } else {
        Write-ColoredOutput "❌ Problème avec Kafka" "Red"
    }
    
    # Test des interfaces web
    $urls = @{
        "Kafka UI" = "http://localhost:8080"
        "Grafana" = "http://localhost:3000"
        "Dashboard" = "http://localhost:8501"
        "Prometheus" = "http://localhost:9090"
    }
    
    foreach ($service in $urls.Keys) {
        try {
            $response = Invoke-WebRequest -Uri $urls[$service] -TimeoutSec 5 -UseBasicParsing
            Write-ColoredOutput "✅ $service accessible" "Green"
        } catch {
            Write-ColoredOutput "⚠️ $service en cours de démarrage" "Yellow"
        }
    }
}

function Show-Status {
    Write-ColoredOutput "`n📊 Statut des services:" "Blue"
    & docker-compose -f $ComposeFile ps
    
    Write-ColoredOutput "`n🌐 URLs d'accès:" "Blue"
    Write-ColoredOutput "  • Kafka UI: http://localhost:8080" "White"
    Write-ColoredOutput "  • Grafana: http://localhost:3000 (admin/admin123)" "White"
    Write-ColoredOutput "  • Prometheus: http://localhost:9090" "White"
    Write-ColoredOutput "  • Dashboard: http://localhost:8501" "White"
    
    Write-ColoredOutput "`n💡 Commandes utiles:" "Blue"
    Write-ColoredOutput "  docker-compose logs [service]" "White"
    Write-ColoredOutput "  docker-compose exec [service] bash" "White"
    Write-ColoredOutput "  docker-compose down" "White"
}

# Exécution selon l'action
switch ($Action) {
    "check" {
        Test-Prerequisites
    }
    "build" {
        Test-Prerequisites
        Build-Images
    }
    "deploy" {
        Test-Prerequisites
        Build-Images
        Deploy-Services
        Test-Services
        Show-Status
    }
    "test" {
        Test-Services
    }
    "status" {
        Show-Status
    }
    "stop" {
        Write-ColoredOutput "🛑 Arrêt des services..." "Yellow"
        & docker-compose -f $ComposeFile down
        Write-ColoredOutput "✅ Services arrêtés" "Green"
    }
    "clean" {
        Write-ColoredOutput "🧹 Nettoyage complet..." "Yellow"
        & docker-compose -f $ComposeFile down -v --rmi all
        & docker system prune -f
        Write-ColoredOutput "✅ Nettoyage terminé" "Green"
    }
}
```

## 📋 Instructions d'Utilisation

### **Déploiement Rapide**
```bash
# Linux/macOS
chmod +x deploy.sh
./deploy.sh deploy

# Windows PowerShell
.\deploy.ps1 -Action deploy
```

### **Commandes Docker Compose**
```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f geo-weather-producer

# Arrêter les services
docker-compose down

# Nettoyage complet
docker-compose down -v --rmi all
```

### **Accès aux Services**
- **Kafka UI**: http://localhost:8080
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Dashboard Visualisations**: http://localhost:8501

🐳 **L'environnement Docker est maintenant prêt pour le développement et la production !**