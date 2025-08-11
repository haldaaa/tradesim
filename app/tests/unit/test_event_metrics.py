#!/usr/bin/env python3
"""
Tests unitaires pour le service de métriques d'événements
========================================================

Tests complets du EventMetricsService avec validation de tous les calculs
et métriques d'événements.

Instructions de lancement :
- Test complet : pytest tests/unit/test_event_metrics.py -v
- Test spécifique : pytest tests/unit/test_event_metrics.py::TestEventMetricsService::test_calculer_metriques_evenements -v
- Test avec couverture : pytest tests/unit/test_event_metrics.py --cov=services.event_metrics_service -v
"""

import pytest
import statistics
from unittest.mock import patch, MagicMock
from pydantic.main import _object_setattr

from models.models import Entreprise, Fournisseur, Produit, TypeProduit
from services.event_metrics_service import EventMetricsService
from config.config import (
    EVENT_CRITIQUE_FREQUENCE, EVENT_CRITIQUE_IMPACT, EVENT_CRITIQUE_INTENSITE,
    EVENT_HISTORY_MAX_TOURS
)


class TestEventMetricsService:
    """Tests unitaires pour EventMetricsService"""
    
    def setup_method(self):
        """Configuration initiale pour chaque test"""
        self.service = EventMetricsService()
        
        # Données de test
        self.evenement_positif = {
            'type': 'inflation',
            'impact': 0.1,
            'intensite': 0.5,
            'duree': 3,
            'impact_budget': 0.05,
            'impact_prix': 0.1,
            'impact_stock': 0.0
        }
        
        self.evenement_negatif = {
            'type': 'crise',
            'impact': -0.2,
            'intensite': 0.8,
            'duree': 5,
            'impact_budget': -0.1,
            'impact_prix': -0.15,
            'impact_stock': -0.05
        }
    
    def teardown_method(self):
        """Nettoyage après chaque test"""
        self.service.reset()
    
    def test_initialisation(self):
        """Test de l'initialisation du service"""
        assert self.service.historique_evenements is not None
        assert self.service.evenements_par_tour == {}
        assert self.service.evenements_totaux == []
        assert self.service.impacts_historique == []
        assert self.service.intensites_historique == []
        assert self.service.tour_actuel == 0
    
    def test_enregistrer_evenement(self):
        """Test de l'enregistrement d'un événement"""
        self.service.enregistrer_evenement(self.evenement_positif)
        
        assert len(self.service.evenements_totaux) == 1
        assert len(self.service.evenements_par_tour[0]) == 1
        assert self.service.impacts_historique == [0.1]
        assert self.service.intensites_historique == [0.5]
        
        # Vérifier les métadonnées ajoutées
        evenement = self.service.evenements_totaux[0]
        assert 'timestamp' in evenement
        assert evenement['tour'] == 0
        assert evenement['type'] == 'inflation'
    
    def test_ajouter_tour(self):
        """Test de l'ajout d'un tour à l'historique"""
        # Ajouter quelques événements
        self.service.enregistrer_evenement(self.evenement_positif)
        self.service.enregistrer_evenement(self.evenement_negatif)
        
        self.service.ajouter_tour(1)
        
        assert len(self.service.historique_evenements) == 1
        assert self.service.tour_actuel == 1
        
        tour_data = self.service.historique_evenements[0]
        assert tour_data['tour'] == 1
        assert tour_data['evenements_count'] == 2
        assert tour_data['impact_total'] == -0.1  # 0.1 + (-0.2)
        assert abs(tour_data['intensite_moyenne'] - 0.65) < 0.01  # (0.5 + 0.8) / 2
        assert 'inflation' in tour_data['types_evenements']
        assert 'crise' in tour_data['types_evenements']
    
    def test_calculer_metriques_evenements_avec_evenements(self):
        """Test du calcul des métriques d'événements avec des événements"""
        # Ajouter quelques événements
        self.service.enregistrer_evenement(self.evenement_positif)
        self.service.enregistrer_evenement(self.evenement_negatif)
        
        # Ajouter un tour
        self.service.ajouter_tour(1)
        
        # Calculer les métriques
        metrics = self.service.calculer_metriques_evenements()
        
        # Vérifications de base
        assert metrics['evenements_total'] == 2
        assert metrics['tour_actuel'] == 1
        assert metrics['total_impact'] == -0.1  # 0.1 + (-0.2)
        assert abs(metrics['total_intensite'] - 1.3) < 0.01  # 0.5 + 0.8
        
        # Vérifications des répartitions
        assert metrics['evenements_par_type']['inflation'] == 1
        assert metrics['evenements_par_type']['crise'] == 1
        assert metrics['evenements_par_impact']['positif'] == 1
        assert metrics['evenements_par_impact']['negatif'] == 1
        
        # Vérifications des métriques de performance
        assert abs(metrics['evenements_intensite_moyenne'] - 0.65) < 0.01  # (0.5 + 0.8) / 2
        assert abs(metrics['evenements_duree_moyenne'] - 4.0) < 0.01  # (3 + 5) / 2
    
    def test_calculer_metriques_evenements_sans_evenements(self):
        """Test du calcul des métriques d'événements sans événements"""
        metrics = self.service.calculer_metriques_evenements()
        
        # Vérifications pour liste vide
        assert metrics['evenements_total'] == 0
        assert metrics['tour_actuel'] == 0
        assert metrics['total_impact'] == 0
        assert metrics['total_intensite'] == 0
    
    def test_calculer_metriques_base(self):
        """Test du calcul des métriques de base"""
        # Ajouter des événements
        self.service.enregistrer_evenement(self.evenement_positif)
        self.service.enregistrer_evenement(self.evenement_negatif)
        
        metriques_base = self.service._calculer_metriques_base()
        
        assert metriques_base['total'] == 2
        
        # Vérifier les répartitions
        assert metriques_base['par_type']['inflation'] == 1
        assert metriques_base['par_type']['crise'] == 1
        assert metriques_base['par_impact']['positif'] == 1
        assert metriques_base['par_impact']['negatif'] == 1
        
        # Vérifier les moyennes
        assert abs(metriques_base['intensite_moyenne'] - 0.65) < 0.01  # (0.5 + 0.8) / 2
        assert abs(metriques_base['duree_moyenne'] - 4.0) < 0.01  # (3 + 5) / 2
    
    def test_calculer_metriques_performance(self):
        """Test du calcul des métriques de performance"""
        # Ajouter des événements
        self.service.enregistrer_evenement(self.evenement_positif)
        self.service.enregistrer_evenement(self.evenement_negatif)
        
        metriques_performance = self.service._calculer_metriques_performance()
        
        # Impact moyen sur les budgets
        assert abs(metriques_performance['impact_budget'] - (-0.025)) < 0.01  # (0.05 + (-0.1)) / 2
        
        # Impact moyen sur les prix
        assert abs(metriques_performance['impact_prix'] - (-0.025)) < 0.01  # (0.1 + (-0.15)) / 2
        
        # Impact moyen sur les stocks
        assert abs(metriques_performance['impact_stock'] - (-0.025)) < 0.01  # (0.0 + (-0.05)) / 2
        
        # Efficacité (basée sur l'impact vs intensité)
        assert metriques_performance['efficacite'] > 0.0
        
        # Rentabilité (basée sur l'impact positif vs négatif)
        assert metriques_performance['rentabilite'] > 0.0
    
    def test_calculer_metriques_comportement(self):
        """Test du calcul des métriques de comportement"""
        # Ajouter plusieurs événements avec des impacts différents
        evenement1 = self.evenement_positif.copy()
        evenement1['impact'] = 0.1
        evenement1['intensite'] = 0.5
        
        evenement2 = self.evenement_negatif.copy()
        evenement2['impact'] = -0.2
        evenement2['intensite'] = 0.8
        
        evenement3 = self.evenement_positif.copy()
        evenement3['impact'] = 0.3
        evenement3['intensite'] = 0.6
        
        self.service.enregistrer_evenement(evenement1)
        self.service.enregistrer_evenement(evenement2)
        self.service.enregistrer_evenement(evenement3)
        
        metriques_comportement = self.service._calculer_metriques_comportement()
        
        # Volatilité des événements (devrait être > 0 avec des impacts différents)
        assert metriques_comportement['volatilite'] > 0.0
        
        # Tendance des événements (devrait être positive avec des impacts qui augmentent)
        assert metriques_comportement['tendance'] > 0.0
        
        # Corrélation entre impacts et intensités
        assert abs(metriques_comportement['correlation']) <= 1.0  # Corrélation entre -1 et 1
        
        # Prédictibilité (basée sur la régularité des patterns)
        assert metriques_comportement['predictibilite'] >= 0.0
        assert metriques_comportement['predictibilite'] <= 1.0
    
    def test_calculer_alertes_evenements(self):
        """Test du calcul des alertes d'événements"""
        # Créer des événements avec différents niveaux critiques
        evenement_frequence_critique = self.evenement_positif.copy()
        evenement_frequence_critique['impact'] = 0.1
        
        evenement_impact_critique = self.evenement_negatif.copy()
        evenement_impact_critique['impact'] = -0.8  # Impact négatif élevé
        
        evenement_intensite_critique = self.evenement_positif.copy()
        evenement_intensite_critique['intensite'] = 0.9  # Intensité élevée
        
        self.service.enregistrer_evenement(evenement_frequence_critique)
        self.service.enregistrer_evenement(evenement_impact_critique)
        self.service.enregistrer_evenement(evenement_intensite_critique)
        
        alertes = self.service._calculer_alertes_evenements()
        
        # Vérifier que les alertes sont calculées
        assert 'evenements_frequence_critique' in alertes
        assert 'evenements_impact_critique' in alertes
        assert 'evenements_intensite_critique' in alertes
    
    def test_historique_max_tours(self):
        """Test de la limite de l'historique"""
        # Ajouter plus de tours que la limite
        for i in range(EVENT_HISTORY_MAX_TOURS + 10):
            self.service.ajouter_tour(i)
        
        # L'historique ne devrait pas dépasser la limite
        assert len(self.service.historique_evenements) == EVENT_HISTORY_MAX_TOURS
        
        # Le premier tour devrait être le plus ancien
        assert self.service.historique_evenements[0]['tour'] == 10  # Les 10 premiers ont été supprimés
    
    def test_cache_lru(self):
        """Test du cache LRU pour les calculs complexes"""
        evenements_ids = tuple(range(5))
        
        # Premier appel (pas en cache)
        stats1 = self.service._calculer_statistiques_evenements(evenements_ids)
        
        # Deuxième appel (en cache)
        stats2 = self.service._calculer_statistiques_evenements(evenements_ids)
        
        # Les résultats doivent être identiques
        assert stats1 == stats2
    
    def test_reset(self):
        """Test de la réinitialisation du service"""
        # Ajouter des données
        self.service.enregistrer_evenement(self.evenement_positif)
        self.service.ajouter_tour(1)
        
        # Réinitialiser
        self.service.reset()
        
        # Vérifier que tout est remis à zéro
        assert self.service.evenements_par_tour == {}
        assert self.service.evenements_totaux == []
        assert self.service.impacts_historique == []
        assert self.service.intensites_historique == []
        assert self.service.tour_actuel == 0
        assert len(self.service.historique_evenements) == 0
    
    def test_metriques_vides(self):
        """Test des métriques vides"""
        metrics = self.service._metriques_vides()
        
        # Vérifier que toutes les métriques sont à 0
        assert metrics['evenements_total'] == 0
        assert metrics['tour_actuel'] == 0
        assert metrics['total_impact'] == 0
        assert metrics['total_intensite'] == 0
    
    def test_integration_complete(self):
        """Test d'intégration complète"""
        # Simuler une session complète
        for tour in range(1, 4):
            # Ajouter des événements
            evenement = self.evenement_positif.copy()
            evenement['impact'] = 0.1 * tour
            evenement['intensite'] = 0.5 * tour
            
            self.service.enregistrer_evenement(evenement)
            
            # Ajouter le tour
            self.service.ajouter_tour(tour)
            
            # Calculer les métriques
            metrics = self.service.calculer_metriques_evenements()
            
            # Vérifications de base
            assert metrics['evenements_total'] == tour
            assert metrics['tour_actuel'] == tour
        
        # Vérifier l'historique
        assert len(self.service.historique_evenements) == 3
        
        # Vérifier les événements cumulés
        assert len(self.service.evenements_totaux) == 3
        assert len(self.service.impacts_historique) == 3
        assert len(self.service.intensites_historique) == 3
    
    def test_evenements_avec_impacts_variables(self):
        """Test avec des événements ayant des impacts variables"""
        # Ajouter plusieurs événements avec des impacts différents
        impacts = [0.1, -0.2, 0.3, -0.1, 0.5]
        intensites = [0.3, 0.7, 0.4, 0.6, 0.8]
        
        for i, (impact, intensite) in enumerate(zip(impacts, intensites)):
            evenement = self.evenement_positif.copy()
            evenement['impact'] = impact
            evenement['intensite'] = intensite
            self.service.enregistrer_evenement(evenement)
        
        metriques_comportement = self.service._calculer_metriques_comportement()
        
        # Volatilité devrait être > 0 avec des impacts variables
        assert metriques_comportement['volatilite'] > 0.0
        
        # Tendance devrait être calculée
        assert isinstance(metriques_comportement['tendance'], float)
    
    def test_evenements_mixtes(self):
        """Test avec des événements mixtes (positifs et négatifs)"""
        # Ajouter des événements mixtes
        self.service.enregistrer_evenement(self.evenement_positif)
        self.service.enregistrer_evenement(self.evenement_negatif)
        self.service.enregistrer_evenement(self.evenement_positif)
        
        metriques_base = self.service._calculer_metriques_base()
        
        assert metriques_base['positif'] == 2  # Deux événements positifs
        assert metriques_base['negatif'] == 1  # Un événement négatif
        assert metriques_base['total'] == 3  # Trois événements au total


if __name__ == "__main__":
    # Instructions de lancement
    print("Tests unitaires pour EventMetricsService")
    print("Lancement : pytest tests/unit/test_event_metrics.py -v")
    print("Couverture : pytest tests/unit/test_event_metrics.py --cov=services.event_metrics_service -v")
