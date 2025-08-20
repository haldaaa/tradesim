#!/usr/bin/env python3
"""
Configuration centralisée pour TradeSim
======================================

ARCHITECTURE :
- Fichier de configuration unique pour toute l'application
- Paramètres de simulation, événements, monitoring
- Validation des données et constantes
- Configuration des métriques et alertes

FONCTIONNEMENT :
1. Import centralisé dans tous les services
2. Validation des valeurs critiques
3. Configuration par environnement
4. Constantes pour éviter la duplication

UTILISATION :
- Import : from config.config import *
- Validation : validate_continent("Europe")
- Configuration : QUANTITE_ACHAT_MAX, TICK_INTERVAL_EVENT, etc.

AJOUTS RÉCENTS (11/08/2025) :
- Validation des continents avec validate_continent()
- Constante DEFAULT_CONTINENT configurable
- Liste VALID_CONTINENTS pour validation

AUTEUR : Assistant IA
DERNIÈRE MISE À JOUR : 11/08/2025
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

# Fichiers de log des événements
EVENT_LOG_JSON = os.path.join(LOG_DIR, "event.jsonl")
EVENT_LOG_HUMAIN = os.path.join(LOG_DIR, "event.log")

# ============================================================================
# ENTREPRISES - Configuration des entreprises
# ============================================================================

# Types de produits préférés par entreprise
TYPES_PRODUITS_PREFERES_MIN = 1       # Nombre minimum de types de produits préférés
TYPES_PRODUITS_PREFERES_MAX = 2       # Nombre maximum de types de produits préférés

# Quantités d'achat par entreprise
QUANTITE_ACHAT_MIN = 1                # Quantité minimum d'achat par entreprise
QUANTITE_ACHAT_MAX = 100              # Quantité maximum d'achat par entreprise

# Quantités d'achat adaptées aux prix (pour éviter la faillite)
QUANTITE_ACHAT_PRIX_ELEVE_MIN = 1     # Quantité minimum pour produits chers
QUANTITE_ACHAT_PRIX_ELEVE_MAX = 20    # Quantité maximum pour produits chers
SEUIL_PRIX_ELEVE = 100.0              # Seuil en euros pour considérer un produit comme cher

# Budgets des entreprises
BUDGET_ENTREPRISE_MIN = 6000          # Budget minimum des entreprises (en euros)
BUDGET_ENTREPRISE_MAX = 20000         # Budget maximum des entreprises (en euros)

# ============================================================================
# PRODUITS - Configuration des produits
# ============================================================================

# Prix des produits (en euros)
PRIX_PRODUIT_MIN = 5.0                # Prix minimum des produits (en euros)
PRIX_PRODUIT_MAX = 500.0              # Prix maximum des produits (en euros)

# Nombre de produits par défaut
NOMBRE_PRODUITS_DEFAUT = 12           # Nombre de produits générés par défaut
PRODUITS_ACTIFS_MIN = 8               # Nombre minimum de produits actifs
PRODUITS_ACTIFS_MAX = 12              # Nombre maximum de produits actifs

# Types de produits disponibles
TYPES_PRODUITS_DISPONIBLES = [
    "matiere_premiere",
    "consommable", 
    "equipement",
    "service"
]

# ============================================================================
# PRIX FOURNISSEURS - Configuration des facteurs de prix
# ============================================================================

# Facteurs de prix fournisseur (logique économique : plus de stock = prix plus bas)
FACTEUR_PRIX_STOCK_REFERENCE = 50      # Stock de référence pour calcul du facteur
FACTEUR_PRIX_STOCK_VARIATION = 1000    # Diviseur pour la variation du facteur stock (±5%)
FACTEUR_PRIX_RANDOM_MIN = 0.95         # Facteur aléatoire minimum (±5%)
FACTEUR_PRIX_RANDOM_MAX = 1.05         # Facteur aléatoire maximum (±5%)

# ============================================================================
# EXEMPLE CONCRET - Calcul du prix fournisseur
# ============================================================================
# 
# Formule utilisée dans game_manager.py :
# facteur_stock = 1.0 + (stock_produit[produit.id] - FACTEUR_PRIX_STOCK_REFERENCE) / FACTEUR_PRIX_STOCK_VARIATION
# facteur_random = random.uniform(FACTEUR_PRIX_RANDOM_MIN, FACTEUR_PRIX_RANDOM_MAX)
# facteur_total = facteur_stock * facteur_random
# prix_fournisseur = round(prix_base * facteur_total, 2)
#
# EXEMPLES :
# 
# 1. PRODUIT AVEC STOCK ÉLEVÉ (100 unités) :
#    - Prix de base : 50€
#    - Stock actuel : 100
#    - facteur_stock = 1.0 + (100 - 50) / 1000 = 1.0 + 0.05 = 1.05
#    - facteur_random = 0.98 (exemple)
#    - facteur_total = 1.05 * 0.98 = 1.029
#    - Prix final = 50€ * 1.029 = 51.45€
#    → Prix LÉGÈREMENT PLUS HAUT car stock élevé
#
# 2. PRODUIT AVEC STOCK FAIBLE (10 unités) :
#    - Prix de base : 50€
#    - Stock actuel : 10
#    - facteur_stock = 1.0 + (10 - 50) / 1000 = 1.0 - 0.04 = 0.96
#    - facteur_random = 1.02 (exemple)
#    - facteur_total = 0.96 * 1.02 = 0.9792
#    - Prix final = 50€ * 0.9792 = 48.96€
#    → Prix LÉGÈREMENT PLUS BAS car stock faible
#
# 3. PRODUIT AVEC STOCK RÉFÉRENCE (50 unités) :
#    - Prix de base : 50€
#    - Stock actuel : 50
#    - facteur_stock = 1.0 + (50 - 50) / 1000 = 1.0 + 0 = 1.0
#    - facteur_random = 1.0 (exemple)
#    - facteur_total = 1.0 * 1.0 = 1.0
#    - Prix final = 50€ * 1.0 = 50€
#    → Prix IDENTIQUE car stock = référence
#
# LOGIQUE ÉCONOMIQUE : Plus de stock = prix plus bas (économie d'échelle)
# VARIATION MAXIMALE : ±5% pour le facteur stock + ±5% pour le facteur aléatoire

# TODO: FUTURE ÉVOLUTION - Événements de réassort fournisseur
# FACTEUR_PRIX_DEMANDE_ENABLED = False  # Activer le facteur demande
# FACTEUR_PRIX_GEOGRAPHIQUE_ENABLED = False  # Activer le facteur géographique
# FREQUENCE_REASSORT_FOURNISSEUR = 20   # Tous les N tours
# PROBABILITE_REASSORT_FOURNISSEUR = 0.3  # 30% de chance par tour

# ============================================================================
# EVENTS - Paramètres des différents événements
# ============================================================================

# Budget (recharge_budget) 
RECHARGE_BUDGET_MIN = 4000             # Montant minimum de recharge de budget
RECHARGE_BUDGET_MAX = 8000             # Montant maximum de recharge de budget

# Reassort (reassort)
REASSORT_QUANTITE_MIN = 10            # Quantité minimum de réassortiment
REASSORT_QUANTITE_MAX = 50            # Quantité maximum de réassortiment

# Configuration par défaut
DEFAULT_CONTINENT = "Europe"          # Continent par défaut pour les entités

# Validation des continents
VALID_CONTINENTS = ["Europe", "Asie", "Amérique", "Afrique", "Océanie"]

def validate_continent(continent: str) -> bool:
    """Valide qu'un continent est dans la liste autorisée"""
    return continent in VALID_CONTINENTS

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
TICK_INTERVAL_EVENT = 2               # Tous les 2 tours, on tente des événements

