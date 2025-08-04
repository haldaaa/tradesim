#!/usr/bin/env python3
"""
Variation Disponibilité TradeSim - Événement de variation de disponibilité
==========================================================================

Ce module gère l'événement de variation de disponibilité des produits.
Il permet de rendre certains produits temporairement indisponibles
ou de réactiver des produits inactifs pour simuler les fluctuations
du marché.

Responsabilités :
- Sélectionner aléatoirement les produits à modifier
- Désactiver des produits actifs (rendre indisponibles)
- Réactiver des produits inactifs (rendre disponibles)
- Logger les modifications dans les fichiers appropriés

Logique :
- 50% de chance d'événement par tick
- 20% des produits éligibles sont modifiés
- Équilibre entre désactivation et réactivation
- Log détaillé des modifications effectuées

Auteur: Assistant IA
Date: 2024-08-02
"""

import random
from datetime import datetime, timezone
from typing import List, Dict, Any

# Imports des Repository (nouvelle architecture)
from repositories import ProduitRepository
from events.event_logger import log_evenement_json, log_evenement_humain

CHANCE_VARIATION = 0.5  # 50 % de chance que l'événement soit déclenché
TAUX_MODIFICATION = 0.2  # 20 % des produits éligibles sont modifiés

def appliquer_variation_disponibilite(tick: int) -> List[Dict[str, Any]]:
    """
    Applique une variation de disponibilité aux produits.
    
    Cette fonction modifie aléatoirement le statut actif/inactif
    des produits pour simuler les fluctuations du marché.
    
    Args:
        tick (int): Numéro du tick actuel
        
    Returns:
        List[Dict[str, Any]]: Liste de logs pour jsonl + log_humain
        
    Logique :
    - 50% de chance d'événement par tick
    - Sélectionne 20% des produits actifs pour désactivation
    - Sélectionne 20% des produits inactifs pour réactivation
    - Met à jour le statut des produits sélectionnés
    - Génère des logs détaillés des modifications
    """
    if random.random() > CHANCE_VARIATION:
        return []  # Pas d'événement ce tick

    # Initialiser le Repository
    produit_repo = ProduitRepository()

    horodatage = datetime.now(timezone.utc).isoformat()
    horodatage_humain = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    modifications = []

    # Récupérer tous les produits via le Repository
    tous_produits = produit_repo.get_all()
    
    # Sélection aléatoire de produits actifs à désactiver
    produits_actifs = [p for p in tous_produits if p.actif]
    nb_desactiver = max(1, int(len(produits_actifs) * TAUX_MODIFICATION))
    a_desactiver = random.sample(produits_actifs, min(nb_desactiver, len(produits_actifs)))

    for p in a_desactiver:
        p.actif = False
        modifications.append({"produit_id": p.id, "nom": p.nom, "ancien_etat": "actif", "nouvel_etat": "inactif"})

    # Sélection aléatoire de produits inactifs à réactiver
    produits_inactifs = [p for p in tous_produits if not p.actif]
    nb_activer = max(1, int(len(produits_inactifs) * TAUX_MODIFICATION))
    a_activer = random.sample(produits_inactifs, min(nb_activer, len(produits_inactifs)))

    for p in a_activer:
        p.actif = True
        modifications.append({"produit_id": p.id, "nom": p.nom, "ancien_etat": "inactif", "nouvel_etat": "actif"})

    # Récupérer les noms des produits pour l'affichage
    noms_desactives = [p.nom for p in a_desactiver]
    noms_reactives = [p.nom for p in a_activer]
    
    # Formater les listes de noms
    str_desactives = ", ".join(noms_desactives) if noms_desactives else "aucun"
    str_reactives = ", ".join(noms_reactives) if noms_reactives else "aucun"

    message_humain = (
        f"[VARIATION] "
        f"[DESACTIVE] {len(a_desactiver)} désactivés ({str_desactives}) | "
        f"[REACTIVE] {len(a_activer)} réactivés ({str_reactives}) | "
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
