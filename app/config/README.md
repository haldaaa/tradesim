# Configuration - TradeSim
==========================

## 📋 **Vue d'ensemble**

Le dossier `config/` centralise toute la configuration de TradeSim, incluant les paramètres de simulation, les modes d'exécution et les constantes de l'application.

## 🏗️ **Structure**

```
config/
├── __init__.py      # Exports de configuration
├── config.py        # Paramètres de simulation
├── mode.py          # Configuration des modes CLI/Web
└── README.md        # Cette documentation
```

## 📁 **Fichiers détaillés**

### **`config.py` - Paramètres de simulation**
Contient tous les paramètres configurables de la simulation :
- **NOMBRE_TOURS** : Nombre de tours de simulation
- **PROBABILITE_EVENEMENT** : Probabilité d'événements aléatoires
- **RECHARGE_BUDGET_MIN/MAX** : Plages de recharge de budget
- **INFLATION_POURCENTAGE_MIN/MAX** : Plages d'inflation
- **REASSORT_QUANTITE_MIN/MAX** : Plages de réassort

### **`mode.py` - Configuration des modes d'exécution**
Gère le basculement entre mode CLI et Web :

```python
# Mode CLI (développement)
CURRENT_MODE = ExecutionMode.CLI

# Mode Web (production)  
CURRENT_MODE = ExecutionMode.WEB
```

**Fonctions disponibles :**
- `get_current_mode()` : Récupère le mode actuel
- `is_cli_mode()` : Vérifie si en mode CLI
- `is_web_mode()` : Vérifie si en mode Web
- `set_mode(mode)` : Change le mode d'exécution

### **`__init__.py` - Exports centralisés**
Exporte toutes les configurations pour faciliter les imports :
```python
from config import NOMBRE_TOURS, PROBABILITE_EVENEMENT
from config import get_current_mode, is_cli_mode
```

## 🔧 **Utilisation**

### **Changer de mode d'exécution :**
```python
from config.mode import set_mode, ExecutionMode

# Passer en mode Web
set_mode(ExecutionMode.WEB)

# Passer en mode CLI
set_mode(ExecutionMode.CLI)
```

### **Vérifier le mode actuel :**
```python
from config.mode import is_cli_mode, is_web_mode

if is_cli_mode():
    print("Mode CLI - Données en mémoire")
elif is_web_mode():
    print("Mode Web - Base de données")
```

### **Récupérer la configuration des Repository :**
```python
from config.mode import get_repository_config

config = get_repository_config()
print(f"Repository produits: {config['produit_repository']}")
```

## 🎯 **Avantages de cette architecture**

### **Centralisation :**
- ✅ Toute la configuration au même endroit
- ✅ Facile à maintenir et modifier
- ✅ Imports simplifiés

### **Flexibilité :**
- ✅ Changement de mode en une ligne
- ✅ Configuration par environnement
- ✅ Tests automatisés

### **Scalabilité :**
- ✅ Ajout facile de nouveaux paramètres
- ✅ Support de multiples environnements
- ✅ Migration transparente

## 📝 **Exemples d'utilisation**

### **Dans les services :**
```python
from config import NOMBRE_TOURS, PROBABILITE_EVENEMENT
from config.mode import is_cli_mode

def run_simulation():
    if is_cli_mode():
        print("Simulation en mode CLI")
    else:
        print("Simulation en mode Web")
    
    for tour in range(NOMBRE_TOURS):
        # Logique de simulation
        pass
```

### **Dans les Repository :**
```python
from config.mode import get_current_mode

def get_repository():
    if get_current_mode() == ExecutionMode.CLI:
        return FakeProduitRepository()
    else:
        return SQLProduitRepository()
```

## 🔄 **Migration vers production**

### **Étape 1 : Configuration de la base de données**
```python
# config/database.py (à créer)
DATABASE_URL = "postgresql://user:password@localhost/tradesim"
```

### **Étape 2 : Changement de mode**
```python
# config/mode.py
CURRENT_MODE = ExecutionMode.WEB
```

### **Étape 3 : Vérification**
```bash
# Tests de validation
pytest tests/ -v

# Test de l'API
uvicorn api.main:app --reload
```

## 📚 **Documentation technique**

### **Pattern de configuration :**
- **Centralisation** : Toute la config dans `config/`
- **Typage** : Utilisation de types Python pour la sécurité
- **Validation** : Vérification des valeurs de configuration
- **Documentation** : Commentaires détaillés pour chaque paramètre

### **Gestion des modes :**
- **Enum** : Types sûrs pour les modes d'exécution
- **Fonctions utilitaires** : API simple pour vérifier le mode
- **Configuration dynamique** : Changement de mode à la volée
- **Tests automatisés** : Validation du bon fonctionnement

## 📝 **Auteur**
Assistant IA - 2024-08-02 