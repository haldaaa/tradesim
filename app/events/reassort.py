# app/events/reassort.py
"""
Module : reassort.py
---------------------
Gère l'événement de réassort de stock dans la simulation TradeSim.

Fonctionnalités :
- Sélectionne des produits actifs aléatoires pour les réapprovisionner.
- Quantité de réassort générée aléatoirement (paramétrable).
- Loggue l'événement dans deux types de fichiers :
    • logs globaux (simulation.jsonl et simulation_humain.log)
    • logs spécifiques aux événements (events.jsonl et events_humain.log)

Ce module est appelé par cycle.py tous les X ticks selon les règles configurées.

Refactorisation (02/08/2025) :
- Utilise les Repository au lieu d'accès directs aux données
- Code plus modulaire et testable
- Interface commune pour CLI et API

Auteur : Fares & GPT
"""

import random
from datetime import datetime, timezone
from typing import List, Dict, Any

# Imports des Repository (nouvelle architecture)
from repositories import ProduitRepository, FournisseurRepository
from events.event_logger import log_evenement_json, log_evenement_humain
from config import REASSORT_QUANTITE_MIN, REASSORT_QUANTITE_MAX

def evenement_reassort(tick: int) -> List[Dict[str, Any]]:
    """
    Événement de réassort de stock. Réapprovisionne certains produits actifs aléatoirement.
    
    Args:
        tick (int): Numéro du tick actuel
        
    Returns:
        List[Dict[str, Any]]: Liste de logs pour jsonl + log_humain
        
    Refactorisation (02/08/2025) :
    - Utilise ProduitRepository au lieu de fake_produits_db
    - Utilise FournisseurRepository au lieu de fake_fournisseurs_db
    - Code plus modulaire et testable
    """

    # Initialiser les Repository
    produit_repo = ProduitRepository()
    fournisseur_repo = FournisseurRepository()

    horodatage = datetime.now(timezone.utc)
    horodatage_iso = horodatage.isoformat()
    horodatage_humain = horodatage.strftime("%Y-%m-%d %H:%M:%S")

    produits_concernes = []

    # Récupérer tous les produits actifs via le Repository
    produits_actifs = produit_repo.get_actifs()
    
    for produit in produits_actifs:
        if random.random() < 0.3:  # 30% de chance par produit actif
            quantite = random.randint(REASSORT_QUANTITE_MIN, REASSORT_QUANTITE_MAX)
            
            # Récupérer tous les fournisseurs via le Repository
            fournisseurs = fournisseur_repo.get_all()
            fournisseur = random.choice(fournisseurs)
            
            if produit.id in fournisseur.stock_produit:
                fournisseur.stock_produit[produit.id] += quantite
                stock_apres = fournisseur.stock_produit[produit.id]
            else:
                fournisseur.stock_produit[produit.id] = quantite
                stock_apres = quantite

            produits_concernes.append({
                "produit": produit.nom,
                "type": produit.type.value,
                "quantite_ajoutee": quantite,
                "stock_apres": stock_apres,
                "fournisseur": fournisseur.nom_entreprise
            })

    if produits_concernes:
        resume = ", ".join(
            f"{p['quantite_ajoutee']}x {p['produit']} (nouveau stock : {p['stock_apres']})"
            for p in produits_concernes
        )
        
        # Calcul des statistiques
        total_quantite = sum(p['quantite_ajoutee'] for p in produits_concernes)
        fournisseurs_concernes = len(set(p['fournisseur'] for p in produits_concernes))
        
        message_humain = (
            f"[REASSORT] "
            f"[PRODUITS] {len(produits_concernes)} produits réapprovisionnés | "
            f"[QUANTITE] +{total_quantite} unités total | "
            f"[FOURNISSEURS] {fournisseurs_concernes} fournisseurs concernés"
        )
        
        log_json = {
            "tick": tick,
            "timestamp": horodatage_iso,
            "timestamp_humain": horodatage_humain,
            "event_type": "reassort",
            "statistiques": {
                "nb_produits_concernes": len(produits_concernes),
                "total_quantite_ajoutee": total_quantite,
                "nb_fournisseurs_concernes": fournisseurs_concernes
            },
            "details": {"produits": produits_concernes},
            "log_humain": message_humain
        }
        
        return [log_json]
    else:
        return []
