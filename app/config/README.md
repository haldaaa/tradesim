# ⚙️ Config - Configuration centralisée TradeSim

## 🎯 **BUT DU DOSSIER**
Ce dossier contient toute la configuration centralisée de TradeSim. Un seul point de configuration pour éviter la duplication et assurer la cohérence.

## 🏗️ **ARCHITECTURE**
- **Configuration unique** : Tous les paramètres dans `config.py`
- **Validation** : Fonctions de validation pour les données critiques
- **Constantes** : Valeurs immuables pour éviter la duplication
- **Environnement** : Support pour différents environnements

## 📋 **FICHIERS PRÉSENTS**

### **⚙️ Configuration principale**
- **`config.py`** : Configuration centralisée
  - Paramètres de simulation (tours, probabilités, durées)
  - Configuration des événements (inflation, recharge, reassort)
  - Paramètres de logging et métriques
  - Validation des données (continents, quantités)
  - Constantes pour les budgets et stocks

- **`mode.py`** : Gestion des modes d'exécution
  - Mode CLI vs Web
  - Configuration par environnement

## 🚀 **UTILISATION**

### **Import de configuration**
```python
from config.config import *

# Paramètres de simulation
print(f"Nombre de tours: {NOMBRE_TOURS}")
print(f"Probabilité événement: {PROBABILITE_EVENEMENT}")

# Validation
if validate_continent("Europe"):
    print("Continent valide")
```

### **Configuration des événements**
```python
from config.config import (
    RECHARGE_BUDGET_MIN, RECHARGE_BUDGET_MAX,
    INFLATION_POURCENTAGE_MIN, INFLATION_POURCENTAGE_MAX
)

# Recharge de budget entre 4000 et 8000
montant = random.randint(RECHARGE_BUDGET_MIN, RECHARGE_BUDGET_MAX)
```

### **Validation des données**
```python
from config.config import validate_continent, VALID_CONTINENTS

# Vérifier un continent
continent = "Europe"
if validate_continent(continent):
    print(f"{continent} est valide")

# Liste des continents autorisés
print(f"Continents valides: {VALID_CONTINENTS}")
```

## 📊 **SECTIONS DE CONFIGURATION**

### **🎮 Simulation**
- `NOMBRE_TOURS` : Nombre total de tours
- `N_ENTREPRISES_PAR_TOUR` : Entreprises sélectionnées par tour
- `DUREE_PAUSE_ENTRE_TOURS` : Pause entre tours
- `PROBABILITE_SELECTION_ENTREPRISE` : Probabilité de sélection

### **💰 Budgets et quantités**
- `BUDGET_ENTREPRISE_MIN/MAX` : Budget des entreprises
- `QUANTITE_ACHAT_MIN/MAX` : Quantités d'achat
- `TYPES_PRODUITS_PREFERES_MIN/MAX` : Types préférés

### **📈 Événements**
- `RECHARGE_BUDGET_MIN/MAX` : Recharge de budget
- `REASSORT_QUANTITE_MIN/MAX` : Réassortiment
- `INFLATION_POURCENTAGE_MIN/MAX` : Inflation
- `TICK_INTERVAL_EVENT` : Fréquence des événements

### **📝 Logs et métriques**
- `FICHIER_LOG` : Fichier de log JSON
- `FICHIER_LOG_HUMAIN` : Fichier de log lisible
- `EVENT_LOG_JSON` : Logs d'événements JSON
- `EVENT_LOG_HUMAIN` : Logs d'événements lisible

### **🌍 Géographie**
- `DEFAULT_CONTINENT` : Continent par défaut
- `VALID_CONTINENTS` : Liste des continents autorisés
- `validate_continent()` : Fonction de validation

## 🔧 **MODIFICATION DE CONFIGURATION**

### **Ajouter un paramètre**
```python
# Dans config.py
NOUVEAU_PARAMETRE = 100

# Validation si nécessaire
def validate_nouveau_parametre(valeur: int) -> bool:
    return 0 <= valeur <= 1000
```

### **Modifier un paramètre existant**
```python
# Changer la durée de pause
DUREE_PAUSE_ENTRE_TOURS = 0.5  # Au lieu de 0.1
```

## 🧪 **TESTS**
Les tests de configuration se trouvent dans `tests/unit/test_monitoring_config.py` :
- Validation des paramètres
- Tests des fonctions de validation
- Vérification des types et valeurs

## 📝 **LOGGING**
La configuration utilise les logs définis dans `config.py` :
- Logs de configuration dans `logs/simulation_humain.log`
- Métriques de configuration dans `logs/simulation.jsonl`

## 🔄 **DERNIÈRES MODIFICATIONS**
- **11/08/2025** : Ajout de `validate_continent()` et `VALID_CONTINENTS`
- **11/08/2025** : Constante `DEFAULT_CONTINENT` configurable
- **11/08/2025** : Validation des données géographiques
- **11/08/2025** : Documentation complète des paramètres

## ⚠️ **BONNES PRATIQUES**
1. **Toujours utiliser les constantes** au lieu de valeurs en dur
2. **Valider les données** avec les fonctions de validation
3. **Documenter les nouveaux paramètres** avec des commentaires
4. **Tester les modifications** avant déploiement
5. **Centraliser** toute configuration dans ce dossier

---
**Auteur** : Assistant IA  
**Dernière mise à jour** : 11/08/2025 