PROBABILITE_EVENEMENT = {
    "recharge_budget": 0.5,           # 50% de chance de recharge de budget
    "reassort": 0.5,                  # 50% de chance de réassortiment
    "inflation": 0.4,                 # 40% de chance d'inflation
    "variation_disponibilite": 0.3    # 30% de chance de variation de disponibilité
}

# ============================================================================
# MONITORING - Configuration Prometheus/Grafana
# ============================================================================

# Activation du monitoring
METRICS_ENABLED = True                # Activer/désactiver le monitoring
METRICS_COLLECTION_INTERVAL = 1.0    # Intervalle de collecte en secondes

# Configuration de l'exporter Prometheus
METRICS_EXPORTER_PORT = 8000         # Port de l'exporter Prometheus
METRICS_EXPORTER_HOST = "0.0.0.0"    # Host de l'exporter (0.0.0.0 = toutes interfaces)

# Configuration Docker (Prometheus/Grafana)
METRICS_PROMETHEUS_PORT = 9090       # Port de Prometheus
METRICS_GRAFANA_PORT = 3000          # Port de Grafana

# Configuration de connectivité Docker (modulaire)
METRICS_DOCKER_HOST = os.getenv('TRADESIM_DOCKER_HOST', 'localhost')  # Host Docker (modifiable par env)
METRICS_EXPORTER_TARGET = os.getenv('TRADESIM_EXPORTER_TARGET', 'localhost:8000')  # Target de l'exporteur

