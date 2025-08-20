#!/usr/bin/env python3
"""
Tests unitaires pour le système automatique de gestion des métriques

Teste le DynamicMetricsManager et sa capacité à créer automatiquement
de nouvelles métriques sans modification du code de l'exporter.
"""

import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from monitoring.prometheus_exporter import DynamicMetricsManager, metrics_manager
from prometheus_client import Gauge, Counter, Histogram


class TestDynamicMetricsManager:
    """Tests pour le gestionnaire dynamique des métriques"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.manager = DynamicMetricsManager()
        # Nettoyer le registre pour les tests
        self.manager.metrics_registry.clear()
    
    def test_create_simple_gauge(self):
        """Test la création d'une métrique Gauge simple"""
        metric = self.manager.get_or_create_metric(
            'test_gauge',
            'gauge',
            'Test gauge metric'
        )
        
        assert isinstance(metric, Gauge)
        assert 'tradesim_test_gauge' in self.manager.metrics_registry
    
    def test_create_gauge_with_labels(self):
        """Test la création d'une métrique Gauge avec labels"""
        metric = self.manager.get_or_create_metric(
            'test_gauge_labels',
            'gauge',
            'Test gauge with labels',
            labels=['label1', 'label2']
        )
        
        assert isinstance(metric, Gauge)
        assert 'tradesim_test_gauge_labels' in self.manager.metrics_registry
    
    def test_create_histogram(self):
        """Test la création d'une métrique Histogram"""
        metric = self.manager.get_or_create_metric(
            'test_histogram',
            'histogram',
            'Test histogram metric',
            buckets=[0.1, 0.5, 1.0]
        )
        
        assert isinstance(metric, Histogram)
        assert 'tradesim_test_histogram' in self.manager.metrics_registry
    
    def test_cache_metrics(self):
        """Test que les métriques sont mises en cache"""
        metric1 = self.manager.get_or_create_metric('test_cache', 'gauge')
        metric2 = self.manager.get_or_create_metric('test_cache', 'gauge')
        
        assert metric1 is metric2  # Même objet
        assert len(self.manager.metrics_registry) == 1
    
    def test_update_simple_metric(self):
        """Test la mise à jour d'une métrique simple"""
        self.manager.update_metric('test_update', 42.5)
        
        assert 'tradesim_test_update' in self.manager.metrics_registry
        metric = self.manager.metrics_registry['tradesim_test_update']
        assert isinstance(metric, Gauge)
    
    def test_update_metric_with_labels(self):
        """Test la mise à jour d'une métrique avec labels"""
        self.manager.update_metric(
            'test_labels',
            100,
            labels={'region': 'Europe', 'type': 'test'}
        )
        
        assert 'tradesim_test_labels' in self.manager.metrics_registry
        metric = self.manager.metrics_registry['tradesim_test_labels']
        assert isinstance(metric, Gauge)


