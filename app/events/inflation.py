# app/events/inflation.py
"""
Événement : Inflation
---------------------
Augmente temporairement le prix de certains produits ou catégories entières.

Logique :
- Tous les X ticks (intervalle configuré)
- Une chance Y d'être déclenché
- Sélection aléatoire : produit(s) ou catégorie(s)
- L'inflation augmente le prix de 30-60% (configurable)
- Si le produit a subi une inflation dans les 50 derniers tours : pénalité de -15%
- La pénalité dure 50 tours et se reset à chaque nouvelle inflation
- Après 30 tours : début du retour progressif vers prix original + 10%
- Baisse linéaire sur 15 tours pour atteindre le prix final

Exemple complet :
- Prix initial : 100€
- 1ère inflation : +20% → 120€
- Après 30 tours : début du retour progressif
- Baisse linéaire sur 15 tours : 120€ → 118€ → 116€ → ... → 110€
- Prix final : 110€ (prix original + 10%)

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
from datetime import datetime, timezone
from typing import List, Dict, Any

# Imports des Repository (nouvelle architecture)
from repositories import ProduitRepository, FournisseurRepository
from models import TypeProduit
from events.event_logger import log_evenement_json, log_evenement_humain

# Configuration centralisée
from config.config import (
    INFLATION_POURCENTAGE_MIN, INFLATION_POURCENTAGE_MAX,
    PENALITE_INFLATION_PRODUIT_EXISTANT, DUREE_PENALITE_INFLATION,
    DUREE_RETOUR_INFLATION, DUREE_BAISSE_INFLATION, POURCENTAGE_FINAL_INFLATION
)

# Configuration (à déplacer vers config.py plus tard)
INFLATION_CHANCE = 0.5  # 50% de chance d'inflation
INFLATION_MULTIPLIER = 1.4

# État global pour l'inflation avec compteurs de pénalité et retour à la normale
# Structure : {produit_id: {
#     "derniere_inflation_tick": tick,
#     "tours_restants_penalite": 50,
#     "prix_origine": 100.0,
#     "prix_apres_inflation": 120.0,
#     "phase_retour": False,
#     "tick_debut_retour": None
# }}
produits_inflation_timers = {}

def reset_inflation_timers():
    """Réinitialise les timers d'inflation (pour les tests)"""
    global produits_inflation_timers
    produits_inflation_timers = {}
    
    # Nettoyer aussi les anciennes données corrompues
    import gc
    gc.collect()
    print("🧹 Timers d'inflation réinitialisés")
    
    # Nettoyer les anciennes données globales
    global produits_ayant_subi_inflation
    if 'produits_ayant_subi_inflation' in globals():
        produits_ayant_subi_inflation.clear()

def appliquer_retour_normal(tick: int) -> List[Dict[str, Any]]:
    """
    Applique le retour à la normale pour les produits en phase de retour.
    
    Args:
        tick (int): Numéro du tick actuel
        
    Returns:
        List[Dict[str, Any]]: Liste de logs pour jsonl + log_humain
    """
    retour_logs = []
    
    # Initialiser les Repository
    produit_repo = ProduitRepository()
    fournisseur_repo = FournisseurRepository()
    
    for produit_id, timer in list(produits_inflation_timers.items()):
        # Vérifier que timer est bien un dict avec la structure attendue
        if not isinstance(timer, dict) or "derniere_inflation_tick" not in timer:
            print(f"⚠️ Timer invalide pour produit {produit_id}: {timer}")
            continue
            
        if not timer["phase_retour"]:
            # Vérifier si on doit commencer la phase de retour
            derniere_tick = timer["derniere_inflation_tick"]
            if not isinstance(derniere_tick, int):
                print(f"⚠️ derniere_inflation_tick invalide pour produit {produit_id}: {derniere_tick}")
                continue
            tours_ecoules = tick - derniere_tick
            if tours_ecoules >= DUREE_RETOUR_INFLATION:
                timer["phase_retour"] = True
                timer["tick_debut_retour"] = tick
        
        if timer["phase_retour"]:
            # Calculer le prix actuel selon la phase de retour
            tours_retour = tick - timer["tick_debut_retour"]
            
            if tours_retour >= DUREE_BAISSE_INFLATION:
                # Retour terminé, prix final
                prix_final = timer["prix_origine"] * (1 + POURCENTAGE_FINAL_INFLATION / 100)
                nouveau_prix = round(prix_final, 2)
                
                # Supprimer l'entrée car retour terminé
                del produits_inflation_timers[produit_id]
            else:
                # Calculer le prix selon la baisse linéaire
                prix_depart = timer["prix_apres_inflation"]
                prix_final = timer["prix_origine"] * (1 + POURCENTAGE_FINAL_INFLATION / 100)
                
                # Baisse linéaire
                progression = tours_retour / DUREE_BAISSE_INFLATION
                nouveau_prix = round(prix_depart - (prix_depart - prix_final) * progression, 2)
            
            # Mettre à jour le prix dans le repository
            produit = produit_repo.get_by_id(produit_id)
            if produit:
                produit.prix = nouveau_prix
                produit_repo.update(produit)
            
            # Mettre à jour le prix dans le PriceService
            from services.price_service import price_service
            fournisseurs = fournisseur_repo.get_all()
            for fournisseur in fournisseurs:
                if produit_id in fournisseur.stock_produit and fournisseur.stock_produit[produit_id] > 0:
                    price_service.set_prix_produit_fournisseur_force(produit_id, fournisseur.id, nouveau_prix)
            
            # Logs détaillés pour le retour à la normale
            log_retour = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "retour_normal_inflation",
                "tick": tick,
                "produit_id": produit_id,
                "produit_nom": produit.nom if produit else "Inconnu",
                "ancien_prix": timer["prix_apres_inflation"],
                "nouveau_prix": nouveau_prix,
                "prix_origine": timer["prix_origine"],
                "phase_retour": True,
                "tours_retour": tours_retour,
                "retour_termine": tours_retour >= DUREE_BAISSE_INFLATION,
                "pourcentage_baisse": round(((timer["prix_apres_inflation"] - nouveau_prix) / timer["prix_apres_inflation"]) * 100, 1)
            }
            
            # Log humain
            if tours_retour >= DUREE_BAISSE_INFLATION:
                message_humain = f"[RETOUR NORMAL] {produit.nom if produit else 'Produit'} - Retour terminé: {nouveau_prix}€ (prix original + {POURCENTAGE_FINAL_INFLATION}%)"
            else:
                message_humain = f"[RETOUR NORMAL] {produit.nom if produit else 'Produit'} - Baisse: {log_retour['pourcentage_baisse']}% → {nouveau_prix}€ (tour {tours_retour}/{DUREE_BAISSE_INFLATION})"
            
            # Ajouter aux logs
            retour_logs.append(log_retour)
            
            # Logs automatiques (comme l'inflation)
            from events.event_logger import log_evenement_json, log_evenement_humain
            log_evenement_json(log_retour)
            log_evenement_humain(message_humain)
    
    return retour_logs


