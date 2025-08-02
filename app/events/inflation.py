# app/events/inflation.py
"""
Événement : Inflation
---------------------
Augmente temporairement le prix de certains produits ou catégories entières.

Logique :
- Tous les X ticks (intervalle configuré)
- Une chance Y d'être déclenché
- Sélection aléatoire : produit(s) ou catégorie(s)
- L'inflation augmente le prix de +40%
- Si le produit/catégorie a déjà été affecté(e) : +15% de bonus
- Après X ticks, retour progressif à un prix proche de l'original (+/- 3 à 15%)

Logs :
- Ajoute un log [EVENT] dans simulation_humain.log et simulation.jsonl
- Ajoute un log dédié dans events_humain.log et events.jsonl

Refactorisation (02/08/2025) :
- Utilise les Repository au lieu d'accès directs aux données
- Code plus modulaire et testable
- Interface commune pour CLI et API
"""

import random
import json
from datetime import datetime
from typing import List, Dict, Any

# Imports des Repository (nouvelle architecture)
from repositories import ProduitRepository, FournisseurRepository
from models import TypeProduit
from events.event_logger import log_evenement_json, log_evenement_humain

# Configuration (à déplacer vers config.py plus tard)
INFLATION_CHANCE = 0.5  # 50% de chance d'inflation
INFLATION_MULTIPLIER = 1.4
BONUS_MULTIPLIER = 1.15

# État global pour l'inflation (à migrer vers un service plus tard)
produits_ayant_subi_inflation = set()

def appliquer_inflation(tick: int) -> List[Dict[str, Any]]:
    """
    Applique une inflation sur un ou plusieurs produits ou types de produits.
    
    Args:
        tick (int): Numéro du tick actuel
        
    Returns:
        List[Dict[str, Any]]: Liste de logs pour jsonl + log_humain
        
    Refactorisation (02/08/2025) :
    - Utilise ProduitRepository au lieu de fake_produits_db
    - Utilise FournisseurRepository au lieu de fake_fournisseurs_db
    - Code plus modulaire et testable
    """
    if random.random() > INFLATION_CHANCE:
        return []  # Pas d'inflation ce tick

    # Initialiser les Repository
    produit_repo = ProduitRepository()
    fournisseur_repo = FournisseurRepository()

    horodatage = datetime.utcnow().isoformat()
    horodatage_humain = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    inflation_logs = []
    pourcentages = []

    cible_type = random.choice(["produit", "categorie"])
    
    if cible_type == "produit":
        # Utiliser le Repository pour récupérer les produits actifs
        produits_eligibles = produit_repo.get_actifs()
        if not produits_eligibles:
            return []
        produit_cible = random.choice(produits_eligibles)
        cible_ids = [produit_cible.id]
        description = f"Produit ciblé : {produit_cible.nom}"
    else:
        type_cible = random.choice(list(TypeProduit))
        # Utiliser le Repository pour filtrer par type
        produits_eligibles = produit_repo.get_actifs_by_type(type_cible)
        if not produits_eligibles:
            return []
        cible_ids = [p.id for p in produits_eligibles]
        description = f"Catégorie ciblée : {type_cible.value}"

    # Récupérer tous les fournisseurs pour les prix
    fournisseurs = fournisseur_repo.get_all()
    
    for produit_id in cible_ids:
        for fournisseur in fournisseurs:
            # Vérifier si le fournisseur a ce produit en stock
            if produit_id in fournisseur.stock_produit and fournisseur.stock_produit[produit_id] > 0:
                # Calculer le prix (simulation - à améliorer avec un vrai système de prix)
                prix_base = 100.0  # Prix de base (à améliorer)
                
                multiplicateur = INFLATION_MULTIPLIER
                if produit_id in produits_ayant_subi_inflation:
                    multiplicateur *= BONUS_MULTIPLIER
                
                ancien_prix = prix_base
                nouveau_prix = round(prix_base * multiplicateur, 2)
                
                # Marquer le produit comme affecté
                produits_ayant_subi_inflation.add(produit_id)

                # Trouver le produit pour les informations
                produit = produit_repo.get_by_id(produit_id)
                
                pourcentage = round(((nouveau_prix - ancien_prix) / ancien_prix) * 100, 1)
                pourcentages.append(pourcentage)

                inflation_logs.append({
                    "produit_id": produit_id,
                    "produit_nom": produit.nom if produit else "Inconnu",
                    "produit_type": produit.type.value if produit else "Inconnu",
                    "fournisseur_id": fournisseur.id,
                    "fournisseur_nom": fournisseur.nom_entreprise,
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
