#!/usr/bin/env python3
"""
Exporter Prometheus pour TradeSim CLI
=====================================

Ce module expose les métriques de TradeSim au format Prometheus.
Il collecte les métriques depuis les services et les expose sur un endpoint HTTP.

ARCHITECTURE :
- Serveur Flask séparé de la simulation principale
- Endpoint /metrics sur port 8000 par défaut
- Métriques système (CPU/mémoire) incluses
- Stockage JSONL pour persistance
- Threading pour la collecte asynchrone
- Cache des métriques pour optimiser les performances

MÉTRIQUES EXPOSÉES (100+ métriques) :
- SIMULATION (8) : tick, événements, durée, configuration
- LATENCE (6) : achat, statistiques, événements, transactions
- BUDGET (14) : total, moyenne, variation, santé financière
- ENTREPRISES (18) : nombre, performance, comportement
- PRODUITS (16) : nombre, prix, demande, offre
- FOURNISSEURS (16) : nombre, ventes, stock, compétitivité
- TRANSACTIONS (16) : nombre, volume, prix, efficacité
- ÉVÉNEMENTS (16) : nombre, impact, fréquence, stabilité
- PERFORMANCE (16) : temps, mémoire, CPU, optimisation
- SYSTÈME (10) : CPU, mémoire, disque, réseau

FONCTIONNALITÉS :
- Exposition des métriques au format Prometheus
- Collecte automatique des métriques système
- Stockage persistant en JSONL
- Monitoring de santé (/health)
- Interface web simple (/)
- Gestion des erreurs et timeouts

Auteur: Assistant IA
Date: 2025-08-10
"""

import time
import json
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
from prometheus_client import (
    start_http_server, 
    Gauge, 
    Counter, 
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)
from flask import Flask, Response, jsonify, request
import psutil

# Configuration
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.config import (
    METRICS_ENABLED,
    METRICS_EXPORTER_PORT,
    METRICS_EXPORTER_HOST,
    METRICS_COLLECTION_INTERVAL,
    METRICS_SYSTEM_ENABLED,
    METRICS_SYSTEM_INTERVAL
)

# ============================================================================
# MÉTRIQUES PROMETHEUS
# ============================================================================

