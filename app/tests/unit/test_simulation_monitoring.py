#!/usr/bin/env python3
"""
Tests unitaires pour l'intégration monitoring dans SimulationService
==================================================================

Ce module teste l'intégration du monitoring dans SimulationService :
- Initialisation avec monitoring
- Collecte des métriques pendant la simulation
- Gestion des erreurs de monitoring
- Tests avec monitoring activé/désactivé

Auteur: Assistant IA
Date: 2025-08-04
"""

import pytest
import sys
import os
import tempfile
import time
from unittest.mock import patch, MagicMock

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.simulation_service import SimulationService
from config.config import METRICS_ENABLED


class TestSimulationServiceMonitoring:
    """Tests pour l'intégration monitoring dans SimulationService"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.test_metrics_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl')
        self.test_metrics_file.close()
    
    def teardown_method(self):
        """Cleanup après chaque test"""
        import os
        if os.path.exists(self.test_metrics_file.name):
            os.unlink(self.test_metrics_file.name)
    
    def test_simulation_service_creation_with_monitoring(self):
        """Test la création de SimulationService avec monitoring"""
        service = SimulationService()
        assert service is not None
        
        # Vérifier que l'exporter est initialisé si le monitoring est activé
        if METRICS_ENABLED:
            # L'exporter peut être None si il y a une erreur d'import
            # mais le service ne devrait pas planter
            assert hasattr(service, 'exporter')
        else:
            assert service.exporter is None
    
    @patch('services.simulation_service.METRICS_ENABLED', True)
    @patch('services.simulation_service.MONITORING_AVAILABLE', True)
    def test_simulation_service_with_monitoring_enabled(self):
        """Test SimulationService quand le monitoring est activé"""
        with patch('services.simulation_service.PrometheusExporter') as mock_exporter:
            mock_exporter.return_value = MagicMock()
            
            service = SimulationService()
            
            assert service.exporter is not None
            mock_exporter.assert_called_once()
    
    @patch('services.simulation_service.METRICS_ENABLED', False)
    def test_simulation_service_with_monitoring_disabled(self):
        """Test SimulationService quand le monitoring est désactivé"""
        service = SimulationService()
        
        assert service.exporter is None
    
    @patch('services.simulation_service.METRICS_ENABLED', True)
    @patch('services.simulation_service.MONITORING_AVAILABLE', False)
    def test_simulation_service_with_monitoring_unavailable(self):
        """Test SimulationService quand le monitoring n'est pas disponible"""
        service = SimulationService()
        
        assert service.exporter is None
    
    def test_collecter_metriques_without_exporter(self):
        """Test collecter_metriques sans exporter"""
        service = SimulationService()
        service.exporter = None
        
        # Ne devrait pas lever d'exception
        service.collecter_metriques()
        assert True
    
    @patch('services.simulation_service.METRICS_ENABLED', True)
    @patch('services.simulation_service.MONITORING_AVAILABLE', True)
    def test_collecter_metriques_with_exporter(self):
        """Test collecter_metriques avec exporter"""
        with patch('services.simulation_service.PrometheusExporter') as mock_exporter:
            mock_exporter_instance = MagicMock()
            mock_exporter.return_value = mock_exporter_instance
            
            service = SimulationService()
            
            # Simuler des statistiques
            service.statistiques = {
                'budget_total_actuel': 100000.0,
                'nombre_produits_actifs': 5
            }
            
            # Collecter les métriques
            service.collecter_metriques()
            
            # Vérifier que update_tradesim_metrics a été appelé
            mock_exporter_instance.update_tradesim_metrics.assert_called_once()
            
            # Vérifier les données passées
            call_args = mock_exporter_instance.update_tradesim_metrics.call_args[0][0]
            assert 'budget_total' in call_args
            assert 'produits_actifs' in call_args
            assert 'tours_completes' in call_args
            assert 'temps_simulation_tour_seconds' in call_args
    
    def test_collecter_metriques_with_exporter_error(self):
        """Test collecter_metriques avec erreur d'exporter"""
        service = SimulationService()
        service.exporter = MagicMock()
        service.exporter.update_tradesim_metrics.side_effect = Exception("Exporter error")
        
        # Ne devrait pas lever d'exception
        service.collecter_metriques()
        assert True
    
    def test_simulation_tour_with_monitoring(self):
        """Test simulation_tour avec monitoring"""
        service = SimulationService()

        # Mock l'exporter
        service.prometheus_exporter = MagicMock()

        # Simuler des statistiques
        service.statistiques = {
            'budget_total_actuel': 100000.0,
            'nombre_produits_actifs': 5
        }

        # Exécuter un tour
        result = service.simulation_tour(verbose=False)

        # Vérifier que collecter_metriques a été appelé
        service.prometheus_exporter.update_tradesim_metrics.assert_called_once()

        # Vérifier le résultat
        assert isinstance(result, dict)
        required_keys = {'tour', 'tick', 'evenements_appliques', 'transactions_effectuees'}
        assert required_keys.issubset(result.keys()), f"Missing keys: {required_keys - result.keys()}"
    
    def test_simulation_tour_without_monitoring(self):
        """Test simulation_tour sans monitoring"""
        service = SimulationService()
        service.prometheus_exporter = None
        
        # Exécuter un tour
        result = service.simulation_tour(verbose=False)
        
        # Vérifier le résultat
        assert isinstance(result, dict)
        required_keys = {'tour', 'tick', 'evenements_appliques', 'transactions_effectuees'}
        assert required_keys.issubset(result.keys()), f"Missing keys: {required_keys - result.keys()}"
    
    def test_run_simulation_tours_with_monitoring(self):
        """Test run_simulation_tours avec monitoring"""
        service = SimulationService()
        service.prometheus_exporter = MagicMock()
        
        # Exécuter 2 tours
        results = service.run_simulation_tours(2, verbose=False)
        
        # Vérifier que collecter_metriques a été appelé 2 fois
        assert service.prometheus_exporter.update_tradesim_metrics.call_count == 2
        
        # Vérifier les résultats
        assert len(results) == 2
        for result in results:
            assert isinstance(result, dict)
            assert 'tour' in result
            assert 'tick' in result
    
    def test_run_simulation_tours_without_monitoring(self):
        """Test run_simulation_tours sans monitoring"""
        service = SimulationService()
        service.prometheus_exporter = None
        
        # Exécuter 2 tours
        results = service.run_simulation_tours(2, verbose=False)
        
        # Vérifier les résultats
        assert len(results) == 2
        for result in results:
            assert isinstance(result, dict)
            assert 'tour' in result
            assert 'tick' in result
    
    def test_calculer_statistiques_with_monitoring(self):
        """Test calculer_statistiques avec monitoring"""
        service = SimulationService()
        service.prometheus_exporter = MagicMock()
        
        # Simuler des données
        service.tours_completes = 5
        service.evenements_appliques = [1, 2, 3]  # 3 événements
        
        # Calculer les statistiques
        stats = service.calculer_statistiques()
        
        # Vérifier les statistiques
        assert isinstance(stats, dict)
        assert 'tours_completes' in stats
        assert 'evenements_appliques' in stats
        assert 'budget_total_actuel' in stats
        assert 'nombre_produits_actifs' in stats
        
        assert stats['tours_completes'] == 5
        assert stats['evenements_appliques'] == 3
    
    def test_reset_simulation_with_monitoring(self):
        """Test reset_simulation avec monitoring"""
        service = SimulationService()
        service.prometheus_exporter = MagicMock()
        
        # Simuler des données
        service.tours_completes = 10
        service.evenements_appliques = [1, 2, 3]
        
        # Reset
        service.reset_simulation()
        
        # Vérifier que les données sont resetées
        assert service.tours_completes == 0
        assert len(service.evenements_appliques) == 0
        
        # L'exporter devrait toujours être présent
        assert service.exporter is not None


