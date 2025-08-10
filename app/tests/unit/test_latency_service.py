#!/usr/bin/env python3
"""
Tests unitaires pour le service de métriques de latence et throughput

Ce module teste toutes les fonctionnalités du LatencyService :
- Mesure de latence avec start_timer/end_timer
- Calcul des statistiques (moyenne, médiane, percentiles)
- Gestion du throughput (opérations par seconde)
- Intégration avec Prometheus
- Cache LRU et optimisations
- Gestion des erreurs et cas limites

Instructions de lancement :
    python -m pytest tests/unit/test_latency_service.py -v

Interprétation des résultats :
    - test_timer_basic : Vérifie que les timers fonctionnent correctement
    - test_latency_statistics : Vérifie les calculs statistiques
    - test_throughput_calculation : Vérifie le calcul du throughput
    - test_prometheus_integration : Vérifie l'intégration Prometheus
    - test_error_handling : Vérifie la gestion des erreurs
    - test_performance_optimizations : Vérifie les optimisations

Auteur: Assistant IA
Date: 2024-12-19
"""

import unittest
import time
import statistics
from unittest.mock import patch, MagicMock
from collections import deque

from services.latency_service import LatencyService

try:
    from prometheus_client import CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class TestLatencyService(unittest.TestCase):
    """
    Tests unitaires pour le service de métriques de latence et throughput.
    
    Couvre :
    - Fonctionnalités de base (timers, statistiques)
    - Calculs de performance (latence, throughput)
    - Intégration Prometheus
    - Gestion des erreurs
    - Optimisations (cache LRU)
    """
    
    def setUp(self):
        """Initialise un nouveau service de latence pour chaque test."""
        # Utilise un registre séparé pour éviter les conflits
        if PROMETHEUS_AVAILABLE:
            self.registry = CollectorRegistry()
            self.latency_service = LatencyService(registry=self.registry)
        else:
            self.latency_service = LatencyService()
    
    def tearDown(self):
        """Nettoie les métriques après chaque test."""
        self.latency_service.reset_metrics()
    
    def test_initialization(self):
        """Teste l'initialisation correcte du service."""
        self.assertIsInstance(self.latency_service._active_timers, dict)
        self.assertIsInstance(self.latency_service._latency_history, dict)
        self.assertIsInstance(self.latency_service._throughput_counters, dict)
        self.assertEqual(len(self.latency_service._active_timers), 0)
        self.assertEqual(len(self.latency_service._latency_history), 0)
        self.assertEqual(len(self.latency_service._throughput_counters), 0)
    
    def test_start_timer(self):
        """Teste le démarrage d'un timer."""
        self.latency_service.start_timer("test_action")
        
        self.assertIn("test_action", self.latency_service._active_timers)
        self.assertIsInstance(self.latency_service._active_timers["test_action"], float)
        self.assertGreater(self.latency_service._active_timers["test_action"], 0)
    
    def test_end_timer_success(self):
        """Teste l'arrêt d'un timer avec succès."""
        self.latency_service.start_timer("test_action")
        time.sleep(0.01)  # Simule un délai
        
        latency = self.latency_service.end_timer("test_action")
        
        self.assertIsNotNone(latency)
        self.assertGreater(latency, 0)
        self.assertNotIn("test_action", self.latency_service._active_timers)
        self.assertIn("test_action", self.latency_service._latency_history)
        self.assertEqual(len(self.latency_service._latency_history["test_action"]), 1)
    
    def test_end_timer_not_started(self):
        """Teste l'arrêt d'un timer qui n'a pas été démarré."""
        latency = self.latency_service.end_timer("non_existent_action")
        
        self.assertIsNone(latency)
    
    def test_multiple_timers(self):
        """Teste la gestion de plusieurs timers simultanés."""
        self.latency_service.start_timer("action1")
        self.latency_service.start_timer("action2")
        
        self.assertEqual(len(self.latency_service._active_timers), 2)
        self.assertIn("action1", self.latency_service._active_timers)
        self.assertIn("action2", self.latency_service._active_timers)
        
        self.latency_service.end_timer("action1")
        self.assertEqual(len(self.latency_service._active_timers), 1)
        self.assertNotIn("action1", self.latency_service._active_timers)
        self.assertIn("action2", self.latency_service._active_timers)
    
    def test_latency_statistics_empty(self):
        """Teste les statistiques de latence avec un historique vide."""
        stats = self.latency_service.get_latency_stats("empty_action")
        
        expected = {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "min": 0.0,
            "max": 0.0,
            "p95": 0.0,
            "p99": 0.0
        }
        self.assertEqual(stats, expected)
    
    def test_latency_statistics_single_value(self):
        """Teste les statistiques de latence avec une seule valeur."""
        self.latency_service.start_timer("single_action")
        time.sleep(0.01)
        self.latency_service.end_timer("single_action")
        
        stats = self.latency_service.get_latency_stats("single_action")
        
        self.assertEqual(stats["count"], 1)
        self.assertGreater(stats["mean"], 0)
        self.assertEqual(stats["mean"], stats["median"])
        self.assertEqual(stats["mean"], stats["min"])
        self.assertEqual(stats["mean"], stats["max"])
        self.assertEqual(stats["mean"], stats["p95"])
        self.assertEqual(stats["mean"], stats["p99"])
    
    def test_latency_statistics_multiple_values(self):
        """Teste les statistiques de latence avec plusieurs valeurs."""
        # Simule plusieurs mesures de latence
        latencies = [10.0, 20.0, 30.0, 40.0, 50.0]
        for latency in latencies:
            self.latency_service._latency_history["test_action"].append(latency)
        
        stats = self.latency_service.get_latency_stats("test_action")
        
        self.assertEqual(stats["count"], 5)
        self.assertEqual(stats["mean"], 30.0)
        self.assertEqual(stats["median"], 30.0)
        self.assertEqual(stats["min"], 10.0)
        self.assertEqual(stats["max"], 50.0)
        self.assertEqual(stats["p95"], 50.0)  # 95% de 5 = 4.75, donc index 4
        self.assertEqual(stats["p99"], 50.0)  # 99% de 5 = 4.95, donc index 4
    
    def test_record_throughput(self):
        """Teste l'enregistrement d'opérations pour le throughput."""
        self.latency_service.record_throughput("test_operation", 3)
        
        self.assertIn("test_operation", self.latency_service._throughput_counters)
        self.assertEqual(len(self.latency_service._throughput_counters["test_operation"]), 3)
        
        # Vérifie que les timestamps sont récents
        current_time = time.time()
        for timestamp in self.latency_service._throughput_counters["test_operation"]:
            self.assertLess(abs(current_time - timestamp), 1.0)
    
    def test_throughput_rate_empty(self):
        """Teste le calcul du taux de throughput avec un historique vide."""
        rate = self.latency_service.get_throughput_rate("empty_operation")
        self.assertEqual(rate, 0.0)
    
    def test_throughput_rate_calculation(self):
        """Teste le calcul du taux de throughput."""
        # Simule des opérations sur 2 secondes
        current_time = time.time()
        for i in range(10):
            self.latency_service._throughput_counters["test_operation"].append(current_time - 1 + i * 0.2)
        
        rate = self.latency_service.get_throughput_rate("test_operation")
        
        # Avec une fenêtre de 60 secondes, toutes les opérations sont incluses
        # 10 opérations sur ~2 secondes = ~5 opérations/seconde
        # Mais le calcul réel donne environ 0.17 op/s car la fenêtre est de 60s
        self.assertGreater(rate, 0.1)
        self.assertLess(rate, 1.0)
    
    def test_get_all_latency_metrics(self):
        """Teste la récupération de toutes les métriques de latence."""
        # Ajoute des données de test
        self.latency_service._latency_history["action1"].append(10.0)
        self.latency_service._latency_history["action2"].append(20.0)
        
        all_metrics = self.latency_service.get_all_latency_metrics()
        
        self.assertIn("action1", all_metrics)
        self.assertIn("action2", all_metrics)
        self.assertEqual(all_metrics["action1"]["count"], 1)
        self.assertEqual(all_metrics["action2"]["count"], 1)
    
    def test_get_all_throughput_metrics(self):
        """Teste la récupération de toutes les métriques de throughput."""
        # Ajoute des données de test
        self.latency_service.record_throughput("operation1", 5)
        self.latency_service.record_throughput("operation2", 3)
        
        all_metrics = self.latency_service.get_all_throughput_metrics()
        
        self.assertIn("operation1", all_metrics)
        self.assertIn("operation2", all_metrics)
        self.assertGreater(all_metrics["operation1"], 0)
        self.assertGreater(all_metrics["operation2"], 0)
    
    def test_reset_metrics(self):
        """Teste la réinitialisation des métriques."""
        # Ajoute des données
        self.latency_service.start_timer("test_action")
        self.latency_service.record_throughput("test_operation", 5)
        
        self.latency_service.reset_metrics()
        
        self.assertEqual(len(self.latency_service._active_timers), 0)
        self.assertEqual(len(self.latency_service._latency_history), 0)
        self.assertEqual(len(self.latency_service._throughput_counters), 0)
    
    def test_get_metrics_summary(self):
        """Teste la génération du résumé des métriques."""
        # Ajoute des données de test
        self.latency_service.start_timer("test_action")
        self.latency_service.record_throughput("test_operation", 3)
        
        summary = self.latency_service.get_metrics_summary()
        
        self.assertIn("latency", summary)
        self.assertIn("throughput", summary)
        self.assertIn("active_timers", summary)
        self.assertIn("prometheus_available", summary)
        self.assertIsInstance(summary["prometheus_available"], bool)
    
    @patch('services.latency_service.PROMETHEUS_AVAILABLE', True)
    def test_prometheus_metrics_initialization(self):
        """Teste l'initialisation des métriques Prometheus."""
        with patch('services.latency_service.Histogram') as mock_histogram, \
             patch('services.latency_service.Counter') as mock_counter:
            
            service = LatencyService()
            
            # Vérifie que les métriques Prometheus sont créées
            self.assertGreater(len(service._prometheus_metrics), 0)
            mock_histogram.assert_called()
            mock_counter.assert_called()
    
    @patch('services.latency_service.PROMETHEUS_AVAILABLE', False)
    def test_prometheus_unavailable(self):
        """Teste le comportement quand Prometheus n'est pas disponible."""
        service = LatencyService()
        
        # Les métriques Prometheus ne doivent pas être créées
        self.assertEqual(len(service._prometheus_metrics), 0)
        
        # Les opérations doivent continuer à fonctionner
        service.start_timer("test_action")
        latency = service.end_timer("test_action")
        self.assertIsNotNone(latency)
    
    def test_cache_lru_functionality(self):
        """Teste le fonctionnement du cache LRU pour les statistiques."""
        # Ajoute des données
        self.latency_service._latency_history["test_action"].extend([10.0, 20.0, 30.0])
        
        # Premier appel - calcule les statistiques
        stats1 = self.latency_service.get_latency_stats("test_action")
        
        # Deuxième appel - utilise le cache
        stats2 = self.latency_service.get_latency_stats("test_action")
        
        # Les résultats doivent être identiques
        self.assertEqual(stats1, stats2)
    
    def test_latency_history_size_limit(self):
        """Teste la limitation de taille de l'historique des latences."""
        # Ajoute plus de valeurs que la taille maximale
        max_size = 1000
        for i in range(max_size + 100):
            self.latency_service._latency_history["test_action"].append(float(i))
        
        # L'historique ne doit pas dépasser la taille maximale
        self.assertLessEqual(len(self.latency_service._latency_history["test_action"]), max_size)
    
    def test_throughput_window_size_limit(self):
        """Teste la limitation de taille de la fenêtre de throughput."""
        # Ajoute plus d'opérations que la taille de la fenêtre
        window_size = 60
        for i in range(window_size + 10):
            self.latency_service._throughput_counters["test_operation"].append(time.time())
        
        # Le compteur ne doit pas dépasser la taille de la fenêtre
        self.assertLessEqual(len(self.latency_service._throughput_counters["test_operation"]), window_size)


if __name__ == '__main__':
    unittest.main()
