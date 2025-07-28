from pydantic import BaseModel
from enum import Enum
from typing import Dict, List


class TypeProduit(str, Enum):
    produit_fini = "produit_fini"
    consommable = "consommable"
    matiere_premiere = "matiere_premiere"


class Produit(BaseModel):
    id: int
    nom: str
    prix: float
    actif: bool
    type: TypeProduit


class Fournisseur(BaseModel):
    id: int
    nom_entreprise: str
    pays: str
    stock_produit: Dict[int, int]  # produit_id → stock possédé


class ProduitChezFournisseur(BaseModel):
    produit_id: int
    nom: str
    stock: int
    prix_unitaire: float


class FournisseurComplet(BaseModel):
    id: int
    nom_entreprise: str
    pays: str
    produits: List[ProduitChezFournisseur]


class Entreprise(BaseModel):
    id: int
    nom: str
    pays: str
    budget: float
    budget_initial: float
    types_preferes: List[TypeProduit]
    strategie: str  # "moins_cher" ou "par_type"
