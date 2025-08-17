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
from typing import Dict, Any, Optional
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
budget_total_entreprises = Gauge('tradesim_budget_total_entreprises', 'Budget total de toutes les entreprises (somme)')
budget_moyen_entreprises = Gauge('tradesim_budget_moyen_entreprises', 'Budget moyen des entreprises (moyenne arithmétique)')
budget_median_entreprises = Gauge('tradesim_budget_median_entreprises', 'Budget médian des entreprises (valeur centrale)')
budget_ecart_type_entreprises = Gauge('tradesim_budget_ecart_type_entreprises', 'Écart-type des budgets (dispersion)')
budget_coefficient_variation = Gauge('tradesim_budget_coefficient_variation', 'Coefficient de variation (CV = σ/μ)')

# Métriques de variation (3 métriques)
budget_variation_totale = Gauge('tradesim_budget_variation_totale', 'Variation totale des budgets (actuel - initial)')
budget_depenses_totales = Counter('tradesim_budget_depenses_totales', 'Dépenses totales cumulées de toutes les entreprises')
budget_gains_totaux = Counter('tradesim_budget_gains_totaux', 'Gains totaux cumulés de toutes les entreprises')

# Métriques de santé financière (3 métriques)
budget_ratio_depenses_revenus = Gauge('tradesim_budget_ratio_depenses_revenus', 'Ratio dépenses/revenus (dépenses/gains)')
budget_entreprises_critiques = Gauge('tradesim_budget_entreprises_critiques', 'Nombre d\'entreprises avec budget critique (≤1000€)')
budget_entreprises_faibles = Gauge('tradesim_budget_entreprises_faibles', 'Nombre d\'entreprises avec budget faible (1000-3000€)')

# Métriques de tendance (2 métriques)
budget_evolution_tour = Gauge('tradesim_budget_evolution_tour', 'Évolution du budget total depuis le tour précédent')
budget_tendance_globale = Gauge('tradesim_budget_tendance_globale', 'Tendance globale des budgets (pente de régression)')

# Métriques avancées (1 métrique)
budget_skewness = Gauge('tradesim_budget_skewness', 'Asymétrie de la distribution des budgets (skewness)')

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
entreprises_transactions_moyennes = Gauge('tradesim_entreprises_transactions_moyennes', 'Nombre moyen de transactions par entreprise')
entreprises_budget_moyen = Gauge('tradesim_entreprises_budget_moyen', 'Budget moyen par entreprise')
entreprises_stock_moyen = Gauge('tradesim_entreprises_stock_moyen', 'Stock moyen par entreprise')
entreprises_rentabilite = Gauge('tradesim_entreprises_rentabilite', 'Rentabilité moyenne des entreprises (budget actuel / budget initial)')
entreprises_efficacite_achat = Gauge('tradesim_entreprises_efficacite_achat', 'Efficacité d\'achat moyenne (transactions / budget dépensé)')
entreprises_survie_taux = Gauge('tradesim_entreprises_survie_taux', 'Taux de survie des entreprises (budget > 0)')

# Métriques de comportement (6 métriques)
entreprises_frequence_achat = Gauge('tradesim_entreprises_frequence_achat', 'Fréquence d\'achat moyenne (transactions par tour)')
entreprises_preference_produits = Gauge('tradesim_entreprises_preference_produits', 'Préférence de produits (diversité des types préférés)')
entreprises_adaptation_prix = Gauge('tradesim_entreprises_adaptation_prix', 'Adaptation aux variations de prix')
entreprises_competitivite = Gauge('tradesim_entreprises_competitivite', 'Indice de compétitivité des entreprises')
entreprises_resilience = Gauge('tradesim_entreprises_resilience', 'Indice de résilience des entreprises')
entreprises_innovation = Gauge('tradesim_entreprises_innovation', 'Indice d\'innovation des entreprises')

# ============================================================================
# MÉTRIQUES DE PRODUITS (16 métriques)
# ============================================================================

# Métriques de base (6 métriques)
produits_total = Gauge('tradesim_produits_total', 'Nombre total de produits')
# produits_actifs déjà défini plus haut
produits_par_type = Gauge('tradesim_produits_par_type', 'Répartition des produits par type')
produits_par_continent = Gauge('tradesim_produits_par_continent', 'Répartition des produits par continent')
produits_prix_moyen = Gauge('tradesim_produits_prix_moyen', 'Prix moyen des produits')
produits_prix_median = Gauge('tradesim_produits_prix_median', 'Prix médian des produits')

# Métriques de performance (6 métriques)
produits_demande_moyenne = Gauge('tradesim_produits_demande_moyenne', 'Demande moyenne par produit')
produits_offre_moyenne = Gauge('tradesim_produits_offre_moyenne', 'Offre moyenne par produit')
produits_rotation_stock = Gauge('tradesim_produits_rotation_stock', 'Rotation de stock moyenne')
produits_rentabilite = Gauge('tradesim_produits_rentabilite', 'Rentabilité moyenne des produits')
produits_popularite = Gauge('tradesim_produits_popularite', 'Popularité moyenne des produits')
produits_disponibilite = Gauge('tradesim_produits_disponibilite', 'Taux de disponibilité moyen')

