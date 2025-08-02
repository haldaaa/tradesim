# app/events/cycle.py

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
    Appelé tous les TICK_INTERVAL_EVENT ticks.
    Chaque événement est tenté selon sa probabilité.
    Les événements déclenchés sont aussi loggués dans les fichiers globaux avec le tag [EVENT].
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
