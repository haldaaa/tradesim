# Models - Modèles Pydantic TradeSim
====================================

## 📋 **Vue d'ensemble**

Le dossier `models/` contient tous les modèles de données de TradeSim, définis avec Pydantic. Ces modèles assurent la validation des données et la sérialisation automatique pour l'API.

**MODE CLI (développement) :** Modèles utilisés pour la validation des données en mémoire
**MODE WEB (production) :** Modèles utilisés pour la validation des données de l'API et de la base de données

## 🏗️ **Architecture**

### **Pydantic Framework :**
- **Validation automatique** : Vérification des types et contraintes
- **Sérialisation** : Conversion automatique JSON ↔ Python
- **Documentation** : Génération automatique de la documentation API
- **Type hints** : Support complet des types Python

### **Structure :**
```
models/
├── __init__.py      # Exports des modèles
├── models.py        # Définitions des modèles
└── README.md        # Cette documentation
```

## 📁 **Modèles disponibles**

### **`Produit` - Modèle des produits**
```python
class Produit(BaseModel):
    id: int
    nom: str
    prix: float
    actif: bool
    type: TypeProduit
```

**Champs :**
- **id** : Identifiant unique du produit
- **nom** : Nom du produit (ex: "Bois", "Acier")
- **prix** : Prix en euros (float)
- **actif** : Si le produit est disponible à la vente
- **type** : Type de produit (matiere_premiere, consommable, produit_fini)

**MODE CLI :** Validation des données en mémoire
**MODE WEB :** Validation des données de l'API

### **`Fournisseur` - Modèle des fournisseurs**
```python
class Fournisseur(BaseModel):
    id: int
    nom_entreprise: str
    pays: str
    stock_produit: Dict[int, int]
```

**Champs :**
- **id** : Identifiant unique du fournisseur
- **nom_entreprise** : Nom de l'entreprise fournisseur
- **pays** : Pays d'origine du fournisseur
- **stock_produit** : Dictionnaire {produit_id: quantite}

**MODE CLI :** Stockage en mémoire
**MODE WEB :** Persistance en base de données

### **`Entreprise` - Modèle des entreprises**
```python
class Entreprise(BaseModel):
    id: int
    nom: str
    pays: str
    budget: float
    budget_initial: float
    types_preferes: List[TypeProduit]
    strategie: str
```

**Champs :**
- **id** : Identifiant unique de l'entreprise
- **nom** : Nom de l'entreprise
- **pays** : Pays d'origine de l'entreprise
- **budget** : Budget actuel en euros
- **budget_initial** : Budget initial en euros
- **types_preferes** : Types de produits préférés
- **strategie** : Stratégie d'achat ("moins_cher", "par_type")

**MODE CLI :** Gestion en mémoire
**MODE WEB :** Gestion via API et base de données

### **`TypeProduit` - Enum des types de produits**
```python
class TypeProduit(str, Enum):
    matiere_premiere = "matiere_premiere"
    consommable = "consommable"
    produit_fini = "produit_fini"
```

**Valeurs :**
- **matiere_premiere** : Matériaux de base (bois, acier, etc.)
- **consommable** : Produits consommables (papier, cartouches, etc.)
- **produit_fini** : Produits finis (meubles, électronique, etc.)

## 🔧 **Utilisation**

### **Création d'un produit :**
```python
from models import Produit, TypeProduit

# Création avec validation automatique
produit = Produit(
    id=1,
    nom="Bois",
    prix=25.50,
    actif=True,
    type=TypeProduit.matiere_premiere
)

# Validation automatique
print(produit.dict())  # Sérialisation en dictionnaire
print(produit.json())  # Sérialisation en JSON
```

### **Validation des données :**
```python
from models import Produit

# Validation automatique
try:
    produit = Produit(
        id="invalid",  # Erreur : int attendu
        nom="Bois",
        prix=-10,      # Erreur : prix négatif
        actif=True,
        type="invalid" # Erreur : type invalide
    )
except ValidationError as e:
    print(f"Erreur de validation: {e}")
```

