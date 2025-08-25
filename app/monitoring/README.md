# Monitoring TradeSim
====================

Ce dossier contient tout le système de monitoring de TradeSim avec Prometheus et Grafana.

## 📁 Structure du dossier

```
monitoring/
├── README.md                           # Ce fichier
├── docker-compose.yml                  # Configuration Docker (Prometheus + Grafana)
├── prometheus.yml                      # Configuration Prometheus
├── start_monitoring.sh                 # Script de démarrage automatique
├── import_dashboards.py                # Script d'import des dashboards
├── configure_prometheus.py             # Configuration automatique Prometheus
├── prometheus_exporter.py              # Exporteur Prometheus Python
├── grafana/
│   ├── provisioning/
│   │   ├── dashboards/
│   │   │   ├── dashboard.yml           # Configuration provisioning
│   │   │   ├── 01_simulation_overview.json
│   │   │   ├── 02_finances_budgets.json
│   │   │   ├── 03_entreprises_strategies.json
│   │   │   ├── 04_produits_fournisseurs.json
│   │   │   ├── 05_evenements_metriques_avancees.json
│   │   │   ├── 06_produit_template.json
│   │   │   ├── 07_entreprise_template.json
│   │   │   └── 08_fournisseur_template.json
│   │   └── datasources/
│   │       └── prometheus.yml          # Source de données Prometheus
│   └── dashboards/                     # Dashboards utilisateur (optionnel)
└── logs/                               # Logs de monitoring (créé automatiquement)
```

## 🚀 Démarrage rapide

### **Méthode automatique (recommandée)**
```bash
./monitoring/start_monitoring.sh
```

### **Méthode manuelle**
```bash
# 1. Démarrer les services
cd monitoring
docker-compose up -d

# 2. Importer les dashboards
cd ..
python monitoring/import_dashboards.py
```

## 📊 Services disponibles

### **Prometheus** (http://localhost:9090)
- **Rôle** : Collecte et stockage des métriques
- **Configuration** : `prometheus.yml`
- **Targets** : Exporteur Python sur port 8000

### **Grafana** (http://localhost:3000)
- **Login** : `admin/admin`
- **Rôle** : Visualisation et dashboards
- **Source de données** : Prometheus configurée automatiquement

### **Exporteur Python** (http://localhost:8000)
- **Rôle** : Exposition des métriques TradeSim
- **Format** : Prometheus metrics
- **Démarrage** : Automatique avec la simulation

## 📈 Dashboards disponibles

### **Dashboards de base**
1. **TradeSim - Simulation Overview** : Vue d'ensemble générale
2. **TradeSim - Finances & Budgets** : Métriques financières
3. **TradeSim - Entreprises & Stratégies** : Performance des entreprises
4. **TradeSim - Produits & Fournisseurs** : Gestion des produits
5. **TradeSim - Événements & Métriques Avancées** : Événements système

### **Dashboards templates (avec variables)**
6. **TradeSim - Produit: $produit** : Métriques par produit spécifique
7. **TradeSim - Entreprise: $entreprise** : Métriques par entreprise spécifique
8. **TradeSim - Fournisseur: $fournisseur** : Métriques par fournisseur spécifique

## 🔧 Scripts disponibles

### **start_monitoring.sh**
Script de démarrage complet qui :
- Démarre Prometheus et Grafana
- Attend que Grafana soit prêt
- Importe automatiquement tous les dashboards
- Affiche les URLs d'accès

### **import_dashboards.py**
Script d'import des dashboards qui :
- Détecte automatiquement les fichiers JSON
- Importe via l'API REST Grafana
- Gère les erreurs et affiche le statut
- Ignore les fichiers de configuration

### **configure_prometheus.py**
Script de configuration Prometheus qui :
- Détecte automatiquement l'environnement (Mac/Windows/Linux)
- Configure le host Docker approprié
- Met à jour les targets automatiquement

## 📊 Métriques exposées

### **Métriques de base**
- `tradesim_budget_total_entreprises` - Budget total des entreprises
- `tradesim_tours_completes` - Tours de simulation
- `tradesim_evenements_total` - Événements totaux
- `tradesim_transactions_total` - Transactions totales
- `tradesim_produits_actifs` - Nombre de produits actifs
- `tradesim_entreprises_nombre_total` - Nombre d'entreprises
- `tradesim_fournisseurs_nombre_total` - Nombre de fournisseurs

### **Métriques avec labels**
- `tradesim_entreprise_budget{nom="VietnameseCorp"}` - Budget par entreprise
- `tradesim_produits_prix_moyen{produit="Ordinateur"}` - Prix moyen par produit
- `tradesim_transactions_reussies{type="achat"}` - Transactions réussies par type
- `tradesim_transactions_echouees{raison="budget_insuffisant"}` - Transactions échouées par raison

### **Métriques système**
- `tradesim_cpu_usage_percent` - Utilisation CPU
- `tradesim_memory_usage_percent` - Utilisation mémoire
- `tradesim_latency_average_ms` - Latence moyenne
- `tradesim_throughput_requests_per_second` - Throughput

## 🛠️ Configuration

### **Variables de configuration** (`config/config.py`)
```python
METRICS_ENABLED = True                 # Activer/désactiver le monitoring
METRICS_COLLECTION_INTERVAL = 1.0     # Intervalle de collecte (secondes)
METRICS_EXPORTER_PORT = 8000          # Port de l'exporteur
METRICS_PROMETHEUS_PORT = 9090        # Port de Prometheus
METRICS_GRAFANA_PORT = 3000           # Port de Grafana
```

