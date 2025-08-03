# Events - Événements de simulation TradeSim
============================================

## 📋 **Vue d'ensemble**

Le dossier `events/` contient tous les événements aléatoires de la simulation TradeSim. Ces événements modifient l'état du jeu de manière imprévisible, ajoutant du réalisme et de la complexité à la simulation.

**MODE CLI (développement) :** Événements utilisent les Repository Fake (données en mémoire)
**MODE WEB (production) :** Événements utilisent les Repository SQL (base de données)

## 🏗️ **Architecture**

### **Pattern Event :**
- **Découplage** : Événements indépendants les uns des autres
- **Configurabilité** : Probabilités et paramètres ajustables
- **Observabilité** : Logs détaillés de chaque événement
- **Extensibilité** : Ajout facile de nouveaux événements

### **Structure :**
```
events/
├── __init__.py                    # Exports des événements
├── inflation.py                   # Modification des prix
├── reassort.py                    # Réapprovisionnement des stocks
├── recharge_budget.py             # Recharge des budgets
├── variation_disponibilite.py     # Activation/désactivation de produits
├── event_logger.py                # Système de logging des événements
├── inflation_backup.py            # Version de sauvegarde (ancienne)
└── README.md                      # Cette documentation
```

## 📁 **Événements disponibles**

### **`inflation.py` - Modification des prix**
**Fonction :** `appliquer_inflation(tick: int)`

**Comportement :**
- **Probabilité** : 40% de chance d'être déclenché
- **Cible** : Produit(s) ou catégorie(s) aléatoire(s)
- **Effet** : Augmentation du prix de +40% (+15% si déjà affecté)
- **Durée** : Temporaire, retour progressif au prix original

**MODE CLI :** Modifie les prix en mémoire
**MODE WEB :** Modifie les prix en base de données

**Logs générés :**
```json
{
  "timestamp": "2024-08-02T10:30:00",
  "event": "inflation",
  "tick": 25,
  "cible": "produit",
  "produit_id": 3,
  "prix_avant": 100.0,
  "prix_apres": 140.0,
  "pourcentage": 40
}
```

### **`reassort.py` - Réapprovisionnement des stocks**
**Fonction :** `appliquer_reassort(tick: int)`

**Comportement :**
- **Probabilité** : 50% de chance d'être déclenché
- **Cible** : Fournisseur(s) aléatoire(s)
- **Effet** : Ajout de stock (10-50 unités par produit)
- **Impact** : Amélioration de la disponibilité des produits

**MODE CLI :** Met à jour les stocks en mémoire
**MODE WEB :** Met à jour les stocks en base de données

**Logs générés :**
```json
{
  "timestamp": "2024-08-02T10:30:00",
  "event": "reassort",
  "tick": 25,
  "fournisseur_id": 2,
  "produits_reassortis": [
    {"produit_id": 1, "quantite_ajoutee": 25},
    {"produit_id": 3, "quantite_ajoutee": 15}
  ]
}
```

### **`recharge_budget.py` - Recharge des budgets**
**Fonction :** `appliquer_recharge_budget(tick: int)`

**Comportement :**
- **Probabilité** : 50% de chance d'être déclenché
- **Cible** : Entreprise(s) aléatoire(s)
- **Effet** : Ajout de budget (200-600€)
- **Impact** : Permet aux entreprises de continuer à acheter

**MODE CLI :** Met à jour les budgets en mémoire
**MODE WEB :** Met à jour les budgets en base de données

**Logs générés :**
```json
{
  "timestamp": "2024-08-02T10:30:00",
  "event": "recharge_budget",
  "tick": 25,
  "entreprise_id": 1,
  "budget_avant": 150.0,
  "budget_apres": 450.0,
  "montant_ajoute": 300.0
}
```

### **`variation_disponibilite.py` - Activation/désactivation de produits**
**Fonction :** `appliquer_variation_disponibilite(tick: int)`

**Comportement :**
- **Probabilité** : 30% de chance d'être déclenché
- **Cible** : Produit(s) aléatoire(s)
- **Effet** : Activation (20%) ou désactivation (10%) de produits
- **Impact** : Modification de l'offre disponible

**MODE CLI :** Modifie l'état des produits en mémoire
**MODE WEB :** Modifie l'état des produits en base de données

**Logs générés :**
```json
{
  "timestamp": "2024-08-02T10:30:00",
  "event": "variation_disponibilite",
  "tick": 25,
  "produit_id": 5,
  "action": "activation",
  "etat_avant": false,
  "etat_apres": true
}
```

## 🔧 **Utilisation**

