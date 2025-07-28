## Création le 28 Juillet 2025 16h13 (heure local) a Phnom Phen Cambodge
## Ici sera inscrit tout ce que j'ai fait pour le projet



28/08/2025 16h14 :

⏱ Durée estimée :
Démarrage vers 22h50, fin vers 01h00 ➝ ≈ 2h à 2h15 de travail effectif

🧱 Avancées techniques :
Initialisation du projet FastAPI

Création du dépôt Git local

Création d’un environnement virtuel + installation de fastapi, uvicorn, jinja2

Génération du requirements.txt

Démarrage de l’app avec une route / de test

Définition des modèles Pydantic (app/models.py)

Produit avec type, prix, actif, id, etc.

Fournisseur avec stock_produit (Dict[produit_id, stock])

FournisseurComplet pour l’API enrichie

ProduitChezFournisseur pour modéliser le lien avec prix/stock

Entreprise avec budget, types_preferes, strategie

Génération des données fictives (app/data.py)

20 produits, 5 actifs au démarrage

5 fournisseurs chacun avec des stocks et prix personnalisés par produit

3 entreprises avec budgets initiaux, stratégie d’achat, types préférés

Calcul des prix fournisseurs selon formule :
prix_fournisseur = produit.prix * facteur(stock + random)

Création des routes FastAPI (app/main.py)

/ ➝ message d’accueil

/produits ➝ liste des produits actifs

/fournisseurs ➝ liste enrichie avec stock et prix de chaque produit par fournisseur

/entreprises ➝ liste brute des entreprises (budget, stratégie, etc.)

📊 Environ :
4 fichiers principaux (models.py, data.py, main.py, requirements.txt)

≈ 180–200 lignes de code écrites (sans les imports)

Zéro dépendance inutile, tout est propre, structuré, fonctionnel.
