#!/usr/bin/env python3
"""
Tests unitaires pour le service de métriques de fournisseurs
===========================================================

Tests complets du SupplierMetricsService avec validation de tous les calculs
et métriques de fournisseurs.

Instructions de lancement :
- Test complet : pytest tests/unit/test_supplier_metrics.py -v
- Test spécifique : pytest tests/unit/test_supplier_metrics.py::TestSupplierMetricsService::test_calculer_metriques_fournisseurs -v
- Test avec couverture : pytest tests/unit/test_supplier_metrics.py --cov=services.supplier_metrics_service -v
"""

import pytest
import statistics
from unittest.mock import patch, MagicMock
from pydantic.main import _object_setattr

from models.models import Fournisseur, Produit, TypeProduit
from services.supplier_metrics_service import SupplierMetricsService
from config.config import (
    SUPPLIER_CRITIQUE_STOCK, SUPPLIER_CRITIQUE_VENTES, SUPPLIER_CRITIQUE_PRODUITS,
    SUPPLIER_HISTORY_MAX_TOURS
)


class TestSupplierMetricsService:
    """Tests unitaires pour SupplierMetricsService"""
    
    def setup_method(self):
        """Configuration initiale pour chaque test"""
        self.service = SupplierMetricsService()
        
        # Données de test
        self.fournisseurs = [
            Fournisseur(id=1, nom_entreprise="Four1", pays="France", continent="Europe", stock_produit={1: 50, 2: 30}),
            Fournisseur(id=2, nom_entreprise="Four2", pays="Allemagne", continent="Europe", stock_produit={1: 20, 3: 40}),
            Fournisseur(id=3, nom_entreprise="Four3", pays="Italie", continent="Europe", stock_produit={2: 25})
        ]
        
        self.produits = [
            Produit(id=1, nom="Prod1", prix=100.0, type=TypeProduit.matiere_premiere, actif=True),
            Produit(id=2, nom="Prod2", prix=200.0, type=TypeProduit.produit_fini, actif=True),
            Produit(id=3, nom="Prod3", prix=150.0, type=TypeProduit.matiere_premiere, actif=False)
        ]
    
    def teardown_method(self):
        """Nettoyage après chaque test"""
        self.service.reset()
    
    def test_initialisation(self):
        """Test de l'initialisation du service"""
        assert self.service.historique_fournisseurs is not None
        assert self.service.ventes_par_fournisseur == {}
        assert self.service.transactions_par_fournisseur == {}
        assert self.service.prix_historique == {}
        assert self.service.tour_actuel == 0
    
    def test_ajouter_tour(self):
        """Test de l'ajout d'un tour à l'historique"""
        self.service.ajouter_tour(self.fournisseurs, self.produits, 1)
        
        assert len(self.service.historique_fournisseurs) == 1
        assert self.service.tour_actuel == 1
        
        tour_data = self.service.historique_fournisseurs[0]
        assert tour_data['tour'] == 1
        assert tour_data['fournisseurs_count'] == 3
        assert len(tour_data['fournisseurs']) == 3
        
        # Vérifier les données d'un fournisseur
        fournisseur_data = tour_data['fournisseurs'][0]
        assert fournisseur_data['id'] == 1
        assert fournisseur_data['nom_entreprise'] == "Four1"
        assert fournisseur_data['pays'] == "France"
        assert fournisseur_data['continent'] == "Europe"
        assert fournisseur_data['produits_count'] == 2
        assert fournisseur_data['stock_total'] == 80  # 50 + 30
    
    def test_enregistrer_vente(self):
        """Test de l'enregistrement d'une vente"""
        vente_data = {
            'entreprise': 'TestEnt',
            'produit': 'TestProd',
            'quantite': 10,
            'prix_unitaire': 100.0,
            'montant_total': 1000.0,
            'strategie': 'moins_cher'
        }
        
        self.service.enregistrer_vente(1, vente_data)
        
        assert self.service.ventes_par_fournisseur[1] == 1
        assert len(self.service.transactions_par_fournisseur[1]) == 1
        assert self.service.transactions_par_fournisseur[1][0] == vente_data
    
    def test_calculer_metriques_fournisseurs_avec_fournisseurs(self):
        """Test du calcul des métriques de fournisseurs avec des fournisseurs"""
        # Ajouter quelques ventes
        self.service.enregistrer_vente(1, {'montant_total': 1000.0})
        self.service.enregistrer_vente(2, {'montant_total': 500.0})
        
        # Ajouter un tour
        self.service.ajouter_tour(self.fournisseurs, self.produits, 1)
        
        # Calculer les métriques
        metrics = self.service.calculer_metriques_fournisseurs(self.fournisseurs, self.produits)
        
        # Vérifications de base
        assert metrics['fournisseurs_total'] == 3
        assert metrics['fournisseurs_actifs'] == 3  # Tous ont du stock
        assert metrics['fournisseurs_count'] == 3
        assert metrics['total_ventes'] == 2
        
        # Vérifications des répartitions
        assert metrics['fournisseurs_par_pays']['France'] == 1
        assert metrics['fournisseurs_par_pays']['Allemagne'] == 1
        assert metrics['fournisseurs_par_pays']['Italie'] == 1
        assert metrics['fournisseurs_par_continent']['Europe'] == 3
        
        # Vérifications des métriques de performance
        assert metrics['fournisseurs_ventes_moyennes'] == 2/3  # 2 ventes / 3 fournisseurs
        assert abs(metrics['fournisseurs_stock_moyen'] - 55.0) < 0.1  # (80 + 60 + 25) / 3 = 55
        assert abs(metrics['fournisseurs_produits_moyen'] - 1.67) < 0.1  # (2 + 2 + 1) / 3 ≈ 1.67
    
    def test_calculer_metriques_fournisseurs_sans_fournisseurs(self):
        """Test du calcul des métriques de fournisseurs sans fournisseurs"""
        metrics = self.service.calculer_metriques_fournisseurs([], [])
        
        # Vérifications pour liste vide
        assert metrics['fournisseurs_total'] == 0
        assert metrics['fournisseurs_actifs'] == 0
        assert metrics['fournisseurs_count'] == 0
        assert metrics['total_ventes'] == 0
    
    def test_calculer_metriques_base(self):
        """Test du calcul des métriques de base"""
        metriques_base = self.service._calculer_metriques_base(self.fournisseurs)
        
        assert metriques_base['total'] == 3
        assert metriques_base['actifs'] == 3  # Tous ont du stock
        
        # Vérifier les répartitions
        assert metriques_base['par_pays']['France'] == 1
        assert metriques_base['par_pays']['Allemagne'] == 1
        assert metriques_base['par_pays']['Italie'] == 1
        assert metriques_base['par_continent']['Europe'] == 3
        
        # Vérifier les moyennes
        assert abs(metriques_base['stock_moyen'] - 55.0) < 0.1  # (80 + 60 + 25) / 3 = 55
        assert abs(metriques_base['produits_moyen'] - 1.67) < 0.1  # (2 + 2 + 1) / 3 ≈ 1.67
    
    def test_calculer_metriques_performance(self):
        """Test du calcul des métriques de performance"""
        # Ajouter des ventes
        self.service.enregistrer_vente(1, {'montant_total': 1000.0})
        self.service.enregistrer_vente(2, {'montant_total': 500.0})
        self.service.enregistrer_vente(2, {'montant_total': 300.0})
        
        metriques_performance = self.service._calculer_metriques_performance(self.fournisseurs)
        
        # Ventes moyennes
        assert metriques_performance['ventes_moyennes'] == 1  # (1 + 2 + 0) / 3 = 1
        
        # Disponibilité (fournisseurs avec stock > 0)
        assert metriques_performance['disponibilite'] == 1.0  # Tous les fournisseurs ont du stock
        
        # Rotation de stock (ventes / stock total)
        # Four1: 1/80 = 0.0125, Four2: 2/60 = 0.0333, Four3: 0/25 = 0
        # Moyenne: (0.0125 + 0.0333 + 0) / 3 ≈ 0.015
        assert metriques_performance['rotation_stock'] > 0.0
    
    def test_calculer_metriques_comportement(self):
        """Test du calcul des métriques de comportement"""
        # Ajouter des ventes
        self.service.enregistrer_vente(1, {'montant_total': 1000.0})
        self.service.enregistrer_vente(2, {'montant_total': 500.0})
        
        metriques_comportement = self.service._calculer_metriques_comportement(self.fournisseurs)
        
        # Volatilité et tendance des prix (pour l'instant, valeurs par défaut)
        assert metriques_comportement['volatilite_prix'] == 0.0
        assert metriques_comportement['tendance_prix'] == 0.0
        
        # Compétitivité (basée sur les ventes et la diversité)
        assert metriques_comportement['competitivite'] >= 0.0
        
        # Résilience (capacité à maintenir le stock)
        assert metriques_comportement['resilience'] >= 0.0
    
    def test_calculer_alertes_fournisseurs(self):
        """Test du calcul des alertes de fournisseurs"""
        # Créer des fournisseurs avec différents niveaux critiques
        fournisseurs_critiques = [
            Fournisseur(id=1, nom_entreprise="Critique1", pays="France", continent="Europe", stock_produit={1: 5}),  # Stock critique
            Fournisseur(id=2, nom_entreprise="Critique2", pays="Allemagne", continent="Europe", stock_produit={1: 50})  # Normal
        ]
        
        alertes = self.service._calculer_alertes_fournisseurs(fournisseurs_critiques)
        
        assert alertes['fournisseurs_stock_critique'] == 1  # 1 fournisseur avec stock ≤ 10
        assert alertes['fournisseurs_ventes_critique'] == 2  # 0 ventes pour les deux fournisseurs
        assert alertes['fournisseurs_produits_critique'] == 2  # Tous ont 1 produit (≤ 1)
    
    def test_historique_max_tours(self):
        """Test de la limite de l'historique"""
        # Ajouter plus de tours que la limite
        for i in range(SUPPLIER_HISTORY_MAX_TOURS + 10):
            self.service.ajouter_tour(self.fournisseurs, self.produits, i)
        
        # L'historique ne devrait pas dépasser la limite
        assert len(self.service.historique_fournisseurs) == SUPPLIER_HISTORY_MAX_TOURS
        
        # Le premier tour devrait être le plus ancien
        assert self.service.historique_fournisseurs[0]['tour'] == 10  # Les 10 premiers ont été supprimés
    
    def test_cache_lru(self):
        """Test du cache LRU pour les calculs complexes"""
        fournisseurs_ids = tuple(fournisseur.id for fournisseur in self.fournisseurs)
        
        # Premier appel (pas en cache)
        stats1 = self.service._calculer_statistiques_fournisseurs(fournisseurs_ids)
        
        # Deuxième appel (en cache)
        stats2 = self.service._calculer_statistiques_fournisseurs(fournisseurs_ids)
        
        # Les résultats doivent être identiques
        assert stats1 == stats2
    
    def test_reset(self):
        """Test de la réinitialisation du service"""
        # Ajouter des données
        self.service.enregistrer_vente(1, {'montant_total': 1000.0})
        self.service.ajouter_tour(self.fournisseurs, self.produits, 1)
        
        # Réinitialiser
        self.service.reset()
        
        # Vérifier que tout est remis à zéro
        assert self.service.ventes_par_fournisseur == {}
        assert self.service.transactions_par_fournisseur == {}
        assert self.service.prix_historique == {}
        assert self.service.tour_actuel == 0
        assert len(self.service.historique_fournisseurs) == 0
    
    def test_metriques_vides(self):
        """Test des métriques vides"""
        metrics = self.service._metriques_vides()
        
        # Vérifier que toutes les métriques sont à 0
        assert metrics['fournisseurs_total'] == 0
        assert metrics['fournisseurs_actifs'] == 0
        assert metrics['fournisseurs_count'] == 0
        assert metrics['total_ventes'] == 0
    
    def test_integration_complete(self):
        """Test d'intégration complète"""
        # Simuler une session complète
        for tour in range(1, 4):
            # Ajouter des ventes
            self.service.enregistrer_vente(1, {'montant_total': 1000.0 * tour})
            self.service.enregistrer_vente(2, {'montant_total': 500.0 * tour})
            
            # Ajouter le tour
            self.service.ajouter_tour(self.fournisseurs, self.produits, tour)
            
            # Calculer les métriques
            metrics = self.service.calculer_metriques_fournisseurs(self.fournisseurs, self.produits)
            
            # Vérifications de base
            assert metrics['fournisseurs_total'] == 3
            assert metrics['fournisseurs_count'] == 3
            assert metrics['total_ventes'] == tour * 2
        
        # Vérifier l'historique
        assert len(self.service.historique_fournisseurs) == 3
        
        # Vérifier les ventes cumulées
        assert self.service.ventes_par_fournisseur[1] == 3
        assert self.service.ventes_par_fournisseur[2] == 3
        assert self.service.ventes_par_fournisseur[3] == 0
    
    def test_fournisseurs_avec_stock_variable(self):
        """Test avec des fournisseurs ayant des stocks variables"""
        # Créer des fournisseurs avec des stocks différents
        fournisseurs_variables = [
            Fournisseur(id=1, nom_entreprise="Stock1", pays="France", continent="Europe", stock_produit={1: 100}),
            Fournisseur(id=2, nom_entreprise="Stock2", pays="Allemagne", continent="Europe", stock_produit={1: 50}),
            Fournisseur(id=3, nom_entreprise="Stock3", pays="Italie", continent="Europe", stock_produit={1: 25})
        ]
        
        metriques_base = self.service._calculer_metriques_base(fournisseurs_variables)
        
        # Stock moyen devrait être (100 + 50 + 25) / 3 = 58.33
        assert abs(metriques_base['stock_moyen'] - 58.33) < 0.1
        
        # Tous devraient être actifs
        assert metriques_base['actifs'] == 3
    
    def test_fournisseurs_inactifs(self):
        """Test avec des fournisseurs inactifs (sans stock)"""
        fournisseurs_mixtes = [
            Fournisseur(id=1, nom_entreprise="Actif", pays="France", continent="Europe", stock_produit={1: 50}),
            Fournisseur(id=2, nom_entreprise="Inactif", pays="Allemagne", continent="Europe", stock_produit={})
        ]
        
        metriques_base = self.service._calculer_metriques_base(fournisseurs_mixtes)
        
        assert metriques_base['actifs'] == 1  # Seulement un fournisseur actif
        assert metriques_base['total'] == 2  # Deux fournisseurs au total
        assert metriques_base['stock_moyen'] == 25.0  # (50 + 0) / 2 = 25


if __name__ == "__main__":
    # Instructions de lancement
    print("Tests unitaires pour SupplierMetricsService")
    print("Lancement : pytest tests/unit/test_supplier_metrics.py -v")
    print("Couverture : pytest tests/unit/test_supplier_metrics.py --cov=services.supplier_metrics_service -v")
