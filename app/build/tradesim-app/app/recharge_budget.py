#!/usr/bin/env python3
"""
Recharge Budget TradeSim - Événement de recharge de budget
=========================================================

Ce module gère l'événement de recharge de budget pour les entreprises.
Il permet aux entreprises de recevoir des fonds supplémentaires
à intervalles réguliers pour maintenir l'activité économique.

Responsabilités :
- Sélectionner aléatoirement les entreprises à recharger
- Calculer les montants de recharge selon les paramètres
- Mettre à jour les budgets des entreprises
- Logger les recharges dans les fichiers appropriés

Logique :
- 70% de chance de recharge par entreprise
- Montant aléatoire entre RECHARGE_BUDGET_MIN et RECHARGE_BUDGET_MAX
- Log détaillé de chaque recharge
- Résumé statistique des recharges effectuées

Auteur: Assistant IA
Date: 2024-08-02
"""

import random
from typing import List, Dict, Any

# Imports des Repository (nouvelle architecture)
from repositories import EntrepriseRepository
from config.config import RECHARGE_BUDGET_MIN, RECHARGE_BUDGET_MAX

def appliquer_recharge_budget(tick: int) -> List[Dict[str, Any]]:
    """
    Applique une recharge de budget aux entreprises.
    
    Cette fonction sélectionne aléatoirement les entreprises à recharger
    et ajoute un montant à leur budget selon les paramètres configurés.
    
    Args:
        tick (int): Numéro du tick actuel
        
    Returns:
        List[Dict[str, Any]]: Liste de logs pour jsonl + log_humain
        
    Logique :
    - Parcourt toutes les entreprises
    - 70% de chance de recharge par entreprise
    - Montant aléatoire entre RECHARGE_BUDGET_MIN et RECHARGE_BUDGET_MAX
    - Met à jour le budget de l'entreprise
    - Génère des logs détaillés et un résumé statistique
    """
    # Initialiser le Repository
    entreprise_repo = EntrepriseRepository()
    
    logs = []
    entreprises_rechargees = []
    total_recharge = 0

    # Récupérer toutes les entreprises via le Repository
    entreprises = entreprise_repo.get_all()
    
    for entreprise in entreprises:
        # 70% de chance de recharge
        if random.random() < 0.7:
            montant = random.randint(RECHARGE_BUDGET_MIN, RECHARGE_BUDGET_MAX)
            ancien_budget = entreprise.budget
            entreprise.budget += montant
            total_recharge += montant

            entreprises_rechargees.append({
                "entreprise_id": entreprise.id,
                "entreprise_nom": entreprise.nom,
                "ancien_budget": ancien_budget,
                "montant_recharge": montant,
                "nouveau_budget": entreprise.budget
            })

            log_json = {
                "tick": tick,
                "event_type": "recharge_budget",
                "entreprise_id": entreprise.id,
                "entreprise_nom": entreprise.nom,
                "ancien_budget": ancien_budget,
                "montant_recharge": montant,
                "nouveau_budget": entreprise.budget,
                "log_humain": f"💰 Tour {tick} - {entreprise.nom} reçoit +{montant}€ (budget: {int(ancien_budget)}€ → {int(entreprise.budget)}€)"
            }

            logs.append(log_json)

    # Ajout d'un log de résumé si des recharges ont eu lieu
    if entreprises_rechargees:
        nb_entreprises = len(entreprises_rechargees)
        moy_recharge = round(total_recharge / nb_entreprises, 2)
        
        # Créer la liste des entreprises avec leurs montants
        entreprises_liste = ", ".join([f"{e['entreprise_nom']}(+{e['montant_recharge']}€)" for e in entreprises_rechargees])
        
        log_resume = {
            "tick": tick,
            "event_type": "recharge_budget_resume",
            "statistiques": {
                "nb_entreprises_rechargees": nb_entreprises,
                "total_recharge": total_recharge,
                "moyenne_recharge": moy_recharge
            },
            "entreprises": entreprises_rechargees,
            "log_humain": f"📊 RECHARGE - {nb_entreprises} entreprises: {entreprises_liste}"
        }
        
        logs.append(log_resume)

    return logs