# Métriques système (CPU/Mémoire)
METRICS_SYSTEM_ENABLED = True        # Activer les métriques système
METRICS_SYSTEM_INTERVAL = 5.0        # Intervalle de collecte système en secondes

# Labels (Phase 1: désactivés, Phase 2: activés)
METRICS_LABELS_ENABLED = False       # Activer les labels sur les métriques
METRICS_LABELS_CONTINENT = False     # Label {continent}
METRICS_LABELS_PRODUIT_TYPE = False  # Label {produit_type}

# Configuration des IDs uniques
ID_FORMAT = "DATE_HHMMSS_TYPE_COUNTER"
ID_SESSION_FORMAT = "%Y%m%d_%H%M%S"
MAX_COUNTER = 99999
VALID_ACTION_TYPES = ['TXN', 'EVT', 'METRIC', 'TICK', 'ALERT', 'TEMPLATE']

# Configuration des optimisations
BATCH_LOG_SIZE = 10  # Nombre de logs avant écriture en batch
CACHE_MAX_SIZE = 100  # Taille max du cache LRU
COMPRESSION_DAYS = 7  # Compresser les logs de plus de X jours
INDEX_ENABLED = True  # Activer l'index pour recherche rapide
VALIDATION_ENABLED = True  # Activer la validation des données
REALTIME_MONITORING = True  # Alertes temps réel
PERFORMANCE_THRESHOLD = 1.0  # Seuil performance en secondes

# Seuils d'alerte temps réel
ALERT_BUDGET_CRITIQUE = 1000  # Budget critique en euros
ALERT_STOCK_CRITIQUE = 10  # Stock critique en unités
ALERT_ERROR_RATE = 0.1  # Taux d'erreur critique (10%)

# Configuration des métriques
# METRICS_COLLECTION_INTERVAL déjà défini plus haut = 1.0
METRICS_RETENTION_DAYS = 30  # Rétention des métriques en jours

# ============================================================================
# BUDGET METRICS - Configuration des métriques de budget
# ============================================================================

# Fréquence de calcul des métriques de budget
BUDGET_METRICS_FREQUENCY = "tour"  # "tour" | "transaction" | "both"

# Historique des budgets (nombre maximum de tours à conserver)
BUDGET_HISTORY_MAX_TOURS = 200  # Historique maximum en tours

# Cache pour les calculs complexes de budget
BUDGET_CACHE_ENABLED = True  # Activer le cache LRU pour les calculs
BUDGET_CACHE_SIZE = 50  # Taille du cache LRU

