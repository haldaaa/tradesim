#!/usr/bin/env python3
"""
Recharge Stock Fournisseur TradeSim - Événement de recharge des stocks
=====================================================================

Ce module gère l'événement de recharge des stocks des fournisseurs.
Il permet aux fournisseurs de voir leurs stocks augmentés pour leurs
produits actifs, simulant un réapprovisionnement.

Responsabilités :
- Sélectionner aléatoirement les fournisseurs à recharger
- Sélectionner aléatoirement les produits actifs du fournisseur
- Calculer les quantités de recharge selon les paramètres
- Mettre à jour les stocks des fournisseurs
- Logger les recharges dans les fichiers appropriés

Logique :
- Déclenchement : Tous les 20 tours (RECHARGE_FOURNISSEUR_INTERVAL)
- 40% de chance de recharge par fournisseur
- 60% de chance de recharge par produit actif du fournisseur
- Quantité aléatoire entre 10-50 unités par produit
- Log détaillé de chaque recharge
- Résumé statistique des recharges effectuées

Différence avec reassort.py :
- reassort.py : Met des produits inactifs à actifs
- recharge_stock_fournisseur.py : Augmente le stock des produits actifs

Auteur: Assistant IA
Date: 2025-08-21
"""

import random
from datetime import datetime, timezone
from typing import List, Dict, Any

# Imports des Repository (nouvelle architecture)
from repositories import ProduitRepository, FournisseurRepository
from events.event_logger import log_evenement_json, log_evenement_humain
from config.config import (
    RECHARGE_FOURNISSEUR_INTERVAL,
    PROBABILITE_RECHARGE_FOURNISSEUR,
    PROBABILITE_RECHARGE_PRODUIT,
    RECHARGE_QUANTITE_MIN,
    RECHARGE_QUANTITE_MAX
)


