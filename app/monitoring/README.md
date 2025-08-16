# 📊 MONITORING - TradeSim

## 🎯 **VUE D'ENSEMBLE**

Le dossier `monitoring/` contient tous les composants nécessaires au monitoring avancé de TradeSim, incluant l'export Prometheus, la configuration Grafana, et les métriques système.

## 🚀 **DÉMARRAGE RAPIDE**

### **1. Démarrage automatique (RECOMMANDÉ)**
```bash
# Démarrer le monitoring complet avec détection automatique
./monitoring/start_monitoring.sh
```

### **2. Démarrage manuel**
```bash
# Démarrer Prometheus et Grafana
docker-compose -f monitoring/docker-compose.yml up -d

# Démarrer l'exporteur Prometheus
python monitoring/prometheus_exporter.py &
```

### **3. Accès aux services**
- **Prometheus** : http://localhost:9090
- **Grafana** : http://localhost:3000 (admin/admin)
- **Exporteur** : http://localhost:8000

## 🔧 **CONFIGURATION MODULAIRE**

### **Détection automatique de la plateforme**
Le système détecte automatiquement votre plateforme et configure la connectivité Docker :
- **macOS/Windows** : `host.docker.internal`
- **Linux** : IP du bridge Docker ou localhost
- **Override** : `export TRADESIM_DOCKER_HOST=custom_host`

### **Scripts disponibles**
- `detect_docker_host.sh` : Détection automatique du host Docker
- `start_monitoring.sh` : Démarrage complet du monitoring

## 🏗️ **ARCHITECTURE DU MONITORING**

### **Composants Principaux**

#### **1. prometheus_exporter.py** 🚀
- **Rôle** : Exporteur Prometheus principal
- **Fonction** : Expose les métriques TradeSim au format Prometheus
- **Port** : 8000 (par défaut)
- **Endpoints** :
  - `/metrics` : Métriques Prometheus
  - `/health` : État de santé
  - `/` : Interface web simple

#### **2. docker-compose.yml** 🐳
- **Rôle** : Orchestration des services de monitoring
- **Services** :
  - Prometheus (port 9090)
  - Grafana (port 3000)
  - TradeSim Exporter (port 8000)

#### **3. prometheus.yml** ⚙️
- **Rôle** : Configuration Prometheus
- **Fonction** : Définit les cibles de scraping et les règles

#### **4. grafana/dashboards/** 📈
- **Rôle** : Dashboards Grafana préconfigurés
- **Fonction** : Visualisation des métriques TradeSim

## 📊 **MÉTRIQUES DISPONIBLES (100+)**

### **Métriques de Simulation (8)**
- `tradesim_tick_actuel` : Numéro du tick actuel
- `tradesim_evenements_appliques` : Événements appliqués
- `tradesim_duree_simulation_seconds` : Durée de simulation
- `tradesim_probabilite_selection_entreprise` : Probabilité de sélection
- `tradesim_duree_pause_entre_tours_seconds` : Pause entre tours
- `tradesim_tick_interval_event` : Intervalle événements
- `tradesim_probabilite_evenement` : Probabilité événements
- `tradesim_frequence_evenements` : Fréquence événements

### **Métriques de Latence (6)**
- `tradesim_latency_achat_produit_ms` : Latence achat produit
- `tradesim_latency_calcul_statistiques_ms` : Latence calcul stats
- `tradesim_latency_application_evenement_ms` : Latence événements
- `tradesim_latency_collecte_metriques_ms` : Latence collecte
- `tradesim_latency_validation_donnees_ms` : Latence validation
- `tradesim_latency_generation_id_ms` : Latence génération ID

### **Métriques de Budget (14)**
- `tradesim_budget_total_entreprises` : Budget total
- `tradesim_budget_moyen_entreprises` : Budget moyen
- `tradesim_budget_median_entreprises` : Budget médian
- `tradesim_budget_ecart_type_entreprises` : Écart-type budget
- `tradesim_budget_coefficient_variation` : Coefficient variation
- `tradesim_budget_variation_totale` : Variation totale
- `tradesim_budget_depenses_totales` : Dépenses totales
- `tradesim_budget_gains_totaux` : Gains totaux
- `tradesim_budget_sante_financiere` : Santé financière
- `tradesim_budget_ratio_depenses_revenus` : Ratio dépenses/revenus
- `tradesim_budget_efficacite_moyenne` : Efficacité moyenne
- `tradesim_budget_stabilite_moyenne` : Stabilité moyenne
- `tradesim_budget_alertes_critiques` : Alertes critiques