# Seuils d'alerte pour les budgets
BUDGET_CRITIQUE_SEUIL = 1000  # Budget critique en euros
BUDGET_FAIBLE_SEUIL = 3000    # Budget faible en euros
BUDGET_ELEVE_SEUIL = 15000    # Budget élevé en euros

# Configuration des labels pour les métriques de budget
BUDGET_LABELS_ENABLED = False  # Activer les labels par entreprise
BUDGET_LABELS_CONTINENT = False  # Label {continent}
BUDGET_LABELS_STRATEGIE = False  # Label {strategie}

# ============================================================================
# ENTERPRISE METRICS - Configuration des métriques d'entreprises
# ============================================================================

# Fréquence de calcul des métriques d'entreprises
ENTERPRISE_METRICS_FREQUENCY = "tour"  # "tour" | "transaction" | "both"

# Historique des entreprises (nombre maximum de tours à conserver)
ENTERPRISE_HISTORY_MAX_TOURS = 200  # Historique maximum en tours

# Cache pour les calculs complexes d'entreprises
ENTERPRISE_CACHE_ENABLED = True  # Activer le cache LRU pour les calculs
ENTERPRISE_CACHE_SIZE = 50  # Taille du cache LRU

# Seuils d'alerte pour les entreprises
ENTERPRISE_CRITIQUE_BUDGET = 1000  # Budget critique en euros
ENTERPRISE_CRITIQUE_STOCK = 10     # Stock critique en unités
ENTERPRISE_CRITIQUE_TRANSACTIONS = 0  # Nombre de transactions critique

# Configuration des labels pour les métriques d'entreprises
ENTERPRISE_LABELS_ENABLED = False  # Activer les labels par entreprise
ENTERPRISE_LABELS_PAYS = False     # Label {pays}
ENTERPRISE_LABELS_CONTINENT = False # Label {continent}
ENTERPRISE_LABELS_STRATEGIE = False # Label {strategie}

# ============================================================================
# PRODUCT METRICS - Configuration des métriques de produits
# ============================================================================

# Fréquence de calcul des métriques de produits
PRODUCT_METRICS_FREQUENCY = "tour"  # "tour" | "transaction" | "both"

# Historique des produits (nombre maximum de tours à conserver)
PRODUCT_HISTORY_MAX_TOURS = 200  # Historique maximum en tours

# Cache pour les calculs complexes de produits
PRODUCT_CACHE_ENABLED = True  # Activer le cache LRU pour les calculs
PRODUCT_CACHE_SIZE = 50  # Taille du cache LRU

# Seuils d'alerte pour les produits
PRODUCT_CRITIQUE_PRIX = 0  # Prix critique en euros
PRODUCT_CRITIQUE_STOCK = 5  # Stock critique en unités
PRODUCT_CRITIQUE_DEMANDE = 0  # Demande critique

# Configuration des labels pour les métriques de produits
PRODUCT_LABELS_ENABLED = False  # Activer les labels par produit
PRODUCT_LABELS_TYPE = False     # Label {type}
PRODUCT_LABELS_CONTINENT = False # Label {continent}

# ============================================================================
# SUPPLIER METRICS - Configuration des métriques de fournisseurs
# ============================================================================

# Fréquence de calcul des métriques de fournisseurs
SUPPLIER_METRICS_FREQUENCY = "tour"  # "tour" | "transaction" | "both"

# Historique des fournisseurs (nombre maximum de tours à conserver)
SUPPLIER_HISTORY_MAX_TOURS = 200  # Historique maximum en tours

# Cache pour les calculs complexes de fournisseurs
SUPPLIER_CACHE_ENABLED = True  # Activer le cache LRU pour les calculs
SUPPLIER_CACHE_SIZE = 50  # Taille du cache LRU

