# Monitoring TradeSim - Prometheus/Grafana CLI
=============================================

Ce dossier contient l'infrastructure de monitoring pour TradeSim en mode CLI.

## 📁 Structure

```
monitoring/
├── README.md                    # Cette documentation
├── prometheus_exporter.py       # Exporter Prometheus (à créer)
├── docker-compose.yml          # Stack Docker (à créer)
├── prometheus.yml              # Configuration Prometheus (à créer)
└── grafana/                    # Dashboards Grafana (à créer)
    └── dashboards/
```

## 🎯 Objectif

Fournir un monitoring temps réel de TradeSim avec :
- **Prometheus** : Collecte et stockage des métriques
- **Grafana** : Visualisation et dashboards
- **Exporter Python** : Exposition des métriques depuis l'application

## 🔧 Architecture

### Processus séparé (recommandé)
- L'exporter Prometheus tourne en parallèle de la simulation CLI
- Avantages : Isolation, monitoring de l'app ET de Prometheus, redémarrage indépendant
- Activation/désactivation sans affecter la simulation

### Métriques de test (Phase 1)
- `budget_total` (Gauge) - Budget total des entreprises
- `transactions_total` (Counter) - Nombre total de transactions
- `produits_actifs` (Gauge) - Nombre de produits actifs
- `tours_completes` (Counter) - Nombre de tours effectués
- `temps_simulation_tour_seconds` (Histogram) - Durée d'un tour
- Métriques système (CPU/mémoire)

### Configuration
- Ports : Exporter 8000, Prometheus 9090, Grafana 3000
- Fréquence : Configurable via `config/config.py`
- Labels : Phase 1 désactivés, Phase 2 activés

## 🚀 Utilisation

### Démarrage rapide
```bash
# 1. Démarrer la stack monitoring
docker-compose up -d

# 2. Lancer la simulation avec monitoring
python services/simulate.py --tours 10 --with-metrics

# 3. Accéder aux interfaces
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
```

### Validation
```bash
# Tester l'exporter
curl localhost:8000/metrics

# Vérifier les métriques
curl localhost:9090/api/v1/query?query=budget_total
```

## 📊 Métriques disponibles

### Métriques métier
- **Budgets** : Total, moyen, min/max, entreprises solvables
- **Transactions** : Nombre total, réussies/échouées, montants
- **Produits** : Actifs/inactifs, types, prix
- **Simulation** : Tours, temps, événements

### Métriques système
- **CPU** : Utilisation processeur
- **Mémoire** : Utilisation RAM
- **Performance** : Latence, débit

## 🔄 Transition CLI → Web

### Réutilisation
- L'exporter sera réutilisé comme sidecar ou middleware FastAPI
- Configuration Prometheus/Grafana identique
- Seules les cibles changent (URLs/services)

### Kubernetes
- Déploiement en pods séparés
- ServiceMonitor pour Prometheus Operator
- Volumes persistants pour configs/dashboards

## 🛠️ Développement

### Ajouter une métrique
1. Définir la métrique dans `prometheus_exporter.py`
2. L'exposer via l'endpoint `/metrics`
3. Tester avec `curl localhost:8000/metrics`
4. Ajouter au dashboard Grafana

### Tests
- Tests unitaires pour l'exporter
- Tests d'intégration (simulation + monitoring)
- Tests de performance (impact sur simulation)

## 📝 Notes

- **Phase 1** : Métriques de base sans labels
- **Phase 2** : Ajout de labels `{continent}`, `{produit_type}`
- **Volumes** : Commencer sans, ajouter après que ça marche
- **Packaging** : Inclus dans `create_package.sh`

---

**Auteur :** Assistant IA  
**Date :** 2025-08-04  
**Version :** 1.0 - Architecture monitoring 