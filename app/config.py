# app/config.py
import os
"""
Fichier de configuration centralisée.
Toutes les constantes du projet sont regroupées ici
pour permettre une modification rapide et propre.
"""

# Simulation
NOMBRE_TOURS = 100                     # Nombre total de tours à simuler
N_ENTREPRISES_PAR_TOUR = 2            # Nombre d'entreprises sélectionnées aléatoirement par tour
DUREE_PAUSE_ENTRE_TOURS = 0.1         # En secondes (peut servir pour la version crontab/finale)
PROBABILITE_SELECTION_ENTREPRISE = 0.3 # Probabilité qu'une entreprise soit sélectionnée pour un tour


# Mode debug (plus tard si besoin)
DEBUG_MODE = False


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Fichiers de log
FICHIER_LOG = os.path.join(LOG_DIR, "simulation.jsonl")
FICHIER_LOG_HUMAIN = os.path.join(LOG_DIR, "simulation_humain.log")


# Events  

## Budget (recharge_budget) 
RECHARGE_BUDGET_MIN = 200
RECHARGE_BUDGET_MAX = 600

## Reassort (reassort)
REASSORT_QUANTITE_MIN = 10
REASSORT_QUANTITE_MAX = 50

## Inflation (inflation)
INFLATION_POURCENTAGE_MIN = 30
INFLATION_POURCENTAGE_MAX = 60
BONUS_INFLATION_PRODUIT_EXISTANT = 15

## Variation de disponibilité (variation_disponibilite)
PROBABILITE_DESACTIVATION = 0.1  # 10% de chance de désactiver un produit actif
PROBABILITE_REACTIVATION = 0.2   # 20% de chance de réactiver un produit inactif

TICK_INTERVAL_EVENT = 20  # Tous les 20 ticks, on tente des événements

PROBABILITE_EVENEMENT = {
    "recharge_budget": 0.5,
    "reassort": 0.5,
    "inflation": 0.4,
    "variation_disponibilite": 0.3
}