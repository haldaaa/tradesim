# Guide d'utilisation TradeSim

## 🎯 **OBJECTIF DE L'APPLICATION**

**TradeSim est un système de simulation économique CONTINU avec monitoring temps réel.**

### **Architecture Cible (Production)**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TradeSim      │    │   Prometheus    │    │     Grafana     │
│   Simulation    │───▶│   Monitoring    │───▶│   Dashboards    │
│   Continue      │    │   Métriques     │    │   Visualisation │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**L'application doit tourner 24/7 avec :**
- ✅ Simulation économique continue
- ✅ Monitoring Prometheus temps réel
- ✅ Dashboards Grafana
- ✅ Métriques 100+ collectées
- ✅ Alertes automatiques

---

## 🚀 **MÉTHODES DE LANCEMENT - GUIDE COMPLET**

### **📋 TABLEAU COMPARATIF**

| Méthode | Quand l'utiliser | Avantages | Inconvénients |
|---------|------------------|-----------|---------------|
| **Mode Production** | 🎯 **RECOMMANDÉ** - Simulation continue | Monitoring 24/7, métriques complètes | Plus de ressources |
| **Mode Test** | 🧪 Tests rapides, développement | Rapide, simple | Pas de monitoring |
| **Mode Debug** | 🐛 Debug, analyse détaillée | Logs complets | Performance réduite |
| **Mode Web** | 🌐 Interface utilisateur | Interface graphique | Plus complexe |

---

## 🎯 **1. MODE PRODUCTION (RECOMMANDÉ)**

### **Objectif : Simulation continue avec monitoring**

```bash
# Méthode officielle pour production
python services/simulate.py --infinite --with-metrics --verbose
```

**Caractéristiques :**
- ✅ **Simulation continue** : 1000+ tours
- ✅ **Monitoring intégré** : Prometheus sur port 8000
- ✅ **151 métriques** collectées en temps réel
- ✅ **Logs persistants** : JSONL + logs humains
- ✅ **Dashboards** : Grafana accessible sur port 3000

**Utilisation :**
```bash
# Démarrer la simulation continue
python services/simulate.py --infinite --with-metrics --verbose
```

# Dans un autre terminal, vérifier le monitoring
curl http://localhost:8000/health
curl http://localhost:8000/metrics | grep tradesim_ | wc -l

# Accéder aux dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
```

**Quand l'utiliser :**
- 🎯 **Production** : Simulation économique continue
- 📊 **Monitoring** : Analyse des métriques en temps réel
- 🔍 **Observabilité** : Dashboards et alertes
- 📈 **Performance** : Optimisation continue

---

## 🧪 **2. MODE TEST (Développement)**

### **Objectif : Tests rapides sans monitoring**

```bash
# Test simple et rapide
python services/simulate.py --tours 10
```

**Caractéristiques :**
- ✅ **Rapide** : Pas de monitoring
- ✅ **Simple** : Une seule commande
- ✅ **Debug** : Logs de base
- ❌ **Pas de métriques** : Monitoring désactivé

**Quand l'utiliser :**
- 🧪 **Développement** : Tests de fonctionnalités
- 🔧 **Debug** : Correction de bugs
- ⚡ **Rapide** : Validation rapide
- 📝 **Documentation** : Exemples simples

---

## 🐛 **3. MODE DEBUG (Analyse détaillée)**

### **Objectif : Debug et analyse complète**

```bash
# Mode debug avec logs détaillés
python services/simulate.py --tours 5 --verbose --debug
```

**Caractéristiques :**
- ✅ **Logs détaillés** : Chaque action visible
- ✅ **Debug complet** : Traçabilité totale
- ✅ **Événements visibles** : Pas à pas
- ❌ **Performance** : Plus lent

**Quand l'utiliser :**
- 🐛 **Debug** : Problèmes complexes
- 📊 **Analyse** : Comportement détaillé
- 🎓 **Apprentissage** : Comprendre le système
- 🔍 **Investigation** : Problèmes spécifiques

---

## 🌐 **4. MODE WEB (Interface utilisateur)**

### **Objectif : Interface graphique et API REST**

```bash
# Démarrer l'API web
python api/main.py --with-metrics
```

**Caractéristiques :**
- ✅ **Interface web** : API REST + interface
- ✅ **Monitoring** : Métriques via API
- ✅ **Interactif** : Contrôle via web
- ❌ **Complexe** : Plus de configuration

**Quand l'utiliser :**
- 🌐 **Interface** : Contrôle via web
- 🔌 **API** : Intégration avec d'autres systèmes
- 👥 **Utilisateurs** : Interface graphique
- 🔗 **Intégration** : Systèmes externes

---

## 🎯 **RECOMMANDATION OFFICIELLE**

### **Pour Production (Simulation continue)**
```bash
python services/simulate.py --infinite --with-metrics --verbose
```

### **Pour Développement (Tests rapides)**
```bash
python services/simulate.py --tours 10
```

### **Pour Debug (Analyse détaillée)**
```bash
python services/simulate.py --tours 5 --verbose --debug
```

---

## 📊 **MONITORING ET MÉTRIQUES**

### **Métriques Disponibles (151)**
- **Budget** : 14 métriques (total, moyenne, variation)
- **Entreprises** : 18 métriques (performance, comportement)
- **Produits** : 16 métriques (prix, demande, offre)
- **Fournisseurs** : 16 métriques (ventes, stock, compétitivité)
- **Transactions** : 16 métriques (volume, prix, efficacité)
- **Événements** : 16 métriques (impact, fréquence, stabilité)
- **Performance** : 16 métriques (temps, mémoire, CPU)
- **Système** : 10 métriques (CPU, mémoire, disque, réseau)

### **Endpoints Monitoring**
- **Métriques** : `http://localhost:8000/metrics`
- **Santé** : `http://localhost:8000/health`
- **Interface** : `http://localhost:8000/`

