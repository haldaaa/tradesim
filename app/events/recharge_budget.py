# app/events/recharge_budget.py

"""
Recharge de budget pour les entreprises à intervalles réguliers.
Ce module est appelé depuis cycle.py tous les X ticks.

Refactorisation (02/08/2025) :
- Utilise les Repository au lieu d'accès directs aux données
- Code plus modulaire et testable
- Interface commune pour CLI et API
"""

import random
from typing import List, Dict, Any

# Imports des Repository (nouvelle architecture)
from repositories import EntrepriseRepository
from config import RECHARGE_BUDGET_MIN, RECHARGE_BUDGET_MAX

def appliquer_recharge_budget(tick: int) -> List[Dict[str, Any]]:
    """
    Recharge aléatoirement le budget de certaines entreprises.
    
    Args:
        tick (int): Numéro du tick actuel
        
    Returns:
        List[Dict[str, Any]]: Liste de logs pour jsonl + log_humain
        
    Refactorisation (02/08/2025) :
    - Utilise EntrepriseRepository au lieu de fake_entreprises_db
    - Code plus modulaire et testable
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
                "log_humain": f"[RECHARGE] {entreprise.nom}: +{montant}€ (ancien: {ancien_budget}€ → nouveau: {entreprise.budget}€)"
            }

            logs.append(log_json)

    # Ajout d'un log de résumé si des recharges ont eu lieu
    if entreprises_rechargees:
        nb_entreprises = len(entreprises_rechargees)
        moy_recharge = round(total_recharge / nb_entreprises, 2)
        
        log_resume = {
            "tick": tick,
            "event_type": "recharge_budget_resume",
            "statistiques": {
                "nb_entreprises_rechargees": nb_entreprises,
                "total_recharge": total_recharge,
                "moyenne_recharge": moy_recharge
            },
            "entreprises": entreprises_rechargees,
            "log_humain": f"[RESUME RECHARGE] {nb_entreprises} entreprises rechargées | Total: +{total_recharge}€ | Moyenne: +{moy_recharge}€"
        }
        
        logs.append(log_resume)

    return logs
