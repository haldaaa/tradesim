# Guide d'utilisation TradeSim

## 🚀 **DÉMARRAGE RAPIDE**

### **Point d'entrée unique :**
```bash
# Depuis le répertoire app/
python services/simulate.py [options]
```

**⚠️ IMPORTANT :** Vous ne lancez JAMAIS directement `simulateur.py` ou `simulation_service.py` !

## 📋 **Modes de lancement**

### **Mode interactif (recommandé)**
```bash
python services/simulate.py --new-game
```
- Configuration interactive complète
- Choix du monitoring Prometheus/Grafana
- Sauvegarde de templates
- **Utilise le système principal avec IDs**

### **Mode direct (simulation rapide)**
```bash
python services/simulate.py --tours 10
python services/simulate.py --tours 5 --verbose
python services/simulate.py --tours 10 --with-metrics
```
- Simulation immédiate
- Options en ligne de commande
- **Utilise le système principal avec IDs**

## 🔄 **Systèmes en coulisses**

### **Ce qui se passe quand vous lancez l'app :**
```python
# simulate.py (point d'entrée)
├── Importe simulation_service.py (système principal)
├── Utilise SimulationService avec IDs
├── Logs enrichis avec traçabilité
└── Monitoring Prometheus/Grafana
```

### **simulateur.py vs simulation_service.py :**
- **simulateur.py** : Ancien système (gardé pour tests)
- **simulation_service.py** : Système principal (production)
- **Vous n'avez pas à choisir** : simulate.py utilise automatiquement le bon !

## 📊 **Exemples d'utilisation**

### **Session interactive complète :**
```bash
$ python services/simulate.py --new-game

🎮 CONFIGURATION DE NOUVELLE PARTIE
[1] Configuration rapide (défaut)
[2] Configuration personnalisée
[3] Charger un template existant

# → Configuration interactive
# → Choix du monitoring
# → Lancement de la simulation
```

### **Simulation rapide avec monitoring :**
```bash
$ python services/simulate.py --tours 25 --with-metrics

🚀 Lancement de la simulation sur 25 tours...
📊 Monitoring Prometheus/Grafana activé
🔄 Tour 1 - Tick 0
🎯 ThaiTech achète 99 Colle (stratégie: moins_cher)
✅ Simulation terminée
```

## 🎯 **QUEL MODE CHOISIR ?**

| Mode | Quand l'utiliser | Avantages |
|------|------------------|-----------|
| **`--new-game`** | Nouvelle partie, configuration complète | Configuration interactive, monitoring, templates |
| **`--tours N`** | Test rapide, simulation simple | Rapide, direct, pas de configuration |
| **`--tours N --verbose`** | Debug, analyse détaillée | Logs complets, événements visibles |
| **`--tours N --with-metrics`** | Monitoring, analyse performance | Métriques Prometheus, dashboards Grafana |

## 📁 **Fichiers générés**

### **Logs avec IDs (système principal) :**
```
logs/
├── simulation_humain.log    # Logs humains des transactions
├── simulation.jsonl         # Données JSON avec IDs
├── event.log               # Logs humains des événements  
├── event.jsonl             # Données JSON des événements avec IDs
├── metrics.jsonl           # Métriques Prometheus avec IDs
└── monitoring.log          # Erreurs et alertes
```

### **Format des IDs :**
```
20250810_143022_TXN_001  # Transaction #1
20250810_143022_EVT_001  # Événement #1
20250810_143022_METRIC_001  # Métrique #1
```

## 🔧 **Dépannage**

### **Erreur "Module not found" :**
```bash
# Assurez-vous d'être dans le bon répertoire
cd /Users/fares/Desktop/DevVoyage/tradesim/app

# Activez l'environnement virtuel
source venv/bin/activate

# Lancez l'application
python services/simulate.py --new-game
```

### **Monitoring ne fonctionne pas :**
```bash
# Vérifiez que Docker est lancé
docker ps

# Vérifiez les logs
tail -f logs/monitoring.log
```

---

**Résumé :** Lancez toujours `python services/simulate.py` et l'application utilise automatiquement le système principal avec IDs ! 