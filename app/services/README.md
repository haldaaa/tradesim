# 📁 Services - Logique métier TradeSim

## 🎯 **BUT DU DOSSIER**
Ce dossier contient tous les services de logique métier de TradeSim. Chaque service encapsule une fonctionnalité spécifique et peut être utilisé de manière indépendante.

## 🏗️ **ARCHITECTURE**
- **Services principaux** : Simulation, Game Manager, Price
- **Services de métriques** : Budget, Enterprise, Product, Supplier, Transaction, Event
- **Services utilitaires** : Latency, Name Manager
- **Templates** : Modèles de configuration pour les tests

## 📋 **FICHIERS PRÉSENTS**

### **🔄 Services Principaux**
- **`simulation_service.py`** : Service central de simulation
  - Gestion des tours de simulation
  - Transactions entre entreprises et fournisseurs
  - Application d'événements (inflation, recharge, etc.)
  - Monitoring et métriques en temps réel
  - Cache thread-safe pour les repositories

- **`game_manager_service.py`** : Gestionnaire de jeu
  - Génération des données initiales
  - Reset et initialisation des parties
  - Lancement des simulations

- **`price_service.py`** : Service de gestion des prix
  - Calcul et mise à jour des prix
  - Gestion des variations de prix

### **📊 Services de Métriques**
- **`budget_metrics_service.py`** : Métriques de budget
- **`enterprise_metrics_service.py`** : Métriques d'entreprises
- **`product_metrics_service.py`** : Métriques de produits
- **`supplier_metrics_service.py`** : Métriques de fournisseurs
- **`transaction_metrics_service.py`** : Métriques de transactions
- **`event_metrics_service.py`** : Métriques d'événements
- **`performance_metrics_service.py`** : Métriques de performance

### **🔧 Services Utilitaires**
- **`latency_service.py`** : Mesure des latences
- **`name_manager.py`** : Gestion des noms d'entreprises

### **📁 Templates**
- **`templates/`** : Modèles de configuration pour les tests

## 🚀 **UTILISATION**

### **Simulation de base**
```python
from services.simulation_service import SimulationService

# Créer un service de simulation
service = SimulationService(verbose=True)

# Exécuter un tour
result = service.simulation_tour()

# Obtenir les statistiques
stats = service.calculer_statistiques()
```

### **Nouvelle partie**
```python
from services.game_manager_service import reset_game, run_simulation_tours

# Reset et nouvelle partie
reset_game()

# Lancer une simulation de 10 tours
run_simulation_tours(10, verbose=True)
```

### **Monitoring des métriques**
```python
from services.budget_metrics_service import BudgetMetricsService

# Service de métriques de budget
budget_service = BudgetMetricsService()
metrics = budget_service.calculer_metriques_budget()
```

## 🔧 **CONFIGURATION**
Tous les services utilisent la configuration centralisée dans `config/config.py` :
- Paramètres de simulation
- Seuils de métriques
- Configuration des événements
- Validation des données

## 📈 **MÉTRIQUES DISPONIBLES**
- **Budget** : Revenus, dépenses, ratios
- **Entreprises** : Performance, stratégies
- **Produits** : Prix, stocks, disponibilité
- **Fournisseurs** : Stocks, prix, performance
- **Transactions** : Volume, succès, échecs
- **Événements** : Fréquence, impact
- **Performance** : Latences, débits

## 🧪 **TESTS**
Chaque service a ses tests unitaires dans `tests/unit/` :
- Tests de fonctionnalité
- Tests de performance
- Tests de thread-safety
- Tests d'intégration

## 📝 **LOGGING**
Tous les services utilisent un logging structuré :
- Logs humains dans `logs/simulation_humain.log`
- Logs JSON dans `logs/simulation.jsonl`
- Logs d'événements dans `logs/event.log` et `logs/event.jsonl`

## 🔄 **DERNIÈRES MODIFICATIONS**
- **11/08/2025** : Cache thread-safe dans SimulationService
- **11/08/2025** : Validation des configurations
- **11/08/2025** : Tests de performance complets
- **11/08/2025** : Logging structuré amélioré

---
**Auteur** : Assistant IA  
**Dernière mise à jour** : 11/08/2025 