def appliquer_inflation_et_retour(tick: int) -> List[Dict[str, Any]]:
    """
    Applique l'inflation ET le retour à la normale pour les produits.
    
    Args:
        tick (int): Numéro du tick actuel
        
    Returns:
        List[Dict[str, Any]]: Liste de logs pour jsonl + log_humain
    """
    logs = []
    
    # 1. Appliquer l'inflation (si déclenchée)
    logs_inflation = appliquer_inflation(tick)
    logs.extend(logs_inflation)
    
    # 2. Appliquer le retour à la normale (toujours)
    logs_retour = appliquer_retour_normal(tick)
    logs.extend(logs_retour)
    
    return logs


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

    horodatage = datetime.now(timezone.utc).isoformat()
    horodatage_humain = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    inflation_logs = []
    pourcentages = []

    cible_type = random.choice(["produit", "categorie"])
    type_cible = None  # Initialiser pour éviter l'erreur
    
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
                
                # Vérifier si le produit a subi une inflation récemment (pénalité active)
                penalite_active = False
                if produit_id in produits_inflation_timers:
                    timer = produits_inflation_timers[produit_id]
                    if isinstance(timer, dict) and "derniere_inflation_tick" in timer:
                        derniere_tick = timer["derniere_inflation_tick"]
                        if isinstance(derniere_tick, int):
                            tours_ecoules = tick - derniere_tick
                            
                            if tours_ecoules <= DUREE_PENALITE_INFLATION:
                                penalite_active = True
                                # Reset du compteur à 50 tours
                                timer["tours_restants_penalite"] = DUREE_PENALITE_INFLATION
                            else:
                                # Pénalité expirée, supprimer l'entrée
                                del produits_inflation_timers[produit_id]
                        else:
                            print(f"⚠️ derniere_inflation_tick invalide pour produit {produit_id}: {derniere_tick}")
                            tours_ecoules = 0
                    else:
                        print(f"⚠️ Timer invalide pour produit {produit_id}: {timer}")
                        tours_ecoules = 0
                
                # Calculer le pourcentage d'inflation
                pourcentage_inflation = random.uniform(INFLATION_POURCENTAGE_MIN, INFLATION_POURCENTAGE_MAX)
                
                # Appliquer la pénalité si nécessaire
                if penalite_active:
                    pourcentage_inflation -= PENALITE_INFLATION_PRODUIT_EXISTANT
                    pourcentage_inflation = max(pourcentage_inflation, 5)  # Minimum 5% d'inflation
                
                multiplicateur = 1 + (pourcentage_inflation / 100)
                
                ancien_prix = prix_base
                nouveau_prix = round(prix_base * multiplicateur, 2)
                
                # Marquer le produit comme affecté et enregistrer les informations
                # Si le produit était en phase de retour, on l'arrête et on reset la pénalité
                produits_inflation_timers[produit_id] = {
                    "derniere_inflation_tick": tick,
                    "tours_restants_penalite": DUREE_PENALITE_INFLATION,
                    "prix_origine": ancien_prix,
                    "prix_apres_inflation": nouveau_prix,
                    "phase_retour": False,  # Nouvelle inflation arrête le retour
                    "tick_debut_retour": None
                }

                # Trouver le produit pour les informations
                produit = produit_repo.get_by_id(produit_id)
                
                # Mettre à jour le prix du produit dans le repository ET dans le PriceService
                if produit:
                    produit.prix = nouveau_prix
                    produit_repo.update(produit)
                
                # Mettre à jour le prix dans le PriceService
                from services.price_service import price_service
                price_service.set_prix_produit_fournisseur_force(produit_id, fournisseur.id, nouveau_prix)
                
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
                    "penalite_active": penalite_active,
                    "pourcentage_inflation_original": pourcentage_inflation + PENALITE_INFLATION_PRODUIT_EXISTANT if penalite_active else pourcentage_inflation
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
                f"💰 Tour {tick} - INFLATION {produit_cible_nom}: {ancien_prix}€ → {nouveau_prix}€ (+{pourcentage_produit_cible}%)"
            )
        else:
            # Plusieurs prix modifiés, afficher les statistiques
            type_display = type_cible.value if type_cible else "Catégorie"
            message_humain = (
                f"💰 Tour {tick} - INFLATION {type_display}: {len(inflation_logs)} produits affectés (prix +{min_pourcentage}% à +{max_pourcentage}%)"
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
