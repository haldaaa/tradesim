from .models import Produit, TypeProduit, Fournisseur, Entreprise
import random
from typing import List, Dict, Tuple

# -------------------------
# Produits
# -------------------------
noms_produits = [
    "Bois", "Acier", "Planches", "Ours en peluche", "Aspirateur",
    "Lampe", "Clavier", "Moniteur", "Chocolat", "Téléphone",
    "Vélo", "Chaise", "Table", "Sac à dos", "Batterie externe",
    "Câble USB", "Tapis de souris", "Tente", "Bureau", "Écouteurs"
]

types_possibles = [
    TypeProduit.matiere_premiere,
    TypeProduit.consommable,
    TypeProduit.produit_fini
]

fake_produits_db: List[Produit] = []

for i, nom in enumerate(noms_produits):
    produit = Produit(
        id=i + 1,
        nom=nom,
        prix=round(random.uniform(5.0, 500.0), 2),
        actif=(i < 5),
        type=random.choice(types_possibles)
    )
    fake_produits_db.append(produit)

# -------------------------
# Fournisseurs
# -------------------------
noms_fournisseurs = [
    ("PlancheCompagnie", "France"),
    ("TechDistrib", "Allemagne"),
    ("AsieImport", "Chine"),
    ("NordicTools", "Suède"),
    ("ElectroPlus", "Corée du Sud")
]

fake_fournisseurs_db: List[Fournisseur] = []
prix_par_fournisseur: Dict[Tuple[int, int], float] = {}  # (produit_id, fournisseur_id) → prix

for fid, (nom, pays) in enumerate(noms_fournisseurs, start=1):
    stock_produit = {}
    nb_produits = random.randint(3, 8)  # chaque fournisseur propose entre 3 et 8 produits

    produits_attribués = random.sample(fake_produits_db, nb_produits)

    for produit in produits_attribués:
        stock = random.randint(10, 200)
        stock_produit[produit.id] = stock

        # Calcul d’un prix fournisseur spécifique
        prix_base = produit.prix
        facteur = random.uniform(0.9, 1.2) * (100 / (stock + 1))
        prix_fournisseur = round(prix_base * facteur, 2)
        prix_par_fournisseur[(produit.id, fid)] = prix_fournisseur

    fournisseur = Fournisseur(
        id=fid,
        nom_entreprise=nom,
        pays=pays,
        stock_produit=stock_produit
    )

    fake_fournisseurs_db.append(fournisseur)




noms_entreprises = ["MagaToys", "BuildTech", "BioLogix"]
pays_possibles = ["France", "Allemagne", "Canada"]
strategies_possibles = ["moins_cher", "par_type"]

fake_entreprises_db: List[Entreprise] = []

for i in range(3):
    budget_initial = round(random.uniform(1000, 3000), 2)
    types_pref = random.sample(
        [TypeProduit.matiere_premiere, TypeProduit.consommable, TypeProduit.produit_fini],
        k=random.randint(1, 2)
    )

    entreprise = Entreprise(
        id=i + 1,
        nom=noms_entreprises[i],
        pays=pays_possibles[i],
        budget=budget_initial,
        budget_initial=budget_initial,
        types_preferes=types_pref,
        strategie=random.choice(strategies_possibles)
    )

    fake_entreprises_db.append(entreprise)