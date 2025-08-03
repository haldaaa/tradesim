# Services - Logique métier TradeSim
====================================

## 📋 **Vue d'ensemble**

Le dossier `services/` contient toute la logique métier de TradeSim, organisée en services spécialisés. Chaque service a une responsabilité précise et utilise les Repository pour accéder aux données.

**MODE CLI (développement) :** Utilise les Repository Fake (données en mémoire)
**MODE WEB (production) :** Utilise les Repository SQL (base de données)

## 🏗️ **Architecture**

### **Pattern Service :**
- **Séparation des responsabilités** : Chaque service a un rôle précis
- **Réutilisabilité** : Services utilisables par CLI et API
- **Maintenabilité** : Code modulaire et organisé
- **Extensibilité** : Ajout facile de nouveaux services

### **Structure :**
```
services/
├── __init__.py              # Exports des services
├── game_manager.py          # Gestion du jeu et templates
├── simulateur.py            # Orchestration de la simulation
├── simulate.py              # Interface de simulation
├── transaction_service.py    # Gestion des transactions
├── budget_service.py        # Gestion des budgets
├── game_manager_service.py  # Service de gestion de jeu
├── simulation_service.py    # Service de simulation
├── templates/               # Templates de configuration
└── README.md               # Cette documentation
```

## 📁 **Services détaillés**

### **`game_manager.py` - Gestion du jeu**
**Responsabilité :** Gestion des templates, configuration et orchestration générale.

**Fonctions principales :**
- `reset_game()` : Remet le jeu à zéro
- `generate_game_data(config)` : Génère les données de jeu
- `save_template(nom)` : Sauvegarde un template
- `load_template(nom)` : Charge un template
- `get_current_config()` : Récupère la configuration actuelle

**MODE CLI :** Utilise les Repository Fake pour les données en mémoire
**MODE WEB :** Utilise les Repository SQL pour la persistance

### **`simulateur.py` - Orchestration de simulation**
**Responsabilité :** Orchestration des tours de simulation et événements.

**Fonctions principales :**
- `simulation_tour(tick)` : Exécute un tour de simulation
- `appliquer_evenements(tick)` : Applique les événements aléatoires
- `selectionner_entreprises()` : Sélectionne les entreprises actives

**MODE CLI :** Logs vers fichiers locaux
**MODE WEB :** Logs vers base de données + API

### **`transaction_service.py` - Gestion des transactions**
**Responsabilité :** Gestion des achats, ventes et transactions entre entreprises.

**Fonctions principales :**
- `effectuer_achat(entreprise, produit_id, quantite)` : Effectue un achat
- `get_statistiques_transactions()` : Récupère les statistiques
- `calculer_prix_final(produit, fournisseur)` : Calcule le prix final

**MODE CLI :** Transactions en mémoire
**MODE WEB :** Transactions persistées en base

### **`budget_service.py` - Gestion des budgets**
**Responsabilité :** Gestion des budgets des entreprises et recharges.

**Fonctions principales :**
- `ajouter_budget(entreprise_id, montant)` : Ajoute du budget
- `recharge_budget_aleatoire(entreprise_id)` : Recharge aléatoire
- `get_entreprises_en_difficulte(seuil)` : Détecte les entreprises en difficulté

**MODE CLI :** Budgets en mémoire
**MODE WEB :** Budgets persistés en base

### **`simulation_service.py` - Service de simulation**
**Responsabilité :** Interface de haut niveau pour la simulation.

**Fonctions principales :**
- `run_simulation_tours(n_tours)` : Lance une simulation de N tours
- `run_simulation_infinite()` : Lance une simulation infinie
- `reset_simulation()` : Remet la simulation à zéro

**MODE CLI :** Interface console
**MODE WEB :** Interface API REST

## 🔧 **Utilisation**

### **Mode CLI (développement) :**
```python
from services import game_manager, simulation_service

# Initialiser le jeu
game_manager.reset_game()

# Lancer une simulation
simulation_service.run_simulation_tours(10, verbose=True)
```

### **Mode Web (production) :**
```python
from services import transaction_service, budget_service

# Effectuer une transaction via API
transaction = transaction_service.effectuer_achat(entreprise_id=1, produit_id=2, quantite=5)

# Gérer les budgets
budget_service.ajouter_budget(entreprise_id=1, montant=500)
```

## 🎯 **Avantages de cette architecture**

### **Séparation des responsabilités :**
- ✅ Chaque service a un rôle précis
- ✅ Code modulaire et maintenable
- ✅ Tests unitaires facilités

### **Réutilisabilité :**
- ✅ Services utilisables par CLI et API
- ✅ Interface commune pour tous les modes
- ✅ Code partagé entre les interfaces

### **Extensibilité :**
- ✅ Ajout facile de nouveaux services
- ✅ Modification sans impact sur les autres services
- ✅ Configuration centralisée

## 📝 **Exemples d'utilisation**

### **Dans les événements :**
```python
from services import transaction_service

def appliquer_inflation(tick: int):
    # Logique d'inflation...
    # Utilise transaction_service pour les mises à jour
    pass
```

### **Dans l'API :**
```python
from services import game_manager, transaction_service

@app.get("/entreprises")
def get_entreprises():
    return game_manager.get_current_config()["entreprises"]

@app.post("/transactions")
def create_transaction(transaction_data):
    return transaction_service.effectuer_achat(**transaction_data)
```

### **Dans les tests :**
```python
from services import game_manager, simulation_service

def test_simulation():
    game_manager.reset_game()
    resultats = simulation_service.run_simulation_tours(5)
    assert len(resultats) == 5
```

## 🔄 **Migration CLI → Web**

### **Étape 1 : Vérifier le mode**
```python
from config.mode import is_web_mode

if is_web_mode():
    # Utiliser les Repository SQL
    pass
else:
    # Utiliser les Repository Fake
    pass
```

### **Étape 2 : Adapter les services**
```python
# Les services utilisent déjà les Repository
# Pas de modification nécessaire !
```

### **Étape 3 : Tester**
```bash
# Tests des services
pytest tests/unit/test_services.py -v

# Tests d'intégration
pytest tests/integration/test_services_integration.py -v
```

## 📚 **Documentation technique**

### **Pattern Service :**
- **Interface commune** : Tous les services ont la même structure
- **Dépendances injectées** : Repository passés en paramètre
- **Tests unitaires** : Services testables indépendamment
- **Documentation** : Commentaires détaillés pour chaque fonction

### **Gestion des modes :**
- **Repository pattern** : Abstraction de l'accès aux données
- **Configuration centralisée** : Mode défini dans config/mode.py
- **Tests automatisés** : Validation du bon fonctionnement
- **Migration transparente** : Pas de refactorisation nécessaire

## 📝 **Auteur**
Assistant IA - 2024-08-02 