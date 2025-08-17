# Guide Monitoring CLI - TradeSim
================================

Ce guide explique comment utiliser le monitoring Prometheus/Grafana avec TradeSim en mode CLI.

## 🎯 Objectif

Fournir un monitoring temps réel de TradeSim avec :
- **Prometheus** : Collecte et stockage des métriques
- **Grafana** : Visualisation et dashboards
- **Exporter Python** : Exposition des métriques depuis l'application
- **Import automatique** : Dashboards pré-configurés via API REST

## 🚀 Démarrage rapide

### 1. Démarrage automatique complet

```bash
# Démarrage complet avec import automatique des dashboards
./monitoring/start_monitoring.sh
```

**Ce script fait automatiquement :**
- Démarre Prometheus et Grafana
- Attend que Grafana soit prêt
- Importe automatiquement tous les dashboards
- Affiche les URLs d'accès

### 2. Démarrage manuel (ancienne méthode)

```bash
# Démarrer Prometheus et Grafana
cd monitoring
docker-compose up -d

# Importer les dashboards manuellement
cd ..
python monitoring/import_dashboards.py
```

### 3. Accéder aux interfaces

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Exporter**: http://localhost:8000

## 📊 Dashboards disponibles

### **Dashboards de base**
- **TradeSim - Simulation Overview** : Vue d'ensemble de la simulation
- **TradeSim - Finances & Budgets** : Métriques financières
- **TradeSim - Entreprises & Stratégies** : Performance des entreprises
- **TradeSim - Produits & Fournisseurs** : Gestion des produits
- **TradeSim - Événements & Métriques Avancées** : Événements système

### **Dashboards templates (avec variables)**
- **TradeSim - Produit: $produit** : Métriques par produit spécifique
- **TradeSim - Entreprise: $entreprise** : Métriques par entreprise spécifique
- **TradeSim - Fournisseur: $fournisseur** : Métriques par fournisseur spécifique

### **Utilisation des dashboards templates**
1. **Ouvrir** le dashboard template (ex: "TradeSim - Produit: $produit")
2. **Sélectionner** la variable en haut (ex: choisir "Ordinateur")
3. **Tous les panels** se mettent à jour automatiquement

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

# Configuration Latency & Throughput
LATENCY_COLLECTION_INTERVAL = 0.1    # Intervalle de collecte des latences (100ms)
LATENCY_HISTOGRAM_BUCKETS = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]  # Buckets pour histogrammes
LATENCY_HISTORY_SIZE = 1000          # Nombre de mesures à conserver en historique
THROUGHPUT_WINDOW_SIZE = 60          # Fenêtre de calcul du throughput (60 secondes)
THROUGHPUT_MIN_INTERVAL = 0.01       # Intervalle minimum entre mesures (10ms)

# Seuils de performance pour les alertes
LATENCY_WARNING_THRESHOLD = 100.0    # Seuil d'avertissement latence (100ms)
LATENCY_CRITICAL_THRESHOLD = 500.0   # Seuil critique latence (500ms)
```

## 🔧 Scripts disponibles

### **Script de démarrage automatique**
```bash
./monitoring/start_monitoring.sh
```
- Démarre tous les services
- Importe automatiquement les dashboards
- Affiche les URLs d'accès

### **Script d'import des dashboards**
```bash
python monitoring/import_dashboards.py
```
- Importe tous les dashboards JSON
- Gestion des erreurs automatique
- Affiche le statut de chaque import

### **Script de configuration Prometheus**
```bash
python monitoring/configure_prometheus.py
```
- Configure automatiquement Prometheus
- Détecte l'environnement (Mac/Windows/Linux)
- Met à jour les targets automatiquement

## 📈 Métriques principales disponibles

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

## 🛠️ Dépannage

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
1. **Vérifier** que les métriques existent : `curl http://localhost:8000/metrics | grep nom_metrique`
2. **Relancer** une simulation pour générer des données
3. **Actualiser** le dashboard dans Grafana

## 📝 Création de nouveaux dashboards

### **Via l'interface Grafana**
1. **"+"** → **"Dashboard"**
2. **"Add panel"**
3. **Query** : Utiliser les métriques TradeSim
4. **Sauvegarder** le dashboard

### **Via fichier JSON**
1. **Créer** un fichier JSON dans `monitoring/grafana/provisioning/dashboards/`
2. **Relancer** l'import : `python monitoring/import_dashboards.py`

### **Structure JSON d'un dashboard**
```json
{
  "dashboard": {
    "id": null,
    "title": "Mon Dashboard",
    "tags": ["tradesim"],
    "panels": [
      {
        "id": 1,
        "title": "Mon Panel",
        "type": "stat",
        "targets": [
          {
            "expr": "tradesim_transactions_total"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
      }
    ]
  }
}
```

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

### **Alertes Grafana**
1. **Créer** une alerte dans un panel
2. **Condition** : `tradesim_budget_total_entreprises < 1000`
3. **Notification** : Email, Slack, etc.

### **Variables de dashboard**
1. **Settings** → **Variables**
2. **Ajouter** une variable de type "Query"
3. **Query** : `label_values(tradesim_entreprise_budget, nom)`
4. **Utiliser** avec `$variable` dans les requêtes 