# Config - Configuration centralisée
====================================

## 📋 **Vue d'ensemble**

Le module `config` contient toute la configuration centralisée de TradeSim.
Cette approche permet de modifier facilement les paramètres de l'application
sans avoir à chercher dans plusieurs fichiers.

## 🏗️ **Architecture**

### **Configuration disponible :**
- **Simulation** - Paramètres de la simulation (tours, intervalles, etc.)
- **Logs** - Configuration des fichiers de logs
- **Événements** - Probabilités et paramètres des événements
- **Debug** - Mode debug et options de développement

### **Avantages de la centralisation :**
- ✅ **Facilité de modification** - Un seul endroit pour changer les paramètres
- ✅ **Cohérence** - Tous les modules utilisent la même configuration
- ✅ **Maintenabilité** - Configuration organisée et documentée
- ✅ **Environnements** - Facile de changer entre dev/prod

## 📁 **Structure**

```
config/
├── __init__.py              # Exports de la configuration
├── config.py                # Configuration principale
├── environments/            # Configurations par environnement
│   ├── development.py      # Configuration de développement
│   ├── production.py       # Configuration de production
│   └── testing.py          # Configuration de test
└── README.md               # Cette documentation
```

## 🔧 **Utilisation**

### **Import de la configuration :**
```python
from config import (
    NOMBRE_TOURS,
    N_ENTREPRISES_PAR_TOUR,
    FICHIER_LOG,
    PROBABILITE_EVENEMENT
)
```

### **Utilisation dans le code :**
```python
from config import NOMBRE_TOURS, DEBUG_MODE

def run_simulation():
    tours = NOMBRE_TOURS if not DEBUG_MODE else 10
    # Logique de simulation...
```

### **Modification de la configuration :**
```python
# Dans config.py
NOMBRE_TOURS = 100  # Changer le nombre de tours
DEBUG_MODE = True   # Activer le mode debug
```

## 📝 **Configuration détaillée**

### **Simulation**
```python
# Nombre total de tours à simuler
NOMBRE_TOURS = 100

# Nombre d'entreprises sélectionnées par tour
N_ENTREPRISES_PAR_TOUR = 2

# Durée de pause entre les tours (secondes)
DUREE_PAUSE_ENTRE_TOURS = 0.1

# Probabilité qu'une entreprise soit sélectionnée
PROBABILITE_SELECTION_ENTREPRISE = 0.3
```

### **Logs**
```python
# Fichiers de logs
FICHIER_LOG = "logs/simulation.jsonl"
FICHIER_LOG_HUMAIN = "logs/simulation_humain.log"

# Répertoire des logs
LOG_DIR = "logs"
```

### **Événements**
```python
# Probabilités des événements
PROBABILITE_EVENEMENT = {
    "inflation": 0.3,
    "reassort": 0.4,
    "recharge_budget": 0.5,
    "variation_disponibilite": 0.2
}

# Paramètres des événements
RECHARGE_BUDGET_MIN = 200
RECHARGE_BUDGET_MAX = 600
REASSORT_QUANTITE_MIN = 10
REASSORT_QUANTITE_MAX = 50
```

### **Debug**
```python
# Mode debug
DEBUG_MODE = False

# Niveau de verbosité
VERBOSE_MODE = True
```

## 🧪 **Tests**

### **Tests de configuration :**
```bash
pytest tests/unit/test_config.py -v
```

### **Exemple de test :**
```python
def test_config_validation():
    """Test que la configuration est valide."""
    from config import NOMBRE_TOURS, PROBABILITE_EVENEMENT
    
    # Vérifier que les valeurs sont cohérentes
    assert NOMBRE_TOURS > 0
    assert all(0 <= prob <= 1 for prob in PROBABILITE_EVENEMENT.values())
```

## 🔄 **Environnements**

### **Développement :**
```python
# config/environments/development.py
DEBUG_MODE = True
VERBOSE_MODE = True
NOMBRE_TOURS = 10  # Moins de tours pour les tests
```

### **Production :**
```python
# config/environments/production.py
DEBUG_MODE = False
VERBOSE_MODE = False
NOMBRE_TOURS = 1000  # Plus de tours
```

### **Test :**
```python
# config/environments/testing.py
DEBUG_MODE = True
NOMBRE_TOURS = 5
PROBABILITE_EVENEMENT = {
    "inflation": 1.0,  # Événements forcés pour les tests
    "reassort": 1.0,
    "recharge_budget": 1.0,
    "variation_disponibilite": 1.0
}
```

## 📚 **Exemples d'utilisation**

### **Dans les services :**
```python
from config import NOMBRE_TOURS, PROBABILITE_SELECTION_ENTREPRISE

class SimulationService:
    def run_simulation(self):
        for tour in range(NOMBRE_TOURS):
            # Sélectionner les entreprises
            entreprises = self._select_entreprises(PROBABILITE_SELECTION_ENTREPRISE)
            # Logique de simulation...
```

### **Dans les événements :**
```python
from config import PROBABILITE_EVENEMENT, RECHARGE_BUDGET_MIN, RECHARGE_BUDGET_MAX

def appliquer_recharge_budget():
    if random.random() < PROBABILITE_EVENEMENT["recharge_budget"]:
        montant = random.randint(RECHARGE_BUDGET_MIN, RECHARGE_BUDGET_MAX)
        # Logique de recharge...
```

### **Dans les logs :**
```python
from config import FICHIER_LOG, FICHIER_LOG_HUMAIN

def log_event(event_data):
    # Log JSON
    with open(FICHIER_LOG, "a") as f:
        json.dump(event_data, f)
        f.write("\n")
    
    # Log humain
    with open(FICHIER_LOG_HUMAIN, "a") as f:
        f.write(f"[EVENT] {event_data['message']}\n")
```

## 🔧 **Configuration avancée**

### **Variables d'environnement :**
```python
import os

# Charger depuis les variables d'environnement
DEBUG_MODE = os.getenv("TRADESIM_DEBUG", "False").lower() == "true"
NOMBRE_TOURS = int(os.getenv("TRADESIM_TOURS", "100"))
```

### **Configuration par fichier :**
```python
import json

def load_config_from_file(filename: str):
    """Charge la configuration depuis un fichier JSON."""
    with open(filename, 'r') as f:
        return json.load(f)

# Charger la configuration
config = load_config_from_file("config.json")
NOMBRE_TOURS = config.get("nombre_tours", 100)
```

### **Validation de configuration :**
```python
def validate_config():
    """Valide que la configuration est cohérente."""
    assert NOMBRE_TOURS > 0, "NOMBRE_TOURS doit être positif"
    assert 0 <= PROBABILITE_SELECTION_ENTREPRISE <= 1, "Probabilité invalide"
    
    for event, prob in PROBABILITE_EVENEMENT.items():
        assert 0 <= prob <= 1, f"Probabilité invalide pour {event}"
```

## 📝 **Auteur**
Assistant IA - 2024-08-02 