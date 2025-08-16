# 📊 TUTORIEL COMPLET - CRÉATION DE MÉTRIQUES PROMETHEUS

## 🎯 **OBJECTIF DU TUTORIEL**

Ce tutoriel détaille comment implémenter des métriques Prometheus dans une application Python, basé sur l'expérience du projet TradeSim. Vous apprendrez à créer, calculer et exposer des métriques de manière professionnelle.

---

## 🏗️ **ARCHITECTURE GÉNÉRALE**

### **Modèle en 3 Couches**

```
┌─────────────────────────────────────────────────────────────┐
│                    PROMETHEUS EXPORTER                      │
│  (monitoring/prometheus_exporter.py)                        │
│  - Définit les métriques Prometheus                         │
│  - Expose l'endpoint /metrics                               │
│  - Collecte les données depuis les services                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVICES DE MÉTRIQUES                    │
│  (services/*_metrics_service.py)                            │
│  - Calculent les métriques métier                           │
│  - Gèrent l'historique et le cache                          │
│  - Retournent des dictionnaires de données                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    SIMULATION SERVICE                       │
│  (services/simulation_service.py)                           │
│  - Appelle les services de métriques                        │
│  - Collecte les données à chaque tour                       │
│  - Stocke en JSONL pour persistance                         │
└─────────────────────────────────────────────────────────────┘
```

### **Avantages de cette Architecture**

- **Séparation des responsabilités** : Chaque couche a un rôle précis
- **Modularité** : Services indépendants et réutilisables
- **Testabilité** : Chaque composant peut être testé isolément
- **Extensibilité** : Ajout facile de nouvelles métriques
- **Performance** : Cache et optimisations intégrés

---

## 🔧 **TYPES DE MÉTRIQUES PROMETHEUS**

### **1. GAUGE - Valeur qui varie**

```python
from prometheus_client import Gauge

# Définition
budget_total = Gauge('tradesim_budget_total', 'Budget total des entreprises')

# Utilisation
budget_total.set(15000.50)  # Définir une valeur
budget_total.inc(100)       # Incrémenter
budget_total.dec(50)        # Décrémenter
```

**Cas d'usage :** Budgets, température, nombre d'utilisateurs actifs, utilisation mémoire

### **2. COUNTER - Compteur qui monte**

```python
from prometheus_client import Counter

# Définition
transactions_total = Counter('tradesim_transactions_total', 'Nombre total de transactions')

# Utilisation
transactions_total.inc()        # Incrémenter de 1
transactions_total.inc(5)       # Incrémenter de 5
# transactions_total.dec()      # ❌ ERREUR : Counter ne peut que monter
```

**Cas d'usage :** Nombre de requêtes, erreurs, transactions, événements

### **3. HISTOGRAM - Distribution de valeurs**

```python
from prometheus_client import Histogram

# Définition
temps_simulation = Histogram(
    'tradesim_temps_simulation_seconds',
    'Durée de simulation',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]  # Seuils personnalisés
)

# Utilisation
with temps_simulation.time():  # Mesure automatique du temps
    # Code à mesurer
    pass

# Ou manuellement
temps_simulation.observe(2.5)  # Observer une valeur
```

**Cas d'usage :** Temps de réponse, taille des requêtes, latence

---

## 🚀 **ÉTAPE 1 : CRÉER UNE MÉTRIQUE PROMETHEUS**

### **Fichier : `monitoring/prometheus_exporter.py`**

```python
Ce module expose les métriques au format Prometheus.
"""

import time
import json
from prometheus_client import (
    start_http_server, 
    Gauge, 
    Counter, 
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)
from flask import Flask, Response

# ============================================================================
# DÉFINITION DES MÉTRIQUES PROMETHEUS
# ============================================================================

# 1. GAUGE - Valeur qui varie
ma_metrique_gauge = Gauge('mon_app_ma_metrique', 'Description de ma métrique')

# 2. COUNTER - Compteur qui monte
mon_compteur = Counter('mon_app_mon_compteur', 'Description du compteur')

# 3. HISTOGRAM - Distribution
mon_histogram = Histogram(
    'mon_app_mon_histogram',
    'Description de l\'histogramme',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# 4. MÉTRIQUES SYSTÈME
cpu_usage = Gauge('mon_app_cpu_usage_percent', 'Utilisation CPU (%)')
memory_usage = Gauge('mon_app_memory_usage_bytes', 'Utilisation mémoire (bytes)')

# ============================================================================
# FONCTIONS DE COLLECTE
# ============================================================================

def collecter_mes_metriques():
    """Collecte mes métriques personnalisées"""
    try:
        # Récupérer les données depuis vos services
        donnees = recuperer_donnees()
        
        # Calculer les métriques
        metriques = mon_service.calculer_ma_metrique(donnees)
        
        # Mettre à jour Prometheus
        ma_metrique_gauge.set(metriques['ma_metrique_valeur'])
        mon_compteur.inc(metriques['nombre_evenements'])
        
        # Stocker en JSONL pour persistance
        with open('logs/metrics.jsonl', 'a') as f:
            f.write(json.dumps({
                'timestamp': time.time(),
                'metriques': metriques
            }) + '
')
            
    except Exception as e:
        print(f"Erreur lors de la collecte des métriques: {e}")

def collecter_metriques_systeme():
    """Collecte les métriques système"""
    try:
        import psutil
        
        # CPU
        cpu_usage.set(psutil.cpu_percent())
        
        # Mémoire
        memory = psutil.virtual_memory()
        memory_usage.set(memory.used)
        
    except Exception as e:
        print(f"Erreur lors de la collecte des métriques système: {e}")

# ============================================================================
# SERVEUR FLASK
# ============================================================================

app = Flask(__name__)

@app.route('/metrics')
def metrics():
    """Endpoint Prometheus /metrics"""