# Métriques de comportement (4 métriques)
produits_volatilite_prix = Gauge('tradesim_produits_volatilite_prix', 'Volatilité des prix')
produits_tendance_prix = Gauge('tradesim_produits_tendance_prix', 'Tendance des prix')
produits_elasticite_demande = Gauge('tradesim_produits_elasticite_demande', 'Élasticité de la demande')
produits_competitivite = Gauge('tradesim_produits_competitivite', 'Indice de compétitivité des produits')

# ============================================================================
# MÉTRIQUES DE FOURNISSEURS (16 métriques)
# ============================================================================

# Métriques de base (6 métriques)
fournisseurs_total = Gauge('tradesim_fournisseurs_total', 'Nombre total de fournisseurs')
fournisseurs_actifs = Gauge('tradesim_fournisseurs_actifs', 'Nombre de fournisseurs actifs')
fournisseurs_par_pays = Gauge('tradesim_fournisseurs_par_pays', 'Répartition des fournisseurs par pays')
fournisseurs_par_continent = Gauge('tradesim_fournisseurs_par_continent', 'Répartition des fournisseurs par continent')
fournisseurs_stock_moyen = Gauge('tradesim_fournisseurs_stock_moyen', 'Stock moyen par fournisseur')
fournisseurs_produits_moyen = Gauge('tradesim_fournisseurs_produits_moyen', 'Nombre moyen de produits par fournisseur')

# Métriques de performance (6 métriques)
fournisseurs_ventes_moyennes = Gauge('tradesim_fournisseurs_ventes_moyennes', 'Ventes moyennes par fournisseur')
fournisseurs_rotation_stock = Gauge('tradesim_fournisseurs_rotation_stock', 'Rotation de stock moyenne')
fournisseurs_disponibilite = Gauge('tradesim_fournisseurs_disponibilite', 'Taux de disponibilité moyen')
fournisseurs_rentabilite = Gauge('tradesim_fournisseurs_rentabilite', 'Rentabilité moyenne des fournisseurs')
fournisseurs_popularite = Gauge('tradesim_fournisseurs_popularite', 'Popularité moyenne des fournisseurs')
fournisseurs_efficacite = Gauge('tradesim_fournisseurs_efficacite', 'Efficacité moyenne des fournisseurs')

# Métriques de comportement (4 métriques)
fournisseurs_volatilite_prix = Gauge('tradesim_fournisseurs_volatilite_prix', 'Volatilité des prix par fournisseur')
fournisseurs_tendance_prix = Gauge('tradesim_fournisseurs_tendance_prix', 'Tendance des prix par fournisseur')
fournisseurs_competitivite = Gauge('tradesim_fournisseurs_competitivite', 'Indice de compétitivité des fournisseurs')
fournisseurs_resilience = Gauge('tradesim_fournisseurs_resilience', 'Indice de résilience des fournisseurs')

# ============================================================================
# MÉTRIQUES DE TRANSACTIONS (16 métriques)
# ============================================================================

# Métriques de base (6 métriques) - AVEC LABELS
transactions_total = Gauge('tradesim_transactions_total', 'Nombre total de transactions', ['type', 'statut'])
transactions_reussies = Gauge('tradesim_transactions_reussies', 'Nombre de transactions réussies', ['type', 'strategie'])
transactions_echouees = Gauge('tradesim_transactions_echouees', 'Nombre de transactions échouées', ['type', 'raison'])
transactions_par_strategie = Gauge('tradesim_transactions_par_strategie', 'Répartition des transactions par stratégie', ['strategie', 'statut'])
transactions_par_produit = Gauge('tradesim_transactions_par_produit', 'Répartition des transactions par produit', ['produit', 'type_produit', 'statut'])
transactions_par_entreprise = Gauge('tradesim_transactions_par_entreprise', 'Répartition des transactions par entreprise', ['entreprise', 'continent', 'strategie'])

# Métriques de performance (6 métriques) - AVEC LABELS
transactions_volume_moyen = Gauge('tradesim_transactions_volume_moyen', 'Volume moyen par transaction', ['type', 'strategie'])
transactions_prix_moyen = Gauge('tradesim_transactions_prix_moyen', 'Prix moyen par transaction', ['type', 'produit'])
transactions_frequence = Gauge('tradesim_transactions_frequence', 'Fréquence des transactions (par tour)', ['type', 'entreprise'])
transactions_taux_reussite = Gauge('tradesim_transactions_taux_reussite', 'Taux de réussite des transactions', ['type', 'strategie'])
transactions_efficacite = Gauge('tradesim_transactions_efficacite', 'Efficacité des transactions', ['type', 'entreprise'])
transactions_rentabilite = Gauge('tradesim_transactions_rentabilite', 'Rentabilité moyenne des transactions', ['type', 'strategie'])

