#!/usr/bin/env python3
"""
Data Generator TradeSim - Générateur de données de test
======================================================

Ce module génère les données initiales pour TradeSim :
- Produits avec types, prix et statut actif/inactif
- Fournisseurs avec stocks et prix spécifiques
- Entreprises avec budgets et stratégies
- Prix par fournisseur pour chaque produit

Responsabilités :
- Génération aléatoire de données cohérentes
- Création de l'écosystème commercial initial
- Configuration des prix et stocks réalistes
- Utilisation du NameManager pour les noms uniques

Note : Ce module est utilisé pour les tests et le développement.
En production, les données viendront de la base de données.

Auteur: Assistant IA
Date: 2024-08-02
Mise à jour: 2025-01-27 - Intégration du NameManager
"""

from models import Produit, TypeProduit, Fournisseur, Entreprise
import random
from typing import List, Dict, Tuple
# Import des données de noms directement
from data.names_data import ENTREPRISES_DATA, FOURNISSEURS_DATA, PRODUITS_DATA
from config import BUDGET_ENTREPRISE_MIN, BUDGET_ENTREPRISE_MAX


# -------------------------
# Produits
# -------------------------
fake_produits_db: List[Produit] = []

# Nombre de produits actifs au début (entre 3 et 8)
nb_produits_actifs = random.randint(3, 8)

# Sélectionner des produits aléatoirement
produits_selectionnes = random.sample(PRODUITS_DATA, 20)  # 20 produits pour commencer

for i, produit_data in enumerate(produits_selectionnes):
    produit = Produit(
        id=i + 1,
        nom=produit_data["nom"],
        prix=round(random.uniform(5.0, 500.0), 2),
        actif=(i < nb_produits_actifs),
        type=TypeProduit(produit_data["type"])
    )
    fake_produits_db.append(produit)

# -------------------------
# Fournisseurs
# -------------------------
fake_fournisseurs_db: List[Fournisseur] = []
prix_par_fournisseur: Dict[Tuple[int, int], float] = {}  # (produit_id, fournisseur_id) → prix

# Sélectionner des fournisseurs aléatoirement
fournisseurs_selectionnes = random.sample(FOURNISSEURS_DATA, 5)  # 5 fournisseurs pour commencer

for fid, fournisseur_data in enumerate(fournisseurs_selectionnes, start=1):
    stock_produit = {}
    nb_produits = random.randint(3, 8)  # chaque fournisseur propose entre 3 et 8 produits

    produits_attribués = random.sample(fake_produits_db, nb_produits)

    for produit in produits_attribués:
        stock = random.randint(10, 200)
        stock_produit[produit.id] = stock

        # Calcul d'un prix fournisseur spécifique
        prix_base = produit.prix
        facteur = random.uniform(0.9, 1.2) * (100 / (stock + 1))
        prix_fournisseur = round(prix_base * facteur, 2)
        prix_par_fournisseur[(produit.id, fid)] = prix_fournisseur

    fournisseur = Fournisseur(
        id=fid,
        nom_entreprise=fournisseur_data["nom"],
        pays=fournisseur_data["pays"],
        continent=fournisseur_data["continent"],
        stock_produit=stock_produit
    )

    fake_fournisseurs_db.append(fournisseur)

# Vérification que tous les prix sont bien définis
# print(f"DEBUG: {len(prix_par_fournisseur)} prix définis")
# print(f"DEBUG: Fournisseurs: {len(fake_fournisseurs_db)}")
# print(f"DEBUG: Produits: {len(fake_produits_db)}")


# -------------------------
# Entreprises
# -------------------------
strategies_possibles = ["moins_cher", "par_type"]

fake_entreprises_db: List[Entreprise] = []

# Sélectionner des entreprises aléatoirement
entreprises_selectionnees = random.sample(ENTREPRISES_DATA, 3)  # 3 entreprises pour commencer

for i, entreprise_data in enumerate(entreprises_selectionnees):
    budget_initial = round(random.uniform(BUDGET_ENTREPRISE_MIN, BUDGET_ENTREPRISE_MAX), 2)
    types_pref = random.sample(
        [TypeProduit.matiere_premiere, TypeProduit.consommable, TypeProduit.produit_fini],
        k=random.randint(1, 2)
    )

    entreprise = Entreprise(
        id=i + 1,
        nom=entreprise_data["nom"],
        pays=entreprise_data["pays"],
        continent=entreprise_data["continent"],
        budget=budget_initial,
        budget_initial=budget_initial,
        types_preferes=types_pref,
        strategie=random.choice(strategies_possibles)
    )

    fake_entreprises_db.append(entreprise)



# Events 
##  Liste des produits ou catégories ayant déjà subi une inflation
produits_ayant_subi_inflation = set()