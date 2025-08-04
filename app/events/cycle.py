#!/usr/bin/env python3
"""
Cycle Events TradeSim - Gestionnaire d'événements cycliques
==========================================================

Ce module gère le cycle des événements dans TradeSim.
Il orchestre l'exécution des différents événements selon
des intervalles et probabilités configurés.

Responsabilités :
- Déclencher les événements selon les intervalles
- Gérer les probabilités d'occurrence
- Logger les événements dans les fichiers appropriés
- Coordonner l'exécution des différents types d'événements

Événements gérés :
- Recharge de budget
- Réassortiment des stocks
- Inflation des prix
- Variation de disponibilité

Auteur: Assistant IA
Date: 2024-08-02
"""

import random
from config import (
    TICK_INTERVAL_EVENT,
    PROBABILITE_EVENEMENT,
)
from events.recharge_budget import appliquer_recharge_budget
from events.reassort import appliquer_reassort
from events.inflation import appliquer_inflation
from events.variation_disponibilite import appliquer_variation_disponibilite
from utils.logger import log_humain, log_json  # On logue aussi dans simulation + tag [EVENT]

def gerer_evenements(tick: int):
    """
    Gère le cycle des événements pour un tick donné.
    
    Cette fonction est appelée à chaque tick et vérifie si des événements
    doivent être déclenchés selon les intervalles et probabilités configurés.
    
    Args:
        tick (int): Numéro du tick actuel
        
    Logique :
    - Vérifie si le tick correspond à l'intervalle d'événements
    - Pour chaque type d'événement, teste la probabilité d'occurrence
    - Déclenche les événements selon les probabilités
    - Log tous les événements dans les fichiers appropriés
    """
    if tick % TICK_INTERVAL_EVENT != 0:
        return

    log_humain(f"[EVENT] Tick {tick} → Évaluation des événements")
    log_json({"event": "tick_event_check", "tick": tick})

    if random.random() < PROBABILITE_EVENEMENT.get("recharge_budget", 0):
        appliquer_recharge_budget(tick)

    if random.random() < PROBABILITE_EVENEMENT.get("reassort", 0):
        appliquer_reassort(tick)

    if random.random() < PROBABILITE_EVENEMENT.get("inflation", 0):
        appliquer_inflation(tick)

    if random.random() < PROBABILITE_EVENEMENT.get("variation_disponibilite", 0):
        appliquer_variation_disponibilite(tick)
