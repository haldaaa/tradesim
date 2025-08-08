#!/usr/bin/env python3
"""
Tests unitaires pour la configuration monitoring
==============================================

Ce module teste la configuration monitoring de TradeSim :
- Variables METRICS_* dans config/config.py
- Exports dans config/__init__.py
- Validation des valeurs par défaut
- Gestion des erreurs de configuration

Auteur: Assistant IA
Date: 2025-08-04
"""

import pytest
import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import (
    METRICS_ENABLED,
    METRICS_COLLECTION_INTERVAL,
    METRICS_EXPORTER_PORT,
    METRICS_EXPORTER_HOST,
    METRICS_PROMETHEUS_PORT,
    METRICS_GRAFANA_PORT,
    METRICS_SYSTEM_ENABLED,
    METRICS_SYSTEM_INTERVAL,
    METRICS_LABELS_ENABLED,
    METRICS_LABELS_CONTINENT,
    METRICS_LABELS_PRODUIT_TYPE
)


class TestMonitoringConfig:
    """Tests pour la configuration monitoring"""
    
    def test_metrics_enabled_default(self):
        """Test que METRICS_ENABLED est activé par défaut"""
        assert METRICS_ENABLED is True
        assert isinstance(METRICS_ENABLED, bool)
    
    def test_metrics_collection_interval(self):
        """Test que METRICS_COLLECTION_INTERVAL est un float positif"""
        assert isinstance(METRICS_COLLECTION_INTERVAL, float)
        assert METRICS_COLLECTION_INTERVAL > 0
        assert METRICS_COLLECTION_INTERVAL == 1.0
    
    def test_metrics_exporter_port(self):
        """Test que METRICS_EXPORTER_PORT est un int valide"""
        assert isinstance(METRICS_EXPORTER_PORT, int)
        assert METRICS_EXPORTER_PORT > 0
        assert METRICS_EXPORTER_PORT == 8000
    
    def test_metrics_exporter_host(self):
        """Test que METRICS_EXPORTER_HOST est une string valide"""
        assert isinstance(METRICS_EXPORTER_HOST, str)
        assert METRICS_EXPORTER_HOST == "0.0.0.0"
    
    def test_metrics_prometheus_port(self):
        """Test que METRICS_PROMETHEUS_PORT est un int valide"""
        assert isinstance(METRICS_PROMETHEUS_PORT, int)
        assert METRICS_PROMETHEUS_PORT > 0
        assert METRICS_PROMETHEUS_PORT == 9090
    
    def test_metrics_grafana_port(self):
        """Test que METRICS_GRAFANA_PORT est un int valide"""
        assert isinstance(METRICS_GRAFANA_PORT, int)
        assert METRICS_GRAFANA_PORT > 0
        assert METRICS_GRAFANA_PORT == 3000
    
    def test_metrics_system_enabled(self):
        """Test que METRICS_SYSTEM_ENABLED est activé par défaut"""
        assert METRICS_SYSTEM_ENABLED is True
        assert isinstance(METRICS_SYSTEM_ENABLED, bool)
    
    def test_metrics_system_interval(self):
        """Test que METRICS_SYSTEM_INTERVAL est un float positif"""
        assert isinstance(METRICS_SYSTEM_INTERVAL, float)
        assert METRICS_SYSTEM_INTERVAL > 0
        assert METRICS_SYSTEM_INTERVAL == 5.0
    
    def test_metrics_labels_enabled(self):
        """Test que METRICS_LABELS_ENABLED est désactivé par défaut (phase 1)"""
        assert METRICS_LABELS_ENABLED is False
        assert isinstance(METRICS_LABELS_ENABLED, bool)
    
    def test_metrics_labels_continent(self):
        """Test que METRICS_LABELS_CONTINENT est désactivé par défaut"""
        assert METRICS_LABELS_CONTINENT is False
        assert isinstance(METRICS_LABELS_CONTINENT, bool)
    
    def test_metrics_labels_produit_type(self):
        """Test que METRICS_LABELS_PRODUIT_TYPE est désactivé par défaut"""
        assert METRICS_LABELS_PRODUIT_TYPE is False
        assert isinstance(METRICS_LABELS_PRODUIT_TYPE, bool)
    
    def test_ports_are_different(self):
        """Test que les ports sont différents pour éviter les conflits"""
        assert METRICS_EXPORTER_PORT != METRICS_PROMETHEUS_PORT
        assert METRICS_EXPORTER_PORT != METRICS_GRAFANA_PORT
        assert METRICS_PROMETHEUS_PORT != METRICS_GRAFANA_PORT
    
    def test_intervals_are_positive(self):
        """Test que tous les intervalles sont positifs"""
        assert METRICS_COLLECTION_INTERVAL > 0
        assert METRICS_SYSTEM_INTERVAL > 0
    
    def test_boolean_values(self):
        """Test que toutes les valeurs booléennes sont bien des bool"""
        boolean_vars = [
            METRICS_ENABLED,
            METRICS_SYSTEM_ENABLED,
            METRICS_LABELS_ENABLED,
            METRICS_LABELS_CONTINENT,
            METRICS_LABELS_PRODUIT_TYPE
        ]
        
        for var in boolean_vars:
            assert isinstance(var, bool)
    
    def test_numeric_values(self):
        """Test que toutes les valeurs numériques sont bien des nombres"""
        numeric_vars = [
            METRICS_COLLECTION_INTERVAL,
            METRICS_EXPORTER_PORT,
            METRICS_PROMETHEUS_PORT,
            METRICS_GRAFANA_PORT,
            METRICS_SYSTEM_INTERVAL
        ]
        
        for var in numeric_vars:
            assert isinstance(var, (int, float))
            assert var > 0
    
    def test_string_values(self):
        """Test que toutes les valeurs string sont bien des strings"""
        string_vars = [
            METRICS_EXPORTER_HOST
        ]
        
        for var in string_vars:
            assert isinstance(var, str)
            assert len(var) > 0


class TestMonitoringConfigIntegration:
    """Tests d'intégration pour la configuration monitoring"""
    
    def test_all_metrics_vars_importable(self):
        """Test que toutes les variables METRICS_* sont importables"""
        from config import (
            METRICS_ENABLED,
            METRICS_COLLECTION_INTERVAL,
            METRICS_EXPORTER_PORT,
            METRICS_EXPORTER_HOST,
            METRICS_PROMETHEUS_PORT,
            METRICS_GRAFANA_PORT,
            METRICS_SYSTEM_ENABLED,
            METRICS_SYSTEM_INTERVAL,
            METRICS_LABELS_ENABLED,
            METRICS_LABELS_CONTINENT,
            METRICS_LABELS_PRODUIT_TYPE
        )
        
        # Si on arrive ici, l'import a réussi
        assert True
    
    def test_config_consistency(self):
        """Test la cohérence de la configuration"""
        # Si le monitoring est activé, les ports doivent être définis
        if METRICS_ENABLED:
            assert METRICS_EXPORTER_PORT > 0
            assert METRICS_PROMETHEUS_PORT > 0
            assert METRICS_GRAFANA_PORT > 0
        
        # Si les labels sont activés, les labels individuels doivent être cohérents
        if METRICS_LABELS_ENABLED:
            # En phase 1, les labels sont désactivés
            assert METRICS_LABELS_CONTINENT is False
            assert METRICS_LABELS_PRODUIT_TYPE is False 