# app/events/recharge_budget.py

"""
Recharge de budget pour les entreprises à intervalles réguliers.
Ce module est appelé depuis cycle.py tous les X ticks.
"""

import random
from app.data import fake_entreprises_db
from app.config import RECHARGE_BUDGET_MIN, RECHARGE_BUDGET_MAX

def appliquer_recharge_budget(tick: int) -> list:
    """
    Recharge aléatoirement le budget de certaines entreprises.
    Retourne une liste de dictionnaires (logs JSON) avec éventuellement une clé "log_humain".
    """
    logs = []
    entreprises_rechargees = []
    total_recharge = 0

    for entreprise in fake_entreprises_db:
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
                "log_humain": f"💰 {entreprise.nom}: +{montant}€ (ancien: {ancien_budget}€ → nouveau: {entreprise.budget}€)"
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
            "log_humain": f"💸 {nb_entreprises} entreprises rechargées | Total: +{total_recharge}€ | Moyenne: +{moy_recharge}€"
        }
        
        logs.append(log_resume)

    return logs