class TestSimulationServiceMonitoringErrors:
    """Tests de gestion d'erreurs pour le monitoring dans SimulationService"""
    
    @patch('services.simulation_service.METRICS_ENABLED', True)
    @patch('services.simulation_service.MONITORING_AVAILABLE', True)
    def test_simulation_service_creation_with_exporter_error(self):
        """Test la création avec erreur d'exporter"""
        with patch('services.simulation_service.PrometheusExporter', side_effect=Exception("Exporter error")):
            # Ne devrait pas lever d'exception
            service = SimulationService()
            assert service.exporter is None
    
    def test_collecter_metriques_with_calculation_error(self):
        """Test collecter_metriques avec erreur de calcul"""
        service = SimulationService()
        service.exporter = MagicMock()
        
        # Mock calculer_statistiques pour lever une exception
        service.calculer_statistiques = MagicMock(side_effect=Exception("Calculation error"))
        
        # Ne devrait pas lever d'exception
        service.collecter_metriques()
        assert True
    
    def test_simulation_tour_with_monitoring_error(self):
        """Test simulation_tour avec erreur de monitoring"""
        service = SimulationService()
        service.exporter = MagicMock()
        service.exporter.update_tradesim_metrics.side_effect = Exception("Monitoring error")
        
        # Exécuter un tour
        result = service.simulation_tour(verbose=False)
        
        # Le tour devrait se terminer normalement malgré l'erreur de monitoring
        assert isinstance(result, dict)
        assert 'tour' in result
    
    def test_run_simulation_tours_with_monitoring_error(self):
        """Test run_simulation_tours avec erreur de monitoring"""
        service = SimulationService()
        service.exporter = MagicMock()
        service.exporter.update_tradesim_metrics.side_effect = Exception("Monitoring error")
        
        # Exécuter 2 tours
        results = service.run_simulation_tours(2, verbose=False)
        
        # Les tours devraient se terminer normalement
        assert len(results) == 2
        for result in results:
            assert isinstance(result, dict)
            assert 'tour' in result 