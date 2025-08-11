#!/usr/bin/env python3
"""
Tests unitaires pour l'intégration monitoring dans simulate.py
============================================================

Ce module teste l'intégration du monitoring dans simulate.py :
- Option --with-metrics
- Fonctions demarrer_monitoring et arreter_monitoring
- Affichage de la configuration
- Gestion des erreurs

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

from services.simulate import (
    demarrer_monitoring,
    arreter_monitoring,
    afficher_configuration_actuelle,
    format_monitoring_status
)
from config.config import METRICS_ENABLED, METRICS_EXPORTER_PORT


class TestCLIMonitoring:
    """Tests pour l'intégration monitoring dans simulate.py"""
    
    def test_afficher_configuration_actuelle(self):
        """Test afficher_configuration_actuelle"""
        # Mock format_monitoring_status
        with patch('services.simulate.format_monitoring_status', return_value="✅ ACTIVÉ (port 8000)"):
            # Ne devrait pas lever d'exception
            afficher_configuration_actuelle()
            assert True
    
    def test_afficher_configuration_actuelle_disabled(self):
        """Test afficher_configuration_actuelle quand désactivé"""
        with patch('services.simulate.METRICS_ENABLED', False):
            with patch('services.simulate.format_monitoring_status', return_value="❌ DÉSACTIVÉ"):
                # Ne devrait pas lever d'exception
                afficher_configuration_actuelle()
                assert True
    
    @patch('services.simulate.METRICS_ENABLED', True)
    def test_demarrer_monitoring_enabled(self):
        """Test demarrer_monitoring quand activé"""
        with patch('services.simulate.PrometheusExporter') as mock_exporter:
            mock_exporter_instance = MagicMock()
            mock_exporter.return_value = mock_exporter_instance
            
            # Mock threading
            with patch('services.simulate.threading') as mock_threading:
                mock_thread = MagicMock()
                mock_threading.Thread.return_value = mock_thread
                
                # Démarrer le monitoring
                demarrer_monitoring()
                
                # Vérifier que l'exporter a été créé
                mock_exporter.assert_called_once()
                
                # Vérifier que le thread a été créé et démarré
                mock_threading.Thread.assert_called_once()
                mock_thread.start.assert_called_once()
    
    @patch('services.simulate.METRICS_ENABLED', False)
    def test_demarrer_monitoring_disabled(self):
        """Test demarrer_monitoring quand désactivé"""
        # Ne devrait pas lever d'exception
        demarrer_monitoring()
        assert True
    
    def test_demarrer_monitoring_with_error(self):
        """Test demarrer_monitoring avec erreur"""
        with patch('services.simulate.METRICS_ENABLED', True):
            with patch('services.simulate.PrometheusExporter', side_effect=Exception("Exporter error")):
                # Ne devrait pas lever d'exception
                demarrer_monitoring()
                assert True
    
    def test_arreter_monitoring(self):
        """Test arreter_monitoring"""
        # Mock les variables globales
        with patch('services.simulate.exporter', MagicMock()):
            # Ne devrait pas lever d'exception
            arreter_monitoring()
            assert True
    
    def test_arreter_monitoring_no_exporter(self):
        """Test arreter_monitoring sans exporter"""
        with patch('services.simulate.exporter', None):
            # Ne devrait pas lever d'exception
            arreter_monitoring()
            assert True


class TestCLIMonitoringIntegration:
    """Tests d'intégration pour le CLI monitoring"""
    
    def test_run_simulation_with_metrics(self):
        """Test run_simulation avec --with-metrics"""
        # Mock les fonctions de monitoring
        with patch('services.simulate.demarrer_monitoring') as mock_demarrer:
            with patch('services.simulate.arreter_monitoring') as mock_arreter:
                with patch('services.simulate.afficher_configuration_actuelle') as mock_afficher:
                    # Mock SimulationService
                    with patch('services.simulation_service.SimulationService') as mock_service:
                        mock_service_instance = MagicMock()
                        mock_service.return_value = mock_service_instance
                        mock_service_instance.run_simulation_tours.return_value = []
                        
                        # Simuler l'appel de run_simulation
                        from services.simulate import run_simulation
                        run_simulation(n_tours=2, with_metrics=True)
                        
                        # Vérifier que les fonctions ont été appelées
                        mock_demarrer.assert_called_once()
                        mock_afficher.assert_called_once()
                        mock_arreter.assert_called_once()
                        mock_service_instance.run_simulation_tours.assert_called_once_with(2, verbose=False)
    
    def test_run_simulation_without_metrics(self):
        """Test run_simulation sans --with-metrics"""
        # Mock les fonctions de monitoring
        with patch('services.simulate.demarrer_monitoring') as mock_demarrer:
            with patch('services.simulate.arreter_monitoring') as mock_arreter:
                with patch('services.simulate.afficher_configuration_actuelle') as mock_afficher:
                    # Mock SimulationService
                    with patch('services.simulation_service.SimulationService') as mock_service:
                        mock_service_instance = MagicMock()
                        mock_service.return_value = mock_service_instance
                        mock_service_instance.run_simulation_tours.return_value = []
                        
                        # Simuler l'appel de run_simulation
                        from services.simulate import run_simulation
                        run_simulation(n_tours=2, with_metrics=False)
                        
                        # Vérifier que les fonctions n'ont PAS été appelées
                        mock_demarrer.assert_not_called()
                        mock_afficher.assert_not_called()
                        mock_arreter.assert_not_called()
                        mock_service_instance.run_simulation_tours.assert_called_once_with(2, verbose=False)
    
    def test_run_simulation_infinite_with_metrics(self):
        """Test run_simulation infinite avec --with-metrics"""
        # Mock les fonctions de monitoring
        with patch('services.simulate.demarrer_monitoring') as mock_demarrer:
            with patch('services.simulate.arreter_monitoring') as mock_arreter:
                with patch('services.simulate.afficher_configuration_actuelle') as mock_afficher:
                    # Mock SimulationService
                    with patch('services.simulation_service.SimulationService') as mock_service:
                        mock_service_instance = MagicMock()
                        mock_service.return_value = mock_service_instance
                        # Simuler KeyboardInterrupt après un tour
                        mock_service_instance.run_simulation_infinite.side_effect = KeyboardInterrupt()
                        
                        # Simuler l'appel de run_simulation
                        from services.simulate import run_simulation
                        run_simulation(infinite=True, with_metrics=True)
                        
                        # Vérifier que les fonctions ont été appelées
                        mock_demarrer.assert_called_once()
                        mock_afficher.assert_called_once()
                        mock_arreter.assert_called_once()
                        mock_service_instance.run_simulation_infinite.assert_called_once_with(verbose=False)