# Métriques TradeSim
produits_actifs = Gauge('tradesim_produits_actifs', 'Nombre de produits actifs')
tours_completes = Gauge('tradesim_tours_completes', 'Nombre de tours effectués')
temps_simulation_tour_seconds = Histogram(
    'tradesim_temps_simulation_tour_seconds',
    'Durée d\'un tour de simulation',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Métriques de Configuration
config_nombre_tours = Gauge('tradesim_config_nombre_tours', 'Nombre de tours configuré')
config_entreprises_par_tour = Gauge('tradesim_config_entreprises_par_tour', 'Nombre d\'entreprises par tour')
config_probabilite_selection = Gauge('tradesim_config_probabilite_selection', 'Probabilité de sélection d\'entreprise')
config_quantite_achat_max = Gauge('tradesim_config_quantite_achat_max', 'Quantité d\'achat maximum')
config_budget_entreprise_max = Gauge('tradesim_config_budget_entreprise_max', 'Budget maximum des entreprises')
config_tick_interval_event = Gauge('tradesim_config_tick_interval_event', 'Intervalle des événements')

# ============================================================================
# MÉTRIQUES DE SIMULATION (8 métriques)
# ============================================================================

# Métriques de temps et tours
tick_actuel = Gauge('tradesim_tick_actuel', 'Numéro du tick actuel de simulation')
evenements_appliques = Gauge('tradesim_evenements_appliques', 'Nombre d\'événements appliqués')
duree_simulation = Histogram(
    'tradesim_duree_simulation_seconds',
    'Durée totale de la simulation en secondes',
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
)

# Métriques de configuration
probabilite_selection_entreprise = Gauge('tradesim_probabilite_selection_entreprise', 'Probabilité de sélection d\'une entreprise par tour')
duree_pause_entre_tours = Gauge('tradesim_duree_pause_entre_tours_seconds', 'Pause entre les tours en secondes')
tick_interval_event = Gauge('tradesim_tick_interval_event', 'Intervalle entre les événements')
probabilite_evenement = Gauge('tradesim_probabilite_evenement', 'Probabilité d\'occurrence des événements')

# Métriques calculées de simulation
frequence_evenements = Gauge('tradesim_frequence_evenements', 'Fréquence des événements (événements/tour)')
taux_succes_transactions = Gauge('tradesim_taux_succes_transactions', 'Taux de succès des transactions (0-1)')
vitesse_simulation = Gauge('tradesim_vitesse_simulation_tours_par_seconde', 'Vitesse de simulation (tours/seconde)')
stabilite_prix = Gauge('tradesim_stabilite_prix', 'Stabilité des prix (coefficient de variation)')

# ============================================================================
# MÉTRIQUES DE LATENCE ET THROUGHPUT
# ============================================================================

# Métriques de latence et throughput
latency_achat_produit_ms = Histogram(
    'tradesim_latency_achat_produit_ms',
    'Temps de réponse pour un achat (millisecondes)',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
)
latency_calcul_statistiques_ms = Histogram(
    'tradesim_latency_calcul_statistiques_ms',
    'Temps de calcul des statistiques (millisecondes)',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
)
latency_application_evenement_ms = Histogram(
    'tradesim_latency_application_evenement_ms',
    'Temps d\'application d\'un événement (millisecondes)',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
)
latency_collecte_metriques_ms = Histogram(
    'tradesim_latency_collecte_metriques_ms',
    'Temps de collecte des métriques (millisecondes)',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
)
latency_validation_donnees_ms = Histogram(
    'tradesim_latency_validation_donnees_ms',
    'Temps de validation des données (millisecondes)',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
)
latency_generation_id_ms = Histogram(
    'tradesim_latency_generation_id_ms',
    'Temps de génération d\'un ID unique (millisecondes)',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
)

# ============================================================================
# MÉTRIQUES DE PERFORMANCE ET MONITORING
# ============================================================================

# Métriques de performance des calculs
metrics_calculation_duration = Histogram(
    'tradesim_metrics_calculation_duration_seconds',
    'Temps de calcul des métriques historiques (secondes)',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Métriques de cardinalité
metrics_cardinality = Gauge(
    'tradesim_metrics_cardinality',
    'Nombre de séries temporelles créées',
    ['metric_type', 'entity_type']
)

# Métriques de compression
metrics_compression_ratio = Gauge(
    'tradesim_metrics_compression_ratio',
    'Ratio de compression des données historiques',
    ['entity_type']
)

# Métriques de latence d'envoi
metrics_send_latency_ms = Histogram(
    'tradesim_metrics_send_latency_ms',
    'Latence d\'envoi des métriques vers Prometheus (millisecondes)',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
)

# Métriques de throughput
transactions_par_seconde = Counter('tradesim_transactions_par_seconde', 'Nombre de transactions par seconde')
evenements_par_seconde = Counter('tradesim_evenements_par_seconde', 'Nombre d\'événements appliqués par seconde')
metriques_collectees_par_seconde = Counter('tradesim_metriques_collectees_par_seconde', 'Nombre de métriques collectées par seconde')
logs_ecrits_par_seconde = Counter('tradesim_logs_ecrits_par_seconde', 'Nombre de logs écrits par seconde')
actions_validees_par_seconde = Counter('tradesim_actions_validees_par_seconde', 'Nombre d\'actions validées par seconde')
ids_generes_par_seconde = Counter('tradesim_ids_generes_par_seconde', 'Nombre d\'IDs générés par seconde')

# Métriques système
cpu_usage_percent = Gauge('tradesim_cpu_usage_percent', 'Utilisation CPU (%)')
memory_usage_bytes = Gauge('tradesim_memory_usage_bytes', 'Utilisation mémoire (bytes)')
memory_usage_percent = Gauge('tradesim_memory_usage_percent', 'Utilisation mémoire (%)')
disk_usage_percent = Gauge('tradesim_disk_usage_percent', 'Utilisation disque (%)')
process_uptime_seconds = Gauge('tradesim_process_uptime_seconds', 'Temps de fonctionnement du processus')

# ============================================================================
# MÉTRIQUES DE BUDGET (14 métriques)
# ============================================================================

# Métriques de base (5 métriques)
budget_total_entreprises = Gauge('tradesim_budget_total_entreprises', 'Budget total de toutes les entreprises (somme)', ['tick'])
budget_moyen_entreprises = Gauge('tradesim_budget_moyen_entreprises', 'Budget moyen des entreprises (moyenne arithmétique)', ['tick'])
budget_median_entreprises = Gauge('tradesim_budget_median_entreprises', 'Budget médian des entreprises (valeur centrale)', ['tick'])
budget_ecart_type_entreprises = Gauge('tradesim_budget_ecart_type_entreprises', 'Écart-type des budgets (dispersion)', ['tick'])
budget_coefficient_variation = Gauge('tradesim_budget_coefficient_variation', 'Coefficient de variation (CV = σ/μ)', ['tick'])

# Métriques de variation (3 métriques)
budget_variation_totale = Gauge('tradesim_budget_variation_totale', 'Variation totale des budgets (actuel - initial)', ['tick'])
budget_depenses_totales = Counter('tradesim_budget_depenses_totales', 'Dépenses totales cumulées de toutes les entreprises', ['tick'])
budget_gains_totaux = Counter('tradesim_budget_gains_totaux', 'Gains totaux cumulés de toutes les entreprises', ['tick'])

# Métriques de santé financière (3 métriques)
budget_ratio_depenses_revenus = Gauge('tradesim_budget_ratio_depenses_revenus', 'Ratio dépenses/revenus (dépenses/gains)', ['tick'])
budget_entreprises_critiques = Gauge('tradesim_budget_entreprises_critiques', 'Nombre d\'entreprises avec budget critique (≤1000€)', ['tick'])
budget_entreprises_faibles = Gauge('tradesim_budget_entreprises_faibles', 'Nombre d\'entreprises avec budget faible (1000-3000€)', ['tick'])

# Métriques de tendance (2 métriques)
budget_evolution_tour = Gauge('tradesim_budget_evolution_tour', 'Évolution du budget total depuis le tour précédent', ['tick'])
budget_tendance_globale = Gauge('tradesim_budget_tendance_globale', 'Tendance globale des budgets (pente de régression)', ['tick'])

# Métriques avancées (1 métrique)
budget_skewness = Gauge('tradesim_budget_skewness', 'Asymétrie de la distribution des budgets (skewness)', ['tick'])

# ============================================================================
# MÉTRIQUES D'ENTREPRISES (18 métriques)
# ============================================================================

# Métriques de base (6 métriques)
entreprises_total = Gauge('tradesim_entreprises_total', 'Nombre total d\'entreprises')
entreprises_actives = Gauge('tradesim_entreprises_actives', 'Nombre d\'entreprises actives (budget > 0)')
entreprises_par_pays = Gauge('tradesim_entreprises_par_pays', 'Répartition des entreprises par pays')
entreprises_par_continent = Gauge('tradesim_entreprises_par_continent', 'Répartition des entreprises par continent')
entreprises_par_strategie = Gauge('tradesim_entreprises_par_strategie', 'Répartition des entreprises par stratégie')
entreprises_par_type_prefere = Gauge('tradesim_entreprises_par_type_prefere', 'Répartition des entreprises par type de produit préféré')

# Métriques de performance (6 métriques)
entreprises_transactions_moyennes = Gauge('tradesim_entreprises_transactions_moyennes', 'Nombre moyen de transactions par entreprise', ['tick'])
entreprises_budget_moyen = Gauge('tradesim_entreprises_budget_moyen', 'Budget moyen par entreprise', ['tick'])
entreprises_stock_moyen = Gauge('tradesim_entreprises_stock_moyen', 'Stock moyen par entreprise', ['tick'])
entreprises_rentabilite = Gauge('tradesim_entreprises_rentabilite', 'Rentabilité moyenne des entreprises (budget actuel / budget initial)', ['tick'])
entreprises_efficacite_achat = Gauge('tradesim_entreprises_efficacite_achat', 'Efficacité d\'achat moyenne (transactions / budget dépensé)', ['tick'])
entreprises_survie_taux = Gauge('tradesim_entreprises_survie_taux', 'Taux de survie des entreprises (budget > 0)', ['tick'])

# Métriques de comportement (6 métriques)
entreprises_frequence_achat = Gauge('tradesim_entreprises_frequence_achat', 'Fréquence d\'achat moyenne (transactions par tour)', ['tick'])
entreprises_preference_produits = Gauge('tradesim_entreprises_preference_produits', 'Préférence de produits (diversité des types préférés)', ['tick'])
entreprises_adaptation_prix = Gauge('tradesim_entreprises_adaptation_prix', 'Adaptation aux variations de prix', ['tick'])
entreprises_competitivite = Gauge('tradesim_entreprises_competitivite', 'Indice de compétitivité des entreprises', ['tick'])
entreprises_resilience = Gauge('tradesim_entreprises_resilience', 'Indice de résilience des entreprises', ['tick'])
entreprises_innovation = Gauge('tradesim_entreprises_innovation', 'Indice d\'innovation des entreprises', ['tick'])

# ============================================================================
# MÉTRIQUES DE PRODUITS (16 métriques)
# ============================================================================

# Métriques de base (6 métriques)
produits_total = Gauge('tradesim_produits_total', 'Nombre total de produits')
# produits_actifs déjà défini plus haut
produits_par_type = Gauge('tradesim_produits_par_type', 'Répartition des produits par type')
produits_par_continent = Gauge('tradesim_produits_par_continent', 'Répartition des produits par continent')
produits_prix_moyen = Gauge('tradesim_produits_prix_moyen', 'Prix moyen des produits', ['tick'])
produits_prix_median = Gauge('tradesim_produits_prix_median', 'Prix médian des produits', ['tick'])

# Métriques de performance (6 métriques)
produits_demande_moyenne = Gauge('tradesim_produits_demande_moyenne', 'Demande moyenne par produit', ['tick'])
produits_offre_moyenne = Gauge('tradesim_produits_offre_moyenne', 'Offre moyenne par produit', ['tick'])
produits_rotation_stock = Gauge('tradesim_produits_rotation_stock', 'Rotation de stock moyenne', ['tick'])
produits_rentabilite = Gauge('tradesim_produits_rentabilite', 'Rentabilité moyenne des produits', ['tick'])
produits_popularite = Gauge('tradesim_produits_popularite', 'Popularité moyenne des produits', ['tick'])
produits_disponibilite = Gauge('tradesim_produits_disponibilite', 'Taux de disponibilité moyen', ['tick'])

# Métriques de comportement (4 métriques)
produits_volatilite_prix = Gauge('tradesim_produits_volatilite_prix', 'Volatilité des prix', ['tick'])
produits_tendance_prix = Gauge('tradesim_produits_tendance_prix', 'Tendance des prix', ['tick'])
produits_elasticite_demande = Gauge('tradesim_produits_elasticite_demande', 'Élasticité de la demande', ['tick'])
produits_competitivite = Gauge('tradesim_produits_competitivite', 'Indice de compétitivité des produits', ['tick'])

# ============================================================================
# MÉTRIQUES DE FOURNISSEURS (16 métriques)
# ============================================================================

# Métriques de base (6 métriques)
fournisseurs_total = Gauge('tradesim_fournisseurs_total', 'Nombre total de fournisseurs')
fournisseurs_actifs = Gauge('tradesim_fournisseurs_actifs', 'Nombre de fournisseurs actifs')
fournisseurs_par_pays = Gauge('tradesim_fournisseurs_par_pays', 'Répartition des fournisseurs par pays')
fournisseurs_par_continent = Gauge('tradesim_fournisseurs_par_continent', 'Répartition des fournisseurs par continent')
fournisseurs_stock_moyen = Gauge('tradesim_fournisseurs_stock_moyen', 'Stock moyen par fournisseur', ['tick'])
fournisseurs_produits_moyen = Gauge('tradesim_fournisseurs_produits_moyen', 'Nombre moyen de produits par fournisseur', ['tick'])

# Métriques de performance (6 métriques)
fournisseurs_ventes_moyennes = Gauge('tradesim_fournisseurs_ventes_moyennes', 'Ventes moyennes par fournisseur', ['tick'])
fournisseurs_rotation_stock = Gauge('tradesim_fournisseurs_rotation_stock', 'Rotation de stock moyenne', ['tick'])
fournisseurs_disponibilite = Gauge('tradesim_fournisseurs_disponibilite', 'Taux de disponibilité moyen', ['tick'])
fournisseurs_rentabilite = Gauge('tradesim_fournisseurs_rentabilite', 'Rentabilité moyenne des fournisseurs', ['tick'])
fournisseurs_popularite = Gauge('tradesim_fournisseurs_popularite', 'Popularité moyenne des fournisseurs', ['tick'])
fournisseurs_efficacite = Gauge('tradesim_fournisseurs_efficacite', 'Efficacité moyenne des fournisseurs', ['tick'])

# Métriques de comportement (4 métriques)
fournisseurs_volatilite_prix = Gauge('tradesim_fournisseurs_volatilite_prix', 'Volatilité des prix par fournisseur')
fournisseurs_tendance_prix = Gauge('tradesim_fournisseurs_tendance_prix', 'Tendance des prix par fournisseur')
fournisseurs_competitivite = Gauge('tradesim_fournisseurs_competitivite', 'Indice de compétitivité des fournisseurs')
fournisseurs_resilience = Gauge('tradesim_fournisseurs_resilience', 'Indice de résilience des fournisseurs')

# ============================================================================
# MÉTRIQUES DE TRANSACTIONS (16 métriques)
# ============================================================================

# Métriques de base (6 métriques) - SANS LABELS (simplifiées)
transactions_total = Gauge('tradesim_transactions_total', 'Nombre total de transactions')
transactions_reussies = Counter('tradesim_transactions_reussies_total', 'Nombre de transactions réussies')
transactions_echouees = Counter('tradesim_transactions_echouees_total', 'Nombre de transactions échouées')
transactions_par_strategie = Gauge('tradesim_transactions_par_strategie', 'Répartition des transactions par stratégie')
transactions_par_produit = Gauge('tradesim_transactions_par_produit', 'Répartition des transactions par produit')
transactions_par_entreprise = Gauge('tradesim_transactions_par_entreprise', 'Répartition des transactions par entreprise')
transactions_par_fournisseur = Gauge('tradesim_transactions_par_fournisseur', 'Répartition des transactions par fournisseur')

# Métriques de performance (6 métriques) - SANS LABELS (simplifiées)
transactions_volume_moyen = Gauge('tradesim_transactions_volume_moyen', 'Volume moyen par transaction')
transactions_prix_moyen = Gauge('tradesim_transactions_prix_moyen', 'Prix moyen par transaction')
transactions_frequence = Gauge('tradesim_transactions_frequence', 'Fréquence des transactions (par tour)')
transactions_taux_reussite = Gauge('tradesim_transactions_taux_reussite', 'Taux de réussite des transactions')
transactions_efficacite = Gauge('tradesim_transactions_efficacite', 'Efficacité des transactions')
transactions_rentabilite = Gauge('tradesim_transactions_rentabilite', 'Rentabilité moyenne des transactions')

# Métriques de comportement (4 métriques) - SANS LABELS (simplifiées)
transactions_volatilite_prix = Gauge('tradesim_transactions_volatilite_prix', 'Volatilité des prix de transaction')
transactions_tendance_volume = Gauge('tradesim_transactions_tendance_volume', 'Tendance des volumes de transaction')
transactions_preference_strategie = Gauge('tradesim_transactions_preference_strategie', 'Préférence de stratégie')
transactions_competitivite = Gauge('tradesim_transactions_competitivite', 'Indice de compétitivité des transactions')

# Métriques de transactions supplémentaires (utilisées dans le code)
transactions_moyennes_par_tour = Gauge('tradesim_transactions_moyennes_par_tour', 'Nombre moyen de transactions par tour', ['tick'])
taux_reussite_transactions = Gauge('tradesim_taux_reussite_transactions', 'Taux de réussite des transactions', ['tick'])
montant_moyen_transaction = Gauge('tradesim_montant_moyen_transaction', 'Montant moyen par transaction', ['tick'])
volume_total_transactions = Counter('tradesim_volume_total_transactions_total', 'Volume total des transactions', ['tick'])
frequence_transactions = Gauge('tradesim_frequence_transactions', 'Fréquence des transactions', ['tick'])
efficacite_transactions = Gauge('tradesim_efficacite_transactions', 'Efficacité des transactions', ['tick'])

# ============================================================================
# MÉTRIQUES D'ÉVÉNEMENTS (16 métriques)
# ============================================================================

# Métriques de base (6 métriques)
evenements_total = Gauge('tradesim_evenements_total', 'Nombre total d\'événements')
evenements_par_type = Gauge('tradesim_evenements_par_type', 'Répartition des événements par type')
evenements_par_impact = Gauge('tradesim_evenements_par_impact', 'Répartition des événements par impact')
evenements_frequence = Gauge('tradesim_evenements_frequence', 'Fréquence des événements (par tour)')
evenements_duree_moyenne = Gauge('tradesim_evenements_duree_moyenne', 'Durée moyenne des événements')
evenements_intensite_moyenne = Gauge('tradesim_evenements_intensite_moyenne', 'Intensité moyenne des événements')

# Métriques de performance (6 métriques)
evenements_impact_budget = Gauge('tradesim_evenements_impact_budget', 'Impact moyen sur les budgets')
evenements_impact_prix = Gauge('tradesim_evenements_impact_prix', 'Impact moyen sur les prix')
evenements_impact_stock = Gauge('tradesim_evenements_impact_stock', 'Impact moyen sur les stocks')
evenements_efficacite = Gauge('tradesim_evenements_efficacite', 'Efficacité des événements')
evenements_rentabilite = Gauge('tradesim_evenements_rentabilite', 'Rentabilité des événements')
evenements_stabilite = Gauge('tradesim_evenements_stabilite', 'Stabilité du système d\'événements')

# Métriques de comportement (4 métriques)
evenements_volatilite = Gauge('tradesim_evenements_volatilite', 'Volatilité des événements')
evenements_tendance = Gauge('tradesim_evenements_tendance', 'Tendance des événements')
evenements_correlation = Gauge('tradesim_evenements_correlation', 'Corrélation entre événements')
evenements_predictibilite = Gauge('tradesim_evenements_predictibilite', 'Prédictibilité des événements')

# Métriques d'événements supplémentaires (utilisées dans le code)
evenements_inflation = Gauge('tradesim_evenements_inflation', 'Nombre d\'événements d\'inflation', ['tick'])
evenements_reassort = Gauge('tradesim_evenements_reassort', 'Nombre d\'événements de reassort', ['tick'])
evenements_recharge_budget = Gauge('tradesim_evenements_recharge_budget', 'Nombre d\'événements de recharge budget', ['tick'])
evenements_variation_disponibilite = Gauge('tradesim_evenements_variation_disponibilite', 'Nombre d\'événements de variation disponibilité', ['tick'])
impact_moyen_evenements = Gauge('tradesim_impact_moyen_evenements', 'Impact moyen des événements', ['tick'])
frequence_evenements_inflation = Gauge('tradesim_frequence_evenements_inflation', 'Fréquence des événements d\'inflation', ['tick'])
frequence_evenements_reassort = Gauge('tradesim_frequence_evenements_reassort', 'Fréquence des événements de reassort', ['tick'])
frequence_evenements_recharge = Gauge('tradesim_frequence_evenements_recharge', 'Fréquence des événements de recharge', ['tick'])
frequence_evenements_disponibilite = Gauge('tradesim_frequence_evenements_disponibilite', 'Fréquence des événements de disponibilité', ['tick'])

# ============================================================================
# MÉTRIQUES DE PERFORMANCE (16 métriques)
# ============================================================================

# Métriques de base (6 métriques)
performance_temps_execution = Gauge('tradesim_performance_temps_execution', 'Temps d\'exécution moyen')
performance_memoire_utilisee = Gauge('tradesim_performance_memoire_utilisee', 'Mémoire utilisée (MB)')
performance_cpu_utilisation = Gauge('tradesim_performance_cpu_utilisation', 'Utilisation CPU (%)')
performance_temps_reponse = Gauge('tradesim_performance_temps_reponse', 'Temps de réponse moyen')
performance_throughput = Gauge('tradesim_performance_throughput', 'Débit de traitement (ops/sec)')
performance_latence = Gauge('tradesim_performance_latence', 'Latence moyenne')

# Métriques de performance (6 métriques)
performance_efficacite_cache = Gauge('tradesim_performance_efficacite_cache', 'Efficacité du cache')
performance_optimisation = Gauge('tradesim_performance_optimisation', 'Niveau d\'optimisation')
performance_charge_systeme = Gauge('tradesim_performance_charge_systeme', 'Charge du système (%)')
performance_stabilite = Gauge('tradesim_performance_stabilite', 'Stabilité des performances')
performance_scalabilite = Gauge('tradesim_performance_scalabilite', 'Indice de scalabilité')
performance_qualite = Gauge('tradesim_performance_qualite', 'Qualité des performances')

# Métriques de comportement (4 métriques)
performance_volatilite = Gauge('tradesim_performance_volatilite', 'Volatilité des performances')
performance_tendance = Gauge('tradesim_performance_tendance', 'Tendance des performances')
performance_bottlenecks = Gauge('tradesim_performance_bottlenecks', 'Nombre de goulots d\'étranglement')
performance_optimisations_disponibles = Gauge('tradesim_performance_optimisations_disponibles', 'Optimisations disponibles')

# ============================================================================
# MÉTRIQUES INDIVIDUELLES AVEC LABELS (NOUVELLES)
# ============================================================================

# Métriques par entreprise (avec labels pour filtrage et agrégation)
entreprise_budget = Gauge('tradesim_entreprise_budget', 'Budget actuel par entreprise', ['id', 'nom', 'continent', 'strategie', 'tick'])
entreprise_budget_initial = Gauge('tradesim_entreprise_budget_initial', 'Budget initial par entreprise', ['id', 'nom', 'tick'])
entreprise_budget_evolution = Gauge('tradesim_entreprise_budget_evolution', 'Évolution du budget depuis le tour précédent', ['id', 'nom', 'tick'])
entreprise_budget_tendance = Gauge('tradesim_entreprise_budget_tendance', 'Tendance du budget sur 5 tours', ['id', 'nom', 'tick'])
entreprise_transactions_total = Gauge('tradesim_entreprise_transactions_total', 'Nombre total de transactions par entreprise', ['id', 'nom', 'continent', 'tick'])

# Métriques de stock par produit par entreprise (granularité complète)
entreprise_stock_produit = Gauge('tradesim_entreprise_stock_produit', 'Stock par produit par entreprise', ['id_entreprise', 'nom_entreprise', 'id_produit', 'nom_produit', 'type_produit', 'tick'])

# Métriques par produit (prix et évolution uniquement)
produit_prix = Gauge('tradesim_produit_prix', 'Prix actuel par produit', ['id', 'nom', 'type', 'tick'])
produit_prix_evolution = Gauge('tradesim_produit_prix_evolution', 'Évolution du prix depuis le tour précédent', ['id', 'nom', 'type', 'tick'])
produit_prix_tendance = Gauge('tradesim_produit_prix_tendance', 'Tendance du prix sur 5 tours', ['id', 'nom', 'type', 'tick'])

# Métriques de stock par produit par fournisseur (granularité complète)
fournisseur_stock_produit = Gauge('tradesim_fournisseur_stock_produit', 'Stock par produit par fournisseur', ['id_fournisseur', 'nom_fournisseur', 'id_produit', 'nom_produit', 'type_produit', 'tick'])

# ============================================================================
# MÉTRIQUES HISTORIQUES DE STOCK
# ============================================================================

# Métriques historiques de stock par entité
entreprise_stock_historique = Gauge(
    'tradesim_entreprise_stock_historique',
    'Stock historique par produit par entreprise par tour',
    ['id_entite', 'nom_entite', 'id_produit', 'nom_produit', 'tour', 'tick']
)

fournisseur_stock_historique = Gauge(
    'tradesim_fournisseur_stock_historique',
    'Stock historique par produit par fournisseur par tour',
    ['id_entite', 'nom_entite', 'id_produit', 'nom_produit', 'tour', 'tick']
)

# Métriques d'évolution de stock
entreprise_stock_evolution = Gauge(
    'tradesim_entreprise_stock_evolution',
    'Évolution du stock par produit par entreprise sur une période',
    ['id_entite', 'nom_entite', 'id_produit', 'nom_produit', 'periode', 'tick']
)

fournisseur_stock_evolution = Gauge(
    'tradesim_fournisseur_stock_evolution',
    'Évolution du stock par produit par fournisseur sur une période',
    ['id_entite', 'nom_entite', 'id_produit', 'nom_produit', 'periode', 'tick']
)

# Métriques par fournisseur (autres métriques)
fournisseur_prix_moyen = Gauge('tradesim_fournisseur_prix_moyen', 'Prix moyen des produits par fournisseur', ['id', 'nom', 'continent', 'tick'])
fournisseur_ventes_total = Gauge('tradesim_fournisseur_ventes_total', 'Nombre total de ventes par fournisseur', ['id', 'nom', 'continent', 'tick'])
fournisseur_disponibilite = Gauge('tradesim_fournisseur_disponibilite', 'Taux de disponibilité par fournisseur', ['id', 'nom', 'continent', 'tick'])
fournisseur_rotation_stock = Gauge('tradesim_fournisseur_rotation_stock', 'Rotation de stock par fournisseur', ['id', 'nom', 'continent', 'tick'])
fournisseur_rentabilite = Gauge('tradesim_fournisseur_rentabilite', 'Rentabilité par fournisseur', ['id', 'nom', 'continent', 'tick'])

# ============================================================================
# CLASSE EXPORTER
# ============================================================================

class PrometheusExporter:
    """
    Exporteur Prometheus pour TradeSim
    
    ARCHITECTURE :
    - Serveur Flask avec endpoints REST
    - Threading pour la collecte asynchrone des métriques système
    - Cache des métriques pour optimiser les performances
    - Stockage persistant en JSONL
    - Gestion des erreurs et timeouts
    
    RESPONSABILITÉS :
    - Exposition des métriques au format Prometheus (/metrics)
    - Collecte automatique des métriques système (CPU, mémoire, disque)
    - Stockage des métriques en JSONL pour persistance
    - Gestion du serveur HTTP avec monitoring de santé (/health)
    - Interface web simple pour visualisation (/)
    - Mise à jour des métriques TradeSim en temps réel
    
    ENDPOINTS :
    - /metrics : Métriques Prometheus (format texte)
    - /health : État de santé du service (JSON)
    - / : Interface web simple (HTML)
    
    MÉTRIQUES GÉRÉES (100+) :
    - Métriques de simulation (tick, événements, durée)
    - Métriques de latence et throughput
    - Métriques de budget, entreprises, produits
    - Métriques de fournisseurs, transactions, événements
    - Métriques de performance système
    - Métriques système (CPU, mémoire, disque, réseau)
    """
    
    def __init__(self, port: int = None, host: str = None):
        """
        Initialise l'exporteur Prometheus
        
        Args:
            port: Port de l'exporter (défaut: METRICS_EXPORTER_PORT)
            host: Host de l'exporter (défaut: METRICS_EXPORTER_HOST)
        """
        self.port = port or METRICS_EXPORTER_PORT
        self.host = host or METRICS_EXPORTER_HOST
        self.app = Flask(__name__)
        self.collection_thread = None
        self.running = False
        self.start_time = time.time()
        
        # Configuration des routes Flask
        self._setup_routes()
        
                        # Fichier de stockage JSONL
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        self.metrics_file = os.path.join(logs_dir, 'metrics.jsonl')
        
        # Initialiser les métriques de configuration
        self._init_config_metrics()
        
    def _setup_routes(self):
        """Configure les routes Flask pour l'exporter"""
        
        @self.app.route('/metrics')
        def metrics():
            """Endpoint principal pour les métriques Prometheus"""
            return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
        
        @self.app.route('/health')
        def health():
            """Endpoint de santé de l'exporter"""
            return {
                'status': 'healthy',
                'uptime': time.time() - self.start_time,
                'metrics_enabled': METRICS_ENABLED
            }
        
        @self.app.route('/')
        def index():
            """Page d'accueil avec informations sur l'exporter"""
            return {
                'service': 'TradeSim Prometheus Exporter',
                'version': '1.0.0',
                'endpoints': {
                    '/metrics': 'Métriques Prometheus',
                    '/health': 'Santé du service',
                    '/update_metrics': 'Mise à jour métriques',
                    '/': 'Cette page'
                },
                'configuration': {
                    'port': self.port,
                    'host': self.host,
                    'metrics_enabled': METRICS_ENABLED,
                    'collection_interval': METRICS_COLLECTION_INTERVAL
                }
            }
        
        @self.app.route('/update_metrics', methods=['POST'])
        def update_metrics():
            """Endpoint pour mettre à jour les métriques via HTTP"""
            try:
                data = request.get_json()
                if data:

                    self.update_tradesim_metrics(data)
                    return jsonify({'status': 'success', 'message': 'Métriques mises à jour'})
                else:
                    return jsonify({'status': 'error', 'message': 'Données manquantes'}), 400
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
    
    def start(self):
        """Démarre l'exporteur Prometheus"""
        if not METRICS_ENABLED:
            print("⚠️  Monitoring désactivé dans la configuration")
            return
            
        try:
            # Démarrage du serveur Flask
            self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False
            )
            print(f"✅ Exporter Prometheus démarré sur {self.host}:{self.port}")
            
        except Exception as e:
            print(f"❌ Erreur lors du démarrage de l'exporter: {e}")
    
    def _init_config_metrics(self):
        """Initialise les métriques de configuration depuis config.py"""
        try:
            from config.config import (
                NOMBRE_TOURS, N_ENTREPRISES_PAR_TOUR, PROBABILITE_SELECTION_ENTREPRISE,
                QUANTITE_ACHAT_MAX, BUDGET_ENTREPRISE_MAX, TICK_INTERVAL_EVENT
            )
            
            # Mise à jour des métriques de configuration
            config_nombre_tours.set(NOMBRE_TOURS)
            config_entreprises_par_tour.set(N_ENTREPRISES_PAR_TOUR)
            config_probabilite_selection.set(PROBABILITE_SELECTION_ENTREPRISE)
            config_quantite_achat_max.set(QUANTITE_ACHAT_MAX)
            config_budget_entreprise_max.set(BUDGET_ENTREPRISE_MAX)
            config_tick_interval_event.set(TICK_INTERVAL_EVENT)
            
            print("📊 Métriques de configuration initialisées")
            
        except Exception as e:
            print(f"⚠️ Erreur lors de l'initialisation des métriques de configuration: {e}")
    
    def collect_system_metrics(self):
        """Collecte les métriques système"""
        if not METRICS_SYSTEM_ENABLED:
            return
            
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_usage_percent.set(cpu_percent)
            
            # Mémoire
            memory = psutil.virtual_memory()
            memory_usage_bytes.set(memory.used)
            memory_usage_percent.set(memory.percent)
            
            # Disque
            disk = psutil.disk_usage('/')
            disk_usage_percent.set(disk.percent)
            
            # Uptime du processus
            process_uptime_seconds.set(time.time() - self.start_time)
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la collecte des métriques système: {e}")
    
    def update_tradesim_metrics(self, metrics_data: Dict[str, Any]):
        """
        Met à jour les métriques TradeSim
        
        Args:
            metrics_data: Dictionnaire contenant les métriques à mettre à jour
        """
        try:

            # Mise à jour des métriques de base
            if 'transactions_total' in metrics_data:
                transactions_total.inc(metrics_data['transactions_total'])
            
            if 'produits_actifs' in metrics_data:
                produits_actifs.set(metrics_data['produits_actifs'])
            
            if 'tours_completes' in metrics_data:
                tours_completes.set(metrics_data['tours_completes'])
            
            if 'temps_simulation_tour_seconds' in metrics_data:
                temps_simulation_tour_seconds.observe(metrics_data['temps_simulation_tour_seconds'])
            
            # ============================================================================
            # MÉTRIQUES DE SIMULATION (8 métriques)
            # ============================================================================
            
            # Métriques de temps et tours
            # Initialiser tick_value avec une valeur par défaut
            tick_value = 0
            if 'tick_actuel' in metrics_data:
                tick_actuel.set(metrics_data['tick_actuel'])
                # Stocker la valeur du tick pour l'utiliser dans les labels
                tick_value = metrics_data['tick_actuel']
            
            if 'evenements_appliques' in metrics_data:
                evenements_appliques.set(metrics_data['evenements_appliques'])
            
            if 'duree_simulation' in metrics_data:
                duree_simulation.observe(metrics_data['duree_simulation'])
            
            # Métriques de configuration
            if 'probabilite_selection_entreprise' in metrics_data:
                probabilite_selection_entreprise.set(metrics_data['probabilite_selection_entreprise'])
            
            if 'duree_pause_entre_tours' in metrics_data:
                duree_pause_entre_tours.set(metrics_data['duree_pause_entre_tours'])
            
            if 'tick_interval_event' in metrics_data:
                tick_interval_event.set(metrics_data['tick_interval_event'])
            
            if 'probabilite_evenement' in metrics_data:
                probabilite_evenement.set(metrics_data['probabilite_evenement'])
            
            # Métriques calculées de simulation
            if 'frequence_evenements' in metrics_data:
                frequence_evenements.set(metrics_data['frequence_evenements'])
            
            if 'taux_succes_transactions' in metrics_data:
                taux_succes_transactions.set(metrics_data['taux_succes_transactions'])
            
            if 'vitesse_simulation' in metrics_data:
                vitesse_simulation.set(metrics_data['vitesse_simulation'])
            
            if 'stabilite_prix' in metrics_data:
                stabilite_prix.set(metrics_data['stabilite_prix'])
            
            # ============================================================================
            # MÉTRIQUES DE BUDGET (14 métriques)
            # ============================================================================
            
            if 'budget_total_entreprises' in metrics_data:
                budget_total_entreprises.labels(tick=str(tick_value)).set(metrics_data['budget_total_entreprises'])
            
            if 'budget_moyen_entreprises' in metrics_data:
                budget_moyen_entreprises.labels(tick=str(tick_value)).set(metrics_data['budget_moyen_entreprises'])
            
            if 'budget_median_entreprises' in metrics_data:
                budget_median_entreprises.labels(tick=str(tick_value)).set(metrics_data['budget_median_entreprises'])
            
            if 'budget_ecart_type_entreprises' in metrics_data:
                budget_ecart_type_entreprises.labels(tick=str(tick_value)).set(metrics_data['budget_ecart_type_entreprises'])
            
            if 'budget_coefficient_variation' in metrics_data:
                budget_coefficient_variation.labels(tick=str(tick_value)).set(metrics_data['budget_coefficient_variation'])
            
            if 'budget_variation_totale' in metrics_data:
                budget_variation_totale.labels(tick=str(tick_value)).set(metrics_data['budget_variation_totale'])
            
            if 'budget_depenses_totales' in metrics_data:
                budget_depenses_totales.labels(tick=str(tick_value)).inc(metrics_data['budget_depenses_totales'])
            
            if 'budget_gains_totaux' in metrics_data:
                budget_gains_totaux.labels(tick=str(tick_value)).inc(metrics_data['budget_gains_totaux'])
            
            if 'budget_ratio_depenses_revenus' in metrics_data:
                budget_ratio_depenses_revenus.labels(tick=str(tick_value)).set(metrics_data['budget_ratio_depenses_revenus'])
            
            if 'budget_entreprises_critiques' in metrics_data:
                budget_entreprises_critiques.labels(tick=str(tick_value)).set(metrics_data['budget_entreprises_critiques'])
            
            if 'budget_entreprises_faibles' in metrics_data:
                budget_entreprises_faibles.labels(tick=str(tick_value)).set(metrics_data['budget_entreprises_faibles'])
            
            if 'budget_evolution_tour' in metrics_data:
                budget_evolution_tour.labels(tick=str(tick_value)).set(metrics_data['budget_evolution_tour'])
            
            if 'budget_tendance_globale' in metrics_data:
                budget_tendance_globale.labels(tick=str(tick_value)).set(metrics_data['budget_tendance_globale'])
            
            if 'budget_skewness' in metrics_data:
                budget_skewness.labels(tick=str(tick_value)).set(metrics_data['budget_skewness'])
            
            # ============================================================================
            # MÉTRIQUES D'ENTREPRISES (18 métriques)
            # ============================================================================
            
            if 'entreprises_total' in metrics_data:
                entreprises_total.set(metrics_data['entreprises_total'])
            
            if 'entreprises_actives' in metrics_data:
                entreprises_actives.set(metrics_data['entreprises_actives'])
            
            if 'entreprises_par_pays' in metrics_data:
                if isinstance(metrics_data['entreprises_par_pays'], dict):
                    entreprises_par_pays.set(sum(metrics_data['entreprises_par_pays'].values()))
                else:
                    entreprises_par_pays.set(metrics_data['entreprises_par_pays'])
            
            if 'entreprises_par_continent' in metrics_data:
                if isinstance(metrics_data['entreprises_par_continent'], dict):
                    entreprises_par_continent.set(sum(metrics_data['entreprises_par_continent'].values()))
                else:
                    entreprises_par_continent.set(metrics_data['entreprises_par_continent'])
            
            if 'entreprises_par_strategie' in metrics_data:
                if isinstance(metrics_data['entreprises_par_strategie'], dict):
                    entreprises_par_strategie.set(sum(metrics_data['entreprises_par_strategie'].values()))
                else:
                    entreprises_par_strategie.set(metrics_data['entreprises_par_strategie'])
            
            if 'entreprises_par_type_prefere' in metrics_data:
                if isinstance(metrics_data['entreprises_par_type_prefere'], dict):
                    entreprises_par_type_prefere.set(sum(metrics_data['entreprises_par_type_prefere'].values()))
                else:
                    entreprises_par_type_prefere.set(metrics_data['entreprises_par_type_prefere'])
            
            if 'entreprises_transactions_moyennes' in metrics_data:
                entreprises_transactions_moyennes.labels(tick=str(tick_value)).set(metrics_data['entreprises_transactions_moyennes'])
            
            if 'entreprises_budget_moyen' in metrics_data:
                entreprises_budget_moyen.labels(tick=str(tick_value)).set(metrics_data['entreprises_budget_moyen'])
            
            if 'entreprises_stock_moyen' in metrics_data:
                entreprises_stock_moyen.labels(tick=str(tick_value)).set(metrics_data['entreprises_stock_moyen'])
            
            if 'entreprises_rentabilite' in metrics_data:
                entreprises_rentabilite.labels(tick=str(tick_value)).set(metrics_data['entreprises_rentabilite'])
            
            if 'entreprises_efficacite_achat' in metrics_data:
                entreprises_efficacite_achat.labels(tick=str(tick_value)).set(metrics_data['entreprises_efficacite_achat'])
            
            if 'entreprises_survie_taux' in metrics_data:
                entreprises_survie_taux.labels(tick=str(tick_value)).set(metrics_data['entreprises_survie_taux'])
            
            if 'entreprises_frequence_achat' in metrics_data:
                entreprises_frequence_achat.labels(tick=str(tick_value)).set(metrics_data['entreprises_frequence_achat'])
            
            if 'entreprises_preference_produits' in metrics_data:
                entreprises_preference_produits.labels(tick=str(tick_value)).set(metrics_data['entreprises_preference_produits'])
            
            if 'entreprises_adaptation_prix' in metrics_data:
                entreprises_adaptation_prix.labels(tick=str(tick_value)).set(metrics_data['entreprises_adaptation_prix'])
            
            if 'entreprises_competitivite' in metrics_data:
                entreprises_competitivite.labels(tick=str(tick_value)).set(metrics_data['entreprises_competitivite'])
            
            if 'entreprises_resilience' in metrics_data:
                entreprises_resilience.labels(tick=str(tick_value)).set(metrics_data['entreprises_resilience'])
            
            if 'entreprises_innovation' in metrics_data:
                entreprises_innovation.labels(tick=str(tick_value)).set(metrics_data['entreprises_innovation'])
            
            # ============================================================================
            # MÉTRIQUES DE PRODUITS (16 métriques)
            # ============================================================================
            
            if 'produits_total' in metrics_data:
                produits_total.set(metrics_data['produits_total'])
            
            if 'produits_par_type' in metrics_data:
                if isinstance(metrics_data['produits_par_type'], dict):
                    produits_par_type.set(sum(metrics_data['produits_par_type'].values()))
                else:
                    produits_par_type.set(metrics_data['produits_par_type'])
            
            if 'produits_par_continent' in metrics_data:
                if isinstance(metrics_data['produits_par_continent'], dict):
                    produits_par_continent.set(sum(metrics_data['produits_par_continent'].values()))
                else:
                    produits_par_continent.set(metrics_data['produits_par_continent'])
            
            if 'produits_prix_moyen' in metrics_data:
                produits_prix_moyen.labels(tick=str(tick_value)).set(metrics_data['produits_prix_moyen'])
            
            if 'produits_prix_median' in metrics_data:
                produits_prix_median.labels(tick=str(tick_value)).set(metrics_data['produits_prix_median'])
            
            if 'produits_demande_moyenne' in metrics_data:
                produits_demande_moyenne.labels(tick=str(tick_value)).set(metrics_data['produits_demande_moyenne'])
            
            if 'produits_offre_moyenne' in metrics_data:
                produits_offre_moyenne.labels(tick=str(tick_value)).set(metrics_data['produits_offre_moyenne'])
            
            if 'produits_rotation_stock' in metrics_data:
                produits_rotation_stock.labels(tick=str(tick_value)).set(metrics_data['produits_rotation_stock'])
            
            if 'produits_rentabilite' in metrics_data:
                produits_rentabilite.labels(tick=str(tick_value)).set(metrics_data['produits_rentabilite'])
            
            if 'produits_popularite' in metrics_data:
                produits_popularite.labels(tick=str(tick_value)).set(metrics_data['produits_popularite'])
            
            if 'produits_disponibilite' in metrics_data:
                produits_disponibilite.labels(tick=str(tick_value)).set(metrics_data['produits_disponibilite'])
            
            if 'produits_volatilite_prix' in metrics_data:
                produits_volatilite_prix.labels(tick=str(tick_value)).set(metrics_data['produits_volatilite_prix'])
            
            if 'produits_tendance_prix' in metrics_data:
                produits_tendance_prix.labels(tick=str(tick_value)).set(metrics_data['produits_tendance_prix'])
            
            if 'produits_elasticite_demande' in metrics_data:
                produits_elasticite_demande.labels(tick=str(tick_value)).set(metrics_data['produits_elasticite_demande'])
            
            if 'produits_competitivite' in metrics_data:
                produits_competitivite.labels(tick=str(tick_value)).set(metrics_data['produits_competitivite'])
            
            # ============================================================================
            # MÉTRIQUES DE FOURNISSEURS (16 métriques)
            # ============================================================================
            
            if 'fournisseurs_total' in metrics_data:
                fournisseurs_total.set(metrics_data['fournisseurs_total'])
            
            if 'fournisseurs_actifs' in metrics_data:
                fournisseurs_actifs.set(metrics_data['fournisseurs_actifs'])
            
            if 'fournisseurs_par_pays' in metrics_data:
                if isinstance(metrics_data['fournisseurs_par_pays'], dict):
                    fournisseurs_par_pays.set(sum(metrics_data['fournisseurs_par_pays'].values()))
                else:
                    fournisseurs_par_pays.set(metrics_data['fournisseurs_par_pays'])
            
            if 'fournisseurs_par_continent' in metrics_data:
                if isinstance(metrics_data['fournisseurs_par_continent'], dict):
                    fournisseurs_par_continent.set(sum(metrics_data['fournisseurs_par_continent'].values()))
                else:
                    fournisseurs_par_continent.set(metrics_data['fournisseurs_par_continent'])
            
            if 'fournisseurs_stock_moyen' in metrics_data:
                fournisseurs_stock_moyen.labels(tick=str(tick_value)).set(metrics_data['fournisseurs_stock_moyen'])
            
            if 'fournisseurs_produits_moyen' in metrics_data:
                fournisseurs_produits_moyen.labels(tick=str(tick_value)).set(metrics_data['fournisseurs_produits_moyen'])
            
            if 'fournisseurs_ventes_moyennes' in metrics_data:
                fournisseurs_ventes_moyennes.labels(tick=str(tick_value)).set(metrics_data['fournisseurs_ventes_moyennes'])
            
            if 'fournisseurs_rotation_stock' in metrics_data:
                fournisseurs_rotation_stock.labels(tick=str(tick_value)).set(metrics_data['fournisseurs_rotation_stock'])
            
            if 'fournisseurs_disponibilite' in metrics_data:
                fournisseurs_disponibilite.labels(tick=str(tick_value)).set(metrics_data['fournisseurs_disponibilite'])
            
            if 'fournisseurs_rentabilite' in metrics_data:
                fournisseurs_rentabilite.labels(tick=str(tick_value)).set(metrics_data['fournisseurs_rentabilite'])
            
            if 'fournisseurs_popularite' in metrics_data:
                fournisseurs_popularite.labels(tick=str(tick_value)).set(metrics_data['fournisseurs_popularite'])
            
            # ============================================================================
            # MÉTRIQUES DE TRANSACTIONS (12 métriques)
            # ============================================================================
            
            if 'transactions_par_seconde' in metrics_data:
                transactions_par_seconde.inc(metrics_data['transactions_par_seconde'])
            
            if 'transactions_moyennes_par_tour' in metrics_data:
                transactions_moyennes_par_tour.set(metrics_data['transactions_moyennes_par_tour'])
            
            if 'transactions_reussies' in metrics_data:
                transactions_reussies.inc(metrics_data['transactions_reussies'])
            
            if 'transactions_echouees' in metrics_data:
                transactions_echouees.inc(metrics_data['transactions_echouees'])
            
            if 'taux_reussite_transactions' in metrics_data:
                taux_reussite_transactions.labels(tick=str(tick_value)).set(metrics_data['taux_reussite_transactions'])
            
            if 'montant_moyen_transaction' in metrics_data:
                montant_moyen_transaction.labels(tick=str(tick_value)).set(metrics_data['montant_moyen_transaction'])
            
            if 'volume_total_transactions' in metrics_data:
                volume_total_transactions.labels(tick=str(tick_value)).inc(metrics_data['volume_total_transactions'])
            
            if 'transactions_par_produit' in metrics_data:
                if isinstance(metrics_data['transactions_par_produit'], dict):
                    transactions_par_produit.set(sum(metrics_data['transactions_par_produit'].values()))
                else:
                    transactions_par_produit.set(metrics_data['transactions_par_produit'])
            
            if 'transactions_par_entreprise' in metrics_data:
                if isinstance(metrics_data['transactions_par_entreprise'], dict):
                    transactions_par_entreprise.set(sum(metrics_data['transactions_par_entreprise'].values()))
                else:
                    transactions_par_entreprise.set(metrics_data['transactions_par_entreprise'])
            
            if 'transactions_par_fournisseur' in metrics_data:
                if isinstance(metrics_data['transactions_par_fournisseur'], dict):
                    transactions_par_fournisseur.set(sum(metrics_data['transactions_par_fournisseur'].values()))
                else:
                    transactions_par_fournisseur.set(metrics_data['transactions_par_fournisseur'])
            
            if 'frequence_transactions' in metrics_data:
                frequence_transactions.set(metrics_data['frequence_transactions'])
            
            if 'efficacite_transactions' in metrics_data:
                efficacite_transactions.set(metrics_data['efficacite_transactions'])
            
            # ============================================================================
            # MÉTRIQUES D'ÉVÉNEMENTS (10 métriques)
            # ============================================================================
            
            if 'evenements_par_seconde' in metrics_data:
                evenements_par_seconde.inc(metrics_data['evenements_par_seconde'])
            
            if 'evenements_inflation' in metrics_data:
                evenements_inflation.inc(metrics_data['evenements_inflation'])
            
            if 'evenements_reassort' in metrics_data:
                evenements_reassort.inc(metrics_data['evenements_reassort'])
            
            if 'evenements_recharge_budget' in metrics_data:
                evenements_recharge_budget.inc(metrics_data['evenements_recharge_budget'])
            
            if 'evenements_variation_disponibilite' in metrics_data:
                evenements_variation_disponibilite.inc(metrics_data['evenements_variation_disponibilite'])
            
            if 'impact_moyen_evenements' in metrics_data:
                impact_moyen_evenements.labels(tick=str(tick_value)).set(metrics_data['impact_moyen_evenements'])
            
            if 'frequence_evenements_inflation' in metrics_data:
                frequence_evenements_inflation.labels(tick=str(tick_value)).set(metrics_data['frequence_evenements_inflation'])
            
            if 'frequence_evenements_reassort' in metrics_data:
                frequence_evenements_reassort.labels(tick=str(tick_value)).set(metrics_data['frequence_evenements_reassort'])
            
            if 'frequence_evenements_recharge' in metrics_data:
                frequence_evenements_recharge.labels(tick=str(tick_value)).set(metrics_data['frequence_evenements_recharge'])
            
            if 'frequence_evenements_disponibilite' in metrics_data:
                frequence_evenements_disponibilite.labels(tick=str(tick_value)).set(metrics_data['frequence_evenements_disponibilite'])
            
            # Mise à jour des métriques de latence
            if 'latency' in metrics_data:
                latency_data = metrics_data['latency']
                for action_name, stats in latency_data.items():
                    if 'mean' in stats and stats['mean'] > 0:
                        # Mappe les noms d'actions aux métriques Prometheus
                        metric_mapping = {
                            'achat_produit': latency_achat_produit_ms,
                            'calcul_statistiques': latency_calcul_statistiques_ms,
                            'application_evenement': latency_application_evenement_ms,
                            'collecte_metriques': latency_collecte_metriques_ms,
                            'validation_donnees': latency_validation_donnees_ms,
                            'generation_id': latency_generation_id_ms
                        }
                        
                        if action_name in metric_mapping:
                            metric_mapping[action_name].observe(stats['mean'])
            
            # Mise à jour des métriques de throughput
            if 'throughput' in metrics_data:
                throughput_data = metrics_data['throughput']
                for operation_type, rate in throughput_data.items():
                    if rate > 0:
                        # Mappe les types d'opérations aux métriques Prometheus
                        metric_mapping = {
                            'transactions': transactions_par_seconde,
                            'evenements': evenements_par_seconde,
                            'metriques': metriques_collectees_par_seconde,
                            'logs': logs_ecrits_par_seconde,
                            'actions_validees': actions_validees_par_seconde,
                            'ids_generes': ids_generes_par_seconde
                        }
                        
                        if operation_type in metric_mapping:
                            metric_mapping[operation_type].inc(int(rate))
            
            # ============================================================================
            # MÉTRIQUES INDIVIDUELLES AVEC LABELS
            # ============================================================================
            
            # Traitement des métriques individuelles par entreprise
            if 'entreprises_individuales' in metrics_data:
                for entreprise_metrics in metrics_data['entreprises_individuales']:
                    try:
                        # Métriques de budget par entreprise
                        entreprise_budget.labels(
                            id=str(entreprise_metrics['id']),
                            nom=entreprise_metrics['nom'],
                            continent=entreprise_metrics['continent'],
                            strategie=entreprise_metrics['strategie'],
                            tick=str(tick_value)
                        ).set(entreprise_metrics['budget'])
                        
                        entreprise_budget_initial.labels(
                            id=str(entreprise_metrics['id']),
                            nom=entreprise_metrics['nom'],
                            tick=str(tick_value)
                        ).set(entreprise_metrics['budget_initial'])
                        
                        entreprise_budget_evolution.labels(
                            id=str(entreprise_metrics['id']),
                            nom=entreprise_metrics['nom'],
                            tick=str(tick_value)
                        ).set(entreprise_metrics['budget_evolution'])
                        
                        entreprise_budget_tendance.labels(
                            id=str(entreprise_metrics['id']),
                            nom=entreprise_metrics['nom'],
                            tick=str(tick_value)
                        ).set(entreprise_metrics['budget_tendance'])
                        
                        entreprise_transactions_total.labels(
                            id=str(entreprise_metrics['id']),
                            nom=entreprise_metrics['nom'],
                            continent=entreprise_metrics['continent'],
                            tick=str(tick_value)
                        ).set(entreprise_metrics['transactions_total'])
                        
                        # Métriques de stock par produit par entreprise
                        if 'stocks_produits' in entreprise_metrics:
                            for stock_info in entreprise_metrics['stocks_produits']:
                                try:
                                    entreprise_stock_produit.labels(
                                        id_entreprise=str(entreprise_metrics['id']),
                                        nom_entreprise=entreprise_metrics['nom'],
                                        id_produit=str(stock_info.get('id_produit', 'unknown')),
                                        nom_produit=stock_info.get('nom_produit', 'unknown'),
                                        type_produit=stock_info.get('type_produit', 'unknown'),
                                        tick=str(tick_value)
                                    ).set(stock_info.get('stock', 0))
                                except Exception as e:
                                    print(f"⚠️ Erreur stock entreprise {entreprise_metrics.get('id', 'unknown')}: {e}")
                                
                    except Exception as e:
                        print(f"⚠️ Erreur lors du traitement des métriques entreprise {entreprise_metrics.get('id', 'unknown')}: {e}")
            
            # Traitement des métriques individuelles par produit
            if 'produits_individuales' in metrics_data:
                for produit_metrics in metrics_data['produits_individuales']:
                    try:
                        produit_prix.labels(
                            id=str(produit_metrics['id']),
                            nom=produit_metrics['nom'],
                            type=produit_metrics['type'],
                            tick=str(tick_value)
                        ).set(produit_metrics['prix'])
                        
                        produit_prix_evolution.labels(
                            id=str(produit_metrics['id']),
                            nom=produit_metrics['nom'],
                            type=produit_metrics['type'],
                            tick=str(tick_value)
                        ).set(produit_metrics['prix_evolution'])
                        
                        produit_prix_tendance.labels(
                            id=str(produit_metrics['id']),
                            nom=produit_metrics['nom'],
                            type=produit_metrics['type'],
                            tick=str(tick_value)
                        ).set(produit_metrics['prix_tendance'])
                        
                    except Exception as e:
                        print(f"⚠️ Erreur lors du traitement des métriques produit {produit_metrics.get('id', 'unknown')}: {e}")
            
            # Traitement des métriques individuelles par fournisseur
            if 'fournisseurs_individuales' in metrics_data:
                for fournisseur_metrics in metrics_data['fournisseurs_individuales']:
                    try:
                        fournisseur_prix_moyen.labels(
                            id=str(fournisseur_metrics['id']),
                            nom=fournisseur_metrics['nom'],
                            continent=fournisseur_metrics['continent'],
                            tick=str(tick_value)
                        ).set(fournisseur_metrics['prix_moyen'])
                        
                        fournisseur_ventes_total.labels(
                            id=str(fournisseur_metrics['id']),
                            nom=fournisseur_metrics['nom'],
                            continent=fournisseur_metrics['continent'],
                            tick=str(tick_value)
                        ).set(fournisseur_metrics['ventes_total'])
                        
                        fournisseur_disponibilite.labels(
                            id=str(fournisseur_metrics['id']),
                            nom=fournisseur_metrics['nom'],
                            continent=fournisseur_metrics['continent'],
                            tick=str(tick_value)
                        ).set(fournisseur_metrics['disponibilite'])
                        
                        fournisseur_rotation_stock.labels(
                            id=str(fournisseur_metrics['id']),
                            nom=fournisseur_metrics['nom'],
                            continent=fournisseur_metrics['continent'],
                            tick=str(tick_value)
                        ).set(fournisseur_metrics['rotation_stock'])
                        
                        fournisseur_rentabilite.labels(
                            id=str(fournisseur_metrics['id']),
                            nom=fournisseur_metrics['nom'],
                            continent=fournisseur_metrics['continent'],
                            tick=str(tick_value)
                        ).set(fournisseur_metrics['rentabilite'])
                        
                        # Métriques de stock par produit par fournisseur
                        if 'stocks_produits' in fournisseur_metrics:
                            for stock_info in fournisseur_metrics['stocks_produits']:
                                try:
                                    fournisseur_stock_produit.labels(
                                        id_fournisseur=str(fournisseur_metrics['id']),
                                        nom_fournisseur=fournisseur_metrics['nom'],
                                        id_produit=str(stock_info.get('id_produit', 'unknown')),
                                        nom_produit=stock_info.get('nom_produit', 'unknown'),
                                        type_produit=stock_info.get('type_produit', 'unknown'),
                                        tick=str(tick_value)
                                    ).set(stock_info.get('stock', 0))
                                except Exception as e:
                                    print(f"⚠️ Erreur stock fournisseur {fournisseur_metrics.get('id', 'unknown')}: {e}")
                                
                    except Exception as e:
                        print(f"⚠️ Erreur lors du traitement des métriques fournisseur {fournisseur_metrics.get('id', 'unknown')}: {e}")
            
            # ============================================================================
            # MÉTRIQUES HISTORIQUES DE STOCK
            # ============================================================================
            
            # Traitement des métriques historiques de stock
            if 'stocks_historiques' in metrics_data:
                stocks_data = metrics_data['stocks_historiques']
                
                # Métriques historiques pour entreprises
                if 'entreprises' in stocks_data:
                    for stock_hist in stocks_data['entreprises']:
                        hist_labels = {
                            'id_entite': str(stock_hist['id_entite']),
                            'nom_entite': stock_hist['nom_entite'],
                            'id_produit': str(stock_hist['id_produit']),
                            'nom_produit': stock_hist['nom_produit'],
                            'tour': str(stock_hist['tour']),
                            'tick': str(tick_value)
                        }
                        entreprise_stock_historique.labels(**hist_labels).set(stock_hist['stock'])
                
                # Métriques historiques pour fournisseurs
                if 'fournisseurs' in stocks_data:
                    for stock_hist in stocks_data['fournisseurs']:
                        hist_labels = {
                            'id_entite': str(stock_hist['id_entite']),
                            'nom_entite': stock_hist['nom_entite'],
                            'id_produit': str(stock_hist['id_produit']),
                            'nom_produit': stock_hist['nom_produit'],
                            'tour': str(stock_hist['tour']),
                            'tick': str(tick_value)
                        }
                        fournisseur_stock_historique.labels(**hist_labels).set(stock_hist['stock'])
                
                # Métriques d'évolution
                if 'evolution' in stocks_data:
                    # Évolution pour entreprises
                    if 'entreprises' in stocks_data['evolution']:
                        for evolution in stocks_data['evolution']['entreprises']:
                            evol_labels = {
                                'id_entite': str(evolution['id_entite']),
                                'nom_entite': evolution['nom_entite'],
                                'id_produit': str(evolution['id_produit']),
                                'nom_produit': evolution['nom_produit'],
                                'periode': evolution['periode'],
                                'tick': str(tick_value)
                            }
                            entreprise_stock_evolution.labels(**evol_labels).set(evolution['evolution'])
                    
                    # Évolution pour fournisseurs
                    if 'fournisseurs' in stocks_data['evolution']:
                        for evolution in stocks_data['evolution']['fournisseurs']:
                            evol_labels = {
                                'id_entite': str(evolution['id_entite']),
                                'nom_entite': evolution['nom_entite'],
                                'id_produit': str(evolution['id_produit']),
                                'nom_produit': evolution['nom_produit'],
                                'periode': evolution['periode'],
                                'tick': str(tick_value)
                            }
                            fournisseur_stock_evolution.labels(**evol_labels).set(evolution['evolution'])
            
            # ============================================================================
            # MÉTRIQUES DE PERFORMANCE
            # ============================================================================
            
            # Métriques de performance des calculs historiques
            if 'stock_history_performance' in metrics_data:
                perf_data = metrics_data['stock_history_performance']
                
                if 'calculation_time' in perf_data:
                    metrics_calculation_duration.observe(perf_data['calculation_time'])
                
                if 'cardinality' in perf_data:
                    metrics_cardinality.labels(metric_type='stock_history', entity_type='all').set(perf_data['cardinality'])
                
                if 'compression_ratio' in perf_data:
                    metrics_compression_ratio.labels(entity_type='all').set(perf_data['compression_ratio'])
            
            # Stockage en JSONL
            self._store_metrics_jsonl(metrics_data)
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la mise à jour des métriques: {e}")
    
    def _store_metrics_jsonl(self, metrics_data: Dict[str, Any]):
        """
        Stocke les métriques en format JSONL
        
        Args:
            metrics_data: Données des métriques à stocker
        """
        try:
            # Ajout du timestamp
            metrics_entry = {
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics_data
            }
            
            # Écriture en JSONL
            with open(self.metrics_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metrics_entry) + '\n')
                
        except Exception as e:
            print(f"⚠️  Erreur lors du stockage JSONL: {e}")

