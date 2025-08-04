#!/usr/bin/env python3
"""
Event Logger TradeSim - Système de logging des événements
=======================================================

Ce module gère le logging spécialisé des événements dans TradeSim.
Il fournit des fonctions pour logger les événements dans différents
formats (JSON et humain) et dans différents fichiers.

Responsabilités :
- Logger les événements en format JSON (JSONL)
- Logger les événements en format humain (.log)
- Gérer les fichiers de logs dédiés aux événements
- Assurer la cohérence des logs entre fichiers

Fichiers de logs :
- simulation.jsonl : Log global avec tag [EVENT]
- event.jsonl : Log dédié aux événements
- simulation_humain.log : Log global humain avec [EVENT]
- event.log : Log dédié aux événements en format humain

Auteur: Assistant IA
Date: 2024-08-02
"""

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
    Log un événement dans les fichiers JSONL.
    
    Args:
        tick (int): Numéro du tick de l'événement
        horodatage_iso (str): Horodatage ISO de l'événement
        horodatage_humain (str): Horodatage lisible de l'événement
        event_type (str): Type d'événement (inflation, reassort, etc.)
        details (dict): Détails de l'événement
        
    Fichiers de sortie :
    - simulation.jsonl : Log global avec tag [EVENT]
    - event.jsonl : Log dédié aux événements
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
    Log un événement dans les fichiers .log humains.
    
    Args:
        tick (int): Numéro du tick de l'événement
        horodatage_humain (str): Horodatage lisible de l'événement
        event_type (str): Type d'événement (inflation, reassort, etc.)
        message (str): Message humain de l'événement
        
    Fichiers de sortie :
    - simulation_humain.log : Log global avec [EVENT]
    - event.log : Log dédié aux événements en format humain
    """
    ligne = f"[{horodatage_humain}] (tick {tick}) [EVENT-{event_type.upper()}] {message}"

    with open(FICHIER_LOG_HUMAIN, "a", encoding="utf-8") as f:
        f.write(ligne + "\n")

    with open(FICHIER_EVENT_LOG_HUMAIN, "a", encoding="utf-8") as f:
        f.write(ligne + "\n")