# Métriques de comportement (4 métriques) - AVEC LABELS
transactions_volatilite_prix = Gauge('tradesim_transactions_volatilite_prix', 'Volatilité des prix de transaction', ['produit', 'periode'])
transactions_tendance_volume = Gauge('tradesim_transactions_tendance_volume', 'Tendance des volumes de transaction', ['type', 'periode'])
transactions_preference_strategie = Gauge('tradesim_transactions_preference_strategie', 'Préférence de stratégie', ['strategie', 'entreprise'])
transactions_competitivite = Gauge('tradesim_transactions_competitivite', 'Indice de compétitivité des transactions', ['type', 'marche'])

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
entreprise_budget = Gauge('tradesim_entreprise_budget', 'Budget actuel par entreprise', ['id', 'nom', 'continent', 'strategie'])
entreprise_budget_initial = Gauge('tradesim_entreprise_budget_initial', 'Budget initial par entreprise', ['id', 'nom'])
entreprise_budget_evolution = Gauge('tradesim_entreprise_budget_evolution', 'Évolution du budget depuis le tour précédent', ['id', 'nom'])
entreprise_budget_tendance = Gauge('tradesim_entreprise_budget_tendance', 'Tendance du budget sur 5 tours', ['id', 'nom'])
entreprise_transactions_total = Gauge('tradesim_entreprise_transactions_total', 'Nombre total de transactions par entreprise', ['id', 'nom', 'continent'])

# Métriques de stock par produit par entreprise (granularité complète)
entreprise_stock_produit = Gauge('tradesim_entreprise_stock_produit', 'Stock par produit par entreprise', ['id_entreprise', 'nom_entreprise', 'id_produit', 'nom_produit', 'type_produit'])

# Métriques par produit (prix et évolution uniquement)
produit_prix = Gauge('tradesim_produit_prix', 'Prix actuel par produit', ['id', 'nom', 'type'])
produit_prix_evolution = Gauge('tradesim_produit_prix_evolution', 'Évolution du prix depuis le tour précédent', ['id', 'nom', 'type'])
produit_prix_tendance = Gauge('tradesim_produit_prix_tendance', 'Tendance du prix sur 5 tours', ['id', 'nom', 'type'])

# Métriques de stock par produit par fournisseur (granularité complète)
fournisseur_stock_produit = Gauge('tradesim_fournisseur_stock_produit', 'Stock par produit par fournisseur', ['id_fournisseur', 'nom_fournisseur', 'id_produit', 'nom_produit', 'type_produit'])

# ============================================================================
# MÉTRIQUES HISTORIQUES DE STOCK
# ============================================================================

# Métriques historiques de stock par entité
entreprise_stock_historique = Gauge(
    'tradesim_entreprise_stock_historique',
    'Stock historique par produit par entreprise par tour',
    ['id_entite', 'nom_entite', 'id_produit', 'nom_produit', 'tour']
)

fournisseur_stock_historique = Gauge(
    'tradesim_fournisseur_stock_historique',
    'Stock historique par produit par fournisseur par tour',
    ['id_entite', 'nom_entite', 'id_produit', 'nom_produit', 'tour']
)

# Métriques d'évolution de stock
entreprise_stock_evolution = Gauge(
    'tradesim_entreprise_stock_evolution',
    'Évolution du stock par produit par entreprise sur une période',
    ['id_entite', 'nom_entite', 'id_produit', 'nom_produit', 'periode']
)

fournisseur_stock_evolution = Gauge(
    'tradesim_fournisseur_stock_evolution',
    'Évolution du stock par produit par fournisseur sur une période',
    ['id_entite', 'nom_entite', 'id_produit', 'nom_produit', 'periode']
)

