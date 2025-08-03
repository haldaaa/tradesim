# app/events/event_logger.py

import json
import os
from datetime import datetime
from config import (
    FICHIER_LOG,
    FICHIER_LOG_HUMAIN,
)

# Définition des fichiers de logs spéciaux event
FICHIER_EVENT_LOG = os.path.join(os.path.dirname(FICHIER_LOG), "event.jsonl")
FICHIER_EVENT_LOG_HUMAIN = os.path.join(os.path.dirname(FICHIER_LOG_HUMAIN), "event.log")

# Crée les dossiers de logs si nécessaire
os.makedirs(os.path.dirname(FICHIER_LOG), exist_ok=True)
os.makedirs(os.path.dirname(FICHIER_EVENT_LOG), exist_ok=True)

def log_evenement_json(tick: int, horodatage_iso: str, horodatage_humain: str, event_type: str, details: dict):
    """
    Loggue un événement dans les fichiers JSONL :
    - `simulation.jsonl` (log global avec tag [EVENT])
    - `events.jsonl` (log dédié aux événements)
    """
    log_entry = {
        "tick": tick,
        "timestamp": horodatage_iso,
        "timestamp_humain": horodatage_humain,
        "type": event_type,
        "details": details
    }

    # Ajout du tag EVENT dans le log principal
    log_global = log_entry.copy()
    log_global["tag"] = "[EVENT]"

    with open(FICHIER_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_global) + "\n")

    with open(FICHIER_EVENT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def log_evenement_humain(tick: int, horodatage_humain: str, event_type: str, message: str):
    """
    Loggue un événement dans les fichiers .log humains :
    - `simulation_humain.log` (global avec [EVENT])
    - `events_humain.log` (spécifique)
    """
    ligne = f"[{horodatage_humain}] (tick {tick}) [EVENT-{event_type.upper()}] {message}"

    with open(FICHIER_LOG_HUMAIN, "a", encoding="utf-8") as f:
        f.write(ligne + "\n")

    with open(FICHIER_EVENT_LOG_HUMAIN, "a", encoding="utf-8") as f:
        f.write(ligne + "\n")
