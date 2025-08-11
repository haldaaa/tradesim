#!/usr/bin/env python3
"""
Tests unitaires pour le service de métriques de budget
=====================================================

Tests complets du BudgetMetricsService avec validation de tous les calculs
et métriques de budget.

Instructions de lancement :
- Test complet : pytest tests/unit/test_budget_metrics.py -v
- Test spécifique : pytest tests/unit/test_budget_metrics.py::TestBudgetMetricsService::test_calculer_metriques_budget -v
- Test avec couverture : pytest tests/unit/test_budget_metrics.py --cov=services.budget_metrics_service -v
"""

import pytest
import statistics
import math
from unittest.mock import patch, MagicMock

from models.models import Entreprise, TypeProduit
from services.budget_metrics_service import BudgetMetricsService
from config.config import (
    BUDGET_CRITIQUE_SEUIL, BUDGET_FAIBLE_SEUIL, BUDGET_ELEVE_SEUIL,
    BUDGET_HISTORY_MAX_TOURS
)


class TestBudgetMetricsService:
    """Tests unitaires pour BudgetMetricsService"""
    
    def setup_method(self):
        """Configuration initiale pour chaque test"""
        self.service = BudgetMetricsService()
        
        # Données de test
        self.entreprises = [
            Entreprise(
                id=1, nom="TestEnt1", pays="France", continent="Europe",
                budget=10000, budget_initial=12000,
                types_preferes=[TypeProduit.matiere_premiere], strategie="moins_cher"
            ),
            Entreprise(
                id=2, nom="TestEnt2", pays="Allemagne", continent="Europe",
                budget=5000, budget_initial=8000,
                types_preferes=[TypeProduit.produit_fini], strategie="moins_cher"
            ),
            Entreprise(
                id=3, nom="TestEnt3", pays="Italie", continent="Europe",
                budget=15000, budget_initial=10000,
                types_preferes=[TypeProduit.matiere_premiere], strategie="moins_cher"
            )
        ]
    
    def teardown_method(self):
        """Nettoyage après chaque test"""
        self.service.reset()
    
    def test_initialisation(self):
        """Test de l'initialisation du service"""
        assert self.service.historique_budgets is not None
        assert self.service.depenses_totales == 0.0
        assert self.service.gains_totaux == 0.0
        assert self.service.transactions_count == 0
        assert self.service.tour_actuel == 0
    
    def test_ajouter_tour(self):
        """Test de l'ajout d'un tour à l'historique"""
        self.service.ajouter_tour(self.entreprises, 1)
        
        assert len(self.service.historique_budgets) == 1
        assert self.service.tour_actuel == 1
        
        tour_data = self.service.historique_budgets[0]
        assert tour_data['tour'] == 1
        assert tour_data['entreprises_count'] == 3
        assert tour_data['budgets'] == [10000, 5000, 15000]
        assert tour_data['budgets_initiaux'] == [12000, 8000, 10000]
    
    def test_enregistrer_transaction_achat(self):
        """Test de l'enregistrement d'une transaction d'achat"""
        self.service.enregistrer_transaction(1000.0, "achat")
        
        assert self.service.transactions_count == 1
        assert self.service.depenses_totales == 1000.0
        assert self.service.gains_totaux == 0.0
    
    def test_enregistrer_transaction_vente(self):
        """Test de l'enregistrement d'une transaction de vente"""
        self.service.enregistrer_transaction(500.0, "vente")
        
        assert self.service.transactions_count == 1
        assert self.service.depenses_totales == 0.0
        assert self.service.gains_totaux == 500.0
    
    def test_calculer_metriques_budget_avec_entreprises(self):
        """Test du calcul des métriques de budget avec des entreprises"""
        # Ajouter quelques transactions
        self.service.enregistrer_transaction(1000.0, "achat")
        self.service.enregistrer_transaction(500.0, "vente")
        
        # Ajouter un tour
        self.service.ajouter_tour(self.entreprises, 1)
        
        # Calculer les métriques
        metrics = self.service.calculer_metriques_budget(self.entreprises)
        
        # Vérifications de base
        assert metrics['budget_total_entreprises'] == 30000  # 10000 + 5000 + 15000
        assert metrics['budget_moyen_entreprises'] == 10000  # 30000 / 3
        assert metrics['budget_median_entreprises'] == 10000  # Médiane de [5000, 10000, 15000]
        assert metrics['entreprises_count'] == 3
        assert metrics['transactions_count'] == 2
        
        # Vérifications des dépenses/gains
        assert metrics['budget_depenses_totales'] == 1000.0
        assert metrics['budget_gains_totaux'] == 500.0
        
        # Vérifications des variations
        assert metrics['budget_variation_totale'] == 0  # (10000-12000) + (5000-8000) + (15000-10000)
    
    def test_calculer_metriques_budget_sans_entreprises(self):
        """Test du calcul des métriques de budget sans entreprises"""
        metrics = self.service.calculer_metriques_budget([])
        
        # Vérifications pour liste vide
        assert metrics['budget_total_entreprises'] == 0.0
        assert metrics['budget_moyen_entreprises'] == 0.0
        assert metrics['budget_median_entreprises'] == 0.0
        assert metrics['entreprises_count'] == 0
        assert metrics['transactions_count'] == 0
    
    def test_calculer_statistiques(self):
        """Test du calcul des statistiques"""
        budgets = [1000, 2000, 3000, 4000, 5000]
        stats = self.service._calculer_statistiques(budgets)
        
        # Vérifications des statistiques
        assert stats['moyenne'] == 3000.0
        assert stats['mediane'] == 3000.0
        assert abs(stats['ecart_type'] - 1581.14) < 0.01  # Écart-type approximatif
        assert abs(stats['coefficient_variation'] - 0.527) < 0.01  # CV approximatif
        assert abs(stats['skewness']) < 1.0  # Skewness devrait être proche de 0 pour une distribution symétrique
    
    def test_calculer_statistiques_liste_vide(self):
        """Test du calcul des statistiques avec une liste vide"""
        stats = self.service._calculer_statistiques([])
        
        assert stats['moyenne'] == 0.0
        assert stats['mediane'] == 0.0
        assert stats['ecart_type'] == 0.0
        assert stats['coefficient_variation'] == 0.0
        assert stats['skewness'] == 0.0
    
    def test_calculer_statistiques_une_valeur(self):
        """Test du calcul des statistiques avec une seule valeur"""
        stats = self.service._calculer_statistiques([1000])
        
        assert stats['moyenne'] == 1000.0
        assert stats['mediane'] == 1000.0
        assert stats['ecart_type'] == 0.0
        assert stats['coefficient_variation'] == 0.0
        assert stats['skewness'] == 0.0
    
    def test_calculer_variations(self):
        """Test du calcul des variations"""
        budgets_actuels = [10000, 5000, 15000]
        budgets_initiaux = [12000, 8000, 10000]
        
        variations = self.service._calculer_variations(budgets_actuels, budgets_initiaux)
        
        # Variation totale = (10000-12000) + (5000-8000) + (15000-10000) = -2000 + -3000 + 5000 = 0
        assert variations['variation_totale'] == 0
    
    def test_calculer_variations_listes_differentes(self):
        """Test du calcul des variations avec des listes de tailles différentes"""
        budgets_actuels = [10000, 5000]
        budgets_initiaux = [12000, 8000, 10000]  # Une valeur de plus
        
        variations = self.service._calculer_variations(budgets_actuels, budgets_initiaux)
        
        # Devrait retourner 0 si les listes ont des tailles différentes
        assert variations['variation_totale'] == 0.0
    
    def test_calculer_tendances_sans_historique(self):
        """Test du calcul des tendances sans historique"""
        tendances = self.service._calculer_tendances()
        
        assert tendances['evolution_tour'] == 0.0
        assert tendances['tendance_globale'] == 0.0
    
    def test_calculer_tendances_avec_historique(self):
        """Test du calcul des tendances avec historique"""
        # Ajouter deux tours
        self.service.ajouter_tour(self.entreprises, 1)
        self.service.ajouter_tour(self.entreprises, 2)
        
        tendances = self.service._calculer_tendances()
        
        # L'évolution devrait être 0 car les budgets sont identiques
        assert tendances['evolution_tour'] == 0.0
        assert tendances['tendance_globale'] == 0.0
    
    def test_calculer_ratio_depenses_revenus(self):
        """Test du calcul du ratio dépenses/revenus"""
        # Aucune transaction
        ratio = self.service._calculer_ratio_depenses_revenus()
        assert ratio == 0.0
        
        # Dépenses mais pas de revenus
        self.service.enregistrer_transaction(1000.0, "achat")
        ratio = self.service._calculer_ratio_depenses_revenus()
        assert ratio == 999999.0  # Valeur fixe pour éviter l'infini
        
        # Dépenses et revenus
        self.service.enregistrer_transaction(500.0, "vente")
        ratio = self.service._calculer_ratio_depenses_revenus()
        assert ratio == 2.0  # 1000 / 500
    
    def test_calculer_alertes(self):
        """Test du calcul des alertes"""
        budgets = [500, 2000, 5000, 20000]  # Critique, Faible, Normal, Élevé
        
        alertes = self.service._calculer_alertes(budgets)
        
        assert alertes['entreprises_critiques'] == 1  # 500 ≤ 1000
        assert alertes['entreprises_faibles'] == 1    # 1000 < 2000 ≤ 3000
        assert alertes['entreprises_normales'] == 1   # 3000 < 5000 ≤ 15000
        assert alertes['entreprises_elevees'] == 1    # 20000 > 15000
    
    def test_historique_max_tours(self):
        """Test de la limite de l'historique"""
        # Ajouter plus de tours que la limite
        for i in range(BUDGET_HISTORY_MAX_TOURS + 10):
            self.service.ajouter_tour(self.entreprises, i)
        
        # L'historique ne devrait pas dépasser la limite
        assert len(self.service.historique_budgets) == BUDGET_HISTORY_MAX_TOURS
        
        # Le premier tour devrait être le plus ancien
        assert self.service.historique_budgets[0]['tour'] == 10  # Les 10 premiers ont été supprimés
    
    def test_cache_lru(self):
        """Test du cache LRU pour les calculs complexes"""
        budgets = [1000, 2000, 3000, 4000, 5000]
        
        # Premier appel (pas en cache)
        stats1 = self.service._calculer_statistiques(budgets)
        
        # Deuxième appel (en cache)
        stats2 = self.service._calculer_statistiques(budgets)
        
        # Les résultats doivent être identiques
        assert stats1 == stats2
    
    def test_reset(self):
        """Test de la réinitialisation du service"""
        # Ajouter des données
        self.service.enregistrer_transaction(1000.0, "achat")
        self.service.ajouter_tour(self.entreprises, 1)
        
        # Réinitialiser
        self.service.reset()
        
        # Vérifier que tout est remis à zéro
        assert self.service.depenses_totales == 0.0
        assert self.service.gains_totaux == 0.0
        assert self.service.transactions_count == 0
        assert self.service.tour_actuel == 0
        assert len(self.service.historique_budgets) == 0
    
    def test_metriques_vides(self):
        """Test des métriques vides"""
        metrics = self.service._metriques_vides()
        
        # Vérifier que toutes les métriques sont à 0
        assert metrics['budget_total_entreprises'] == 0.0
        assert metrics['budget_moyen_entreprises'] == 0.0
        assert metrics['budget_median_entreprises'] == 0.0
        assert metrics['entreprises_count'] == 0
        assert metrics['transactions_count'] == 0
    
    def test_integration_complete(self):
        """Test d'intégration complète"""
        # Simuler une session complète
        for tour in range(1, 6):
            # Ajouter des transactions
            self.service.enregistrer_transaction(1000.0 * tour, "achat")
            self.service.enregistrer_transaction(500.0 * tour, "vente")
            
            # Ajouter le tour
            self.service.ajouter_tour(self.entreprises, tour)
            
            # Calculer les métriques
            metrics = self.service.calculer_metriques_budget(self.entreprises)
            
            # Vérifications de base
            assert metrics['budget_total_entreprises'] == 30000
            assert metrics['entreprises_count'] == 3
            assert metrics['transactions_count'] == tour * 2
        
        # Vérifier l'historique
        assert len(self.service.historique_budgets) == 5
        
        # Vérifier les dépenses/gains cumulés
        assert self.service.depenses_totales == 15000  # 1000 + 2000 + 3000 + 4000 + 5000
        assert self.service.gains_totaux == 7500      # 500 + 1000 + 1500 + 2000 + 2500


if __name__ == "__main__":
    # Instructions de lancement
    print("Tests unitaires pour BudgetMetricsService")
    print("Lancement : pytest tests/unit/test_budget_metrics.py -v")
    print("Couverture : pytest tests/unit/test_budget_metrics.py --cov=services.budget_metrics_service -v")