# ============================================================================
# DYNAMIC METRICS MANAGER
# ============================================================================

class DynamicMetricsManager:
    """
    Gestionnaire dynamique des métriques Prometheus
    
    Permet de créer et gérer automatiquement les métriques Prometheus
    sans modification manuelle du code de l'exporter.
    
    FONCTIONNALITÉS :
    - Création automatique des métriques (Gauge, Counter, Histogram)
    - Cache des métriques pour éviter les doublons
    - Préfixe automatique 'tradesim_'
    - Gestion des labels et types de métriques
    - Traitement automatique des données reçues
    
    UTILISATION :
    - Création : manager.get_or_create_metric('nom', 'gauge', 'description')
    - Mise à jour : manager.update_metric('nom', 42.5)
    - Avec labels : manager.update_metric('nom', 100, {'label': 'valeur'})
    """
    
    def __init__(self):
        """Initialise le gestionnaire de métriques dynamiques"""
        self.metrics_registry = {}
        self.prefix = "tradesim_"
    
    def get_or_create_metric(self, name: str, metric_type: str, description: str = "", 
                           labels: List[str] = None, buckets: List[float] = None):
        """
        Crée ou récupère une métrique Prometheus
        
        Args:
            name: Nom de la métrique (sera préfixé automatiquement)
            metric_type: Type de métrique ('gauge', 'counter', 'histogram')
            description: Description de la métrique
            labels: Liste des labels supportés
            buckets: Buckets pour les histogrammes
            
        Returns:
            Objet métrique Prometheus
        """
        # Préfixer le nom si nécessaire
        full_name = name if name.startswith(self.prefix) else f"{self.prefix}{name}"
        
        # Vérifier si la métrique existe déjà
        if full_name in self.metrics_registry:
            return self.metrics_registry[full_name]
        
        # Créer la nouvelle métrique
        try:
            if metric_type.lower() == 'gauge':
                if labels:
                    metric = Gauge(full_name, description, labels)
                else:
                    metric = Gauge(full_name, description)
            
            elif metric_type.lower() == 'counter':
                if labels:
                    metric = Counter(full_name, description, labels)
                else:
                    metric = Counter(full_name, description)
            
            elif metric_type.lower() == 'histogram':
                if buckets:
                    metric = Histogram(full_name, description, buckets=buckets)
                else:
                    metric = Histogram(full_name, description)
            
            else:
                # Type invalide - utiliser Gauge par défaut
                print(f"⚠️ Type de métrique non supporté: {metric_type}, utilisation de Gauge par défaut")
                metric = Gauge(full_name, description)
            
            # Stocker dans le registre
            self.metrics_registry[full_name] = metric
            return metric
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la création de la métrique {full_name}: {e}")
            return None
    
    def update_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """
        Met à jour une métrique
        
        Args:
            name: Nom de la métrique
            value: Valeur à définir
            labels: Labels pour la métrique
        """
        try:
            # Préfixer le nom si nécessaire
            full_name = name if name.startswith(self.prefix) else f"{self.prefix}{name}"
            
            # Créer la métrique si elle n'existe pas
            if full_name not in self.metrics_registry:
                metric_type = 'gauge'  # Par défaut
                if labels:
                    # Extraire les noms des labels
                    label_names = list(labels.keys())
                    self.get_or_create_metric(name, metric_type, f"Métrique automatique: {name}", labels=label_names)
                else:
                    self.get_or_create_metric(name, metric_type, f"Métrique automatique: {name}")
            
            metric = self.metrics_registry[full_name]
            
            # Mettre à jour la métrique
            if labels:
                metric.labels(**labels).set(value)
            else:
                metric.set(value)
                
        except Exception as e:
            print(f"⚠️ Erreur lors de la mise à jour de {name}: {e}")
    
    def process_metrics_data(self, metrics_data: Dict[str, Any]):
        """
        Traite automatiquement les données de métriques
        
        Args:
            metrics_data: Dictionnaire de données de métriques
        """
        for key, value in metrics_data.items():
            try:
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    # Métrique simple (exclure les booléens)
                    self.update_metric(key, value)
                
                elif isinstance(value, dict):
                    if 'value' in value and 'labels' in value:
                        # Métrique avec labels
                        self.update_metric(key, value['value'], value['labels'])
                    else:
                        # Dictionnaire simple - agrégation
                        total = sum(value.values()) if all(isinstance(v, (int, float)) for v in value.values()) else 0
                        self.update_metric(key, total)
                else:
                    # Type non supporté - ignorer
                    print(f"⚠️ Type de valeur non supporté pour {key}: {type(value)}")
                        
            except Exception as e:
                print(f"⚠️ Erreur lors du traitement de {key}: {e}")

# Instance globale du gestionnaire
metrics_manager = DynamicMetricsManager()

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_exporter_status() -> Dict[str, Any]:
    """
    Retourne le statut de l'exporteur
    
    Returns:
        Dictionnaire contenant le statut de l'exporteur
    """
    return {
        'enabled': METRICS_ENABLED,
        'port': METRICS_EXPORTER_PORT,
        'host': METRICS_EXPORTER_HOST,
        'endpoint': f"http://{METRICS_EXPORTER_HOST}:{METRICS_EXPORTER_PORT}/metrics",
        'health': f"http://{METRICS_EXPORTER_HOST}:{METRICS_EXPORTER_PORT}/health"
    }

def format_monitoring_status() -> str:
    """
    Formate le statut du monitoring pour l'affichage CLI
    
    Returns:
        Chaîne formatée du statut monitoring
    """
    if not METRICS_ENABLED:
        return "❌ DÉSACTIVÉ"
    
    return f"✅ ACTIVÉ (port {METRICS_EXPORTER_PORT})"

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    """Point d'entrée pour tester l'exporteur en standalone"""
    print("🚀 Démarrage de l'exporteur Prometheus TradeSim...")
    
    exporter = PrometheusExporter()
    exporter.start() 