class TestAutomaticProcessing:
    """Tests pour le traitement automatique des données"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.manager = DynamicMetricsManager()
        self.manager.metrics_registry.clear()
    
    def test_process_simple_metrics(self):
        """Test le traitement de métriques simples"""
        metrics_data = {
            'budget_total': 100000,
            'transactions_count': 50,
            'performance_score': 95.5
        }
        
        self.manager.process_metrics_data(metrics_data)
        
        # Vérifier que les métriques sont créées avec le préfixe
        expected_metrics = [
            'tradesim_budget_total',
            'tradesim_transactions_count',
            'tradesim_performance_score'
        ]
        
        for metric_name in expected_metrics:
            assert metric_name in self.manager.metrics_registry
    
    def test_process_prefixed_metrics(self):
        """Test le traitement de métriques déjà préfixées"""
        metrics_data = {
            'tradesim_test_budget_total': 100000,
            'tradesim_test_transactions_count': 50
        }
        
        self.manager.process_metrics_data(metrics_data)
        
        # Vérifier que les métriques sont créées sans double préfixe
        assert 'tradesim_test_budget_total' in self.manager.metrics_registry
        assert 'tradesim_test_transactions_count' in self.manager.metrics_registry
    
    def test_process_metrics_with_labels(self):
        """Test le traitement de métriques avec labels"""
        metrics_data = {
            'prix_produit': {
                'value': 150.0,
                'labels': {
                    'produit': 'Marteau',
                    'fournisseur': 'AsiaImport'
                },
                'type': 'gauge',
                'description': 'Prix du produit'
            }
        }
        
        self.manager.process_metrics_data(metrics_data)
        
        assert 'tradesim_prix_produit' in self.manager.metrics_registry
        metric = self.manager.metrics_registry['tradesim_prix_produit']
        assert isinstance(metric, Gauge)
    
    def test_process_aggregated_metrics(self):
        """Test le traitement de métriques agrégées (dictionnaires)"""
        metrics_data = {
            'ventes_par_pays': {
                'France': 150,
                'Allemagne': 200,
                'Espagne': 100
            }
        }
        
        self.manager.process_metrics_data(metrics_data)
        
        # Vérifier que la métrique agrégée est créée
        assert 'tradesim_ventes_par_pays' in self.manager.metrics_registry
        metric = self.manager.metrics_registry['tradesim_ventes_par_pays']
        assert isinstance(metric, Gauge)
    
    def test_process_mixed_metrics(self):
        """Test le traitement d'un mélange de types de métriques"""
        metrics_data = {
            'mixed_test_budget': 100000,  # Simple
            'mixed_test_prix': {  # Avec labels
                'value': 150.0,
                'labels': {'produit': 'Marteau'},
                'type': 'gauge'
            },
            'mixed_test_ventes': {  # Agrégé
                'Europe': 300,
                'Asie': 250
            }
        }
        
        self.manager.process_metrics_data(metrics_data)
        
        # Vérifier que toutes les métriques sont créées
        expected_metrics = [
            'tradesim_mixed_test_budget',
            'tradesim_mixed_test_prix',
            'tradesim_mixed_test_ventes'
        ]
        
        for metric_name in expected_metrics:
            assert metric_name in self.manager.metrics_registry


class TestErrorHandling:
    """Tests pour la gestion d'erreurs"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.manager = DynamicMetricsManager()
        self.manager.metrics_registry.clear()
    
    def test_invalid_metric_type(self):
        """Test la gestion d'un type de métrique invalide"""
        # Le type invalide devrait être ignoré et utiliser Gauge par défaut
        metric = self.manager.get_or_create_metric(
            'test_invalid_type',
            'invalid_type',
            'Test metric'
        )
        
        assert isinstance(metric, Gauge)  # Type par défaut
    
    def test_invalid_value_type(self):
        """Test la gestion de valeurs invalides"""
        metrics_data = {
            'test_valid_metric': 42,
            'test_invalid_string': 'not_a_number',
            'test_invalid_bool': True,
            'test_invalid_list': [1, 2, 3]
        }
        
        # Ne devrait pas lever d'exception
        self.manager.process_metrics_data(metrics_data)
        
        # Seule la métrique valide devrait être créée
        assert 'tradesim_test_valid_metric' in self.manager.metrics_registry
        assert 'tradesim_test_invalid_string' not in self.manager.metrics_registry
        assert 'tradesim_test_invalid_bool' not in self.manager.metrics_registry
        assert 'tradesim_test_invalid_list' not in self.manager.metrics_registry
    
    def test_malformed_labels(self):
        """Test la gestion de labels malformés"""
        metrics_data = {
            'test_malformed_labels': {
                'value': 100,
                'labels': {
                    'valid_label': 'value',
                    'empty_label': '',
                    'none_label': None
                }
            }
        }
        
        # Ne devrait pas lever d'exception
        self.manager.process_metrics_data(metrics_data)
        
        # La métrique devrait être créée malgré les labels invalides
        assert 'tradesim_test_malformed_labels' in self.manager.metrics_registry


class TestIntegration:
    """Tests d'intégration avec l'exporter"""
    
    def test_metrics_manager_global_instance(self):
        """Test que l'instance globale fonctionne"""
        # Vérifier que l'instance globale existe
        assert metrics_manager is not None
        assert isinstance(metrics_manager, DynamicMetricsManager)
    
    def test_metrics_manager_registry(self):
        """Test que le registre des métriques fonctionne"""
        # Nettoyer le registre
        metrics_manager.metrics_registry.clear()
        
        # Ajouter une métrique
        metrics_manager.update_metric('test_integration', 42)
        
        # Vérifier qu'elle est dans le registre
        assert 'tradesim_test_integration' in metrics_manager.metrics_registry


if __name__ == "__main__":
    pytest.main([__file__])
