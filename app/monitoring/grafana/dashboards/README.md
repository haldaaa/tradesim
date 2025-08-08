# Dashboards Grafana pour TradeSim
==================================

Ce dossier contient les dashboards Grafana pour visualiser les métriques TradeSim.

## 📁 Structure

```
grafana/dashboards/
├── README.md                    # Cette documentation
├── tradesim-overview.json      # Dashboard principal (à créer)
├── tradesim-budgets.json       # Dashboard budgets (à créer)
├── tradesim-transactions.json  # Dashboard transactions (à créer)
└── tradesim-system.json        # Dashboard système (à créer)
```

## 🎯 Dashboards prévus

### 1. TradeSim Overview
- **Fichier**: `tradesim-overview.json`
- **Description**: Vue d'ensemble de la simulation
- **Métriques**: Budgets totaux, transactions, tours, temps de simulation

### 2. TradeSim Budgets
- **Fichier**: `tradesim-budgets.json`
- **Description**: Analyse détaillée des budgets
- **Métriques**: Budget par entreprise, évolution temporelle

### 3. TradeSim Transactions
- **Fichier**: `tradesim-transactions.json`
- **Description**: Analyse des transactions
- **Métriques**: Volume de transactions, types de produits

### 4. TradeSim System
- **Fichier**: `tradesim-system.json`
- **Description**: Métriques système
- **Métriques**: CPU, mémoire, disque, uptime

## 🔧 Import des dashboards

1. Démarrer Grafana: `docker-compose up grafana`
2. Ouvrir http://localhost:3000
3. Login: admin/admin
4. Aller dans Dashboards > Import
5. Importer chaque fichier JSON

## 📊 Métriques disponibles

### Métriques TradeSim
- `tradesim_budget_total` (Gauge)
- `tradesim_transactions_total` (Counter)
- `tradesim_produits_actifs` (Gauge)
- `tradesim_tours_completes` (Counter)
- `tradesim_temps_simulation_tour_seconds` (Histogram)

### Métriques Système
- `tradesim_cpu_usage_percent` (Gauge)
- `tradesim_memory_usage_bytes` (Gauge)
- `tradesim_memory_usage_percent` (Gauge)
- `tradesim_disk_usage_percent` (Gauge)
- `tradesim_process_uptime_seconds` (Gauge)

## 🚀 Prochaines étapes

1. Créer les dashboards JSON
2. Tester l'import dans Grafana
3. Optimiser les requêtes PromQL
4. Ajouter des alertes 