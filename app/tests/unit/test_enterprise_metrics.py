#!/usr/bin/env python3
"""
Tests unitaires pour le service de métriques d'entreprises
=========================================================

Tests complets du EnterpriseMetricsService avec validation de tous les calculs
et métriques d'entreprises.

Instructions de lancement :
- Test complet : pytest tests/unit/test_enterprise_metrics.py -v
- Test spécifique : pytest tests/unit/test_enterprise_metrics.py::TestEnterpriseMetricsService::test_calculer_metriques_entreprises -v
- Test avec couverture : pytest tests/unit/test_enterprise_metrics.py --cov=services.enterprise_metrics_service -v
"""

import pytest
import statistics
from unittest.mock import patch, MagicMock
from pydantic.main import _object_setattr

from models.models import Entreprise, TypeProduit
from services.enterprise_metrics_service import EnterpriseMetricsService
from config.config import (
    ENTERPRISE_CRITIQUE_BUDGET, ENTERPRISE_CRITIQUE_STOCK, ENTERPRISE_CRITIQUE_TRANSACTIONS,
    ENTERPRISE_HISTORY_MAX_TOURS
)


class TestEnterpriseMetricsService:
    """Tests unitaires pour EnterpriseMetricsService"""
    
    def setup_method(self):
        """Configuration initiale pour chaque test"""
        self.service = EnterpriseMetricsService()
        
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
                types_preferes=[TypeProduit.matiere_premiere, TypeProduit.produit_fini], strategie="moins_cher"
            )
        ]
    
    def teardown_method(self):
        """Nettoyage après chaque test"""
        self.service.reset()
    
    def test_initialisation(self):
        """Test de l'initialisation du service"""
        assert self.service.historique_entreprises is not None
        assert self.service.transactions_par_entreprise == {}
        assert self.service.achats_par_entreprise == {}
        assert self.service.tour_actuel == 0
    
    def test_ajouter_tour(self):
        """Test de l'ajout d'un tour à l'historique"""
        self.service.ajouter_tour(self.entreprises, 1)
        
        assert len(self.service.historique_entreprises) == 1
        assert self.service.tour_actuel == 1
        
        tour_data = self.service.historique_entreprises[0]
        assert tour_data['tour'] == 1
        assert tour_data['entreprises_count'] == 3
        assert len(tour_data['entreprises']) == 3
        
        # Vérifier les données d'une entreprise
        entreprise_data = tour_data['entreprises'][0]
        assert entreprise_data['id'] == 1
        assert entreprise_data['nom'] == "TestEnt1"
        assert entreprise_data['pays'] == "France"
        assert entreprise_data['budget'] == 10000
        assert entreprise_data['strategie'] == "moins_cher"
    
    def test_enregistrer_transaction(self):
        """Test de l'enregistrement d'une transaction"""
        transaction_data = {
            'produit': 'TestProd',
            'fournisseur': 'TestFour',
            'quantite': 10,
            'prix_unitaire': 100.0,
            'montant_total': 1000.0,
            'strategie': 'moins_cher'
        }
        
        self.service.enregistrer_transaction(1, transaction_data)
        
        assert self.service.transactions_par_entreprise[1] == 1
        assert len(self.service.achats_par_entreprise[1]) == 1
        assert self.service.achats_par_entreprise[1][0] == transaction_data
    
    def test_calculer_metriques_entreprises_avec_entreprises(self):
        """Test du calcul des métriques d'entreprises avec des entreprises"""
        # Ajouter quelques transactions
        self.service.enregistrer_transaction(1, {'produit': 'Prod1', 'montant_total': 1000.0})
        self.service.enregistrer_transaction(2, {'produit': 'Prod2', 'montant_total': 500.0})
        
        # Ajouter un tour
        self.service.ajouter_tour(self.entreprises, 1)
        
        # Calculer les métriques
        metrics = self.service.calculer_metriques_entreprises(self.entreprises)
        
        # Vérifications de base
        assert metrics['entreprises_total'] == 3
        assert metrics['entreprises_actives'] == 3  # Toutes ont un budget > 0
        assert metrics['entreprises_count'] == 3
        assert metrics['total_transactions'] == 2
        
        # Vérifications des répartitions
        assert metrics['entreprises_par_pays']['France'] == 1
        assert metrics['entreprises_par_pays']['Allemagne'] == 1
        assert metrics['entreprises_par_pays']['Italie'] == 1
        assert metrics['entreprises_par_continent']['Europe'] == 3
        assert metrics['entreprises_par_strategie']['moins_cher'] == 3
        
        # Vérifications des métriques de performance
        assert metrics['entreprises_transactions_moyennes'] == 2/3  # 2 transactions / 3 entreprises
        assert metrics['entreprises_budget_moyen'] == 10000  # (10000 + 5000 + 15000) / 3
        assert metrics['entreprises_survie_taux'] == 1.0  # Toutes ont un budget > 0
    
    def test_calculer_metriques_entreprises_sans_entreprises(self):
        """Test du calcul des métriques d'entreprises sans entreprises"""
        metrics = self.service.calculer_metriques_entreprises([])
        
        # Vérifications pour liste vide
        assert metrics['entreprises_total'] == 0
        assert metrics['entreprises_actives'] == 0
        assert metrics['entreprises_count'] == 0
        assert metrics['total_transactions'] == 0
    
    def test_calculer_metriques_base(self):
        """Test du calcul des métriques de base"""
        metriques_base = self.service._calculer_metriques_base(self.entreprises)
        
        assert metriques_base['total'] == 3
        assert metriques_base['actives'] == 3
        
        # Vérifier les répartitions
        assert metriques_base['par_pays']['France'] == 1
        assert metriques_base['par_pays']['Allemagne'] == 1
        assert metriques_base['par_pays']['Italie'] == 1
        assert metriques_base['par_continent']['Europe'] == 3
        assert metriques_base['par_strategie']['moins_cher'] == 3
        assert metriques_base['par_type_prefere']['matiere_premiere'] == 2
        assert metriques_base['par_type_prefere']['produit_fini'] == 2
    
    def test_calculer_metriques_performance(self):
        """Test du calcul des métriques de performance"""
        # Ajouter des transactions
        self.service.enregistrer_transaction(1, {'montant_total': 1000.0})
        self.service.enregistrer_transaction(2, {'montant_total': 500.0})
        self.service.enregistrer_transaction(2, {'montant_total': 300.0})
        
        metriques_performance = self.service._calculer_metriques_performance(self.entreprises)
        
        # Transactions moyennes
        assert metriques_performance['transactions_moyennes'] == 1  # (1 + 2 + 0) / 3 = 1
        
        # Budget moyen
        assert metriques_performance['budget_moyen'] == 10000  # (10000 + 5000 + 15000) / 3
        
        # Rentabilité
        rentabilites_attendues = [10000/12000, 5000/8000, 15000/10000]
        assert abs(metriques_performance['rentabilite'] - statistics.mean(rentabilites_attendues)) < 0.01
        
        # Taux de survie
        assert metriques_performance['survie_taux'] == 1.0  # Toutes ont un budget > 0
    
    def test_calculer_metriques_comportement(self):
        """Test du calcul des métriques de comportement"""
        # Ajouter des transactions
        self.service.enregistrer_transaction(1, {'produit': 'Prod1', 'montant_total': 1000.0})
        self.service.enregistrer_transaction(2, {'produit': 'Prod2', 'montant_total': 500.0})
        self.service.enregistrer_transaction(2, {'produit': 'Prod3', 'montant_total': 300.0})
        
        # Ajouter un tour
        self.service.ajouter_tour(self.entreprises, 1)
        
        metriques_comportement = self.service._calculer_metriques_comportement(self.entreprises)
        
        # Fréquence d'achat
        assert metriques_comportement['frequence_achat'] == 1  # Moyenne des fréquences individuelles: (1 + 2 + 0) / 3 = 1
        
        # Préférence de produits (diversité des types préférés)
        assert abs(metriques_comportement['preference_produits'] - 1.33) < 0.01  # (1 + 1 + 2) / 3
        
        # Innovation (diversité des achats)
        # Entreprise 1: 1 produit unique, Entreprise 2: 2 produits uniques, Entreprise 3: 0
        innovation_attendue = (1/10 + 2/10 + 0/10) / 3
        assert abs(metriques_comportement['innovation'] - innovation_attendue) < 0.01
    
    def test_calculer_alertes_entreprises(self):
        """Test du calcul des alertes d'entreprises"""
        # Créer des entreprises avec différents niveaux critiques
        entreprises_critiques = [
            Entreprise(id=1, nom="Critique1", pays="France", continent="Europe",
                      budget=500, budget_initial=1000, types_preferes=[TypeProduit.matiere_premiere], strategie="moins_cher"),
            Entreprise(id=2, nom="Critique2", pays="France", continent="Europe",
                      budget=10000, budget_initial=10000, types_preferes=[TypeProduit.matiere_premiere], strategie="moins_cher")
        ]
        
        # Ajouter des stocks critiques à la deuxième entreprise
        _object_setattr(entreprises_critiques[1], 'stocks', {'Prod1': 5})  # Stock critique (≤ 10)
        
        alertes = self.service._calculer_alertes_entreprises(entreprises_critiques)
        
        assert alertes['entreprises_budget_critique'] == 1  # 500 ≤ 1000
        assert alertes['entreprises_stock_critique'] == 1   # 5 ≤ 10
        assert alertes['entreprises_transactions_critique'] == 2  # 0 transactions pour les deux
    
    def test_historique_max_tours(self):
        """Test de la limite de l'historique"""
        # Ajouter plus de tours que la limite
        for i in range(ENTERPRISE_HISTORY_MAX_TOURS + 10):
            self.service.ajouter_tour(self.entreprises, i)
        
        # L'historique ne devrait pas dépasser la limite
        assert len(self.service.historique_entreprises) == ENTERPRISE_HISTORY_MAX_TOURS
        
        # Le premier tour devrait être le plus ancien
        assert self.service.historique_entreprises[0]['tour'] == 10  # Les 10 premiers ont été supprimés
    
    def test_cache_lru(self):
        """Test du cache LRU pour les calculs complexes"""
        entreprises_ids = tuple(entreprise.id for entreprise in self.entreprises)
        
        # Premier appel (pas en cache)
        stats1 = self.service._calculer_statistiques_entreprises(entreprises_ids)
        
        # Deuxième appel (en cache)
        stats2 = self.service._calculer_statistiques_entreprises(entreprises_ids)
        
        # Les résultats doivent être identiques
        assert stats1 == stats2
    
    def test_reset(self):
        """Test de la réinitialisation du service"""
        # Ajouter des données
        self.service.enregistrer_transaction(1, {'produit': 'Test', 'montant_total': 1000.0})
        self.service.ajouter_tour(self.entreprises, 1)
        
        # Réinitialiser
        self.service.reset()
        
        # Vérifier que tout est remis à zéro
        assert self.service.transactions_par_entreprise == {}
        assert self.service.achats_par_entreprise == {}
        assert self.service.tour_actuel == 0
        assert len(self.service.historique_entreprises) == 0
    
    def test_metriques_vides(self):
        """Test des métriques vides"""
        metrics = self.service._metriques_vides()
        
        # Vérifier que toutes les métriques sont à 0
        assert metrics['entreprises_total'] == 0
        assert metrics['entreprises_actives'] == 0
        assert metrics['entreprises_count'] == 0
        assert metrics['total_transactions'] == 0
    
    def test_integration_complete(self):
        """Test d'intégration complète"""
        # Simuler une session complète
        for tour in range(1, 4):
            # Ajouter des transactions
            self.service.enregistrer_transaction(1, {'produit': f'Prod{tour}', 'montant_total': 1000.0 * tour})
            self.service.enregistrer_transaction(2, {'produit': f'Prod{tour+1}', 'montant_total': 500.0 * tour})
            
            # Ajouter le tour
            self.service.ajouter_tour(self.entreprises, tour)
            
            # Calculer les métriques
            metrics = self.service.calculer_metriques_entreprises(self.entreprises)
            
            # Vérifications de base
            assert metrics['entreprises_total'] == 3
            assert metrics['entreprises_count'] == 3
            assert metrics['total_transactions'] == tour * 2
        
        # Vérifier l'historique
        assert len(self.service.historique_entreprises) == 3
        
        # Vérifier les transactions cumulées
        assert self.service.transactions_par_entreprise[1] == 3
        assert self.service.transactions_par_entreprise[2] == 3
        assert self.service.transactions_par_entreprise[3] == 0
    
    def test_entreprises_avec_stocks(self):
        """Test avec des entreprises ayant des stocks"""
        # Ajouter des stocks aux entreprises
        _object_setattr(self.entreprises[0], 'stocks', {'Prod1': 50, 'Prod2': 30})
        _object_setattr(self.entreprises[1], 'stocks', {'Prod1': 20})
        _object_setattr(self.entreprises[2], 'stocks', {})
        
        metriques_performance = self.service._calculer_metriques_performance(self.entreprises)
        
        # Stock moyen = (80 + 20 + 0) / 3 = 33.33
        assert abs(metriques_performance['stock_moyen'] - 33.33) < 0.01
    
    def test_entreprises_inactives(self):
        """Test avec des entreprises inactives (budget = 0)"""
        entreprises_mixtes = [
            Entreprise(id=1, nom="Active", pays="France", continent="Europe",
                      budget=10000, budget_initial=10000, types_preferes=[TypeProduit.matiere_premiere], strategie="moins_cher"),
            Entreprise(id=2, nom="Inactive", pays="France", continent="Europe",
                      budget=0, budget_initial=10000, types_preferes=[TypeProduit.matiere_premiere], strategie="moins_cher")
        ]
        
        metriques_base = self.service._calculer_metriques_base(entreprises_mixtes)
        metriques_performance = self.service._calculer_metriques_performance(entreprises_mixtes)
        
        assert metriques_base['actives'] == 1  # Seule une entreprise a un budget > 0
        assert metriques_performance['survie_taux'] == 0.5  # 1/2 entreprises survivent


if __name__ == "__main__":
    # Instructions de lancement
    print("Tests unitaires pour EnterpriseMetricsService")
    print("Lancement : pytest tests/unit/test_enterprise_metrics.py -v")
    print("Couverture : pytest tests/unit/test_enterprise_metrics.py --cov=services.enterprise_metrics_service -v")
