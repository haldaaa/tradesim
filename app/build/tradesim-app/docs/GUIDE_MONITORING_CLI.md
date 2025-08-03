# Guide de Monitoring CLI - TradeSim
====================================

## 📊 **Vue d'ensemble**

Ce guide explique comment utiliser les solutions de monitoring CLI pour TradeSim, incluant Prometheus, Rich Dashboard, et les métriques disponibles.

## 🎯 **Solutions de monitoring disponibles**

### **1. Prometheus Exporteur**
- **Fichier :** `monitoring/prometheus_exporter.py`
- **Fonction :** Exporte les métriques vers Prometheus
- **Port :** 8000 (par défaut)
- **URL :** http://localhost:8000/metrics

### **2. Dashboard CLI Rich**
- **Fichier :** `monitoring/cli_dashboard.py`
- **Fonction :** Interface CLI moderne avec métriques en temps réel
- **Technologie :** Rich (bibliothèque Python moderne)

### **3. Métriques disponibles**
- **Fichier :** `METRIQUES_DISPONIBLES.md`
- **Contenu :** Liste complète de toutes les métriques

## 🚀 **Démarrage rapide**

### **Option 1 : Dashboard CLI Rich (Recommandé)**
```bash
# Installer Rich si nécessaire
pip install rich

# Démarrer le dashboard
python monitoring/cli_dashboard.py
```

### **Option 2 : Prometheus Exporteur**
```bash
# Installer prometheus_client
pip install prometheus_client

# Démarrer l'exporteur
python monitoring/prometheus_exporter.py
```

### **Option 3 : Les deux ensemble**
```bash
# Terminal 1 - Prometheus Exporteur
python monitoring/prometheus_exporter.py

# Terminal 2 - Dashboard CLI
python monitoring/cli_dashboard.py
```

## 📈 **Métriques critiques**

### **Métriques de santé économique :**
1. **Budget total** - Indicateur principal de santé
2. **Entreprises solvables** - Stabilité du système
3. **Produits actifs** - Disponibilité des biens
4. **Transactions réussies** - Activité du marché

### **Métriques de performance :**
1. **Temps de simulation** - Performance du système
2. **Nombre de tours** - Progression de la simulation
3. **Événements appliqués** - Activité des événements

### **Métriques d'alerte :**
1. **Budget total < 1000€** - Système en difficulté
2. **Aucune transaction** - Marché stagnant
3. **Aucun produit actif** - Offre inexistante
4. **Entreprises en difficulté** - Instabilité

## 🔧 **Configuration Prometheus**

### **Installation de Prometheus :**
```bash
# Télécharger Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar -xzf prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0
```

### **Configuration prometheus.yml :**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'tradesim'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### **Démarrer Prometheus :**
```bash
./prometheus --config.file=prometheus.yml
```

### **Accéder à Prometheus :**
- **URL :** http://localhost:9090
- **Targets :** http://localhost:9090/targets
- **Graph :** http://localhost:9090/graph

## 📊 **Requêtes Prometheus utiles**

### **Métriques de base :**
```promql
# Budget total
tradesim_budget_total

# Nombre de transactions
tradesim_transactions_total

# Produits actifs
tradesim_produits_actifs

# Entreprises solvables
tradesim_entreprises_solvables
```

### **Alertes :**
```promql
# Budget faible
tradesim_budget_total < 1000

# Aucune transaction récente
increase(tradesim_transactions_total[5m]) == 0

# Aucun produit actif
tradesim_produits_actifs == 0
```

### **Graphiques :**
```promql
# Évolution du budget
tradesim_budget_total

# Transactions par minute
rate(tradesim_transactions_total[1m])

# Pourcentage d'entreprises solvables
tradesim_entreprises_solvables / tradesim_entreprises_total * 100
```

## 🎨 **Dashboard CLI Rich**

### **Fonctionnalités :**
- **Affichage en temps réel** des métriques
- **Panneaux colorés** pour chaque type de métrique
- **Alertes visuelles** pour les problèmes
- **Mise à jour automatique** toutes les secondes

### **Panneaux disponibles :**
1. **💰 Budgets** - Budgets des entreprises
2. **💸 Transactions** - Statistiques des transactions
3. **🏢 Entités** - Comptage des entités
4. **🚨 Alertes** - Alertes et problèmes
5. **⚡ Performance** - Métriques de performance

### **Contrôles :**
- **Ctrl+C** - Arrêter le dashboard
- **Automatique** - Mise à jour toutes les secondes
- **Thread-safe** - Pas de blocage de la simulation

## 🔄 **Intégration avec la simulation**