# Seuils d'alerte pour les fournisseurs
SUPPLIER_CRITIQUE_STOCK = 10  # Stock critique en unités
SUPPLIER_CRITIQUE_VENTES = 0  # Ventes critiques
SUPPLIER_CRITIQUE_PRODUITS = 1  # Nombre de produits critique

# Configuration des labels pour les métriques de fournisseurs
SUPPLIER_LABELS_ENABLED = False  # Activer les labels par fournisseur
SUPPLIER_LABELS_PAYS = False     # Label {pays}
SUPPLIER_LABELS_CONTINENT = False # Label {continent}

# ============================================================================
# INDIVIDUAL METRICS - Configuration des métriques individuelles avec labels
# ============================================================================

# Fréquence de calcul des métriques individuelles
INDIVIDUAL_METRICS_FREQUENCY = "tour"  # "tour" | "transaction" | "both"

# Historique des métriques individuelles (nombre maximum de tours à conserver)
INDIVIDUAL_METRICS_HISTORY_MAX_TOURS = 200  # Historique maximum en tours

# Cache pour les calculs complexes de métriques individuelles
INDIVIDUAL_METRICS_CACHE_ENABLED = True  # Activer le cache LRU pour les calculs
INDIVIDUAL_METRICS_CACHE_SIZE = 50  # Taille du cache LRU

# Configuration des labels pour les métriques individuelles
INDIVIDUAL_METRICS_LABELS_ENABLED = True  # Réactivé pour conserver les labels détaillés

# ============================================================================
# STOCK HISTORY METRICS - Configuration des métriques historiques de stock
# ============================================================================

# Configuration de la cardinalité des métriques historiques
STOCK_HISTORY_MAX_CARDINALITY = 10000  # Limite maximum de séries temporelles
STOCK_HISTORY_AUTO_COMPRESSION = True   # Compression automatique des anciennes données
STOCK_HISTORY_PERFORMANCE_MONITORING = True  # Surveillance de la performance

# Configuration de la rétention des données historiques
STOCK_HISTORY_RETENTION_TOURS = -1  # -1 = illimité, sinon nombre de tours
STOCK_HISTORY_GRANULARITY = "all"   # "all" | "daily" | "weekly" | "monthly"
STOCK_HISTORY_PERFORMANCE = "complete"  # "complete" | "sampled" | "compressed"

# Configuration des périodes d'évolution
STOCK_HISTORY_EVOLUTION_PERIODS = [5, 10, 15, 20]  # Périodes en tours
STOCK_HISTORY_DEFAULT_PERIOD = 10  # Période par défaut pour l'évolution

# Configuration de la compression automatique
STOCK_HISTORY_COMPRESSION_THRESHOLD = 50  # Seuil de tours pour activer la compression
STOCK_HISTORY_COMPRESSION_RATIO = 0.5     # Ratio de compression (0.5 = garder 50% des données)
INDIVIDUAL_METRICS_LABELS_ENTREPRISE = True  # Labels {id, nom, continent, strategie}
INDIVIDUAL_METRICS_LABELS_PRODUIT = True     # Labels {id, nom, type}
INDIVIDUAL_METRICS_LABELS_FOURNISSEUR = True # Labels {id, nom, continent}

# ============================================================================
# TRANSACTION METRICS - Configuration des métriques de transactions
# ============================================================================

# Fréquence de calcul des métriques de transactions
TRANSACTION_METRICS_FREQUENCY = "tour"  # "tour" | "transaction" | "both"

# Historique des transactions (nombre maximum de tours à conserver)
TRANSACTION_HISTORY_MAX_TOURS = 200  # Historique maximum en tours

# Cache pour les calculs complexes de transactions
TRANSACTION_CACHE_ENABLED = True  # Activer le cache LRU pour les calculs
TRANSACTION_CACHE_SIZE = 50  # Taille du cache LRU

# Seuils d'alerte pour les transactions
TRANSACTION_CRITIQUE_VOLUME = 0  # Volume critique par transaction
TRANSACTION_CRITIQUE_PRIX = 0  # Prix critique par transaction
TRANSACTION_CRITIQUE_TAUX_REUSSITE = 0.5  # Taux de réussite critique

