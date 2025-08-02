# Repositories - Accès aux données
================================

## 📋 **Vue d'ensemble**

Le module `repositories` implémente le pattern Repository pour gérer l'accès aux données de TradeSim. Cette couche d'abstraction permet de séparer la logique métier de la gestion des données.

## 🏗️ **Architecture**

### **Pattern Repository :**
- **Interface commune** pour tous les accès aux données
- **Implémentations multiples** : In-memory (tests) + Base de données (prod)
- **Code identique** pour CLI et Web

### **Avantages :**
- ✅ **Testabilité** : Facile de mocker les données
- ✅ **Flexibilité** : Changement de source de données transparent
- ✅ **Maintenabilité** : Logique métier séparée de l'accès aux données
- ✅ **Scalabilité** : Ajout de nouvelles sources de données facile

## 📁 **Structure**

```
repositories/
├── __init__.py              # Exports des Repository
├── base_repository.py       # Interface commune
├── produit_repository.py    # Gestion des produits
├── fournisseur_repository.py # Gestion des fournisseurs
├── entreprise_repository.py # Gestion des entreprises
└── README.md               # Cette documentation
```

## 🔧 **Utilisation**

### **Interface commune :**
```python
from repositories.produit_repository import ProduitRepository

# Utilisation identique, quelle que soit l'implémentation
repo = ProduitRepository()
produits = repo.get_all()
produit = repo.get_by_id(1)
```

### **Implémentations :**
```python
# In-memory (pour les tests)
repo = FakeProduitRepository()

# SQL (pour la production)
repo = SQLProduitRepository()
```

## 📝 **Méthodes communes**

Tous les Repository implémentent ces méthodes :

### **CRUD de base :**
- `get_all()` - Récupérer tous les éléments
- `get_by_id(id)` - Récupérer par ID
- `add(entity)` - Ajouter un élément
- `update(entity)` - Mettre à jour un élément
- `delete(id)` - Supprimer un élément

### **Méthodes spécifiques :**
- `get_actifs()` - Récupérer les éléments actifs
- `get_by_type(type)` - Filtrer par type
- `get_by_strategie(strategie)` - Filtrer par stratégie

## 🔄 **Migration vers base de données**

### **Étape 1 :** Créer l'implémentation SQL
```python
class SQLProduitRepository(ProduitRepository):
    def get_all(self) -> List[Produit]:
        return db.query(Produit).all()
```

### **Étape 2 :** Changer l'implémentation
```python
# Avant (tests)
repo = FakeProduitRepository()

# Après (production)
repo = SQLProduitRepository()
```

### **Étape 3 :** Le reste du code reste identique !

## 🧪 **Tests**

### **Tests unitaires :**
```bash
pytest tests/unit/test_repositories.py -v
```

### **Tests d'intégration :**
```bash
pytest tests/integration/test_repositories_integration.py -v
```

## 📚 **Exemples d'utilisation**

### **Dans les services :**
```python
from repositories.produit_repository import ProduitRepository

class SimulationService:
    def __init__(self):
        self.produit_repo = ProduitRepository()
    
    def get_produits_disponibles(self):
        return self.produit_repo.get_actifs()
```

### **Dans les événements :**
```python
from repositories.produit_repository import ProduitRepository

def appliquer_inflation(tick: int):
    repo = ProduitRepository()
    produits = repo.get_actifs()
    # Logique d'inflation...
```

## 🔧 **Configuration**

### **Mode de développement :**
```python
# Utilise les implémentations Fake
REPOSITORY_MODE = "fake"
```

### **Mode de production :**
```python
# Utilise les implémentations SQL
REPOSITORY_MODE = "sql"
```

## 📝 **Auteur**
Assistant IA - 2024-08-02 