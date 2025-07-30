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
    TICK_INTERVAL_EVENT,
    PROBABILITE_EVENEMENT,
)
from app.events.inflation import appliquer_inflation
from app.events.variation_disponibilite import appliquer_variation_disponibilite
from app.events.reassort import evenement_reassort
from app.events.recharge_budget import appliquer_recharge_budget

os.makedirs(os.path.dirname(FICHIER_LOG), exist_ok=True)
os.makedirs(os.path.dirname(FICHIER_LOG_HUMAIN), exist_ok=True)

# Définition des fichiers de logs spéciaux event
EVENT_LOG_JSON = os.path.join(os.path.dirname(FICHIER_LOG), "event.jsonl")
EVENT_LOG_HUMAIN = os.path.join(os.path.dirname(FICHIER_LOG_HUMAIN), "event.log")
os.makedirs(os.path.dirname(EVENT_LOG_JSON), exist_ok=True)
os.makedirs(os.path.dirname(EVENT_LOG_HUMAIN), exist_ok=True)

# Fonction utilitaire pour logguer les events dans tous les fichiers

def log_event(logs, event_type):
    for log in logs:
        # Ajout du type d'event dans le log général
        log_general = dict(log)
        log_general["event_type"] = event_type
        # Log JSON général
        with open(FICHIER_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_general) + "\n")
        # Log humain général
        with open(FICHIER_LOG_HUMAIN, "a", encoding="utf-8") as f:
            f.write(f"[EVENT: {event_type.upper()}] {log['log_humain']}\n")
        # Log JSON event
        with open(EVENT_LOG_JSON, "a", encoding="utf-8") as f:
            f.write(json.dumps(log) + "\n")
        # Log humain event
        with open(EVENT_LOG_HUMAIN, "a", encoding="utf-8") as f:
            f.write(f"[EVENT: {event_type.upper()}] {log['log_humain']}\n")

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
            "message": "Aucune entreprise n'a agi à ce tick."
        }
        with open(FICHIER_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_json) + "\n")

    # Déclenchement des events tous les TICK_INTERVAL_EVENT ticks
    if tick % TICK_INTERVAL_EVENT == 0:
        # Recharge budget
        if random.random() < PROBABILITE_EVENEMENT["recharge_budget"]:
            logs = appliquer_recharge_budget(tick)
            log_event(logs, "recharge_budget")
        # Reassort
        if random.random() < PROBABILITE_EVENEMENT["reassort"]:
            logs = evenement_reassort(tick)
            log_event(logs, "reassort")
        # Inflation
        if random.random() < PROBABILITE_EVENEMENT["inflation"]:
            logs = appliquer_inflation(tick)
            log_event(logs, "inflation")
        # Variation disponibilité
        if random.random() < PROBABILITE_EVENEMENT["variation_disponibilite"]:
            logs = appliquer_variation_disponibilite(tick)
            log_event(logs, "variation_disponibilite")


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