### **Démarrage avec monitoring :**
```python
# Dans votre script de simulation
from monitoring.cli_dashboard import TradeSimDashboard
from monitoring.prometheus_exporter import TradeSimPrometheusExporter

# Démarrer le monitoring
dashboard = TradeSimDashboard()
exporter = TradeSimPrometheusExporter(port=8000)

# Démarrer les services
exporter.start_server()
exporter.start_collection_thread(interval=5)

# Lancer la simulation
simulation_service = SimulationService()
simulation_service.run_simulation_tours(100, verbose=True)
```

### **Monitoring en arrière-plan :**
```python
# Démarrer le dashboard en arrière-plan
import threading

def run_dashboard():
    dashboard = TradeSimDashboard()
    dashboard.start_live_dashboard()

dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
dashboard_thread.start()
```

## 📈 **Métriques avancées**

### **Métriques calculées :**
```python
# Ratio de transactions réussies
ratio_reussite = transactions_reussies / transactions_total * 100

# Évolution du budget
evolution_budget = budget_actuel - budget_initial

# Tendance des prix
tendance_prix = prix_moyen_actuel - prix_moyen_initial
```

### **Métriques de tendance :**
```python
# Budget sur le temps
budget_history = [budget1, budget2, budget3, ...]

# Transactions par minute
transactions_per_minute = transactions_total / minutes_ecoulees

# Événements par tour
evenements_per_tour = evenements_total / tours_completes
```

## 🚨 **Système d'alertes**

### **Alertes automatiques :**
1. **Budget critique** - Budget total < 1000€
2. **Marché stagnant** - Aucune transaction depuis 5 minutes
3. **Offre inexistante** - Aucun produit actif
4. **Instabilité** - Plus de 50% d'entreprises en difficulté

### **Configuration des alertes :**
```python
# Seuils configurables
ALERTE_BUDGET_CRITIQUE = 1000  # €
ALERTE_TRANSACTIONS_STAGNANT = 300  # secondes
ALERTE_PRODUITS_CRITIQUE = 0  # nombre
ALERTE_ENTREPRISES_CRITIQUE = 0.5  # ratio
```

## 🔧 **Dépannage**

### **Problèmes courants :**

#### **1. Port déjà utilisé :**
```bash
# Changer le port
python monitoring/prometheus_exporter.py --port 8001
```

#### **2. Erreur d'import :**
```bash
# Vérifier les dépendances
pip install rich prometheus_client

# Vérifier le PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/chemin/vers/tradesim"
```

#### **3. Dashboard ne s'affiche pas :**
```bash
# Vérifier la taille du terminal
# Le dashboard nécessite un terminal de taille suffisante
```

### **Logs de debug :**
```python
# Activer les logs détaillés
import logging
logging.basicConfig(level=logging.DEBUG)

# Vérifier les métriques
dashboard = TradeSimDashboard()
summary = dashboard.get_metrics_summary()
print(f"Métriques: {summary}")
```

## 📚 **Exemples d'utilisation**

### **Exemple 1 : Monitoring simple**
```bash
# Démarrer le dashboard
python monitoring/cli_dashboard.py

# Dans un autre terminal, lancer la simulation
python services/simulateur.py
```

### **Exemple 2 : Monitoring avec Prometheus**
```bash
# Terminal 1 - Exporteur Prometheus
python monitoring/prometheus_exporter.py

# Terminal 2 - Prometheus
./prometheus --config.file=prometheus.yml

# Terminal 3 - Simulation
python services/simulateur.py

# Navigateur - Prometheus UI
# http://localhost:9090
```

### **Exemple 3 : Monitoring complet**
```bash
# Terminal 1 - Dashboard CLI
python monitoring/cli_dashboard.py

# Terminal 2 - Exporteur Prometheus
python monitoring/prometheus_exporter.py

# Terminal 3 - Prometheus
./prometheus --config.file=prometheus.yml

# Terminal 4 - Simulation
python services/simulateur.py
```

## 🎯 **Bonnes pratiques**

### **1. Monitoring en production :**
- Utiliser Prometheus pour la persistance
- Configurer des alertes automatiques
- Sauvegarder les métriques historiques

### **2. Monitoring en développement :**
- Utiliser le dashboard CLI pour le debug
- Surveiller les métriques en temps réel
- Tester les alertes

### **3. Performance :**
- Collecter les métriques toutes les 5 secondes
- Limiter l'historique à 50 points
- Utiliser des threads daemon

## 📝 **Conclusion**

Le monitoring CLI de TradeSim offre :

✅ **Prometheus Exporteur** - Métriques pour production  
✅ **Dashboard CLI Rich** - Interface moderne pour développement  
✅ **Métriques complètes** - 50+ métriques disponibles  
✅ **Alertes automatiques** - Détection des problèmes  
✅ **Performance optimisée** - Impact minimal sur la simulation  

**Le monitoring CLI est maintenant prêt pour TradeSim !** 🚀

---

**Auteur :** Assistant IA  
**Date :** 2024-08-02  
**Version :** 1.0 