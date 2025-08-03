# app/events/inflation.py
"""
Événement : Inflation
---------------------
Augmente temporairement le prix de certains produits ou catégories entières.

Logique :
- Tous les X ticks (intervalle configuré)
- Une chance Y d’être déclenché
- Sélection aléatoire : produit(s) ou catégorie(s)
- L’inflation augmente le prix de +40%
- Si le produit/catégorie a déjà été affecté(e) : +15% de bonus
- Après X ticks, retour progressif à un prix proche de l’original (+/- 3 à 15%)

Logs :
- Ajoute un log [EVENT] dans simulation_humain.log et simulation.jsonl
- Ajoute un log dédié dans events_humain.log et events.jsonl
"""

import random
import json
from datetime import datetime

from data import (
    fake_produits_db,
    prix_par_fournisseur,
    produits_ayant_subi_inflation,
    fake_fournisseurs_db
)
from models import TypeProduit
from events.event_logger import log_evenement_json, log_evenement_humain

INFLATION_CHANCE = 0.5  # 50% de chance d'inflation
INFLATION_MULTIPLIER = 1.4
BONUS_MULTIPLIER = 1.15

def appliquer_inflation(tick: int):
    """
    Applique une inflation sur un ou plusieurs produits ou types de produits.
    Retourne une liste de logs (dictionnaires) pour jsonl + log_humain.
    """
    if random.random() > INFLATION_CHANCE:
        return []  # Pas d'inflation ce tick

    horodatage = datetime.utcnow().isoformat()
    horodatage_humain = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    inflation_logs = []
    pourcentages = []

    cible_type = random.choice(["produit", "categorie"])
    if cible_type == "produit":
        produits_eligibles = [p for p in fake_produits_db if p.actif]
        if not produits_eligibles:
            return []
        produit_cible = random.choice(produits_eligibles)
        cible_ids = [produit_cible.id]
        description = f"Produit ciblé : {produit_cible.nom}"
    else:
        type_cible = random.choice(list(TypeProduit))
        produits_eligibles = [p for p in fake_produits_db if p.type == type_cible and p.actif]
        if not produits_eligibles:
            return []
        cible_ids = [p.id for p in produits_eligibles]
        description = f"Catégorie ciblée : {type_cible.value}"

    for produit_id in cible_ids:
        for (pid, fid), prix in prix_par_fournisseur.items():
            if pid == produit_id:
                multiplicateur = INFLATION_MULTIPLIER
                if produit_id in produits_ayant_subi_inflation:
                    multiplicateur *= BONUS_MULTIPLIER
                ancien_prix = prix
                nouveau_prix = round(prix * multiplicateur, 2)
                prix_par_fournisseur[(pid, fid)] = nouveau_prix
                produits_ayant_subi_inflation.add(produit_id)

                # Trouver les noms du produit et du fournisseur
                produit = next((p for p in fake_produits_db if p.id == pid), None)
                fournisseur = next((f for f in fake_fournisseurs_db if f.id == fid), None)
                
                pourcentage = round(((nouveau_prix - ancien_prix) / ancien_prix) * 100, 1)
                pourcentages.append(pourcentage)

                inflation_logs.append({
                    "produit_id": pid,
                    "produit_nom": produit.nom if produit else "Inconnu",
                    "produit_type": produit.type.value if produit else "Inconnu",
                    "fournisseur_id": fid,
                    "fournisseur_nom": fournisseur.nom_entreprise if fournisseur else "Inconnu",
                    "ancien_prix": ancien_prix,
                    "nouveau_prix": nouveau_prix,
                    "pourcentage_augmentation": pourcentage,
                    "multiplicateur_applique": multiplicateur,
                    "bonus_inflation": produit_id in produits_ayant_subi_inflation
                })

    if inflation_logs:
        # Calcul des statistiques
        min_pourcentage = min(pourcentages) if pourcentages else 0
        max_pourcentage = max(pourcentages) if pourcentages else 0
        moy_pourcentage = round(sum(pourcentages) / len(pourcentages), 1) if pourcentages else 0
        
        # Trouver le produit ciblé pour afficher son pourcentage
        produit_cible_nom = "Inconnu"
        pourcentage_produit_cible = 0
        if cible_type == "produit" and len(inflation_logs) > 0:
            produit_cible_nom = inflation_logs[0]["produit_nom"]
            pourcentage_produit_cible = inflation_logs[0]["pourcentage_augmentation"]
        
        if len(inflation_logs) == 1:
            # Un seul prix modifié, afficher directement le pourcentage
            message_humain = (
                f"[INFLATION] {description} - "
                f"Prix modifié: +{pourcentage_produit_cible}%"
            )
        else:
            # Plusieurs prix modifiés, afficher les statistiques
            message_humain = (
                f"[INFLATION] {description} - "
                f"{len(inflation_logs)} prix modifiés | "
                f"Min: +{min_pourcentage}% | Max: +{max_pourcentage}% | Moy: +{moy_pourcentage}%"
            )
        
        log_json = {
            "tick": tick,
            "timestamp": horodatage,
            "timestamp_humain": horodatage_humain,
            "type": "inflation",
            "cible": cible_type,
            "description": description,
            "modifications": inflation_logs,
            "statistiques": {
                "nombre_modifications": len(inflation_logs),
                "pourcentage_min": min_pourcentage,
                "pourcentage_max": max_pourcentage,
                "pourcentage_moyen": moy_pourcentage
            },
            "log_humain": message_humain
        }
        
        return [log_json]
    else:
        return []
