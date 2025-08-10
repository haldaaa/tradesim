# Services TradeSim

## 📁 **Fichiers principaux**

### **🚀 Point d'entrée**
- **`simulate.py`** - **Point d'entrée principal** de l'application CLI
  - Gère tous les arguments (`--tours`, `--new-game`, etc.)
  - Interface utilisateur et configuration
  - **C'est le fichier à lancer**

### **⚙️ Logique métier**
- **`simulateur.py`** - **ANCIEN SYSTÈME** (maintenu pour compatibilité)
  - Logique de simulation originale
  - Logs simples sans IDs
  - **PLUS UTILISÉ EN PRODUCTION** (gardé pour tests)
  - Fonctions : `simulation_tour()`, `acheter_produit()`, `log_event()` (sans IDs)

- **`simulation_service.py`** - **NOUVEAU SYSTÈME** (système principal)
  - Service d'orchestration avec monitoring Prometheus
  - Logs enrichis avec IDs uniques
  - **SYSTÈME PRINCIPAL ACTUEL**
  - Classe `SimulationService` avec `IDGenerator`
  - Logs format : `{"action_id": "20250810_143022_TXN_001", "session_id": "20250810_143022", ...}`

- **`game_manager.py`** - Gestion des parties et templates
  - Configuration interactive (`--new-game`)
  - Sauvegarde/chargement de templates
  - **Importé par `simulate.py`**

### **🔄 Services spécialisés**
- **`simulation_service.py`** - Orchestration de simulation
- **`latency_service.py`** - **NOUVEAU** Métriques de latence et throughput
  - Mesure des temps de réponse des actions
  - Calcul des statistiques de performance (moyenne, médiane, percentiles)
  - Gestion du throughput (opérations par seconde)
  - Intégration avec Prometheus
  - Cache LRU pour optimisations
- **`price_service.py`** - Gestion des prix
- **`budget_service.py`** - Gestion des budgets
- **`transaction_service.py`** - Gestion des transactions

## 🎯 **Comment lancer l'application**

### **Point d'entrée unique**
```bash
# Depuis le répertoire app/
python services/simulate.py [options]
```

### **Exemples**
```bash
# Mode interactif (nouvelle partie)
python services/simulate.py --new-game

# Mode direct (simulation rapide)
python services/simulate.py --tours 10

# Avec monitoring
python services/simulate.py --tours 5 --with-metrics
```

## 📋 **Architecture**

```
simulate.py (point d'entrée)
├── game_manager.py (mode interactif)
├── simulation_service.py (logique simulation - NOUVEAU)
├── simulateur.py (logique simulation - ANCIEN, tests)
├── simulation_service.py (orchestration)
└── autres services...
```

## 🔄 **Migration et compatibilité**

### **État actuel :**
- **Production** : Utilise `simulation_service.py` (avec IDs)
- **Tests** : Utilisent encore `simulateur.py` (sans IDs)
- **Logs** : Mélange de formats selon le système utilisé

### **Évolution :**
- `simulation_service.py` : Système principal avec toutes les fonctionnalités
- `simulateur.py` : Gardé pour compatibilité des tests
- **Recommandation** : Utiliser `simulation_service.py` pour tout nouveau développement

**Note :** Il n'y a qu**un seul point d'entrée** : `simulate.py` 