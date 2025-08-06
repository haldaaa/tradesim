#!/usr/bin/env python3
"""
Configuration TradeSim - Paramètres centralisés
==============================================

Ce module contient toutes les constantes de configuration de TradeSim.
Il centralise tous les paramètres pour permettre une modification
rapide et cohérente de l'application.

Sections de configuration :
- Simulation : Paramètres de base de la simulation
- Logs : Configuration des fichiers de logs
- Events : Paramètres des différents événements
- Debug : Mode debug et options de développement

Auteur: Assistant IA
Date: 2024-08-02
"""

import os

# ============================================================================
# SIMULATION - Paramètres de base de la simulation
# ============================================================================

NOMBRE_TOURS = 100                     # Nombre total de tours à simuler
N_ENTREPRISES_PAR_TOUR = 2            # Nombre d'entreprises sélectionnées aléatoirement par tour
DUREE_PAUSE_ENTRE_TOURS = 0.1         # En secondes (peut servir pour la version crontab/finale)
PROBABILITE_SELECTION_ENTREPRISE = 0.3 # Probabilité qu'une entreprise soit sélectionnée pour un tour


# ============================================================================
# DEBUG - Mode debug et options de développement
# ============================================================================

DEBUG_MODE = False                     # Mode debug (plus tard si besoin)

# ============================================================================
# LOGS - Configuration des fichiers de logs
# ============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Fichiers de log
FICHIER_LOG = os.path.join(LOG_DIR, "simulation.jsonl")
FICHIER_LOG_HUMAIN = os.path.join(LOG_DIR, "simulation_humain.log")


# ============================================================================
# ENTREPRISES - Configuration des entreprises
# ============================================================================

# Types de produits préférés par entreprise
TYPES_PRODUITS_PREFERES_MIN = 1       # Nombre minimum de types de produits préférés
TYPES_PRODUITS_PREFERES_MAX = 2       # Nombre maximum de types de produits préférés

# Quantités d'achat par entreprise
QUANTITE_ACHAT_MIN = 1                # Quantité minimum d'achat par entreprise
QUANTITE_ACHAT_MAX = 100              # Quantité maximum d'achat par entreprise

# Budgets des entreprises
BUDGET_ENTREPRISE_MIN = 6000          # Budget minimum des entreprises (en euros)
BUDGET_ENTREPRISE_MAX = 20000         # Budget maximum des entreprises (en euros)

# ============================================================================
# EVENTS - Paramètres des différents événements
# ============================================================================

# Budget (recharge_budget) 
RECHARGE_BUDGET_MIN = 4000             # Montant minimum de recharge de budget
RECHARGE_BUDGET_MAX = 8000             # Montant maximum de recharge de budget

# Reassort (reassort)
REASSORT_QUANTITE_MIN = 10            # Quantité minimum de réassortiment
REASSORT_QUANTITE_MAX = 50            # Quantité maximum de réassortiment

# Inflation (inflation)
INFLATION_POURCENTAGE_MIN = 30        # Pourcentage minimum d'inflation
INFLATION_POURCENTAGE_MAX = 60        # Pourcentage maximum d'inflation
PENALITE_INFLATION_PRODUIT_EXISTANT = 15 # Pénalité d'inflation pour produit déjà affecté (-15%)
DUREE_PENALITE_INFLATION = 50 # Durée de la pénalité d'inflation (en tours)

# Retour à la normale après inflation
DUREE_RETOUR_INFLATION = 30        # Tours avant début du retour progressif
DUREE_BAISSE_INFLATION = 15         # Tours pour la baisse linéaire
POURCENTAGE_FINAL_INFLATION = 10    # Prix final = prix original + 10%

# Exemple concret de logique d'inflation complète :
# Tour 0 : Prix 100€ → Inflation +20% → 120€
# Tours 1-29 : Prix reste à 120€ (DUREE_RETOUR_INFLATION = 30)
# Tours 30-44 : Baisse linéaire 120€ → 118€ → 116€ → ... → 110€ (DUREE_BAISSE_INFLATION = 15)
# Tour 45+ : Prix final 110€ (prix original + POURCENTAGE_FINAL_INFLATION = 10%)
# Si nouvelle inflation pendant le retour : arrêt du retour + reset pénalité

# Variation de disponibilité (variation_disponibilite)
PROBABILITE_DESACTIVATION = 0.1       # 10% de chance de désactiver un produit actif
PROBABILITE_REACTIVATION = 0.2        # 20% de chance de réactiver un produit inactif

# Intervalles et probabilités
TICK_INTERVAL_EVENT = 20              # Tous les 20 ticks, on tente des événements

PROBABILITE_EVENEMENT = {
    "recharge_budget": 0.5,           # 50% de chance de recharge de budget
    "reassort": 0.5,                  # 50% de chance de réassortiment
    "inflation": 0.4,                 # 40% de chance d'inflation
    "variation_disponibilite": 0.3    # 30% de chance de variation de disponibilité
}