### **Dashboards**
- **Prometheus** : `http://localhost:9090`
- **Grafana** : `http://localhost:3000`

---

## 🔧 **CONFIGURATION**

### **Variables d'Environnement**
```bash
# Activation du monitoring
export METRICS_ENABLED=true

# Configuration de l'exporteur
export METRICS_EXPORTER_PORT=8000
export METRICS_EXPORTER_HOST=0.0.0.0

# Intervalles de collecte
export METRICS_COLLECTION_INTERVAL=5
export METRICS_SYSTEM_INTERVAL=10
```

### **Fichiers de Configuration**
- `config/config.py` : Configuration principale
- `monitoring/prometheus.yml` : Configuration Prometheus
- `monitoring/docker-compose.yml` : Stack monitoring

---

## 📁 **FICHIERS GÉNÉRÉS**

### **Logs de Production**
```
logs/
├── simulation_humain.log    # Logs humains des transactions
├── simulation.jsonl         # Données JSON structurées
├── event.log               # Logs humains des événements
├── event.jsonl             # Données JSON des événements
├── metrics.jsonl           # Métriques Prometheus
└── monitoring.log          # Logs du monitoring
```

### **Métriques JSONL**
```json
{
  "timestamp": "2025-08-11T10:30:00Z",
  "tour": 1,
  "metrics": {
    "budget_total": 10484.0,
    "transactions_total": 7,
    "performance_temps_execution": 0.15
  }
}
```

---

## 🚨 **DÉPANNAGE**

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
# Vérifier l'activation
echo $METRICS_ENABLED

# Redémarrer avec monitoring
python services/simulate.py --tours 1 --with-metrics
```

#### **3. Monitoring Ne Démarre Pas**
```bash
# Vérifier les dépendances
pip install prometheus_client flask

# Tester l'exporteur
python monitoring/prometheus_exporter.py
```

---

## 🎯 **CONCLUSION**

**TradeSim est conçu pour tourner en CONTINU avec monitoring temps réel.**

### **Méthode Officielle (Production)**
```bash
python services/simulate.py --infinite --with-metrics --verbose
```

### **Objectifs Atteints**
- ✅ **Simulation continue** : 24/7
- ✅ **Monitoring temps réel** : 151 métriques
- ✅ **Observabilité** : Dashboards et alertes
- ✅ **Performance** : Optimisation continue
- ✅ **Scalabilité** : Architecture modulaire

---

**Auteur** : Assistant IA  
**Date** : 2025-08-11  
**Version** : 2.0 - Guide clarifié pour production continue 