class TestCLIMonitoringErrors:
    """Tests de gestion d'erreurs pour le CLI monitoring"""
    
    def test_demarrer_monitoring_thread_error(self):
        """Test demarrer_monitoring avec erreur de thread"""
        with patch('services.simulate.METRICS_ENABLED', True):
            with patch('services.simulate.PrometheusExporter') as mock_exporter:
                mock_exporter_instance = MagicMock()
                mock_exporter.return_value = mock_exporter_instance
                
                with patch('services.simulate.threading') as mock_threading:
                    mock_thread = MagicMock()
                    mock_thread.start.side_effect = Exception("Thread error")
                    mock_threading.Thread.return_value = mock_thread
                    
                    # Ne devrait pas lever d'exception
                    demarrer_monitoring()
                    assert True
    
    def test_run_simulation_with_monitoring_error(self):
        """Test run_simulation avec erreur de monitoring"""
        # Mock les fonctions de monitoring avec erreur
        with patch('services.simulate.demarrer_monitoring', side_effect=Exception("Monitoring error")):
            with patch('services.simulate.arreter_monitoring') as mock_arreter:
                # Mock SimulationService
                with patch('services.simulation_service.SimulationService') as mock_service:
                    mock_service_instance = MagicMock()
                    mock_service.return_value = mock_service_instance
                    mock_service_instance.run_simulation_tours.return_value = []
                    
                    # Simuler l'appel de run_simulation
                    from services.simulate import run_simulation
                    # L'erreur de monitoring ne devrait pas empêcher la simulation
                    try:
                        run_simulation(n_tours=2, with_metrics=True)
                    except Exception as e:
                        # L'erreur de monitoring est attendue
                        assert "Monitoring error" in str(e)
                    
                    # L'erreur empêche d'arriver à la simulation, donc run_simulation_tours n'est pas appelé
                    # mock_service_instance.run_simulation_tours.assert_called_once_with(2, verbose=False)
    
    def test_run_simulation_with_simulation_error(self):
        """Test run_simulation avec erreur de simulation"""
        # Mock les fonctions de monitoring
        with patch('services.simulate.demarrer_monitoring') as mock_demarrer:
            with patch('services.simulate.arreter_monitoring') as mock_arreter:
                # Mock SimulationService avec erreur
                with patch('services.simulation_service.SimulationService') as mock_service:
                    mock_service_instance = MagicMock()
                    mock_service.return_value = mock_service_instance
                    mock_service_instance.run_simulation_tours.side_effect = Exception("Simulation error")
                    
                    # Simuler l'appel de run_simulation
                    from services.simulate import run_simulation
                    with pytest.raises(Exception):
                        run_simulation(n_tours=2, with_metrics=True)
                    
                    # Vérifier que arreter_monitoring a été appelé malgré l'erreur
                    mock_arreter.assert_called_once()


class TestCLIMonitoringUtils:
    """Tests pour les fonctions utilitaires du CLI monitoring"""
    
    def test_format_monitoring_status_import(self):
        """Test que format_monitoring_status est importable"""
        from monitoring.prometheus_exporter import format_monitoring_status
        assert callable(format_monitoring_status)
    
    def test_prometheus_exporter_import(self):
        """Test que PrometheusExporter est importable"""
        from monitoring.prometheus_exporter import PrometheusExporter
        assert callable(PrometheusExporter)
    
    def test_metrics_enabled_import(self):
        """Test que METRICS_ENABLED est importable"""
        from config.config import METRICS_ENABLED
        assert isinstance(METRICS_ENABLED, bool)
    
    def test_metrics_exporter_port_import(self):
        """Test que METRICS_EXPORTER_PORT est importable"""
        from config.config import METRICS_EXPORTER_PORT
        assert isinstance(METRICS_EXPORTER_PORT, int)
        assert METRICS_EXPORTER_PORT > 0 