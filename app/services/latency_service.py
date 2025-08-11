#!/usr/bin/env python3
"""
Service de métriques de latence et throughput pour TradeSim
==========================================================

Ce service gère la collecte et le calcul des métriques de performance temporelle :
- Latence des actions (temps de réponse pour achats, calculs, etc.)
- Throughput (débit) des opérations par seconde

ARCHITECTURE :
- Cache LRU pour optimiser les calculs répétitifs
- Collecte automatique des timestamps pour chaque action
- Calcul des moyennes, médianes et percentiles
- Intégration avec Prometheus pour l'export des métriques
- Historique des latences par action (1000 mesures max)
- Fenêtres glissantes pour le throughput

MÉTRIQUES CALCULÉES (12 métriques) :
- LATENCE (6) : achat, statistiques, événements, collecte, validation, génération
- THROUGHPUT (6) : transactions, événements, métriques, logs, validations, IDs

FONCTIONNALITÉS :
- Mesure précise des temps d'exécution
- Calcul de statistiques avancées (moyenne, médiane, percentiles)
- Suivi du débit des opérations par seconde
- Export automatique vers Prometheus
- Cache LRU pour optimiser les performances
- Gestion des erreurs et timeouts

Utilisation :
    from services.latency_service import LatencyService
    latency_service = LatencyService()
    latency_service.start_timer("achat_produit")
    # ... action ...
    latency_service.end_timer("achat_produit")

Auteur: Assistant IA
Date: 2025-08-10
"""

import time
import statistics
from typing import Dict, List, Optional, Tuple
from functools import lru_cache
from collections import defaultdict, deque
from datetime import datetime

try:
    from prometheus_client import Histogram, Counter, Gauge, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from config import (
    CACHE_MAX_SIZE, 
    LATENCY_COLLECTION_INTERVAL,
    LATENCY_HISTOGRAM_BUCKETS,
    THROUGHPUT_WINDOW_SIZE
)