### **Configuration Prometheus** (`prometheus.yml`)
```yaml
global:
  scrape_interval: 1s

scrape_configs:
  - job_name: 'tradesim'
    static_configs:
      - targets: ['host.docker.internal:8000']  # Configuré automatiquement
```

### **Configuration Grafana** (`grafana/provisioning/`)
- **Data sources** : Prometheus configuré automatiquement
- **Dashboards** : Import automatique via API REST
- **Variables** : Support des templates dynamiques

## 🔍 Dépannage

### **Problème : Docker daemon non démarré**
**Erreur :** `Cannot connect to the Docker daemon at unix:///Users/fares/.docker/run/docker.sock. Is the docker daemon running?`

**Solution :**
```bash
# 1. Lancer Docker Desktop depuis Applications
# 2. Attendre que l'icône Docker soit stable
# 3. Vérifier : docker --version
# 4. Relancer : docker-compose up -d
```

### **Problème : Aucune donnée dans Grafana**
**Symptôme :** Grafana accessible mais dashboards vides

**Diagnostic :**
```bash
# 1. Vérifier que l'exporter TradeSim fonctionne
curl http://localhost:8000/health
curl http://localhost:8000/metrics

# 2. Si non accessible, démarrer l'exporter :
cd monitoring
python prometheus_exporter.py

# 3. Ou lancer une simulation avec métriques :
python services/simulate.py --tours 20 --with-metrics
```

**Solution :** L'exporter TradeSim (port 8000) doit être démarré pour que Prometheus puisse collecter les métriques.

### **Problème : Dashboards ne s'affichent pas**
```bash
# Vérifier que Grafana est démarré
curl http://localhost:3000/api/health

# Réimporter les dashboards
python monitoring/import_dashboards.py
```

### **Problème : Métriques à zéro**
```bash
# Vérifier que l'exporteur fonctionne
curl http://localhost:8000/metrics

# Vérifier que Prometheus scrape l'exporteur
curl http://localhost:9090/api/v1/targets
```

### **Problème : Variables de dashboard ne fonctionnent pas**
1. Vérifier que les métriques existent : `curl http://localhost:8000/metrics | grep nom_metrique`
2. Relancer une simulation pour générer des données
3. Actualiser le dashboard dans Grafana

### **Problème : Ports déjà utilisés**
**Erreur :** `Address already in use`

**Solution :**
```bash
# 1. Identifier le processus
lsof -i :8000  # Pour l'exporter
lsof -i :9090  # Pour Prometheus
lsof -i :3000  # Pour Grafana

# 2. Tuer le processus
kill -9 <PID>

# 3. Relancer les services
docker-compose up -d
```

### **Problème : Métriques recharge_stock_fournisseur manquantes**
**Symptôme :** Les nouvelles métriques automatiques n'apparaissent pas

**Diagnostic :**
```bash
# 1. Vérifier que l'événement est intégré
grep -r 'recharge_stock_fournisseur' services/simulation_service.py

# 2. Vérifier que les métriques sont générées
curl http://localhost:8000/metrics | grep recharge_stock

# 3. Lancer une simulation avec l'événement
python services/simulate.py --tours 40 --with-metrics
```

**Solution :** L'événement doit être déclenché (tick multiple de 20) pour générer les métriques.

## 📝 Ajout de nouveaux dashboards

### **Via fichier JSON**
1. Créer un fichier JSON dans `grafana/provisioning/dashboards/`
2. Suivre la structure :
```json
{
  "dashboard": {
    "id": null,
    "title": "Mon Dashboard",
    "tags": ["tradesim"],
    "panels": [...]
  }
}
```
3. Relancer l'import : `python monitoring/import_dashboards.py`

### **Via interface Grafana**
1. Créer le dashboard dans l'interface
2. Exporter en JSON
3. Placer dans `grafana/provisioning/dashboards/`
4. Relancer l'import

## 🎯 Utilisation avancée

### **Requêtes PromQL personnalisées**
```promql
# Budget moyen par entreprise
avg(tradesim_entreprise_budget)

# Transactions par type
sum(tradesim_transactions_total) by (type)

# Évolution du budget dans le temps
tradesim_budget_total_entreprises[5m]
```

### **Variables de dashboard**
1. Settings → Variables
2. Ajouter une variable de type "Query"
3. Query : `label_values(tradesim_entreprise_budget, nom)`
4. Utiliser avec `$variable` dans les requêtes

### **Alertes Grafana**
1. Créer une alerte dans un panel
2. Condition : `tradesim_budget_total_entreprises < 1000`
3. Notification : Email, Slack, etc.

## 📚 Ressources

- [Guide Monitoring CLI](../GUIDE_MONITORING_CLI.md) - Guide complet d'utilisation
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Client Python](https://github.com/prometheus/client_python)

## 🔄 Maintenance

### **Mise à jour des dashboards**
```bash
# Réimporter tous les dashboards
python monitoring/import_dashboards.py
```

### **Redémarrage des services**
```bash
# Redémarrer tout
docker-compose restart

# Redémarrer un service spécifique
docker-compose restart grafana
```

### **Nettoyage des logs**
```bash
# Voir les logs
docker-compose logs -f

# Nettoyer les logs
docker-compose logs --tail=100
``` 