### **Utilisation dans l'API :**
```python
from fastapi import FastAPI
from models import Produit

app = FastAPI()

@app.post("/produits")
def create_produit(produit: Produit):
    # Validation automatique par Pydantic
    return produit
```

## 🎯 **Avantages de cette architecture**

### **Validation automatique :**
- ✅ **Types sûrs** : Validation des types Python
- ✅ **Contraintes** : Validation des valeurs (prix > 0, etc.)
- ✅ **Erreurs claires** : Messages d'erreur détaillés
- ✅ **Documentation** : Génération automatique de la doc API

### **Sérialisation :**
- ✅ **JSON automatique** : Conversion Python ↔ JSON
- ✅ **API compatible** : Intégration native avec FastAPI
- ✅ **Base de données** : Compatible avec SQLAlchemy
- ✅ **Tests simplifiés** : Création facile d'objets de test

### **Extensibilité :**
- ✅ **Ajout de champs** : Facile d'ajouter de nouveaux champs
- ✅ **Validation personnalisée** : Validateurs personnalisés
- ✅ **Héritage** : Réutilisation des modèles
- ✅ **Migration** : Évolution des modèles

## 📝 **Exemples d'utilisation**

### **Dans les Repository :**
```python
from models import Produit, TypeProduit

def create_produit(nom: str, prix: float, type_produit: TypeProduit):
    # Validation automatique
    produit = Produit(
        id=next_id(),
        nom=nom,
        prix=prix,
        actif=True,
        type=type_produit
    )
    return produit
```

### **Dans l'API :**
```python
from fastapi import FastAPI
from models import Produit, Fournisseur, Entreprise

app = FastAPI()

@app.get("/produits", response_model=List[Produit])
def get_produits():
    return produit_repo.get_all()

@app.post("/produits", response_model=Produit)
def create_produit(produit: Produit):
    return produit_repo.add(produit)
```

### **Dans les tests :**
```python
from models import Produit, TypeProduit

def test_produit_validation():
    # Test de validation
    produit = Produit(
        id=1,
        nom="Test",
        prix=100.0,
        actif=True,
        type=TypeProduit.matiere_premiere
    )
    assert produit.nom == "Test"
    assert produit.prix == 100.0
```

## 🔄 **Migration CLI → Web**

### **Étape 1 : Modèles compatibles**
```python
# Les modèles sont déjà compatibles CLI et Web
# Pas de modification nécessaire !
```

### **Étape 2 : Validation renforcée**
```python
from pydantic import validator

class Produit(BaseModel):
    id: int
    nom: str
    prix: float
    actif: bool
    type: TypeProduit
    
    @validator('prix')
    def prix_positif(cls, v):
        if v <= 0:
            raise ValueError('Le prix doit être positif')
        return v
```

### **Étape 3 : Tests de validation**
```python
def test_produit_validation():
    # Test mode CLI
    produit = Produit(...)
    assert produit.prix > 0
    
    # Test mode Web
    response = client.post("/produits", json=produit.dict())
    assert response.status_code == 200
```

## 📚 **Documentation technique**

### **Pydantic Features :**
- **Type validation** : Validation automatique des types
- **Custom validators** : Validateurs personnalisés
- **Field constraints** : Contraintes sur les champs
- **Nested models** : Modèles imbriqués
- **Aliases** : Alias pour les champs

### **API Integration :**
- **FastAPI** : Intégration native avec FastAPI
- **OpenAPI** : Génération automatique de la documentation
- **Request/Response** : Validation automatique des requêtes/réponses
- **Serialization** : Sérialisation automatique JSON

### **Database Integration :**
- **SQLAlchemy** : Compatible avec SQLAlchemy
- **ORM mapping** : Mapping automatique ORM
- **Migration** : Support des migrations de base de données
- **Validation** : Validation avant insertion en base

## 📝 **Auteur**
Assistant IA - 2024-08-02 