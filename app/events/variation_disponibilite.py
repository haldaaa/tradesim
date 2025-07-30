# app/events/variation_disponibilite.py
"""
Événement : Variation de Disponibilité
--------------------------------------
Rend certains produits temporairement indisponibles ou disponibles.

Logique :
- Déclenché tous les X ticks avec un facteur chance
- Sélectionne un sous-ensemble de produits actifs ou inactifs
- Rend certains produits inactifs (indisponibles) ou les réactive

Logs :
- Ajoute un log [EVENT] dans simulation_humain.log et simulation.jsonl
- Ajoute un log dédié dans events_humain.log et events.jsonl
"""

import random
from datetime import datetime
from app.data import fake_produits_db
from app.events.event_logger import log_evenement_json, log_evenement_humain

CHANCE_VARIATION = 0.5  # 50 % de chance que l'événement soit déclenché
TAUX_MODIFICATION = 0.2  # 20 % des produits éligibles sont modifiés

def appliquer_variation_disponibilite(tick: int):
    """
    Change aléatoirement la disponibilité de certains produits (actifs <-> inactifs).
    Retourne une liste de logs (dictionnaires) pour jsonl + log_humain.
    """
    if random.random() > CHANCE_VARIATION:
        return []  # Pas d'événement ce tick

    horodatage = datetime.utcnow().isoformat()
    horodatage_humain = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    modifications = []

    # Sélection aléatoire de produits actifs à désactiver
    produits_actifs = [p for p in fake_produits_db if p.actif]
    nb_desactiver = max(1, int(len(produits_actifs) * TAUX_MODIFICATION))
    a_desactiver = random.sample(produits_actifs, min(nb_desactiver, len(produits_actifs)))

    for p in a_desactiver:
        p.actif = False
        modifications.append({"produit_id": p.id, "nom": p.nom, "ancien_etat": "actif", "nouvel_etat": "inactif"})

    # Sélection aléatoire de produits inactifs à réactiver
    produits_inactifs = [p for p in fake_produits_db if not p.actif]
    nb_activer = max(1, int(len(produits_inactifs) * TAUX_MODIFICATION))
    a_activer = random.sample(produits_inactifs, min(nb_activer, len(produits_inactifs)))

    for p in a_activer:
        p.actif = True
        modifications.append({"produit_id": p.id, "nom": p.nom, "ancien_etat": "inactif", "nouvel_etat": "actif"})

    message_humain = (
        f"🔄 "
        f"📉 {len(a_desactiver)} désactivés | "
        f"📈 {len(a_activer)} réactivés | "
        f"Total modifié: {len(modifications)} produits"
    )

    log_json = {
        "tick": tick,
        "timestamp": horodatage,
        "timestamp_humain": horodatage_humain,
        "type": "variation_disponibilite",
        "statistiques": {
            "nb_desactives": len(a_desactiver),
            "nb_reactives": len(a_activer),
            "total_modifications": len(modifications)
        },
        "modifications": modifications,
        "log_humain": message_humain
    }

    return [log_json]