def appliquer_recharge_stock_fournisseur(tick: int) -> List[Dict[str, Any]]:
    """
    Applique une recharge de stock aux fournisseurs.
    
    Cette fonction sélectionne aléatoirement les fournisseurs à recharger
    et augmente le stock de leurs produits actifs selon les paramètres configurés.
    
    Args:
        tick (int): Numéro du tick actuel
        
    Returns:
        List[Dict[str, Any]]: Liste de logs pour jsonl + log_humain
        
    Logique :
    - Vérifie si l'événement doit être déclenché (tous les 20 tours)
    - Parcourt tous les fournisseurs
    - 40% de chance de recharge par fournisseur
    - Pour chaque fournisseur sélectionné, parcourt ses produits actifs
    - 60% de chance de recharge par produit actif
    - Quantité aléatoire entre 10-50 unités par produit
    - Met à jour le stock du fournisseur
    - Génère des logs détaillés et un résumé statistique
    """
    
    # Vérifier si l'événement doit être déclenché (tous les 20 tours)
    if tick % RECHARGE_FOURNISSEUR_INTERVAL != 0:
        return []
    
    # Initialiser les Repository
    produit_repo = ProduitRepository()
    fournisseur_repo = FournisseurRepository()
    
    horodatage = datetime.now(timezone.utc)
    horodatage_iso = horodatage.isoformat()
    horodatage_humain = horodatage.strftime("%Y-%m-%d %H:%M:%S")
    
    logs = []
    fournisseurs_recharges = []
    total_quantite_rechargee = 0
    total_produits_recharges = 0
    
    # Récupérer tous les fournisseurs via le Repository
    fournisseurs = fournisseur_repo.get_all()
    
    for fournisseur in fournisseurs:
        # 40% de chance de recharge pour ce fournisseur
        if random.random() < PROBABILITE_RECHARGE_FOURNISSEUR:
            produits_recharges = []
            quantite_fournisseur = 0
            
            # Récupérer tous les produits actifs
            produits_actifs = produit_repo.get_actifs()
            
            # Pour chaque produit actif, vérifier s'il est en stock chez ce fournisseur
            for produit in produits_actifs:
                if produit.id in fournisseur.stock_produit and fournisseur.stock_produit[produit.id] > 0:
                    # 60% de chance de recharge pour ce produit actif
                    if random.random() < PROBABILITE_RECHARGE_PRODUIT:
                        quantite = random.randint(RECHARGE_QUANTITE_MIN, RECHARGE_QUANTITE_MAX)
                        ancien_stock = fournisseur.stock_produit[produit.id]
                        fournisseur.stock_produit[produit.id] += quantite
                        nouveau_stock = fournisseur.stock_produit[produit.id]
                        
                        quantite_fournisseur += quantite
                        total_quantite_rechargee += quantite
                        total_produits_recharges += 1
                        
                        produits_recharges.append({
                            "produit_id": produit.id,
                            "produit_nom": produit.nom,
                            "produit_type": produit.type.value,
                            "ancien_stock": ancien_stock,
                            "quantite_rechargee": quantite,
                            "nouveau_stock": nouveau_stock
                        })
            
            # Si des produits ont été rechargés pour ce fournisseur
            if produits_recharges:
                fournisseurs_recharges.append({
                    "fournisseur_id": fournisseur.id,
                    "fournisseur_nom": fournisseur.nom_entreprise,
                    "fournisseur_continent": fournisseur.continent,
                    "nb_produits_recharges": len(produits_recharges),
                    "quantite_totale_rechargee": quantite_fournisseur,
                    "produits": produits_recharges
                })
                
                # Log détaillé pour ce fournisseur
                produits_liste = ", ".join([f"{p['produit_nom']}(+{p['quantite_rechargee']})" for p in produits_recharges])
                
                log_json = {
                    "tick": tick,
                    "timestamp": horodatage_iso,
                    "timestamp_humain": horodatage_humain,
                    "event_type": "recharge_stock_fournisseur",
                    "fournisseur_id": fournisseur.id,
                    "fournisseur_nom": fournisseur.nom_entreprise,
                    "fournisseur_continent": fournisseur.continent,
                    "nb_produits_recharges": len(produits_recharges),
                    "quantite_totale_rechargee": quantite_fournisseur,
                    "produits_recharges": produits_recharges,
                    "log_humain": f"📦 Tour {tick} - RECHARGE {fournisseur.nom_entreprise}: {produits_liste} (total: +{quantite_fournisseur} unités)"
                }
                
                logs.append(log_json)
    
    # Ajout d'un log de résumé si des recharges ont eu lieu
    if fournisseurs_recharges:
        nb_fournisseurs = len(fournisseurs_recharges)
        moy_quantite_par_fournisseur = round(total_quantite_rechargee / nb_fournisseurs, 2)
        moy_produits_par_fournisseur = round(total_produits_recharges / nb_fournisseurs, 2)
        
        # Créer la liste des fournisseurs avec leurs quantités
        fournisseurs_liste = ", ".join([f"{f['fournisseur_nom']}(+{f['quantite_totale_rechargee']})" for f in fournisseurs_recharges])
        
        log_resume = {
            "tick": tick,
            "timestamp": horodatage_iso,
            "timestamp_humain": horodatage_humain,
            "event_type": "recharge_stock_fournisseur_resume",
            "statistiques": {
                "nb_fournisseurs_recharges": nb_fournisseurs,
                "nb_produits_recharges": total_produits_recharges,
                "quantite_totale_rechargee": total_quantite_rechargee,
                "moyenne_quantite_par_fournisseur": moy_quantite_par_fournisseur,
                "moyenne_produits_par_fournisseur": moy_produits_par_fournisseur
            },
            "fournisseurs": fournisseurs_recharges,
            "log_humain": f"📊 RECHARGE STOCK - {nb_fournisseurs} fournisseurs: {fournisseurs_liste} (total: +{total_quantite_rechargee} unités)"
        }
        
        logs.append(log_resume)
    
    return logs


if __name__ == "__main__":
    """
    Point d'entrée pour exécuter les tests directement.
    Utile pour le développement et le debugging.
    """
    print("🚀 Test de l'événement Recharge Stock Fournisseur...")
    
    # Test avec un tick qui déclenche l'événement (multiple de 20)
    resultat = appliquer_recharge_stock_fournisseur(20)
    
    if resultat:
        print(f"✅ Événement déclenché - {len(resultat)} logs générés")
        for log in resultat:
            print(f"📝 {log.get('log_humain', str(log))}")
    else:
        print("⏭️ Événement non déclenché (probabilité ou intervalle)")
    
    print("🎉 Test terminé !")
