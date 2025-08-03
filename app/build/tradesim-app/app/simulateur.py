#!/usr/bin/env python3
"""
Simulateur TradeSim - Orchestration de la simulation
===================================================

Ce module orchestre la simulation complète de TradeSim.
Il gère les tours de simulation, les achats, les événements et les logs.

Refactorisation (02/08/2025) :
- Utilise les Repository au lieu d'accès directs aux données
- Code plus modulaire et testable
- Interface commune pour CLI et API

Auteur: Assistant IA
Date: 2024-08-02
"""

import random
import json
import os
from datetime import datetime
from typing import List, Dict, Any

# Imports des Repository (nouvelle architecture)
from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
from models import Produit, Fournisseur, Entreprise, TypeProduit
from config import (
    N_ENTREPRISES_PAR_TOUR,
    FICHIER_LOG,
    FICHIER_LOG_HUMAIN,
    TICK_INTERVAL_EVENT,
    PROBABILITE_EVENEMENT,
    PROBABILITE_SELECTION_ENTREPRISE,
)
from events.inflation import appliquer_inflation
from events.variation_disponibilite import appliquer_variation_disponibilite
from events.reassort import evenement_reassort
from events.recharge_budget import appliquer_recharge_budget

# Création des répertoires de logs
os.makedirs(os.path.dirname(FICHIER_LOG), exist_ok=True)
os.makedirs(os.path.dirname(FICHIER_LOG_HUMAIN), exist_ok=True)

# Définition des fichiers de logs spéciaux event
EVENT_LOG_JSON = os.path.join(os.path.dirname(FICHIER_LOG), "event.jsonl")
EVENT_LOG_HUMAIN = os.path.join(os.path.dirname(FICHIER_LOG_HUMAIN), "event.log")
os.makedirs(os.path.dirname(EVENT_LOG_JSON), exist_ok=True)
os.makedirs(os.path.dirname(EVENT_LOG_HUMAIN), exist_ok=True)

# Initialisation des Repository
produit_repo = ProduitRepository()
fournisseur_repo = FournisseurRepository()
entreprise_repo = EntrepriseRepository()

# Gestion des prix (à migrer vers un service plus tard)
prix_par_fournisseur = {}

def get_prix_produit_fournisseur(produit_id: int, fournisseur_id: int) -> float | None:
    """
    Retourne le prix d'un produit chez un fournisseur.
    
    Args:
        produit_id (int): ID du produit
        fournisseur_id (int): ID du fournisseur
        
    Returns:
        float | None: Prix du produit ou None si non défini
    """
    return prix_par_fournisseur.get((produit_id, fournisseur_id))

def set_prix_produit_fournisseur(produit_id: int, fournisseur_id: int, prix: float):
    """
    Définit le prix d'un produit chez un fournisseur.
    
    Args:
        produit_id (int): ID du produit
        fournisseur_id (int): ID du fournisseur
        prix (float): Prix du produit
    """
    prix_par_fournisseur[(produit_id, fournisseur_id)] = prix

# Fonction utilitaire pour logguer les events dans tous les fichiers
def log_event(logs: List[Dict[str, Any]], event_type: str):
    """
    Logge les événements dans tous les fichiers appropriés.
    
    Args:
        logs (List[Dict[str, Any]]): Liste des logs à écrire
        event_type (str): Type d'événement
    """
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