# Configuration des labels pour les métriques de transactions
TRANSACTION_LABELS_ENABLED = False  # Activer les labels par transaction
TRANSACTION_LABELS_STRATEGIE = False # Label {strategie}
TRANSACTION_LABELS_PRODUIT = False   # Label {produit}

# ============================================================================
# EVENT METRICS - Configuration des métriques d'événements
# ============================================================================

# Fréquence de calcul des métriques d'événements
EVENT_METRICS_FREQUENCY = "tour"  # "tour" | "evenement" | "both"

# Historique des événements (nombre maximum de tours à conserver)
EVENT_HISTORY_MAX_TOURS = 200  # Historique maximum en tours

# Cache pour les calculs complexes d'événements
EVENT_CACHE_ENABLED = True  # Activer le cache LRU pour les calculs
EVENT_CACHE_SIZE = 50  # Taille du cache LRU

# Seuils d'alerte pour les événements
EVENT_CRITIQUE_FREQUENCE = 5  # Fréquence critique d'événements par tour
EVENT_CRITIQUE_IMPACT = 0.5  # Impact critique (ratio)
EVENT_CRITIQUE_INTENSITE = 0.8  # Intensité critique

# Configuration des labels pour les métriques d'événements
EVENT_LABELS_ENABLED = False  # Activer les labels par événement
EVENT_LABELS_TYPE = False     # Label {type}
EVENT_LABELS_IMPACT = False   # Label {impact}

# ============================================================================
# PERFORMANCE METRICS - Configuration des métriques de performance
# ============================================================================

# Fréquence de calcul des métriques de performance
PERFORMANCE_METRICS_FREQUENCY = "tour"  # "tour" | "transaction" | "both"

# Historique des performances (nombre maximum de tours à conserver)
PERFORMANCE_HISTORY_MAX_TOURS = 200  # Historique maximum en tours

# Cache pour les calculs complexes de performance
PERFORMANCE_CACHE_ENABLED = True  # Activer le cache LRU pour les calculs
PERFORMANCE_CACHE_SIZE = 50  # Taille du cache LRU

# Seuils d'alerte pour les performances
PERFORMANCE_CRITIQUE_TEMPS = 5.0  # Temps d'exécution critique (secondes)
PERFORMANCE_CRITIQUE_MEMOIRE = 0.8  # Utilisation mémoire critique (ratio)
PERFORMANCE_CRITIQUE_CPU = 0.9  # Utilisation CPU critique (ratio)

# Configuration des labels pour les métriques de performance
PERFORMANCE_LABELS_ENABLED = False  # Activer les labels par performance
PERFORMANCE_LABELS_COMPOSANT = False # Label {composant}
PERFORMANCE_LABELS_NIVEAU = False    # Label {niveau}

# ============================================================================
# LATENCY & THROUGHPUT - Configuration des métriques de performance
# ============================================================================

# Configuration des métriques de latence
LATENCY_COLLECTION_INTERVAL = 0.1  # Intervalle de collecte des latences (100ms)
LATENCY_HISTOGRAM_BUCKETS = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]  # Buckets pour histogrammes
LATENCY_HISTORY_SIZE = 1000  # Nombre de mesures à conserver en historique

# Configuration du throughput
THROUGHPUT_WINDOW_SIZE = 60  # Fenêtre de calcul du throughput (60 secondes)
THROUGHPUT_MIN_INTERVAL = 0.01  # Intervalle minimum entre mesures (10ms)

# Seuils de performance pour les alertes
LATENCY_WARNING_THRESHOLD = 100.0  # Seuil d'avertissement latence (100ms)
LATENCY_CRITICAL_THRESHOLD = 500.0  # Seuil critique latence (500ms)
THROUGHPUT_MIN_RATE = 0.1  # Taux minimum de throughput (0.1 op/s)