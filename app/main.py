

from fastapi import FastAPI
from models import Produit, TypeProduit, FournisseurComplet, ProduitChezFournisseur, Entreprise
from data import fake_produits_db, fake_fournisseurs_db, fake_entreprises_db, prix_par_fournisseur
from models import Fournisseur  # type: ignore


# Création de l'application FastAPI
app = FastAPI()

# Route GET /
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur TradeSim"}

@app.get("/produits", response_model=list[Produit])
def get_produits():
    return [p for p in fake_produits_db if p.actif]

@app.get("/fournisseurs", response_model=list[FournisseurComplet])
def get_fournisseurs_enrichis():
    result = []

    for fournisseur in fake_fournisseurs_db:
        produits = []

        for produit_id, stock in fournisseur.stock_produit.items():
            nom_produit = next((p.nom for p in fake_produits_db if p.id == produit_id), "???")
            prix = prix_par_fournisseur.get((produit_id, fournisseur.id), None)

            produits.append(ProduitChezFournisseur(
                produit_id=produit_id,
                nom=nom_produit,
                stock=stock,
                prix_unitaire=prix
            ))

        result.append(FournisseurComplet(
            id=fournisseur.id,
            nom_entreprise=fournisseur.nom_entreprise,
            pays=fournisseur.pays,
            produits=produits
        ))

    return result



@app.get("/entreprises", response_model=list[Entreprise])
def get_entreprises():
    return fake_entreprises_db