### **Métriques d'Entreprises (18)**
- `tradesim_entreprises_nombre_total` : Nombre total
- `tradesim_entreprises_repartition_pays` : Répartition pays
- `tradesim_entreprises_repartition_continent` : Répartition continent
- `tradesim_entreprises_strategies_repartition` : Répartition stratégies
- `tradesim_entreprises_transactions_total` : Transactions totales
- `tradesim_entreprises_budget_moyen` : Budget moyen
- `tradesim_entreprises_budget_ecart_type` : Écart-type budget
- `tradesim_entreprises_stock_moyen` : Stock moyen
- `tradesim_entreprises_efficacite_moyenne` : Efficacité moyenne
- `tradesim_entreprises_frequence_transactions` : Fréquence transactions
- `tradesim_entreprises_preferences_types` : Préférences types
- `tradesim_entreprises_adaptation_strategie` : Adaptation stratégie
- `tradesim_entreprises_stabilite_budget` : Stabilité budget
- `tradesim_entreprises_alertes_critiques` : Alertes critiques

### **Métriques de Produits (16)**
- `tradesim_produits_nombre_total` : Nombre total
- `tradesim_produits_repartition_types` : Répartition types
- `tradesim_produits_prix_moyen` : Prix moyen
- `tradesim_produits_prix_ecart_type` : Écart-type prix
- `tradesim_produits_actifs_pourcentage` : Pourcentage actifs
- `tradesim_produits_demande_total` : Demande totale
- `tradesim_produits_offre_total` : Offre totale
- `tradesim_produits_rotation_moyenne` : Rotation moyenne
- `tradesim_produits_disponibilite_moyenne` : Disponibilité moyenne
- `tradesim_produits_volatilite_prix` : Volatilité prix
- `tradesim_produits_tendance_prix` : Tendance prix
- `tradesim_produits_elasticite_demande` : Élasticité demande
- `tradesim_produits_stabilite_prix` : Stabilité prix
- `tradesim_produits_alertes_critiques` : Alertes critiques

### **Métriques de Fournisseurs (16)**
- `tradesim_fournisseurs_nombre_total` : Nombre total
- `tradesim_fournisseurs_repartition_pays` : Répartition pays
- `tradesim_fournisseurs_repartition_continent` : Répartition continent
- `tradesim_fournisseurs_stock_total` : Stock total
- `tradesim_fournisseurs_produits_moyen` : Produits moyen
- `tradesim_fournisseurs_ventes_total` : Ventes totales
- `tradesim_fournisseurs_rotation_moyenne` : Rotation moyenne
- `tradesim_fournisseurs_disponibilite_moyenne` : Disponibilité moyenne
- `tradesim_fournisseurs_efficacite_moyenne` : Efficacité moyenne
- `tradesim_fournisseurs_volatilite_ventes` : Volatilité ventes
- `tradesim_fournisseurs_tendance_ventes` : Tendance ventes
- `tradesim_fournisseurs_competitivite_moyenne` : Compétitivité moyenne
- `tradesim_fournisseurs_stabilite_stock` : Stabilité stock
- `tradesim_fournisseurs_alertes_critiques` : Alertes critiques