### **Mode CLI (développement) :**
```python
from events import inflation, reassort, recharge_budget, variation_disponibilite

# Appliquer un événement d'inflation
logs = inflation.appliquer_inflation(tick=25)

# Appliquer un réassort
logs = reassort.appliquer_reassort(tick=30)

# Appliquer une recharge de budget
logs = recharge_budget.appliquer_recharge_budget(tick=35)
```

### **Mode Web (production) :**
```python
from events import inflation, reassort
from config.mode import is_web_mode

# Les événements utilisent automatiquement les bons Repository
if is_web_mode():
    print("Mode Web - Événements persistés en base")
else:
    print("Mode CLI - Événements en mémoire")

# Appliquer un événement
logs = inflation.appliquer_inflation(tick=25)
```

## 🎯 **Avantages de cette architecture**

### **Découplage :**
- ✅ **Événements indépendants** : Chaque événement fonctionne seul
- ✅ **Ajout facile** : Nouveaux événements sans impact sur les autres
- ✅ **Tests isolés** : Tests unitaires pour chaque événement
- ✅ **Configuration flexible** : Paramètres ajustables par événement

### **Observabilité :**
- ✅ **Logs détaillés** : Chaque événement génère des logs complets
- ✅ **Format JSON** : Logs structurés pour l'analyse
- ✅ **Format humain** : Logs lisibles pour le debugging
- ✅ **Traçabilité** : Horodatage et contexte de chaque événement

### **Extensibilité :**
- ✅ **Nouveaux événements** : Ajout facile de nouveaux types d'événements
- ✅ **Configuration** : Paramètres ajustables sans modification du code
- ✅ **Intégration** : Événements utilisables par CLI et API
- ✅ **Tests** : Framework de tests pour les événements

## 📝 **Exemples d'utilisation**

### **Dans la simulation :**
```python
from events import inflation, reassort, recharge_budget, variation_disponibilite

def appliquer_evenements(tick: int):
    """Applique tous les événements possibles pour un tick."""
    logs = []
    
    # Appliquer chaque événement avec sa probabilité
    logs.extend(inflation.appliquer_inflation(tick))
    logs.extend(reassort.appliquer_reassort(tick))
    logs.extend(recharge_budget.appliquer_recharge_budget(tick))
    logs.extend(variation_disponibilite.appliquer_variation_disponibilite(tick))
    
    return logs
```

### **Dans les tests :**
```python
from events import inflation
from repositories import ProduitRepository

def test_inflation():
    # Préparer les données
    produit_repo = ProduitRepository()
    produit = produit_repo.get_by_id(1)
    prix_initial = produit.prix
    
    # Appliquer l'inflation
    logs = inflation.appliquer_inflation(tick=1)
    
    # Vérifier le résultat
    produit_apres = produit_repo.get_by_id(1)
    assert produit_apres.prix > prix_initial
```

### **Dans l'API :**
```python
from fastapi import FastAPI
from events import inflation

app = FastAPI()

@app.post("/events/inflation")
def trigger_inflation(tick: int):
    """Déclenche manuellement un événement d'inflation."""
    logs = inflation.appliquer_inflation(tick)
    return {"message": "Inflation appliquée", "logs": logs}
```

## 🔄 **Migration CLI → Web**

### **Étape 1 : Vérifier le mode**
```python
from config.mode import is_web_mode

def appliquer_evenement():
    if is_web_mode():
        # Utiliser les Repository SQL
        pass
    else:
        # Utiliser les Repository Fake
        pass
```

### **Étape 2 : Adapter les événements**
```python
# Les événements utilisent déjà les Repository
# Pas de modification nécessaire !
```

### **Étape 3 : Tester les événements**
```bash
# Tests des événements
pytest tests/unit/test_events.py -v

# Tests d'intégration
pytest tests/integration/test_events_integration.py -v
```

## 📚 **Documentation technique**

### **Pattern Event :**
- **Découplage** : Événements indépendants les uns des autres
- **Configurabilité** : Probabilités et paramètres ajustables
- **Observabilité** : Logs détaillés de chaque événement
- **Extensibilité** : Ajout facile de nouveaux événements

### **Repository Integration :**
- **Abstraction** : Événements utilisent les Repository pour l'accès aux données
- **Mode agnostic** : Même code pour CLI et Web
- **Tests** : Tests unitaires et d'intégration
- **Performance** : Optimisé pour les modifications fréquentes

### **Logging System :**
- **JSON logs** : Logs structurés pour l'analyse
- **Human logs** : Logs lisibles pour le debugging
- **Context** : Horodatage et contexte de chaque événement
- **Traçabilité** : Suivi complet des modifications

## 📝 **Auteur**
Assistant IA - 2024-08-02 