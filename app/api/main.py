#!/usr/bin/env python3
"""
API TradeSim - Interface REST pour TradeSim
==========================================

Ce module fournit l'API REST pour TradeSim.
Il expose les endpoints pour accéder aux données
de manière structurée.

Refactorisation (02/08/2025) :
- Utilise les Repository au lieu d'accès directs aux données
- Code plus modulaire et testable
- Interface commune pour CLI et API

Auteur: Assistant IA
Date: 2024-08-02
"""

from fastapi import FastAPI
from models import Produit, TypeProduit, FournisseurComplet, ProduitChezFournisseur, Entreprise
from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
from models import Fournisseur  # type: ignore

# Initialisation des Repository
produit_repo = ProduitRepository()
fournisseur_repo = FournisseurRepository()
entreprise_repo = EntrepriseRepository()

# Création de l'application FastAPI
app = FastAPI(
    title="TradeSim API",
    description="API REST pour la simulation économique TradeSim",
    version="1.0.0"
)

# Route GET /
@app.get("/")
def read_root():
    """Point d'entrée de l'API"""
    return {
        "message": "Bienvenue sur TradeSim",
        "version": "1.0.0",
        "endpoints": {
            "produits": "/produits",
            "fournisseurs": "/fournisseurs", 
            "entreprises": "/entreprises"
        }
    }

@app.get("/produits", response_model=list[Produit])
def get_produits():
    """
    Récupère tous les produits actifs.
    
    Refactorisation (02/08/2025) :
    - Utilise ProduitRepository au lieu d'accès direct aux données
    """
    return [p for p in produit_repo.get_all() if p.actif]

@app.get("/fournisseurs", response_model=list[FournisseurComplet])
def get_fournisseurs_enrichis():
    """
    Récupère tous les fournisseurs avec leurs produits enrichis.
    
    Refactorisation (02/08/2025) :
    - Utilise FournisseurRepository et ProduitRepository
    - Gestion des prix à migrer vers un service plus tard
    """
    result = []

    for fournisseur in fournisseur_repo.get_all():
        produits = []

        for produit_id, stock in fournisseur.stock_produit.items():
            # Récupérer le produit depuis le repository
            produit = produit_repo.get_by_id(produit_id)
            nom_produit = produit.nom if produit else "???"
            
            # TODO: Migrer vers un service de gestion des prix
            # Pour l'instant, on utilise une fonction temporaire
            from services.simulateur import get_prix_produit_fournisseur
            prix = get_prix_produit_fournisseur(produit_id, fournisseur.id)

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
    """
    Récupère toutes les entreprises.
    
    Refactorisation (02/08/2025) :
    - Utilise EntrepriseRepository au lieu d'accès direct aux données
    """
    return entreprise_repo.get_all()