### **Métriques de Transactions (16)**
- `tradesim_transactions_nombre_total` : Nombre total
- `tradesim_transactions_reussies` : Transactions réussies
- `tradesim_transactions_echouees` : Transactions échouées
- `tradesim_transactions_taux_reussite` : Taux de réussite
- `tradesim_transactions_repartition_types` : Répartition types
- `tradesim_transactions_volume_total` : Volume total
- `tradesim_transactions_prix_moyen` : Prix moyen
- `tradesim_transactions_efficacite_moyenne` : Efficacité moyenne
- `tradesim_transactions_latence_moyenne` : Latence moyenne
- `tradesim_transactions_debit_moyen` : Débit moyen
- `tradesim_transactions_volatilite_prix` : Volatilité prix
- `tradesim_transactions_tendance_prix` : Tendance prix
- `tradesim_transactions_competitivite_moyenne` : Compétitivité moyenne
- `tradesim_transactions_stabilite_prix` : Stabilité prix
- `tradesim_transactions_alertes_critiques` : Alertes critiques

### **Métriques d'Événements (16)**
- `tradesim_evenements_nombre_total` : Nombre total
- `tradesim_evenements_appliques` : Événements appliqués
- `tradesim_evenements_frequence_moyenne` : Fréquence moyenne
- `tradesim_evenements_repartition_types` : Répartition types
- `tradesim_evenements_types_actifs` : Types actifs
- `tradesim_evenements_impact_moyen` : Impact moyen
- `tradesim_evenements_efficacite_moyenne` : Efficacité moyenne
- `tradesim_evenements_stabilite_moyenne` : Stabilité moyenne
- `tradesim_evenements_latence_moyenne` : Latence moyenne
- `tradesim_evenements_debit_moyen` : Débit moyen
- `tradesim_evenements_volatilite_impact` : Volatilité impact
- `tradesim_evenements_tendance_impact` : Tendance impact
- `tradesim_evenements_correlation_types` : Corrélation types
- `tradesim_evenements_previsibilite` : Prévisibilité
- `tradesim_evenements_alertes_critiques` : Alertes critiques

### **Métriques de Performance (16)**
- `tradesim_performance_temps_execution` : Temps d'exécution
- `tradesim_performance_memoire_utilisee` : Mémoire utilisée
- `tradesim_performance_cpu_utilisation` : Utilisation CPU
- `tradesim_performance_processus_actifs` : Processus actifs
- `tradesim_performance_efficacite_moyenne` : Efficacité moyenne
- `tradesim_performance_optimisation_moyenne` : Optimisation moyenne
- `tradesim_performance_charge_moyenne` : Charge moyenne
- `tradesim_performance_debit_moyen` : Débit moyen
- `tradesim_performance_latence_moyenne` : Latence moyenne
- `tradesim_performance_utilisation_moyenne` : Utilisation moyenne
- `tradesim_performance_volatilite_temps` : Volatilité temps
- `tradesim_performance_tendance_temps` : Tendance temps
- `tradesim_performance_bottlenecks_identifies` : Bottlenecks identifiés
- `tradesim_performance_stabilite_moyenne` : Stabilité moyenne
- `tradesim_performance_alertes_critiques` : Alertes critiques

### **Métriques Système (10)**
- `tradesim_system_cpu_usage_percent` : Utilisation CPU système
- `tradesim_system_memory_usage_percent` : Utilisation mémoire système
- `tradesim_system_disk_usage_percent` : Utilisation disque système
- `tradesim_system_network_bytes_sent` : Octets réseau envoyés
- `tradesim_system_network_bytes_recv` : Octets réseau reçus
- `tradesim_system_process_count` : Nombre de processus
- `tradesim_system_thread_count` : Nombre de threads
- `tradesim_system_open_files` : Fichiers ouverts
- `tradesim_system_load_average` : Charge moyenne système
- `tradesim_system_uptime_seconds` : Temps de fonctionnement

## 🚀 **UTILISATION**

### **Démarrage du Monitoring**

#### **1. Mode CLI avec Monitoring**
```bash
python services/simulate.py --tours 10 --with-metrics
```

#### **2. Mode Web avec Monitoring**
```bash
python api/main.py --with-metrics
```

#### **3. Monitoring Standalone**
```bash
python monitoring/prometheus_exporter.py
```

### **Accès aux Métriques**

#### **1. Endpoint Prometheus**
```
http://localhost:8000/metrics
```

#### **2. État de Santé**
```
http://localhost:8000/health
```

#### **3. Interface Web**
```
http://localhost:8000/
```

### **Prometheus + Grafana**