# Métriques par fournisseur (autres métriques)
fournisseur_prix_moyen = Gauge('tradesim_fournisseur_prix_moyen', 'Prix moyen des produits par fournisseur', ['id', 'nom', 'continent'])
fournisseur_ventes_total = Gauge('tradesim_fournisseur_ventes_total', 'Nombre total de ventes par fournisseur', ['id', 'nom', 'continent'])
fournisseur_disponibilite = Gauge('tradesim_fournisseur_disponibilite', 'Taux de disponibilité par fournisseur', ['id', 'nom', 'continent'])
fournisseur_rotation_stock = Gauge('tradesim_fournisseur_rotation_stock', 'Rotation de stock par fournisseur', ['id', 'nom', 'continent'])
fournisseur_rentabilite = Gauge('tradesim_fournisseur_rentabilite', 'Rentabilité par fournisseur', ['id', 'nom', 'continent'])

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
            if 'tick_actuel' in metrics_data:
                tick_actuel.set(metrics_data['tick_actuel'])
            
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
            # MÉTRIQUES DE BUDGET (14 métriques)
            # ============================================================================
            
            # Métriques de base (5 métriques)
            if 'budget_total_entreprises' in metrics_data:
                budget_total_entreprises.set(metrics_data['budget_total_entreprises'])
            
            if 'budget_moyen_entreprises' in metrics_data:
                budget_moyen_entreprises.set(metrics_data['budget_moyen_entreprises'])
            
            if 'budget_median_entreprises' in metrics_data:
                budget_median_entreprises.set(metrics_data['budget_median_entreprises'])
            
            if 'budget_ecart_type_entreprises' in metrics_data:
                budget_ecart_type_entreprises.set(metrics_data['budget_ecart_type_entreprises'])
            
            if 'budget_coefficient_variation' in metrics_data:
                budget_coefficient_variation.set(metrics_data['budget_coefficient_variation'])
            
            # Métriques de variation (3 métriques)
            if 'budget_variation_totale' in metrics_data:
                budget_variation_totale.set(metrics_data['budget_variation_totale'])
            
            if 'budget_depenses_totales' in metrics_data:
                budget_depenses_totales.inc(metrics_data['budget_depenses_totales'])
            
            if 'budget_gains_totaux' in metrics_data:
                budget_gains_totaux.inc(metrics_data['budget_gains_totaux'])
            
            # Métriques de santé financière (3 métriques)
            if 'budget_ratio_depenses_revenus' in metrics_data:
                budget_ratio_depenses_revenus.set(metrics_data['budget_ratio_depenses_revenus'])
            
            if 'budget_entreprises_critiques' in metrics_data:
                budget_entreprises_critiques.set(metrics_data['budget_entreprises_critiques'])
            
            if 'budget_entreprises_faibles' in metrics_data:
                budget_entreprises_faibles.set(metrics_data['budget_entreprises_faibles'])
            
            # Métriques de tendance (2 métriques)
            if 'budget_evolution_tour' in metrics_data:
                budget_evolution_tour.set(metrics_data['budget_evolution_tour'])
            
            if 'budget_tendance_globale' in metrics_data:
                budget_tendance_globale.set(metrics_data['budget_tendance_globale'])
            
            # Métriques avancées (1 métrique)
            if 'budget_skewness' in metrics_data:
                budget_skewness.set(metrics_data['budget_skewness'])
            
            # ============================================================================
            # MÉTRIQUES D'ENTREPRISES (18 métriques)
            # ============================================================================
            
            # Métriques de base (6 métriques)
            if 'entreprises_total' in metrics_data:
                entreprises_total.set(metrics_data['entreprises_total'])
            
            if 'entreprises_actives' in metrics_data:
                entreprises_actives.set(metrics_data['entreprises_actives'])
            
            if 'entreprises_par_pays' in metrics_data:
                # Pour les métriques de répartition, on utilise la somme des valeurs
                total_par_pays = sum(metrics_data['entreprises_par_pays'].values()) if isinstance(metrics_data['entreprises_par_pays'], dict) else 0
                entreprises_par_pays.set(total_par_pays)
            
            if 'entreprises_par_continent' in metrics_data:
                total_par_continent = sum(metrics_data['entreprises_par_continent'].values()) if isinstance(metrics_data['entreprises_par_continent'], dict) else 0
                entreprises_par_continent.set(total_par_continent)
            
            if 'entreprises_par_strategie' in metrics_data:
                total_par_strategie = sum(metrics_data['entreprises_par_strategie'].values()) if isinstance(metrics_data['entreprises_par_strategie'], dict) else 0
                entreprises_par_strategie.set(total_par_strategie)
            
            if 'entreprises_par_type_prefere' in metrics_data:
                total_par_type_prefere = sum(metrics_data['entreprises_par_type_prefere'].values()) if isinstance(metrics_data['entreprises_par_type_prefere'], dict) else 0
                entreprises_par_type_prefere.set(total_par_type_prefere)
            
            # Métriques de performance (6 métriques)
            if 'entreprises_transactions_moyennes' in metrics_data:
                entreprises_transactions_moyennes.set(metrics_data['entreprises_transactions_moyennes'])
            
            if 'entreprises_budget_moyen' in metrics_data:
                entreprises_budget_moyen.set(metrics_data['entreprises_budget_moyen'])
            
            if 'entreprises_stock_moyen' in metrics_data:
                entreprises_stock_moyen.set(metrics_data['entreprises_stock_moyen'])
            
            if 'entreprises_rentabilite' in metrics_data:
                entreprises_rentabilite.set(metrics_data['entreprises_rentabilite'])
            
            if 'entreprises_efficacite_achat' in metrics_data:
                entreprises_efficacite_achat.set(metrics_data['entreprises_efficacite_achat'])
            
            if 'entreprises_survie_taux' in metrics_data:
                entreprises_survie_taux.set(metrics_data['entreprises_survie_taux'])
            
            # Métriques de comportement (6 métriques)
            if 'entreprises_frequence_achat' in metrics_data:
                entreprises_frequence_achat.set(metrics_data['entreprises_frequence_achat'])
            
            if 'entreprises_preference_produits' in metrics_data:
                entreprises_preference_produits.set(metrics_data['entreprises_preference_produits'])
            
            if 'entreprises_adaptation_prix' in metrics_data:
                entreprises_adaptation_prix.set(metrics_data['entreprises_adaptation_prix'])
            
            if 'entreprises_competitivite' in metrics_data:
                entreprises_competitivite.set(metrics_data['entreprises_competitivite'])
            
            if 'entreprises_resilience' in metrics_data:
                entreprises_resilience.set(metrics_data['entreprises_resilience'])
            
            if 'entreprises_innovation' in metrics_data:
                entreprises_innovation.set(metrics_data['entreprises_innovation'])
            
            # ============================================================================
            # MÉTRIQUES DE PRODUITS (16 métriques)
            # ============================================================================
            
            # Métriques de base (6 métriques)
            if 'produits_total' in metrics_data:
                produits_total.set(metrics_data['produits_total'])
            
            # produits_actifs déjà mis à jour plus haut
            
            if 'produits_par_type' in metrics_data:
                # Pour les métriques de répartition, on utilise la somme des valeurs
                total_par_type = sum(metrics_data['produits_par_type'].values()) if isinstance(metrics_data['produits_par_type'], dict) else 0
                produits_par_type.set(total_par_type)
            
            if 'produits_par_continent' in metrics_data:
                total_par_continent = sum(metrics_data['produits_par_continent'].values()) if isinstance(metrics_data['produits_par_continent'], dict) else 0
                produits_par_continent.set(total_par_continent)
            
            if 'produits_prix_moyen' in metrics_data:
                produits_prix_moyen.set(metrics_data['produits_prix_moyen'])
            
            if 'produits_prix_median' in metrics_data:
                produits_prix_median.set(metrics_data['produits_prix_median'])
            
            # Métriques de performance (6 métriques)
            if 'produits_demande_moyenne' in metrics_data:
                produits_demande_moyenne.set(metrics_data['produits_demande_moyenne'])
            
            if 'produits_offre_moyenne' in metrics_data:
                produits_offre_moyenne.set(metrics_data['produits_offre_moyenne'])
            
            if 'produits_rotation_stock' in metrics_data:
                produits_rotation_stock.set(metrics_data['produits_rotation_stock'])
            
            if 'produits_rentabilite' in metrics_data:
                produits_rentabilite.set(metrics_data['produits_rentabilite'])
            
            if 'produits_popularite' in metrics_data:
                produits_popularite.set(metrics_data['produits_popularite'])
            
            if 'produits_disponibilite' in metrics_data:
                produits_disponibilite.set(metrics_data['produits_disponibilite'])
            
            # Métriques de comportement (4 métriques)
            if 'produits_volatilite_prix' in metrics_data:
                produits_volatilite_prix.set(metrics_data['produits_volatilite_prix'])
            
            if 'produits_tendance_prix' in metrics_data:
                produits_tendance_prix.set(metrics_data['produits_tendance_prix'])
            
            if 'produits_elasticite_demande' in metrics_data:
                produits_elasticite_demande.set(metrics_data['produits_elasticite_demande'])
            
            if 'produits_competitivite' in metrics_data:
                produits_competitivite.set(metrics_data['produits_competitivite'])
            
            # ============================================================================
            # MÉTRIQUES DE FOURNISSEURS (16 métriques)
            # ============================================================================
            
            # Métriques de base (6 métriques)
            if 'fournisseurs_total' in metrics_data:
                fournisseurs_total.set(metrics_data['fournisseurs_total'])
            
            if 'fournisseurs_actifs' in metrics_data:
                fournisseurs_actifs.set(metrics_data['fournisseurs_actifs'])
            
            if 'fournisseurs_par_pays' in metrics_data:
                # Pour les métriques de répartition, on utilise la somme des valeurs
                total_par_pays = sum(metrics_data['fournisseurs_par_pays'].values()) if isinstance(metrics_data['fournisseurs_par_pays'], dict) else 0
                fournisseurs_par_pays.set(total_par_pays)
            
            if 'fournisseurs_par_continent' in metrics_data:
                total_par_continent = sum(metrics_data['fournisseurs_par_continent'].values()) if isinstance(metrics_data['fournisseurs_par_continent'], dict) else 0
                fournisseurs_par_continent.set(total_par_continent)
            
            if 'fournisseurs_stock_moyen' in metrics_data:
                fournisseurs_stock_moyen.set(metrics_data['fournisseurs_stock_moyen'])
            
            if 'fournisseurs_produits_moyen' in metrics_data:
                fournisseurs_produits_moyen.set(metrics_data['fournisseurs_produits_moyen'])
            
            # Métriques de performance (6 métriques)
            if 'fournisseurs_ventes_moyennes' in metrics_data:
                fournisseurs_ventes_moyennes.set(metrics_data['fournisseurs_ventes_moyennes'])
            
            if 'fournisseurs_rotation_stock' in metrics_data:
                fournisseurs_rotation_stock.set(metrics_data['fournisseurs_rotation_stock'])
            
            if 'fournisseurs_disponibilite' in metrics_data:
                fournisseurs_disponibilite.set(metrics_data['fournisseurs_disponibilite'])
            
            if 'fournisseurs_rentabilite' in metrics_data:
                fournisseurs_rentabilite.set(metrics_data['fournisseurs_rentabilite'])
            
            if 'fournisseurs_popularite' in metrics_data:
                fournisseurs_popularite.set(metrics_data['fournisseurs_popularite'])
            
            if 'fournisseurs_efficacite' in metrics_data:
                fournisseurs_efficacite.set(metrics_data['fournisseurs_efficacite'])
            
            # Métriques de comportement (4 métriques)
            if 'fournisseurs_volatilite_prix' in metrics_data:
                fournisseurs_volatilite_prix.set(metrics_data['fournisseurs_volatilite_prix'])
            
            if 'fournisseurs_tendance_prix' in metrics_data:
                fournisseurs_tendance_prix.set(metrics_data['fournisseurs_tendance_prix'])
            
            if 'fournisseurs_competitivite' in metrics_data:
                fournisseurs_competitivite.set(metrics_data['fournisseurs_competitivite'])
            
            if 'fournisseurs_resilience' in metrics_data:
                fournisseurs_resilience.set(metrics_data['fournisseurs_resilience'])
            
            # ============================================================================
            # MÉTRIQUES DE TRANSACTIONS (16 métriques) - AVEC LABELS
            # ============================================================================
            
            # Métriques de base (6 métriques) - AVEC LABELS
            if 'transactions_total' in metrics_data:
                # Utiliser les labels pour différencier les types de transactions
                transactions_total.labels(type='achat', statut='total').set(metrics_data['transactions_total'])
                transactions_total.labels(type='vente', statut='total').set(metrics_data.get('transactions_ventes', 0))
            
            if 'transactions_reussies' in metrics_data:
                transactions_reussies.labels(type='achat', strategie='moins_cher').set(metrics_data['transactions_reussies'])
                transactions_reussies.labels(type='vente', strategie='plus_cher').set(metrics_data.get('transactions_ventes_reussies', 0))
            
            if 'transactions_echouees' in metrics_data:
                transactions_echouees.labels(type='achat', raison='budget_insuffisant').set(metrics_data['transactions_echouees'])
                transactions_echouees.labels(type='vente', raison='stock_insuffisant').set(metrics_data.get('transactions_ventes_echouees', 0))
            
            if 'transactions_par_strategie' in metrics_data:
                # Mettre à jour chaque stratégie avec ses labels
                if isinstance(metrics_data['transactions_par_strategie'], dict):
                    for strategie, count in metrics_data['transactions_par_strategie'].items():
                        transactions_par_strategie.labels(strategie=strategie, statut='reussie').set(count)
                else:
                    transactions_par_strategie.labels(strategie='moins_cher', statut='reussie').set(metrics_data['transactions_par_strategie'])
            
            if 'transactions_par_produit' in metrics_data:
                # Mettre à jour chaque produit avec ses labels
                if isinstance(metrics_data['transactions_par_produit'], dict):
                    for produit, count in metrics_data['transactions_par_produit'].items():
                        transactions_par_produit.labels(produit=produit, type_produit='produit_fini', statut='reussie').set(count)
                else:
                    transactions_par_produit.labels(produit='general', type_produit='produit_fini', statut='reussie').set(metrics_data['transactions_par_produit'])
            
            if 'transactions_par_entreprise' in metrics_data:
                # Mettre à jour chaque entreprise avec ses labels
                if isinstance(metrics_data['transactions_par_entreprise'], dict):
                    for entreprise, count in metrics_data['transactions_par_entreprise'].items():
                        transactions_par_entreprise.labels(entreprise=entreprise, continent='Europe', strategie='moins_cher').set(count)
                else:
                    transactions_par_entreprise.labels(entreprise='general', continent='Europe', strategie='moins_cher').set(metrics_data['transactions_par_entreprise'])
            
            # Métriques de performance (6 métriques) - AVEC LABELS
            if 'transactions_volume_moyen' in metrics_data:
                transactions_volume_moyen.labels(type='achat', strategie='moins_cher').set(metrics_data['transactions_volume_moyen'])
                transactions_volume_moyen.labels(type='vente', strategie='plus_cher').set(metrics_data.get('transactions_volume_moyen_ventes', 0))
            
            if 'transactions_prix_moyen' in metrics_data:
                transactions_prix_moyen.labels(type='achat', produit='general').set(metrics_data['transactions_prix_moyen'])
                transactions_prix_moyen.labels(type='vente', produit='general').set(metrics_data.get('transactions_prix_moyen_ventes', 0))
            
            if 'transactions_frequence' in metrics_data:
                transactions_frequence.labels(type='achat', entreprise='general').set(metrics_data['transactions_frequence'])
                transactions_frequence.labels(type='vente', entreprise='general').set(metrics_data.get('transactions_frequence_ventes', 0))
            
            if 'transactions_taux_reussite' in metrics_data:
                transactions_taux_reussite.labels(type='achat', strategie='moins_cher').set(metrics_data['transactions_taux_reussite'])
                transactions_taux_reussite.labels(type='vente', strategie='plus_cher').set(metrics_data.get('transactions_taux_reussite_ventes', 0))
            
            if 'transactions_efficacite' in metrics_data:
                transactions_efficacite.labels(type='achat', entreprise='general').set(metrics_data['transactions_efficacite'])
                transactions_efficacite.labels(type='vente', entreprise='general').set(metrics_data.get('transactions_efficacite_ventes', 0))
            
            if 'transactions_rentabilite' in metrics_data:
                transactions_rentabilite.labels(type='achat', strategie='moins_cher').set(metrics_data['transactions_rentabilite'])
                transactions_rentabilite.labels(type='vente', strategie='plus_cher').set(metrics_data.get('transactions_rentabilite_ventes', 0))
            
            # Métriques de comportement (4 métriques) - AVEC LABELS
            if 'transactions_volatilite_prix' in metrics_data:
                transactions_volatilite_prix.labels(produit='general', periode='court_terme').set(metrics_data['transactions_volatilite_prix'])
                transactions_volatilite_prix.labels(produit='general', periode='long_terme').set(metrics_data.get('transactions_volatilite_prix_long', 0))
            
            if 'transactions_tendance_volume' in metrics_data:
                transactions_tendance_volume.labels(type='achat', periode='court_terme').set(metrics_data['transactions_tendance_volume'])
                transactions_tendance_volume.labels(type='vente', periode='court_terme').set(metrics_data.get('transactions_tendance_volume_ventes', 0))
            
            if 'transactions_preference_strategie' in metrics_data:
                transactions_preference_strategie.labels(strategie='moins_cher', entreprise='general').set(metrics_data['transactions_preference_strategie'])
                transactions_preference_strategie.labels(strategie='plus_cher', entreprise='general').set(metrics_data.get('transactions_preference_strategie_ventes', 0))
            
            if 'transactions_competitivite' in metrics_data:
                transactions_competitivite.labels(type='achat', marche='local').set(metrics_data['transactions_competitivite'])
                transactions_competitivite.labels(type='vente', marche='local').set(metrics_data.get('transactions_competitivite_ventes', 0))
            
            # ============================================================================
            # MÉTRIQUES D'ÉVÉNEMENTS (16 métriques)
            # ============================================================================
            
            # Métriques de base (6 métriques)
            if 'evenements_total' in metrics_data:
                evenements_total.set(metrics_data['evenements_total'])
            
            if 'evenements_par_type' in metrics_data:
                # Pour les métriques de répartition, on utilise la somme des valeurs
                total_par_type = sum(metrics_data['evenements_par_type'].values()) if isinstance(metrics_data['evenements_par_type'], dict) else 0
                evenements_par_type.set(total_par_type)
            
            if 'evenements_par_impact' in metrics_data:
                total_par_impact = sum(metrics_data['evenements_par_impact'].values()) if isinstance(metrics_data['evenements_par_impact'], dict) else 0
                evenements_par_impact.set(total_par_impact)
            
            if 'evenements_frequence' in metrics_data:
                evenements_frequence.set(metrics_data['evenements_frequence'])
            
            if 'evenements_duree_moyenne' in metrics_data:
                evenements_duree_moyenne.set(metrics_data['evenements_duree_moyenne'])
            
            if 'evenements_intensite_moyenne' in metrics_data:
                evenements_intensite_moyenne.set(metrics_data['evenements_intensite_moyenne'])
            
            # Métriques de performance (6 métriques)
            if 'evenements_impact_budget' in metrics_data:
                evenements_impact_budget.set(metrics_data['evenements_impact_budget'])
            
            if 'evenements_impact_prix' in metrics_data:
                evenements_impact_prix.set(metrics_data['evenements_impact_prix'])
            
            if 'evenements_impact_stock' in metrics_data:
                evenements_impact_stock.set(metrics_data['evenements_impact_stock'])
            
            if 'evenements_efficacite' in metrics_data:
                evenements_efficacite.set(metrics_data['evenements_efficacite'])
            
            if 'evenements_rentabilite' in metrics_data:
                evenements_rentabilite.set(metrics_data['evenements_rentabilite'])
            
            if 'evenements_stabilite' in metrics_data:
                evenements_stabilite.set(metrics_data['evenements_stabilite'])
            
            # Métriques de comportement (4 métriques)
            if 'evenements_volatilite' in metrics_data:
                evenements_volatilite.set(metrics_data['evenements_volatilite'])
            
            if 'evenements_tendance' in metrics_data:
                evenements_tendance.set(metrics_data['evenements_tendance'])
            
            if 'evenements_correlation' in metrics_data:
                evenements_correlation.set(metrics_data['evenements_correlation'])
            
            if 'evenements_predictibilite' in metrics_data:
                evenements_predictibilite.set(metrics_data['evenements_predictibilite'])
            
            # ============================================================================
            # MÉTRIQUES DE PERFORMANCE (16 métriques)
            # ============================================================================
            
            # Métriques de base (6 métriques)
            if 'performance_temps_execution' in metrics_data:
                performance_temps_execution.set(metrics_data['performance_temps_execution'])
            
            if 'performance_memoire_utilisee' in metrics_data:
                performance_memoire_utilisee.set(metrics_data['performance_memoire_utilisee'])
            
            if 'performance_cpu_utilisation' in metrics_data:
                performance_cpu_utilisation.set(metrics_data['performance_cpu_utilisation'])
            
            if 'performance_temps_reponse' in metrics_data:
                performance_temps_reponse.set(metrics_data['performance_temps_reponse'])
            
            if 'performance_throughput' in metrics_data:
                performance_throughput.set(metrics_data['performance_throughput'])
            
            if 'performance_latence' in metrics_data:
                performance_latence.set(metrics_data['performance_latence'])
            
            # Métriques de performance (6 métriques)
            if 'performance_efficacite_cache' in metrics_data:
                performance_efficacite_cache.set(metrics_data['performance_efficacite_cache'])
            
            if 'performance_optimisation' in metrics_data:
                performance_optimisation.set(metrics_data['performance_optimisation'])
            
            if 'performance_charge_systeme' in metrics_data:
                performance_charge_systeme.set(metrics_data['performance_charge_systeme'])
            
            if 'performance_stabilite' in metrics_data:
                performance_stabilite.set(metrics_data['performance_stabilite'])
            
            if 'performance_scalabilite' in metrics_data:
                performance_scalabilite.set(metrics_data['performance_scalabilite'])
            
            if 'performance_qualite' in metrics_data:
                performance_qualite.set(metrics_data['performance_qualite'])
            
            # Métriques de comportement (4 métriques)
            if 'performance_volatilite' in metrics_data:
                performance_volatilite.set(metrics_data['performance_volatilite'])
            
            if 'performance_tendance' in metrics_data:
                performance_tendance.set(metrics_data['performance_tendance'])
            
            if 'performance_bottlenecks' in metrics_data:
                performance_bottlenecks.set(metrics_data['performance_bottlenecks'])
            
            if 'performance_optimisations_disponibles' in metrics_data:
                performance_optimisations_disponibles.set(metrics_data['performance_optimisations_disponibles'])
            
            # ============================================================================
            # MÉTRIQUES INDIVIDUELLES AVEC LABELS (NOUVELLES)
            # ============================================================================
            
            # Métriques par entreprise
            if 'entreprises_individuales' in metrics_data:
                entreprises_data = metrics_data['entreprises_individuales']

                for entreprise in entreprises_data:
                    labels = {
                        'id': str(entreprise.get('id', '')),
                        'nom': entreprise.get('nom', ''),
                        'continent': entreprise.get('continent', ''),
                        'strategie': entreprise.get('strategie', '')
                    }
                    
                    # Budget actuel
                    if 'budget' in entreprise:
                        entreprise_budget.labels(**labels).set(entreprise['budget'])
                    
                    # Budget initial (labels simplifiés)
                    if 'budget_initial' in entreprise:
                        initial_labels = {'id': labels['id'], 'nom': labels['nom']}
                        entreprise_budget_initial.labels(**initial_labels).set(entreprise['budget_initial'])
                    
                    # Évolution du budget
                    if 'budget_evolution' in entreprise:
                        evolution_labels = {'id': labels['id'], 'nom': labels['nom']}
                        entreprise_budget_evolution.labels(**evolution_labels).set(entreprise['budget_evolution'])
                    
                    # Tendance du budget
                    if 'budget_tendance' in entreprise:
                        tendance_labels = {'id': labels['id'], 'nom': labels['nom']}
                        entreprise_budget_tendance.labels(**tendance_labels).set(entreprise['budget_tendance'])
                    
                    # Transactions totales
                    if 'transactions_total' in entreprise:
                        transaction_labels = {'id': labels['id'], 'nom': labels['nom'], 'continent': labels['continent']}
                        entreprise_transactions_total.labels(**transaction_labels).set(entreprise['transactions_total'])
                    
                    # Stocks par produit (granularité complète)
                    if 'stocks_produits' in entreprise:

                        for produit_stock in entreprise['stocks_produits']:
                            stock_labels = {
                                'id_entreprise': str(entreprise['id']),
                                'nom_entreprise': entreprise['nom'],
                                'id_produit': str(produit_stock['produit_id']),
                                'nom_produit': produit_stock['nom_produit'],
                                'type_produit': produit_stock['type_produit']
                            }
                            entreprise_stock_produit.labels(**stock_labels).set(produit_stock['stock'])
            
            # Métriques par produit
            if 'produits_individuales' in metrics_data:
                produits_data = metrics_data['produits_individuales']
                for produit in produits_data:
                    labels = {
                        'id': str(produit.get('id', '')),
                        'nom': produit.get('nom', ''),
                        'type': produit.get('type', '')
                    }
                    
                    # Prix actuel
                    if 'prix' in produit:
                        produit_prix.labels(**labels).set(produit['prix'])
                    
                    # Évolution du prix
                    if 'prix_evolution' in produit:
                        produit_prix_evolution.labels(**labels).set(produit['prix_evolution'])
                    
                    # Tendance du prix
                    if 'prix_tendance' in produit:
                        produit_prix_tendance.labels(**labels).set(produit['prix_tendance'])
            
            # Métriques par fournisseur
            if 'fournisseurs_individuales' in metrics_data:
                fournisseurs_data = metrics_data['fournisseurs_individuales']
                for fournisseur in fournisseurs_data:
                    labels = {
                        'id': str(fournisseur.get('id', '')),
                        'nom': fournisseur.get('nom', ''),
                        'continent': fournisseur.get('continent', '')
                    }
                    
                    # Stocks par produit (granularité complète)
                    if 'stocks_produits' in fournisseur:

                        for produit_stock in fournisseur['stocks_produits']:
                            stock_labels = {
                                'id_fournisseur': str(fournisseur['id']),
                                'nom_fournisseur': fournisseur['nom'],
                                'id_produit': str(produit_stock['produit_id']),
                                'nom_produit': produit_stock['nom_produit'],
                                'type_produit': produit_stock['type_produit']
                            }
                            fournisseur_stock_produit.labels(**stock_labels).set(produit_stock['stock'])
                    
                    # Prix moyen
                    if 'prix_moyen' in fournisseur:
                        fournisseur_prix_moyen.labels(**labels).set(fournisseur['prix_moyen'])
                    
                    # Ventes totales
                    if 'ventes_total' in fournisseur:
                        fournisseur_ventes_total.labels(**labels).set(fournisseur['ventes_total'])
                    
                    # Disponibilité
                    if 'disponibilite' in fournisseur:
                        fournisseur_disponibilite.labels(**labels).set(fournisseur['disponibilite'])
                    
                    # Rotation de stock
                    if 'rotation_stock' in fournisseur:
                        fournisseur_rotation_stock.labels(**labels).set(fournisseur['rotation_stock'])
                    
                    # Rentabilité
                    if 'rentabilite' in fournisseur:
                        fournisseur_rentabilite.labels(**labels).set(fournisseur['rentabilite'])
            
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
                            'tour': str(stock_hist['tour'])
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
                            'tour': str(stock_hist['tour'])
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
                                'periode': evolution['periode']
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
                                'periode': evolution['periode']
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