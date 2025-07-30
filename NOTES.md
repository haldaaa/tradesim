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





29/07/2025 17h31 PP Cambodge

Durée de la session : ~2h10 (début vers 15h05 - fin vers 17h15 heure Cambodge)

🎯 Objectif principal :
Mise en place du lancement dynamique de la simulation avec nombre de tours définissable, en vue d'une version future tournant en mode infini.

✅ Ce qui a été fait aujourd'hui :
Création du fichier simulate.py :

Permet de lancer la simulation via CLI : python simulate.py --tours 10

Gestion propre du dossier app/

Prévu : support du mode infini plus tard

Ajout d’un log humain clair en cas de tour sans achat :

Exemple : Aucun achat effectué - Tour vide, on continue.

Implémenté dans simulateur.py, tick incrémental + message dans log humain ET JSON

Ajout des timestamps dans les logs (simulateur.py) :

timestamp (format ISO) et timestamp_humain (lisible)

Ajouté dans chaque entrée JSON et dans les logs humains

Ajout du type de produit dans les logs JSON et humains

Nettoyage de la structure de logs :

Suppression du doublon app/logs/

Tous les logs sont désormais dans logs/ à la racine

Gestion via config.py avec BASE_DIR propre

📁 Fichiers modifiés ou créés :
simulate.py ✅

simulateur.py ✅ (refactor complet + commentaires)

config.py ✅ (ajout de BASE_DIR, FICHIER_LOG, FICHIER_LOG_HUMAIN)

logs/simulation.jsonl (généré)

logs/simulation_humain.log (généré)




29/07/2025

 29 juillet 2025
🎯 Objectif de la journée
Mettre en place un système d’événements cycliques dans la simulation TradeSim, avec une architecture modulaire, des logs complets, et un comportement réaliste.

🔧 Modules implémentés / modifiés
1. cycle.py
Orchestrateur principal des événements cycliques.

Appelé à chaque tick (tous les X_TICKS_EVENT) dans simulateur.py.

Déclenche les événements suivants :

Rechargement de budget

Réassort de stock

Inflation des prix

Variation de disponibilité

2. recharge_budget.py
Recharge aléatoirement le budget d’un sous-ensemble d’entreprises.

Montant aléatoire entre RECHARGE_BUDGET_MIN et RECHARGE_BUDGET_MAX.

3. reassort.py
Réapprovisionne certains produits actifs avec une quantité aléatoire.

Seuls les produits actif=True sont concernés.

4. inflation.py
Applique une inflation temporaire sur un produit ou une catégorie.

Le prix revient progressivement à la normale.

Les produits déjà touchés conservent un bonus d’inflation lors d'une future hausse.

5. variation_disponibilite.py
Active ou désactive aléatoirement certains produits.

Simule des ruptures ou retours en stock.

📦 Architecture des logs
Logs généraux :
logs/simulation.jsonl → log machine en JSONL

logs/simulation_humain.log → log humain lisible

Logs d’événements (dédiés) :
logs/events.jsonl → tous les événements en JSONL

logs/events_humain.log → tous les événements en clair

Tous les événements globaux sont marqués avec le tag [EVENT].

🛠️ Fichier event_logger.py (central)
Fonction log_evenement_json() → écrit les logs JSON avec tag [EVENT]

Fonction log_evenement_humain() → écrit les logs texte humains

Utilisé par tous les modules d’événement


