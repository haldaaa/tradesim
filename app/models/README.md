# Models - Modèles Pydantic
============================

## 📋 **Vue d'ensemble**

Le module `models` contient toutes les définitions d'entités de TradeSim utilisant Pydantic.
Ces modèles définissent la structure des données et assurent la validation automatique.

## 🏗️ **Architecture**

### **Modèles disponibles :**
- `Produit` - Produits disponibles dans la simulation
- `Fournisseur` - Fournisseurs qui vendent les produits
- `Entreprise` - Entreprises qui achètent les produits
- `Transaction` - Transactions entre entreprises et fournisseurs
- `TypeProduit` - Enum des types de produits

### **Avantages Pydantic :**
- ✅ **Validation automatique** des données
- ✅ **Sérialisation JSON** native
- ✅ **Documentation automatique** pour l'API
- ✅ **Type hints** complets
- ✅ **Conversion automatique** des types

## 📁 **Structure**

```
models/
├── __init__.py          # Exports des modèles
├── models.py            # Définitions des modèles Pydantic
└── README.md           # Cette documentation
```

## 🔧 **Utilisation**

### **Import des modèles :**
```python
from models import Produit, Fournisseur, Entreprise, TypeProduit
```

### **Création d'un produit :**
```python
produit = Produit(
    id=1,
    nom="Matériel informatique",
    prix=150.0,
    actif=True,
    type=TypeProduit.matiere_premiere
)
```

### **Validation automatique :**
```python
# Pydantic valide automatiquement les données
try:
    produit = Produit(
        id=1,
        nom="Test",
        prix=-10.0,  # ❌ Prix négatif rejeté
        actif=True,
        type=TypeProduit.matiere_premiere
    )
except ValidationError as e:
    print(f"Erreur de validation: {e}")
```

## 📝 **Modèles détaillés**

### **Produit**
```python
class Produit(BaseModel):
    id: int                    # Identifiant unique
    nom: str                   # Nom du produit
    prix: float                # Prix unitaire
    actif: bool               # Si le produit est disponible
    type: TypeProduit         # Type de produit (enum)
```

### **Fournisseur**
```python
class Fournisseur(BaseModel):
    id: int                    # Identifiant unique
    nom_entreprise: str        # Nom de l'entreprise
    pays: str                 # Pays du fournisseur
    stock_produit: Dict[int, int]  # produit_id → stock
```

### **Entreprise**
```python
class Entreprise(BaseModel):
    id: int                    # Identifiant unique
    nom: str                   # Nom de l'entreprise
    pays: str                 # Pays de l'entreprise
    budget: float             # Budget disponible
    budget_initial: float     # Budget initial
    types_preferes: List[TypeProduit]  # Types préférés
    strategie: str            # Stratégie d'achat
```

### **Transaction**
```python
class Transaction(BaseModel):
    timestamp: datetime        # Horodatage de la transaction
    entreprise_id: int        # ID de l'entreprise acheteuse
    fournisseur_id: int       # ID du fournisseur vendeur
    produit_id: int           # ID du produit acheté
    produit_nom: str          # Nom du produit
    quantite: int             # Quantité achetée
    prix_unitaire: float      # Prix unitaire
    total: float              # Montant total
    succes: bool              # Si la transaction a réussi
    raison_echec: str | None  # Raison de l'échec (si applicable)
```

## 🧪 **Tests**

### **Tests unitaires :**
```bash
pytest tests/unit/test_models.py -v
```

### **Tests de validation :**
```python
def test_produit_validation():
    # Test création valide
    produit = Produit(
        id=1, nom="Test", prix=100.0, 
        actif=True, type=TypeProduit.matiere_premiere
    )
    assert produit.prix > 0
    
    # Test validation prix négatif
    with pytest.raises(ValidationError):
        Produit(id=1, nom="Test", prix=-10.0, 
                actif=True, type=TypeProduit.matiere_premiere)
```

## 🔄 **Migration vers base de données**

### **Avec SQLAlchemy :**
```python
# Les modèles Pydantic peuvent être facilement convertis
# en modèles SQLAlchemy pour la persistance
class ProduitSQL(Base):
    __tablename__ = "produits"
    
    id = Column(Integer, primary_key=True)
    nom = Column(String)
    prix = Column(Float)
    actif = Column(Boolean)
    type = Column(Enum(TypeProduit))
```

### **Conversion automatique :**
```python
# Pydantic → SQLAlchemy
produit_pydantic = Produit(...)
produit_sql = ProduitSQL(**produit_pydantic.dict())

# SQLAlchemy → Pydantic
produit_pydantic = Produit(**produit_sql.__dict__)
```

## 📚 **Exemples d'utilisation**

### **Dans les Repository :**
```python
from models import Produit, TypeProduit

class ProduitRepository:
    def add(self, produit: Produit) -> None:
        # Validation automatique par Pydantic
        self._data.append(produit)
```

### **Dans l'API :**
```python
from fastapi import FastAPI
from models import Produit

app = FastAPI()

@app.post("/produits")
def create_produit(produit: Produit):
    # Validation automatique par FastAPI + Pydantic
    return produit
```

### **Dans les événements :**
```python
from models import Produit, TypeProduit

def appliquer_inflation(produits: List[Produit]):
    for produit in produits:
        if produit.actif:  # Validation automatique
            produit.prix *= 1.1
```

## 🔧 **Configuration**

### **Validation stricte :**
```python
# Dans config.py
PYDANTIC_STRICT = True  # Validation stricte des types
```

### **Validation personnalisée :**
```python
from pydantic import validator

class Produit(BaseModel):
    prix: float
    
    @validator('prix')
    def prix_positif(cls, v):
        if v <= 0:
            raise ValueError('Le prix doit être positif')
        return v
```

## 📝 **Auteur**
Assistant IA - 2024-08-02 