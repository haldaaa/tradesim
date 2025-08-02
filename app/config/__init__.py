#!/usr/bin/env python3
"""
Config - Module de configuration centralisée
===========================================

Ce module exporte toute la configuration de TradeSim.
La configuration est centralisée pour faciliter la maintenance.

Auteur: Assistant IA
Date: 2024-08-02
"""

# Imports de la configuration depuis le fichier config.py
from .config import (
    # Simulation
    NOMBRE_TOURS,
    N_ENTREPRISES_PAR_TOUR,
    DUREE_PAUSE_ENTRE_TOURS,
    PROBABILITE_SELECTION_ENTREPRISE,
    
    # Debug
    DEBUG_MODE,
    
    # Logs
    BASE_DIR,
    LOG_DIR,
    FICHIER_LOG,
    FICHIER_LOG_HUMAIN,
    
    # Événements
    RECHARGE_BUDGET_MIN,
    RECHARGE_BUDGET_MAX,
    REASSORT_QUANTITE_MIN,
    REASSORT_QUANTITE_MAX,
    INFLATION_POURCENTAGE_MIN,
    INFLATION_POURCENTAGE_MAX,
    BONUS_INFLATION_PRODUIT_EXISTANT,
    PROBABILITE_DESACTIVATION,
    PROBABILITE_REACTIVATION,
    TICK_INTERVAL_EVENT,
    PROBABILITE_EVENEMENT
)

# Exports publics
__all__ = [
    # Simulation
    'NOMBRE_TOURS',
    'N_ENTREPRISES_PAR_TOUR', 
    'DUREE_PAUSE_ENTRE_TOURS',
    'PROBABILITE_SELECTION_ENTREPRISE',
    
    # Debug
    'DEBUG_MODE',
    
    # Logs
    'BASE_DIR',
    'LOG_DIR',
    'FICHIER_LOG',
    'FICHIER_LOG_HUMAIN',
    
    # Événements
    'RECHARGE_BUDGET_MIN',
    'RECHARGE_BUDGET_MAX',
    'REASSORT_QUANTITE_MIN',
    'REASSORT_QUANTITE_MAX',
    'INFLATION_POURCENTAGE_MIN',
    'INFLATION_POURCENTAGE_MAX',
    'BONUS_INFLATION_PRODUIT_EXISTANT',
    'PROBABILITE_DESACTIVATION',
    'PROBABILITE_REACTIVATION',
    'TICK_INTERVAL_EVENT',
    'PROBABILITE_EVENEMENT'
] 