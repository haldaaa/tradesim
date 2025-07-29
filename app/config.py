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


# Mode debug (plus tard si besoin)
DEBUG_MODE = False


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Fichiers de log
FICHIER_LOG = os.path.join(LOG_DIR, "simulation.jsonl")
FICHIER_LOG_HUMAIN = os.path.join(LOG_DIR, "simulation_humain.log")