#### **1. Démarrage avec Docker**
```bash
cd monitoring/
docker-compose up -d
```

#### **2. Accès Prometheus**
```
http://localhost:9090
```

#### **3. Accès Grafana**
```
http://localhost:3000
```

## ⚙️ **CONFIGURATION**

### **Variables d'Environnement**

```bash
# Activation du monitoring
METRICS_ENABLED=true

# Configuration de l'exporteur
METRICS_EXPORTER_PORT=8000
METRICS_EXPORTER_HOST=0.0.0.0

# Intervalles de collecte
METRICS_COLLECTION_INTERVAL=5
METRICS_SYSTEM_INTERVAL=10

# Activation des métriques système
METRICS_SYSTEM_ENABLED=true
```

### **Fichiers de Configuration**

#### **prometheus.yml**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'tradesim'
    static_configs:
      - targets: ['localhost:8000']
```

#### **docker-compose.yml**
```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 📈 **DASHBOARDS GRAFANA**

### **Dashboards Disponibles**

#### **1. Dashboard Principal TradeSim**
- Vue d'ensemble complète
- Métriques de simulation en temps réel
- Graphiques de performance

#### **2. Dashboard Budget**
- Évolution des budgets
- Santé financière
- Alertes critiques

#### **3. Dashboard Transactions**
- Volume de transactions
- Taux de réussite
- Latence des opérations

#### **4. Dashboard Performance**
- Utilisation système
- Temps d'exécution
- Bottlenecks identifiés

## 🔧 **MAINTENANCE**

### **Logs de Monitoring**

#### **Fichiers de Logs**
- `logs/monitoring.log` : Logs du monitoring
- `logs/metrics.jsonl` : Métriques en JSONL
- `logs/event.log` : Événements de monitoring

#### **Rotation des Logs**
```bash
# Rotation automatique configurée
# Taille max : 100MB
# Rétention : 30 jours
```

### **Nettoyage**

#### **Cache et Historique**
```bash
# Réinitialisation des métriques
python -c "from services.simulation_service import SimulationService; s = SimulationService(); s.reset()"
```

#### **Logs Anciens**
```bash
# Suppression des logs de plus de 30 jours
find logs/ -name "*.log" -mtime +30 -delete
```

## 🐛 **DÉPANNAGE**

### **Problèmes Courants**

#### **1. Port 8000 Occupé**
```bash
# Vérifier le processus
lsof -i :8000

# Tuer le processus
kill -9 <PID>
```

#### **2. Métriques à Zéro**
```bash
# Vérifier l'activation du monitoring
echo $METRICS_ENABLED

# Redémarrer avec monitoring
python services/simulate.py --tours 1 --with-metrics --verbose
```

#### **3. Prometheus Ne Scrape Pas**
```bash
# Vérifier la configuration
curl http://localhost:8000/metrics

# Vérifier Prometheus
curl http://localhost:9090/api/v1/targets
```

### **Logs de Débogage**

#### **Activation du Debug**
```bash
export DEBUG_METRICS=true
python services/simulate.py --tours 1 --with-metrics
```

#### **Vérification des Métriques**
```bash
# Métriques en temps réel
watch -n 1 'curl -s http://localhost:8000/metrics | grep tradesim_'

# État de santé
curl http://localhost:8000/health
```

## 📚 **RESSOURCES**

### **Documentation**
- [GUIDE_MONITORING_CLI.md](../GUIDE_MONITORING_CLI.md) : Guide complet du monitoring CLI
- [METRIQUES_DISPONIBLES.md](../METRIQUES_DISPONIBLES.md) : Liste détaillée des métriques

### **Outils**
- [Prometheus](https://prometheus.io/) : Système de monitoring
- [Grafana](https://grafana.com/) : Visualisation de données
- [psutil](https://pypi.org/project/psutil/) : Métriques système Python

### **Support**
- Logs : `logs/monitoring.log`
- Métriques : `logs/metrics.jsonl`
- Configuration : `config/config.py`

---

**Auteur** : Assistant IA  
**Date** : 2025-08-10  
**Version** : 1.0.0 