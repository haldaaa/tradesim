import random
import json
import os
from datetime import datetime

from app.data import (
    fake_entreprises_db,
    fake_fournisseurs_db,
    fake_produits_db,
    prix_par_fournisseur
)
from app.models import Produit, Fournisseur, Entreprise, TypeProduit
from app.config import (
    N_ENTREPRISES_PAR_TOUR,
    FICHIER_LOG,
    FICHIER_LOG_HUMAIN,
)

os.makedirs(os.path.dirname(FICHIER_LOG), exist_ok=True)
os.makedirs(os.path.dirname(FICHIER_LOG_HUMAIN), exist_ok=True)

tick = 0

def simulation_tour():
    """
    Lance une simulation pour un seul tick :
    - Sélection d'entreprises aléatoires
    - Tentative d'achat selon leur stratégie
    - Logs humains et JSON enrichis (même si rien ne se passe)
    """
    global tick
    tick += 1
    horodatage_iso = datetime.utcnow().isoformat()
    horodatage_humain = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    entreprises_selectionnees = random.sample(
        fake_entreprises_db,
        k=min(N_ENTREPRISES_PAR_TOUR, len(fake_entreprises_db))
    )

    actions_realisees = 0

    for entreprise in entreprises_selectionnees:
        if entreprise.strategie == "moins_cher":
            produits_disponibles = get_produits_disponibles()
            if not produits_disponibles:
                continue
            produit_choisi = min(produits_disponibles, key=lambda p: get_prix_minimum(p.id))
            if acheter_produit(entreprise, produit_choisi, horodatage_iso, horodatage_humain, "moins_cher"):
                actions_realisees += 1

        elif entreprise.strategie == "par_type":
            types_voulus = entreprise.types_preferes
            produits_filtres = [p for p in fake_produits_db if p.type in types_voulus and p.actif]
            if not produits_filtres:
                continue
            produit_choisi = random.choice(produits_filtres)
            if acheter_produit(entreprise, produit_choisi, horodatage_iso, horodatage_humain, "par_type"):
                actions_realisees += 1

    if actions_realisees == 0:
        # Log humain
        log_humain = f"[{horodatage_humain}] (tick {tick}) Aucun achat effectué - Tour vide, on continue."
        with open(FICHIER_LOG_HUMAIN, "a", encoding="utf-8") as f:
            f.write(log_humain + "\n")

        # Log JSON
        log_json = {
            "tick": tick,
            "timestamp": horodatage_iso,
            "timestamp_humain": horodatage_humain,
            "aucune_action": True,
            "message": "Aucune entreprise n’a agi à ce tick."
        }
        with open(FICHIER_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_json) + "\n")


def get_produits_disponibles():
    """Retourne les produits actifs disponibles chez au moins un fournisseur"""
    return [
        p for p in fake_produits_db
        if p.id in {pid for f in fake_fournisseurs_db for pid in f.stock_produit.keys()}
        and p.actif
    ]

def get_prix_minimum(produit_id):
    """Retourne le prix le plus bas d’un produit chez les fournisseurs disponibles"""
    prix = [
        prix_par_fournisseur.get((produit_id, f.id))
        for f in fake_fournisseurs_db
        if produit_id in f.stock_produit and f.stock_produit[produit_id] > 0
        and prix_par_fournisseur.get((produit_id, f.id)) is not None
    ]
    return min(prix) if prix else float('inf')

def acheter_produit(entreprise: Entreprise, produit: Produit, horodatage_iso: str, horodatage_humain: str, strategie: str) -> bool:
    """Effectue un achat si possible. Log les résultats. Retourne True si succès."""
    fournisseurs_possibles = [
        f for f in fake_fournisseurs_db
        if produit.id in f.stock_produit and f.stock_produit[produit.id] > 0
    ]
    if not fournisseurs_possibles:
        return False

    fournisseur = random.choice(fournisseurs_possibles)
    prix = prix_par_fournisseur[(produit.id, fournisseur.id)]
    quantite_max_possible = int(entreprise.budget // prix)
    if quantite_max_possible <= 0:
        return False

    quantite_achat = random.randint(1, min(quantite_max_possible, fournisseur.stock_produit[produit.id]))
    montant_total = round(prix * quantite_achat, 2)

    entreprise.budget -= montant_total
    fournisseur.stock_produit[produit.id] -= quantite_achat

    # Log JSON
    log_entry = {
        "tick": tick,
        "timestamp": horodatage_iso,
        "timestamp_humain": horodatage_humain,
        "strategie": strategie,
        "entreprise_id": entreprise.id,
        "entreprise_nom": entreprise.nom,
        "produit_id": produit.id,
        "produit_nom": produit.nom,
        "produit_type": produit.type.value,
        "fournisseur_id": fournisseur.id,
        "fournisseur_nom": fournisseur.nom_entreprise,
        "quantite": quantite_achat,
        "prix_unitaire": prix,
        "montant_total": montant_total,
        "budget_restant": round(entreprise.budget, 2)
    }
    with open(FICHIER_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Log humain lisible
    log_humain = (
        f"[{horodatage_humain}] (tick {tick}) "
        f"{entreprise.nom} a acheté {quantite_achat}x {produit.nom} ({produit.type.value}) "
        f"chez {fournisseur.nom_entreprise} à {prix:.2f}€ (total: {montant_total:.2f}€) "
        f"[budget restant: {entreprise.budget:.2f}€] [stratégie: {strategie}]"
    )
    with open(FICHIER_LOG_HUMAIN, "a", encoding="utf-8") as f:
        f.write(log_humain + "\n")

    return True
