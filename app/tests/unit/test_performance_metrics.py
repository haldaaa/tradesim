#!/usr/bin/env python3
"""
Tests unitaires pour le service de métriques de performance
==========================================================

Tests complets du PerformanceMetricsService avec validation de tous les calculs
et métriques de performance.

Instructions de lancement :
- Test complet : pytest tests/unit/test_performance_metrics.py -v
- Test spécifique : pytest tests/unit/test_performance_metrics.py::TestPerformanceMetricsService::test_calculer_metriques_performance -v
- Test avec couverture : pytest tests/unit/test_performance_metrics.py --cov=services.performance_metrics_service -v
"""

import pytest
import statistics
import time
from unittest.mock import patch, MagicMock
from pydantic.main import _object_setattr

from models.models import Entreprise, Fournisseur, Produit, TypeProduit
from services.performance_metrics_service import PerformanceMetricsService
from config.config import (
    PERFORMANCE_CRITIQUE_TEMPS, PERFORMANCE_CRITIQUE_MEMOIRE, PERFORMANCE_CRITIQUE_CPU,
    PERFORMANCE_HISTORY_MAX_TOURS
)


class TestPerformanceMetricsService:
    """Tests unitaires pour PerformanceMetricsService"""
    
    def setup_method(self):
        """Configuration initiale pour chaque test"""
        self.service = PerformanceMetricsService()
    
    def teardown_method(self):
        """Nettoyage après chaque test"""
        self.service.reset()
    
    def test_initialisation(self):
        """Test de l'initialisation du service"""
        assert self.service.historique_performance is not None
        assert self.service.mesures_par_tour == {}
        assert self.service.temps_execution == []
        assert self.service.memoire_utilisee == []
        assert self.service.cpu_utilisation == []
        assert self.service.tour_actuel == 0
        assert self.service.debut_tour == 0.0
    
    def test_debut_mesure(self):
        """Test du démarrage d'une mesure"""
        self.service.debut_mesure()
        
        assert self.service.debut_tour > 0.0
    
    def test_fin_mesure(self):
        """Test de la fin d'une mesure"""
        # Démarrer une mesure
        self.service.debut_mesure()
        time.sleep(0.01)  # Attendre un peu
        
        # Finir la mesure
        self.service.fin_mesure(1)
        
        assert len(self.service.temps_execution) == 1
        assert len(self.service.mesures_par_tour[1]) == 1
        assert self.service.debut_tour == 0.0  # Réinitialisé
        
        # Vérifier les données de la mesure
        mesure = self.service.mesures_par_tour[1][0]
        assert mesure['tour'] == 1
        assert 'timestamp' in mesure
        assert mesure['temps_execution'] > 0.0
        assert 'memoire_utilisee' in mesure
        assert 'cpu_utilisation' in mesure
    
    def test_fin_mesure_sans_debut(self):
        """Test de la fin d'une mesure sans avoir démarré"""
        # Essayer de finir une mesure sans avoir démarré
        self.service.fin_mesure(1)
        
        assert len(self.service.temps_execution) == 0
        assert len(self.service.mesures_par_tour) == 0
    
    def test_ajouter_tour(self):
        """Test de l'ajout d'un tour à l'historique"""
        # Ajouter quelques mesures
        self.service.debut_mesure()
        time.sleep(0.01)
        self.service.fin_mesure(1)
        
        self.service.debut_mesure()
        time.sleep(0.01)
        self.service.fin_mesure(1)
        
        self.service.ajouter_tour(1)
        
        assert len(self.service.historique_performance) == 1
        assert self.service.tour_actuel == 1
        
        tour_data = self.service.historique_performance[0]
        assert tour_data['tour'] == 1
        assert tour_data['mesures_count'] == 2
        assert tour_data['temps_execution_moyen'] > 0.0
        assert 'memoire_moyenne' in tour_data
        assert 'cpu_moyen' in tour_data
        assert 'throughput_moyen' in tour_data
    
    def test_ajouter_tour_sans_mesures(self):
        """Test de l'ajout d'un tour sans mesures"""
        self.service.ajouter_tour(1)
        
        assert len(self.service.historique_performance) == 1
        assert self.service.tour_actuel == 1
        
        tour_data = self.service.historique_performance[0]
        assert tour_data['mesures_count'] == 0
        assert tour_data['temps_execution_moyen'] == 0.0
    
    def test_calculer_metriques_performance_avec_mesures(self):
        """Test du calcul des métriques de performance avec des mesures"""
        # Ajouter quelques mesures
        for i in range(3):
            self.service.debut_mesure()
            time.sleep(0.01)
            self.service.fin_mesure(i + 1)
        
        # Ajouter un tour
        self.service.ajouter_tour(1)
        
        # Calculer les métriques
        metrics = self.service.calculer_metriques_performance()
        
        # Vérifications de base
        assert metrics['tour_actuel'] == 1
        assert metrics['total_mesures'] == 3
        assert metrics['total_temps'] > 0.0
        
        # Vérifications des métriques de base
        assert metrics['performance_temps_execution'] > 0.0
        assert metrics['performance_memoire_utilisee'] >= 0.0
        assert metrics['performance_cpu_utilisation'] >= 0.0
        assert metrics['performance_throughput'] > 0.0
        assert metrics['performance_latence'] > 0.0
        
        # Vérifications des métriques de performance
        assert 0.0 <= metrics['performance_efficacite_cache'] <= 1.0
        assert 0.0 <= metrics['performance_optimisation'] <= 1.0
        assert metrics['performance_charge_systeme'] >= 0.0
        assert 0.0 <= metrics['performance_stabilite'] <= 1.0
        assert 0.0 <= metrics['performance_scalabilite'] <= 1.0
        assert 0.0 <= metrics['performance_qualite'] <= 1.0
    
    def test_calculer_metriques_performance_sans_mesures(self):
        """Test du calcul des métriques de performance sans mesures"""
        metrics = self.service.calculer_metriques_performance()
        
        # Vérifications pour liste vide
        assert metrics['tour_actuel'] == 0
        assert metrics['total_mesures'] == 0
        assert metrics['total_temps'] == 0
        
        # Toutes les métriques doivent être à 0
        assert metrics['performance_temps_execution'] == 0.0
        assert metrics['performance_memoire_utilisee'] == 0.0
        assert metrics['performance_cpu_utilisation'] == 0.0
        assert metrics['performance_throughput'] == 0.0
        assert metrics['performance_latence'] == 0.0
    
    def test_calculer_metriques_base(self):
        """Test du calcul des métriques de base"""
        # Ajouter des mesures
        for i in range(3):
            self.service.debut_mesure()
            time.sleep(0.01)
            self.service.fin_mesure(i + 1)
        
        metriques_base = self.service._calculer_metriques_base()
        
        assert metriques_base['temps_execution'] > 0.0
        assert metriques_base['memoire_utilisee'] >= 0.0
        assert metriques_base['cpu_utilisation'] >= 0.0
        assert metriques_base['temps_reponse'] > 0.0
        assert metriques_base['throughput'] > 0.0
        assert metriques_base['latence'] > 0.0
    
    def test_calculer_metriques_performance_avancees(self):
        """Test du calcul des métriques de performance avancées"""
        # Ajouter des mesures avec des temps variables
        for i in range(5):
            self.service.debut_mesure()
            time.sleep(0.01 * (i + 1))  # Temps croissants
            self.service.fin_mesure(i + 1)
        
        metriques_performance = self.service._calculer_metriques_performance()
        
        # Vérifier que toutes les métriques sont calculées
        assert 'efficacite_cache' in metriques_performance
        assert 'optimisation' in metriques_performance
        assert 'charge_systeme' in metriques_performance
        assert 'stabilite' in metriques_performance
        assert 'scalabilite' in metriques_performance
        assert 'qualite' in metriques_performance
        
        # Vérifier les plages de valeurs
        assert 0.0 <= metriques_performance['efficacite_cache'] <= 1.0
        assert 0.0 <= metriques_performance['optimisation'] <= 1.0
        assert metriques_performance['charge_systeme'] >= 0.0
        assert 0.0 <= metriques_performance['stabilite'] <= 1.0
        assert 0.0 <= metriques_performance['scalabilite'] <= 1.0
        assert 0.0 <= metriques_performance['qualite'] <= 1.0
    
    def test_calculer_metriques_comportement(self):
        """Test du calcul des métriques de comportement"""
        # Ajouter des mesures avec des temps variables
        for i in range(5):
            self.service.debut_mesure()
            time.sleep(0.01 * (i + 1))  # Temps croissants
            self.service.fin_mesure(i + 1)
        
        metriques_comportement = self.service._calculer_metriques_comportement()
        
        # Vérifier que toutes les métriques sont calculées
        assert 'volatilite' in metriques_comportement
        assert 'tendance' in metriques_comportement
        assert 'bottlenecks' in metriques_comportement
        assert 'optimisations_disponibles' in metriques_comportement
        
        # Vérifier les types et plages
        assert isinstance(metriques_comportement['volatilite'], float)
        assert isinstance(metriques_comportement['tendance'], float)
        assert isinstance(metriques_comportement['bottlenecks'], int)
        assert isinstance(metriques_comportement['optimisations_disponibles'], int)
        assert metriques_comportement['volatilite'] >= 0.0
        assert metriques_comportement['bottlenecks'] >= 0
        assert metriques_comportement['optimisations_disponibles'] >= 0
    
    def test_calculer_alertes_performance(self):
        """Test du calcul des alertes de performance"""
        # Ajouter des mesures avec des valeurs critiques
        for i in range(3):
            self.service.debut_mesure()
            time.sleep(0.01)
            self.service.fin_mesure(i + 1)
        
        alertes = self.service._calculer_alertes_performance()
        
        # Vérifier que toutes les alertes sont calculées
        assert 'performance_temps_critique' in alertes
        assert 'performance_memoire_critique' in alertes
        assert 'performance_cpu_critique' in alertes
        
        # Vérifier les types
        assert isinstance(alertes['performance_temps_critique'], int)
        assert isinstance(alertes['performance_memoire_critique'], int)
        assert isinstance(alertes['performance_cpu_critique'], int)
        assert alertes['performance_temps_critique'] >= 0
        assert alertes['performance_memoire_critique'] >= 0
        assert alertes['performance_cpu_critique'] >= 0
    
    def test_historique_max_tours(self):
        """Test de la limite de l'historique"""
        # Ajouter plus de tours que la limite
        for i in range(PERFORMANCE_HISTORY_MAX_TOURS + 10):
            self.service.ajouter_tour(i)
        
        # L'historique ne devrait pas dépasser la limite
        assert len(self.service.historique_performance) == PERFORMANCE_HISTORY_MAX_TOURS
        
        # Le premier tour devrait être le plus ancien
        assert self.service.historique_performance[0]['tour'] == 10  # Les 10 premiers ont été supprimés
    
    def test_cache_lru(self):
        """Test du cache LRU pour les calculs complexes"""
        performance_ids = tuple(range(5))
        
        # Premier appel (pas en cache)
        stats1 = self.service._calculer_statistiques_performance(performance_ids)
        
        # Deuxième appel (en cache)
        stats2 = self.service._calculer_statistiques_performance(performance_ids)
        
        # Les résultats doivent être identiques
        assert stats1 == stats2
    
    def test_reset(self):
        """Test de la réinitialisation du service"""
        # Ajouter des données
        self.service.debut_mesure()
        time.sleep(0.01)
        self.service.fin_mesure(1)
        self.service.ajouter_tour(1)
        
        # Réinitialiser
        self.service.reset()
        
        # Vérifier que tout est remis à zéro
        assert self.service.mesures_par_tour == {}
        assert self.service.temps_execution == []
        assert self.service.memoire_utilisee == []
        assert self.service.cpu_utilisation == []
        assert self.service.tour_actuel == 0
        assert self.service.debut_tour == 0.0
        assert len(self.service.historique_performance) == 0
    
    def test_metriques_vides(self):
        """Test des métriques vides"""
        metrics = self.service._metriques_vides()
        
        # Vérifier que toutes les métriques sont à 0
        assert metrics['performance_temps_execution'] == 0.0
        assert metrics['performance_memoire_utilisee'] == 0.0
        assert metrics['performance_cpu_utilisation'] == 0.0
        assert metrics['performance_throughput'] == 0.0
        assert metrics['performance_latence'] == 0.0
        assert metrics['tour_actuel'] == 0
        assert metrics['total_mesures'] == 0
        assert metrics['total_temps'] == 0
    
    def test_integration_complete(self):
        """Test d'intégration complète"""
        # Simuler une session complète
        for tour in range(1, 4):
            # Démarrer la mesure
            self.service.debut_mesure()
            time.sleep(0.01 * tour)  # Temps croissants
            
            # Finir la mesure
            self.service.fin_mesure(tour)
            
            # Ajouter le tour
            self.service.ajouter_tour(tour)
            
            # Calculer les métriques
            metrics = self.service.calculer_metriques_performance()
            
            # Vérifications de base
            assert metrics['tour_actuel'] == tour
            assert metrics['total_mesures'] == tour
            assert metrics['total_temps'] > 0.0
        
        # Vérifier l'historique
        assert len(self.service.historique_performance) == 3
        
        # Vérifier les mesures cumulées
        assert len(self.service.temps_execution) == 3
        assert len(self.service.memoire_utilisee) == 3
        assert len(self.service.cpu_utilisation) == 3
    
    def test_performance_avec_temps_variables(self):
        """Test avec des performances ayant des temps variables"""
        # Ajouter plusieurs mesures avec des temps différents
        temps_variables = [0.01, 0.02, 0.01, 0.03, 0.01]
        
        for i, temps in enumerate(temps_variables):
            self.service.debut_mesure()
            time.sleep(temps)
            self.service.fin_mesure(i + 1)
        
        metriques_comportement = self.service._calculer_metriques_comportement()
        
        # Volatilité devrait être > 0 avec des temps variables
        assert metriques_comportement['volatilite'] > 0.0
        
        # Tendance devrait être calculée
        assert isinstance(metriques_comportement['tendance'], float)
        
        # Bottlenecks devrait être calculé
        assert isinstance(metriques_comportement['bottlenecks'], int)
    
    def test_performance_critique(self):
        """Test avec des performances critiques"""
        # Ajouter des mesures avec des temps critiques
        for i in range(3):
            self.service.debut_mesure()
            time.sleep(PERFORMANCE_CRITIQUE_TEMPS + 0.1)  # Temps critique
            self.service.fin_mesure(i + 1)
        
        alertes = self.service._calculer_alertes_performance()
        
        # Devrait y avoir des alertes de temps critique
        assert alertes['performance_temps_critique'] > 0
    
    @patch('psutil.Process')
    @patch('psutil.virtual_memory')
    def test_mesures_systeme(self, mock_virtual_memory, mock_process):
        """Test des mesures système avec mock"""
        # Configurer les mocks
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value.rss = 100 * 1024 * 1024  # 100 MB
        mock_process_instance.cpu_percent.return_value = 25.0
        mock_process.return_value = mock_process_instance
        
        mock_virtual_memory.return_value.total = 8 * 1024 * 1024 * 1024  # 8 GB
        
        # Ajouter une mesure
        self.service.debut_mesure()
        time.sleep(0.01)
        self.service.fin_mesure(1)
        
        # Vérifier que les mesures système sont collectées
        assert len(self.service.memoire_utilisee) == 1
        assert len(self.service.cpu_utilisation) == 1
        assert self.service.memoire_utilisee[0] == 100.0  # 100 MB
        assert self.service.cpu_utilisation[0] == 25.0  # 25%


if __name__ == "__main__":
    # Instructions de lancement
    print("Tests unitaires pour PerformanceMetricsService")
    print("Lancement : pytest tests/unit/test_performance_metrics.py -v")
    print("Couverture : pytest tests/unit/test_performance_metrics.py --cov=services.performance_metrics_service -v")