def simulation_tour(verbose: bool = False):
    """
    Lance une simulation pour un seul tick :
    - Sélection d'entreprises aléatoires
    - Tentative d'achat selon leur stratégie
    - Logs humains et JSON enrichis (même si rien ne se passe)
    
    Refactorisation (02/08/2025) :
    - Utilise les Repository au lieu d'accès directs aux données
    """
    global tick
    tick += 1
    horodatage_iso = datetime.utcnow().isoformat()
    horodatage_humain = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Récupérer toutes les entreprises via le Repository
    entreprises = entreprise_repo.get_all()
    
    # Sélection des entreprises avec probabilité
    entreprises_selectionnees = []
    for entreprise in entreprises:
        if random.random() < PROBABILITE_SELECTION_ENTREPRISE:
            entreprises_selectionnees.append(entreprise)

    actions_realisees = 0

    for entreprise in entreprises_selectionnees:
        if entreprise.strategie == "moins_cher":
            produits_disponibles = get_produits_disponibles()
            if not produits_disponibles:
                continue
            # Filtrer les produits que l'entreprise peut vraiment acheter
            produits_achetables = []
            for produit in produits_disponibles:
                fournisseurs_possibles = get_fournisseurs_avec_stock(produit.id)
                if fournisseurs_possibles:
                    # Vérifier si au moins un fournisseur a un prix abordable
                    for fournisseur in fournisseurs_possibles:
                        prix = get_prix_produit_fournisseur(produit.id, fournisseur.id)
                        if prix and entreprise.budget >= prix:
                            produits_achetables.append(produit)
                            break
            
            if not produits_achetables:
                if verbose:
                    print(f"😴 {entreprise.nom} (budget: {entreprise.budget:.2f}€) - Aucun produit achetable trouvé")
                continue
                
            produit_choisi = min(produits_achetables, key=lambda p: get_prix_minimum(p.id))
            if acheter_produit(entreprise, produit_choisi, horodatage_iso, horodatage_humain, "moins_cher", verbose):
                actions_realisees += 1
                if verbose:
                    print(f"💰 {entreprise.nom} achète {produit_choisi.nom} (stratégie: moins cher)")

        elif entreprise.strategie == "par_type":
            types_voulus = entreprise.types_preferes
            produits_filtres = [p for p in produit_repo.get_all() if p.type in types_voulus and p.actif]
            if not produits_filtres:
                continue
            # Filtrer les produits que l'entreprise peut vraiment acheter
            produits_achetables = []
            for produit in produits_filtres:
                fournisseurs_possibles = get_fournisseurs_avec_stock(produit.id)
                if fournisseurs_possibles:
                    # Vérifier si au moins un fournisseur a un prix abordable
                    for fournisseur in fournisseurs_possibles:
                        prix = get_prix_produit_fournisseur(produit.id, fournisseur.id)
                        if prix and entreprise.budget >= prix:
                            produits_achetables.append(produit)
                            break
            
            if not produits_achetables:
                if verbose:
                    types_str = ", ".join([t.value for t in types_voulus])
                    print(f"😴 {entreprise.nom} (budget: {entreprise.budget:.2f}€) - Aucun produit de type [{types_str}] achetable trouvé")
                continue
                
            produit_choisi = random.choice(produits_achetables)
            if acheter_produit(entreprise, produit_choisi, horodatage_iso, horodatage_humain, "par_type", verbose):
                actions_realisees += 1
                if verbose:
                    print(f"🎯 {entreprise.nom} achète {produit_choisi.nom} (stratégie: par type)")

    if actions_realisees == 0:
        # Log humain
        log_humain = f"Aucun achat effectué ce tick"
        with open(FICHIER_LOG_HUMAIN, "a", encoding="utf-8") as f:
            f.write(log_humain + "\n")

        # Log JSON
        log_json = {
            "tick": tick,
            "timestamp": horodatage_iso,
            "timestamp_humain": horodatage_humain,
            "aucune_action": True,
            "message": "Aucun achat effectué ce tick"
        }
        with open(FICHIER_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_json) + "\n")
        
        if verbose:
            print("😴 Aucune entreprise n'a pu effectuer d'achat ce tick")

    # Déclenchement des events tous les TICK_INTERVAL_EVENT ticks
    if tick % TICK_INTERVAL_EVENT == 0:
        if verbose:
            print(f"\n🎲 [EVENTS] Tentative d'événements (tick {tick})")
        
        # Recharge budget
        if random.random() < PROBABILITE_EVENEMENT["recharge_budget"]:
            logs = appliquer_recharge_budget(tick)
            log_event(logs, "recharge_budget")
            if verbose:
                proba = PROBABILITE_EVENEMENT["recharge_budget"] * 100
                print(f"💸 [EVENT: RECHARGE_BUDGET] Recharge budget déclenchée (probabilité: {proba:.0f}%)")
        
        # Reassort
        if random.random() < PROBABILITE_EVENEMENT["reassort"]:
            logs = evenement_reassort(tick)
            log_event(logs, "reassort")
            if verbose:
                proba = PROBABILITE_EVENEMENT["reassort"] * 100
                print(f"📦 [EVENT: REASSORT] Reassort déclenché (probabilité: {proba:.0f}%)")
        
        # Inflation
        if random.random() < PROBABILITE_EVENEMENT["inflation"]:
            logs = appliquer_inflation(tick)
            log_event(logs, "inflation")
            if verbose:
                proba = PROBABILITE_EVENEMENT["inflation"] * 100
                print(f"🔴 [EVENT: INFLATION] Inflation déclenchée (probabilité: {proba:.0f}%)")
        
        # Variation disponibilité
        if random.random() < PROBABILITE_EVENEMENT["variation_disponibilite"]:
            logs = appliquer_variation_disponibilite(tick)
            log_event(logs, "variation_disponibilite")
            if verbose:
                proba = PROBABILITE_EVENEMENT["variation_disponibilite"] * 100
                print(f"🔄 [EVENT: VARIATION_DISPONIBILITE] Variation disponibilité déclenchée (probabilité: {proba:.0f}%)")
        
        if verbose:
            print("✅ [EVENTS] Fin des événements\n")


def get_produits_disponibles():
    """Retourne les produits actifs disponibles chez au moins un fournisseur"""
    return [
        p for p in produit_repo.get_all()
        if p.id in {pid for f in fournisseur_repo.get_all() for pid in f.stock_produit.keys()}
        and p.actif
    ]