class LatencyService:
    """
    Service spécialisé dans la collecte et l'analyse des métriques de latence et throughput.
    
    ARCHITECTURE :
    - Timers actifs pour mesurer les latences en temps réel
    - Historique des latences par action (deque avec maxlen=1000)
    - Compteurs pour le throughput avec fenêtres glissantes
    - Cache LRU pour optimiser les calculs statistiques
    - Intégration Prometheus pour l'export des métriques
    - Gestion des erreurs et timeouts
    
    RESPONSABILITÉS :
    - Mesurer le temps d'exécution des actions critiques
    - Calculer les statistiques de performance (moyenne, médiane, percentiles)
    - Suivre le débit des opérations par seconde
    - Exporter les métriques vers Prometheus
    - Optimiser les calculs avec cache LRU
    - Gérer les timers actifs et l'historique
    
    MÉTRIQUES GÉRÉES (12) :
    - latence_achat_produit_ms
    - latence_calcul_statistiques_ms
    - latence_application_evenement_ms
    - latence_collecte_metriques_ms
    - latence_validation_donnees_ms
    - latence_generation_id_ms
    - transactions_par_seconde
    - evenements_par_seconde
    - metriques_collectees_par_seconde
    - logs_ecrits_par_seconde
    - actions_validees_par_seconde
    - ids_generes_par_seconde
    """
    
    def __init__(self, registry: CollectorRegistry = None):
        """
        Initialise le service de latence avec les structures de données nécessaires.
        
        Args:
            registry: Registre Prometheus personnalisé (pour les tests)
        """
        # Timers actifs pour mesurer les latences
        self._active_timers: Dict[str, float] = {}
        
        # Historique des latences par action (pour calculs statistiques)
        self._latency_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)  # Garde les 1000 dernières mesures
        )
        
        # Compteurs pour le throughput (opérations par seconde)
        self._throughput_counters: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=THROUGHPUT_WINDOW_SIZE)
        )
        
        # Métriques Prometheus (si disponible)
        self._registry = registry
        self._prometheus_metrics = self._initialize_prometheus_metrics()
        
        # Cache pour les calculs répétitifs
        self._stats_cache = {}
    
    def _initialize_prometheus_metrics(self) -> Dict[str, object]:
        """
        Initialise les métriques Prometheus pour la latence et le throughput.
        
        Returns:
            Dict contenant les métriques Prometheus initialisées
        """
        if not PROMETHEUS_AVAILABLE:
            return {}
        
        # Histogrammes pour les latences (avec buckets configurables)
        latency_histograms = {
            "achat_produit": Histogram(
                "latence_achat_produit_ms",
                "Temps de réponse pour un achat (millisecondes)",
                buckets=LATENCY_HISTOGRAM_BUCKETS,
                registry=self._registry
            ),
            "calcul_statistiques": Histogram(
                "latence_calcul_statistiques_ms",
                "Temps de calcul des statistiques (millisecondes)",
                buckets=LATENCY_HISTOGRAM_BUCKETS,
                registry=self._registry
            ),
            "application_evenement": Histogram(
                "latence_application_evenement_ms",
                "Temps d'application d'un événement (millisecondes)",
                buckets=LATENCY_HISTOGRAM_BUCKETS,
                registry=self._registry
            ),
            "collecte_metriques": Histogram(
                "latence_collecte_metriques_ms",
                "Temps de collecte des métriques (millisecondes)",
                buckets=LATENCY_HISTOGRAM_BUCKETS,
                registry=self._registry
            ),
            "validation_donnees": Histogram(
                "latence_validation_donnees_ms",
                "Temps de validation des données (millisecondes)",
                buckets=LATENCY_HISTOGRAM_BUCKETS,
                registry=self._registry
            ),
            "generation_id": Histogram(
                "latence_generation_id_ms",
                "Temps de génération d'un ID unique (millisecondes)",
                buckets=LATENCY_HISTOGRAM_BUCKETS,
                registry=self._registry
            )
        }
        
        # Compteurs pour le throughput
        throughput_counters = {
            "transactions": Counter(
                "transactions_par_seconde",
                "Nombre de transactions par seconde",
                registry=self._registry
            ),
            "evenements": Counter(
                "evenements_par_seconde",
                "Nombre d'événements appliqués par seconde",
                registry=self._registry
            ),
            "metriques": Counter(
                "metriques_collectees_par_seconde",
                "Nombre de métriques collectées par seconde",
                registry=self._registry
            ),
            "logs": Counter(
                "logs_ecrits_par_seconde",
                "Nombre de logs écrits par seconde",
                registry=self._registry
            ),
            "actions_validees": Counter(
                "actions_validees_par_seconde",
                "Nombre d'actions validées par seconde",
                registry=self._registry
            ),
            "ids_generes": Counter(
                "ids_generes_par_seconde",
                "Nombre d'IDs générés par seconde",
                registry=self._registry
            )
        }
        
        return {**latency_histograms, **throughput_counters}
    
    def start_timer(self, action_name: str) -> None:
        """
        Démarre un timer pour mesurer la latence d'une action.
        
        Args:
            action_name: Nom de l'action à mesurer (ex: "achat_produit")
        """
        self._active_timers[action_name] = time.time()
    
    def end_timer(self, action_name: str) -> Optional[float]:
        """
        Arrête un timer et enregistre la latence mesurée.
        
        Args:
            action_name: Nom de l'action mesurée
            
        Returns:
            Latence en millisecondes, ou None si le timer n'était pas actif
            
        Raises:
            KeyError: Si le timer n'était pas démarré
        """
        if action_name not in self._active_timers:
            return None
        
        start_time = self._active_timers.pop(action_name)
        latency_ms = (time.time() - start_time) * 1000
        
        # Enregistre la latence dans l'historique
        self._latency_history[action_name].append(latency_ms)
        
        # Met à jour Prometheus si disponible
        if PROMETHEUS_AVAILABLE and action_name in self._prometheus_metrics:
            self._prometheus_metrics[action_name].observe(latency_ms)
        
        return latency_ms
    
    def record_throughput(self, operation_type: str, count: int = 1) -> None:
        """
        Enregistre une opération pour le calcul du throughput.
        
        Args:
            operation_type: Type d'opération (ex: "transactions", "evenements")
            count: Nombre d'opérations (défaut: 1)
        """
        current_time = time.time()
        
        # Ajoute l'opération avec son timestamp
        for _ in range(count):
            self._throughput_counters[operation_type].append(current_time)
        
        # Met à jour Prometheus si disponible
        if PROMETHEUS_AVAILABLE and operation_type in self._prometheus_metrics:
            self._prometheus_metrics[operation_type].inc(count)
    
    @lru_cache(maxsize=CACHE_MAX_SIZE)
    def get_latency_stats(self, action_name: str) -> Dict[str, float]:
        """
        Calcule les statistiques de latence pour une action donnée.
        
        Utilise un cache LRU pour optimiser les calculs répétitifs.
        
        Args:
            action_name: Nom de l'action
            
        Returns:
            Dictionnaire avec les statistiques (moyenne, médiane, min, max, etc.)
        """
        if action_name not in self._latency_history or not self._latency_history[action_name]:
            return {
                "count": 0,
                "mean": 0.0,
                "median": 0.0,
                "min": 0.0,
                "max": 0.0,
                "p95": 0.0,
                "p99": 0.0
            }
        
        latencies = list(self._latency_history[action_name])
        latencies.sort()
        
        return {
            "count": len(latencies),
            "mean": statistics.mean(latencies),
            "median": statistics.median(latencies),
            "min": latencies[0],
            "max": latencies[-1],
            "p95": latencies[int(len(latencies) * 0.95)],
            "p99": latencies[int(len(latencies) * 0.99)]
        }
    
    def get_throughput_rate(self, operation_type: str) -> float:
        """
        Calcule le taux de throughput (opérations par seconde) pour un type d'opération.
        
        Args:
            operation_type: Type d'opération
            
        Returns:
            Nombre d'opérations par seconde sur la fenêtre de temps
        """
        if operation_type not in self._throughput_counters:
            return 0.0
        
        operations = self._throughput_counters[operation_type]
        if not operations:
            return 0.0
        
        current_time = time.time()
        window_start = current_time - THROUGHPUT_WINDOW_SIZE
        
        # Compte les opérations dans la fenêtre de temps
        recent_operations = [op for op in operations if op >= window_start]
        
        if not recent_operations:
            return 0.0
        
        # Calcule le taux par seconde
        time_span = current_time - window_start
        return len(recent_operations) / time_span if time_span > 0 else 0.0
    
    def get_all_latency_metrics(self) -> Dict[str, Dict[str, float]]:
        """
        Récupère toutes les métriques de latence calculées.
        
        Returns:
            Dictionnaire avec toutes les statistiques de latence par action
        """
        metrics = {}
        for action_name in self._latency_history.keys():
            metrics[action_name] = self.get_latency_stats(action_name)
        return metrics
    
    def get_all_throughput_metrics(self) -> Dict[str, float]:
        """
        Récupère toutes les métriques de throughput calculées.
        
        Returns:
            Dictionnaire avec les taux de throughput par type d'opération
        """
        metrics = {}
        for operation_type in self._throughput_counters.keys():
            metrics[operation_type] = self.get_throughput_rate(operation_type)
        return metrics
    
    def reset_metrics(self) -> None:
        """Réinitialise toutes les métriques (utile pour les tests)."""
        self._active_timers.clear()
        self._latency_history.clear()
        self._throughput_counters.clear()
        self._stats_cache.clear()
        self.get_latency_stats.cache_clear()
    
    def get_metrics_summary(self) -> Dict[str, object]:
        """
        Génère un résumé complet de toutes les métriques de latence et throughput.
        
        Returns:
            Dictionnaire avec toutes les métriques organisées par catégorie
        """
        return {
            "latency": self.get_all_latency_metrics(),
            "throughput": self.get_all_throughput_metrics(),
            "active_timers": list(self._active_timers.keys()),
            "prometheus_available": PROMETHEUS_AVAILABLE
        }
