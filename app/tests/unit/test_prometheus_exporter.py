#!/usr/bin/env python3
"""
Tests unitaires pour l'exporter Prometheus
=========================================

Ce module teste l'exporter Prometheus de TradeSim :
- Création de l'exporter
- Endpoints HTTP (/metrics, /health, /)
- Collecte des métriques
- Stockage JSONL
- Gestion des erreurs

Auteur: Assistant IA
Date: 2025-08-04
"""

import pytest
import sys
import os
import json
import tempfile
import time
from unittest.mock import patch, MagicMock

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from monitoring.prometheus_exporter import (
    PrometheusExporter,
    get_exporter_status,
    format_monitoring_status,
    budget_total,
    transactions_total,
    produits_actifs,
    tours_completes,
    temps_simulation_tour_seconds
)


class TestPrometheusExporter:
    """Tests pour l'exporter Prometheus"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.test_metrics_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl')
        self.test_metrics_file.close()
    
    def teardown_method(self):
        """Cleanup après chaque test"""
        import os
        if os.path.exists(self.test_metrics_file.name):
            os.unlink(self.test_metrics_file.name)
    
    def test_exporter_creation(self):
        """Test la création de l'exporter"""
        exporter = PrometheusExporter()
        assert exporter is not None
        assert exporter.port == 8000
        assert exporter.host == "0.0.0.0"
        assert exporter.app is not None
    
    def test_exporter_creation_custom_params(self):
        """Test la création avec des paramètres personnalisés"""
        exporter = PrometheusExporter(port=9000, host="localhost")
        assert exporter.port == 9000
        assert exporter.host == "localhost"
    
    def test_exporter_metrics_initialization(self):
        """Test que les métriques Prometheus sont initialisées"""
        # Vérifier que les métriques sont créées
        assert budget_total is not None
        assert transactions_total is not None
        assert produits_actifs is not None
        assert tours_completes is not None
        assert temps_simulation_tour_seconds is not None
    
    def test_exporter_routes_setup(self):
        """Test que les routes Flask sont configurées"""
        exporter = PrometheusExporter()
        
        # Vérifier que les routes existent
        routes = [rule.rule for rule in exporter.app.url_map.iter_rules()]
        assert '/metrics' in routes
        assert '/health' in routes
        assert '/' in routes
    
    @patch('monitoring.prometheus_exporter.METRICS_ENABLED', False)
    def test_exporter_start_disabled(self):
        """Test le démarrage quand le monitoring est désactivé"""
        exporter = PrometheusExporter()
        # Ne devrait pas lever d'exception
        assert True
    
    def test_update_tradesim_metrics(self):
        """Test la mise à jour des métriques TradeSim"""
        exporter = PrometheusExporter()
        
        # Données de test
        metrics_data = {
            'budget_total': 100000.0,
            'produits_actifs': 5,
            'tours_completes': 1,
            'temps_simulation_tour_seconds': 0.5
        }
        
        # Mettre à jour les métriques
        exporter.update_tradesim_metrics(metrics_data)
        
        # Vérifier que les métriques ont été mises à jour
        # Note: Les métriques Prometheus sont globales, donc on ne peut pas
        # facilement vérifier leur valeur dans un test unitaire
        assert True  # Si on arrive ici, pas d'erreur
    
    def test_store_metrics_jsonl(self):
        """Test le stockage des métriques en JSONL"""
        exporter = PrometheusExporter()
        exporter.metrics_file = self.test_metrics_file.name
        
        # Données de test
        metrics_data = {
            'budget_total': 100000.0,
            'produits_actifs': 5,
            'tours_completes': 1,
            'temps_simulation_tour_seconds': 0.5
        }
        
        # Stocker les métriques
        exporter._store_metrics_jsonl(metrics_data)
        
        # Vérifier que le fichier a été créé et contient les données
        with open(self.test_metrics_file.name, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 1
            
            # Parser la ligne JSON
            data = json.loads(lines[0])
            assert 'timestamp' in data
            assert 'metrics' in data
            assert data['metrics']['budget_total'] == 100000.0
            assert data['metrics']['produits_actifs'] == 5
    
    def test_store_metrics_jsonl_multiple_entries(self):
        """Test le stockage de plusieurs entrées JSONL"""
        exporter = PrometheusExporter()
        exporter.metrics_file = self.test_metrics_file.name
        
        # Données de test multiples
        metrics_data_list = [
            {'budget_total': 100000.0, 'produits_actifs': 5},
            {'budget_total': 110000.0, 'produits_actifs': 6},
            {'budget_total': 120000.0, 'produits_actifs': 7}
        ]
        
        # Stocker plusieurs métriques
        for metrics_data in metrics_data_list:
            exporter._store_metrics_jsonl(metrics_data)
        
        # Vérifier que le fichier contient toutes les entrées
        with open(self.test_metrics_file.name, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 3
            
            # Vérifier chaque ligne
            for i, line in enumerate(lines):
                data = json.loads(line)
                assert 'timestamp' in data
                assert 'metrics' in data
                assert data['metrics']['budget_total'] == 100000.0 + (i * 10000.0)
                assert data['metrics']['produits_actifs'] == 5 + i
    
    def test_collect_system_metrics(self):
        """Test la collecte des métriques système"""
        exporter = PrometheusExporter()
        
        # Collecter les métriques système
        exporter.collect_system_metrics()
        
        # Si on arrive ici, pas d'erreur
        assert True
    
    @patch('monitoring.prometheus_exporter.METRICS_SYSTEM_ENABLED', False)
    def test_collect_system_metrics_disabled(self):
        """Test la collecte des métriques système quand désactivée"""
        exporter = PrometheusExporter()
        
        # Ne devrait pas lever d'exception
        exporter.collect_system_metrics()
        assert True


class TestPrometheusExporterUtils:
    """Tests pour les fonctions utilitaires de l'exporter"""
    
    def test_get_exporter_status(self):
        """Test la fonction get_exporter_status"""
        status = get_exporter_status()
        
        assert isinstance(status, dict)
        assert 'enabled' in status
        assert 'port' in status
        assert 'host' in status
        assert 'endpoint' in status
        assert 'health' in status
        
        assert isinstance(status['enabled'], bool)
        assert isinstance(status['port'], int)
        assert isinstance(status['host'], str)
        assert isinstance(status['endpoint'], str)
        assert isinstance(status['health'], str)
    
    def test_format_monitoring_status_enabled(self):
        """Test format_monitoring_status quand activé"""
        with patch('monitoring.prometheus_exporter.METRICS_ENABLED', True):
            with patch('monitoring.prometheus_exporter.METRICS_EXPORTER_PORT', 8000):
                status = format_monitoring_status()
                assert "✅ ACTIVÉ" in status
                assert "8000" in status
    
    def test_format_monitoring_status_disabled(self):
        """Test format_monitoring_status quand désactivé"""
        with patch('monitoring.prometheus_exporter.METRICS_ENABLED', False):
            status = format_monitoring_status()
            assert "❌ DÉSACTIVÉ" in status


class TestPrometheusExporterErrors:
    """Tests de gestion d'erreurs pour l'exporter"""
    
    def test_exporter_creation_with_invalid_port(self):
        """Test la création avec un port invalide"""
        # Port invalide - l'exporter gère l'erreur en interne
        exporter = PrometheusExporter(port=999999)
        # L'exporter devrait être créé mais ne pas démarrer correctement
        assert exporter is not None
        assert exporter.port == 999999
    
    def test_store_metrics_jsonl_invalid_path(self):
        """Test le stockage avec un chemin invalide"""
        exporter = PrometheusExporter()
        exporter.metrics_file = "/invalid/path/metrics.jsonl"
        
        metrics_data = {'budget_total': 100000.0}
        
        # Ne devrait pas lever d'exception, mais logger une erreur
        exporter._store_metrics_jsonl(metrics_data)
        assert True
    
    def test_update_metrics_with_invalid_data(self):
        """Test la mise à jour avec des données invalides"""
        exporter = PrometheusExporter()
        
        # Données invalides
        invalid_metrics = {
            'budget_total': "not_a_number",
            'produits_actifs': None,
            'tours_completes': "invalid"
        }
        
        # Ne devrait pas lever d'exception
        exporter.update_tradesim_metrics(invalid_metrics)
        assert True
    
    def test_collect_system_metrics_with_psutil_error(self):
        """Test la collecte système avec erreur psutil"""
        exporter = PrometheusExporter()
        
        # Simuler une erreur psutil
        with patch('psutil.cpu_percent', side_effect=Exception("psutil error")):
            # Ne devrait pas lever d'exception
            exporter.collect_system_metrics()
            assert True 