def get_fournisseurs_avec_stock(produit_id):
    """Retourne les fournisseurs qui ont du stock d'un produit donné"""
    return [
        f for f in fournisseur_repo.get_all()
        if produit_id in f.stock_produit and f.stock_produit[produit_id] > 0
    ]

def get_prix_minimum(produit_id):
    """Retourne le prix le plus bas d’un produit chez les fournisseurs disponibles"""
    prix = [
        prix_par_fournisseur.get((produit_id, f.id))
        for f in fournisseur_repo.get_all()
        if produit_id in f.stock_produit and f.stock_produit[produit_id] > 0
        and prix_par_fournisseur.get((produit_id, f.id)) is not None
    ]
    return min(prix) if prix else float('inf')

def acheter_produit(entreprise: Entreprise, produit: Produit, horodatage_iso: str, horodatage_humain: str, strategie: str, verbose: bool = False) -> bool:
    """Effectue un achat si possible. Log les résultats. Retourne True si succès."""
    fournisseurs_possibles = get_fournisseurs_avec_stock(produit.id)
    if not fournisseurs_possibles:
        msg = f"{entreprise.nom} ne peut pas acheter {produit.nom} : produit indisponible (aucun stock chez les fournisseurs)"
        log_json = {
            "tick": tick,
            "timestamp": horodatage_iso,
            "timestamp_humain": horodatage_humain,
            "strategie": strategie,
            "entreprise_id": entreprise.id,
            "entreprise_nom": entreprise.nom,
            "produit_id": produit.id,
            "produit_nom": produit.nom,
            "produit_type": produit.type.value,
            "erreur": "produit_indisponible"
        }
        with open(FICHIER_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_json) + "\n")
        with open(FICHIER_LOG_HUMAIN, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
        if verbose:
            print(f"❌ {msg}")
            print(f"   📊 Budget {entreprise.nom}: {entreprise.budget:.2f}€ | Produit: {produit.nom} | Type: {produit.type.value}")
        return False

    fournisseur = random.choice(fournisseurs_possibles)
    prix = get_prix_produit_fournisseur(produit.id, fournisseur.id)
    if prix is None:
        msg = f"{entreprise.nom} ne peut pas acheter {produit.nom} chez {fournisseur.nom_entreprise} : pas de prix défini"
        log_json = {
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
            "erreur": "pas_de_prix_defini"
        }
        with open(FICHIER_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_json) + "\n")
        with open(FICHIER_LOG_HUMAIN, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
        if verbose:
            print(f"❌ {msg}")
            print(f"   📊 Budget {entreprise.nom}: {entreprise.budget:.2f}€ | Produit: {produit.nom} | Fournisseur: {fournisseur.nom_entreprise}")
        return False

    quantite_max_possible = int(entreprise.budget // prix)
    if quantite_max_possible <= 0:
        # Calculer la quantité qu'elle aurait voulu acheter (1 par défaut)
        quantite_voulue = 1
        prix_total_voulu = prix * quantite_voulue
        
        msg = f"{entreprise.nom} ne peut pas acheter {quantite_voulue} {produit.nom} ({prix:.2f}€ prix unitaire {produit.nom}) pour un total de {prix_total_voulu:.2f}€ car budget insuffisant (budget entreprise: {entreprise.budget:.2f}€)"
        log_json = {
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
            "prix_unitaire": prix,
            "quantite_voulue": quantite_voulue,
            "prix_total_voulu": prix_total_voulu,
            "budget_disponible": round(entreprise.budget, 2),
            "erreur": "budget_insuffisant"
        }
        with open(FICHIER_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_json) + "\n")
        with open(FICHIER_LOG_HUMAIN, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
        if verbose:
            print(f"❌ {msg}")
            print(f"   📊 Budget {entreprise.nom}: {entreprise.budget:.2f}€ | Prix unitaire: {prix:.2f}€ | Total voulu: {prix_total_voulu:.2f}€")
        return False

    quantite_achat = random.randint(1, min(quantite_max_possible, fournisseur.stock_produit[produit.id]))
    montant_total = round(prix * quantite_achat, 2)

    entreprise.budget = round(entreprise.budget - montant_total, 2)
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
        f"{entreprise.nom} achète {quantite_achat} produits ({prix:.2f}€ prix unitaire {produit.nom}) "
        f"chez le fournisseur {fournisseur.nom_entreprise} pour {montant_total:.2f}€ "
        f"(budget restant entreprise: {entreprise.budget:.2f}€)"
    )
    with open(FICHIER_LOG_HUMAIN, "a", encoding="utf-8") as f:
        f.write(log_humain + "\n")

    # Log verbose détaillé pour l'achat réussi
    if verbose:
        print(f"🎯 {entreprise.nom} achète {quantite_achat} {produit.nom} chez {fournisseur.nom_entreprise}")
        print(f"   💰 Prix unitaire: {prix:.2f}€ | Total: {montant_total:.2f}€ | Budget restant: {entreprise.budget:.2f}€")

    return True
