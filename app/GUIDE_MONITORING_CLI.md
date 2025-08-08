# Guide Monitoring CLI - TradeSim
================================

Ce guide explique comment utiliser le monitoring Prometheus/Grafana avec TradeSim en mode CLI.

## 🎯 Objectif

Fournir un monitoring temps réel de TradeSim avec :
- **Prometheus** : Collecte et stockage des métriques
- **Grafana** : Visualisation et dashboards
- **Exporter Python** : Exposition des métriques depuis l'application

## 🚀 Démarrage rapide

### 1. Démarrer le monitoring

```bash
# Démarrer Prometheus et Grafana
cd monitoring
docker-compose up -d

# Lancer la simulation avec monitoring
python services/simulate.py --tours 10 --with-metrics
```

### 2. Accéder aux interfaces

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Exporter**: http://localhost:8000

## ⚙️ Configuration

### Variables de configuration (`config/config.py`)

```python
# Activation du monitoring
METRICS_ENABLED = True                # Activer/désactiver le monitoring
METRICS_COLLECTION_INTERVAL = 1.0    # Intervalle de collecte en secondes

# Configuration de l'exporter Prometheus
METRICS_EXPORTER_PORT = 8000         # Port de l'exporter Prometheus
METRICS_EXPORTER_HOST = "0.0.0.0"    # Host de l'exporter

# Configuration Docker (Prometheus/Grafana)
METRICS_PROMETHEUS_PORT = 9090       # Port de Prometheus
METRICS_GRAFANA_PORT = 3000          # Port de Grafana

# Métriques système
METRICS_SYSTEM_ENABLED = True        # Activer les métriques système
METRICS_SYSTEM_INTERVAL = 5.0        # Intervalle collecte système (secondes)

# Labels (phase 2)
METRICS_LABELS_ENABLED = False       # Activer les labels
METRICS_LABELS_CONTINENT = True      # Label continent
METRICS_LABELS_PRODUIT_TYPE = True   # Label type de produit
```

## 📊 Métriques disponibles

### Métriques TradeSim (5 métriques de base)
- `tradesim_budget_total` (Gauge) - Budget total des entreprises
- `tradesim_transactions_total` (Counter) - Nombre total de transactions
- `tradesim_produits_actifs` (Gauge) - Nombre de produits actifs
- `tradesim_tours_completes` (Counter) - Nombre de tours effectués
- `tradesim_temps_simulation_tour_seconds` (Histogram) - Durée d'un tour

### Métriques Système
- `tradesim_cpu_usage_percent` (Gauge) - Utilisation CPU (%)
- `tradesim_memory_usage_bytes` (Gauge) - Utilisation mémoire (bytes)
- `tradesim_memory_usage_percent` (Gauge) - Utilisation mémoire (%)
- `tradesim_disk_usage_percent` (Gauge) - Utilisation disque (%)
- `tradesim_process_uptime_seconds` (Gauge) - Temps de fonctionnement

## 🔧 Utilisation

### Activer le monitoring

```bash
# Simulation avec monitoring
python services/simulate.py --tours 10 --with-metrics

# Simulation infinie avec monitoring
python services/simulate.py --infinite --with-metrics

# Mode verbose avec monitoring
python services/simulate.py --tours 5 --verbose --with-metrics
```

### Désactiver le monitoring

```python
# Dans config/config.py
METRICS_ENABLED = False
```

### Modifier l'intervalle de collecte

```python
# Dans config/config.py
METRICS_COLLECTION_INTERVAL = 2.0  # Collecte toutes les 2 secondes
```

## 📁 Fichiers de stockage

### Métriques JSONL
- **Fichier**: `logs/metrics.jsonl`
- **Format**: Une ligne JSON par collecte
- **Contenu**: Timestamp + métriques

### Logs de monitoring
- **Fichier**: `logs/event.log`
- **Contenu**: Événements de monitoring (démarrage, erreurs, etc.)

## 🐳 Docker

### Démarrer la stack
```bash
cd monitoring
docker-compose up -d
```

### Arrêter la stack
```bash
docker-compose down
```

### Voir les logs
```bash
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

### Redémarrer un service
```bash
docker-compose restart prometheus
docker-compose restart grafana
```

## 🔍 Debug et dépannage

### Vérifier l'exporter
```bash
# Test de l'endpoint métriques
curl http://localhost:8000/metrics

# Test de l'endpoint santé
curl http://localhost:8000/health
```

### Vérifier Prometheus
```bash
# Test de la configuration
curl http://localhost:9090/-/reload

# Voir les targets
curl http://localhost:9090/api/v1/targets
```

### Vérifier Grafana
```bash
# Test de l'API
curl http://localhost:3000/api/health
```

## 🚨 Problèmes courants

### Port déjà utilisé
```bash
# Vérifier les ports utilisés
lsof -i :8000
lsof -i :9090
lsof -i :3000

# Tuer le processus
kill -9 <PID>
```

### Exporter ne démarre pas
```bash
# Vérifier les dépendances
pip install -r requirements.txt

# Tester l'exporter seul
python monitoring/prometheus_exporter.py
```

### Prometheus ne scrape pas
```bash
# Vérifier la configuration
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml

# Redémarrer Prometheus
docker-compose restart prometheus
```

## 📈 Prochaines étapes

### Phase 2 - Labels
- Activer `METRICS_LABELS_ENABLED = True`
- Ajouter labels `continent` et `produit_type`
- Créer dashboards par continent/type

### Phase 3 - Alertes
- Configurer les règles d'alerte Prometheus
- Intégrer AlertManager
- Notifications Slack/Email

### Phase 4 - Volumes persistants
- Ajouter volumes pour les dashboards
- Persistance des configurations
- Sauvegarde automatique

## 📚 Ressources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Client Python](https://github.com/prometheus/client_python) 