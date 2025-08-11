#!/usr/bin/env python3
"""
Tests unitaires pour le service de métriques de produits
=======================================================

Tests complets du ProductMetricsService avec validation de tous les calculs
et métriques de produits.

Instructions de lancement :
- Test complet : pytest tests/unit/test_product_metrics.py -v
- Test spécifique : pytest tests/unit/test_product_metrics.py::TestProductMetricsService::test_calculer_metriques_produits -v
- Test avec couverture : pytest tests/unit/test_product_metrics.py --cov=services.product_metrics_service -v
"""

import pytest
import statistics
from unittest.mock import patch, MagicMock
from pydantic.main import _object_setattr

from models.models import Produit, TypeProduit, Fournisseur
from services.product_metrics_service import ProductMetricsService
from config.config import (
    PRODUCT_CRITIQUE_PRIX, PRODUCT_CRITIQUE_STOCK, PRODUCT_CRITIQUE_DEMANDE,
    PRODUCT_HISTORY_MAX_TOURS
)


class TestProductMetricsService:
    """Tests unitaires pour ProductMetricsService"""
    
    def setup_method(self):
        """Configuration initiale pour chaque test"""
        self.service = ProductMetricsService()
        
        # Données de test
        self.produits = [
            Produit(id=1, nom="Prod1", prix=100.0, type=TypeProduit.matiere_premiere, actif=True),
            Produit(id=2, nom="Prod2", prix=200.0, type=TypeProduit.produit_fini, actif=True),
            Produit(id=3, nom="Prod3", prix=150.0, type=TypeProduit.matiere_premiere, actif=False)
        ]
        
        self.fournisseurs = [
            Fournisseur(id=1, nom_entreprise="Four1", pays="France", continent="Europe", stock_produit={1: 50, 2: 30}),
            Fournisseur(id=2, nom_entreprise="Four2", pays="Allemagne", continent="Europe", stock_produit={1: 20, 3: 40}),
            Fournisseur(id=3, nom_entreprise="Four3", pays="Italie", continent="Europe", stock_produit={2: 25})
        ]
    
    def teardown_method(self):
        """Nettoyage après chaque test"""
        self.service.reset()
    
    def test_initialisation(self):
        """Test de l'initialisation du service"""
        assert self.service.historique_produits is not None
        assert self.service.demandes_par_produit == {}
        assert self.service.achats_par_produit == {}
        assert self.service.prix_historique == {}
        assert self.service.tour_actuel == 0
    
    def test_ajouter_tour(self):
        """Test de l'ajout d'un tour à l'historique"""
        self.service.ajouter_tour(self.produits, self.fournisseurs, 1)
        
        assert len(self.service.historique_produits) == 1
        assert self.service.tour_actuel == 1
        
        tour_data = self.service.historique_produits[0]
        assert tour_data['tour'] == 1
        assert tour_data['produits_count'] == 3
        assert len(tour_data['produits']) == 3
        
        # Vérifier les données d'un produit
        produit_data = tour_data['produits'][0]
        assert produit_data['id'] == 1
        assert produit_data['nom'] == "Prod1"
        assert produit_data['type'] == "matiere_premiere"
        assert produit_data['prix'] == 100.0
        assert produit_data['actif'] == True
        
        # Vérifier l'historique des prix
        assert len(self.service.prix_historique[1]) == 1
        assert self.service.prix_historique[1][0] == 100.0
    
    def test_enregistrer_achat(self):
        """Test de l'enregistrement d'un achat"""
        achat_data = {
            'entreprise': 'TestEnt',
            'fournisseur': 'TestFour',
            'quantite': 10,
            'prix_unitaire': 100.0,
            'montant_total': 1000.0,
            'strategie': 'moins_cher'
        }
        
        self.service.enregistrer_achat(1, achat_data)
        
        assert self.service.demandes_par_produit[1] == 1
        assert len(self.service.achats_par_produit[1]) == 1
        assert self.service.achats_par_produit[1][0] == achat_data
    
    def test_calculer_metriques_produits_avec_produits(self):
        """Test du calcul des métriques de produits avec des produits"""
        # Ajouter quelques achats
        self.service.enregistrer_achat(1, {'montant_total': 1000.0})
        self.service.enregistrer_achat(2, {'montant_total': 500.0})
        
        # Ajouter un tour
        self.service.ajouter_tour(self.produits, self.fournisseurs, 1)
        
        # Calculer les métriques
        metrics = self.service.calculer_metriques_produits(self.produits, self.fournisseurs)
        
        # Vérifications de base
        assert metrics['produits_total'] == 3
        assert metrics['produits_actifs'] == 2  # 2 produits actifs
        assert metrics['produits_count'] == 3
        assert metrics['total_demandes'] == 2
        
        # Vérifications des répartitions
        assert metrics['produits_par_type']['matiere_premiere'] == 2
        assert metrics['produits_par_type']['produit_fini'] == 1
        
        # Vérifications des métriques de performance
        assert metrics['produits_demande_moyenne'] == 2/3  # 2 demandes / 3 produits
        assert metrics['produits_prix_moyen'] == 150.0  # (100 + 200 + 150) / 3
        assert metrics['produits_prix_median'] == 150.0  # Médiane de [100, 150, 200]
    
    def test_calculer_metriques_produits_sans_produits(self):
        """Test du calcul des métriques de produits sans produits"""
        metrics = self.service.calculer_metriques_produits([], [])
        
        # Vérifications pour liste vide
        assert metrics['produits_total'] == 0
        assert metrics['produits_actifs'] == 0
        assert metrics['produits_count'] == 0
        assert metrics['total_demandes'] == 0
    
    def test_calculer_metriques_base(self):
        """Test du calcul des métriques de base"""
        metriques_base = self.service._calculer_metriques_base(self.produits, self.fournisseurs)
        
        assert metriques_base['total'] == 3
        assert metriques_base['actifs'] == 2
        
        # Vérifier les répartitions
        assert metriques_base['par_type']['matiere_premiere'] == 2
        assert metriques_base['par_type']['produit_fini'] == 1
        assert metriques_base['par_continent']['Europe'] == 3  # Tous les fournisseurs sont en Europe
        
        # Vérifier les prix
        assert metriques_base['prix_moyen'] == 150.0  # (100 + 200 + 150) / 3
        assert metriques_base['prix_median'] == 150.0  # Médiane de [100, 150, 200]
    
    def test_calculer_metriques_performance(self):
        """Test du calcul des métriques de performance"""
        # Ajouter des achats
        self.service.enregistrer_achat(1, {'montant_total': 1000.0})
        self.service.enregistrer_achat(2, {'montant_total': 500.0})
        self.service.enregistrer_achat(2, {'montant_total': 300.0})
        
        metriques_performance = self.service._calculer_metriques_performance(self.produits, self.fournisseurs)
        
        # Demande moyenne
        assert metriques_performance['demande_moyenne'] == 1  # (1 + 2 + 0) / 3 = 1
        
        # Offre moyenne (stock total)
        # Prod1: 50 + 20 = 70, Prod2: 30 + 25 = 55, Prod3: 40
        # Moyenne: (70 + 55 + 40) / 3 = 55
        assert metriques_performance['offre_moyenne'] == 55.0
        
        # Disponibilité (produits avec stock > 0)
        assert metriques_performance['disponibilite'] == 1.0  # Tous les produits ont du stock
    
    def test_calculer_metriques_comportement(self):
        """Test du calcul des métriques de comportement"""
        # Ajouter des achats
        self.service.enregistrer_achat(1, {'montant_total': 1000.0})
        self.service.enregistrer_achat(2, {'montant_total': 500.0})
        
        # Ajouter plusieurs tours pour l'historique des prix
        self.service.ajouter_tour(self.produits, self.fournisseurs, 1)
        
        # Modifier les prix pour le tour suivant
        self.produits[0].prix = 110.0
        self.produits[1].prix = 210.0
        self.service.ajouter_tour(self.produits, self.fournisseurs, 2)
        
        metriques_comportement = self.service._calculer_metriques_comportement(self.produits)
        
        # Volatilité des prix (devrait être > 0 avec des prix différents)
        assert metriques_comportement['volatilite_prix'] >= 0.0
        
        # Tendance des prix (devrait être positive avec des prix qui augmentent)
        assert metriques_comportement['tendance_prix'] >= 0.0
        
        # Compétitivité (basée sur la demande / prix)
        assert metriques_comportement['competitivite'] >= 0.0
    
    def test_calculer_alertes_produits(self):
        """Test du calcul des alertes de produits"""
        # Créer des produits avec différents niveaux critiques
        produits_critiques = [
            Produit(id=1, nom="Critique1", prix=0, type=TypeProduit.matiere_premiere, actif=True),  # Prix critique
            Produit(id=2, nom="Critique2", prix=100.0, type=TypeProduit.matiere_premiere, actif=True)  # Normal
        ]
        
        fournisseurs_critiques = [
            Fournisseur(id=1, nom_entreprise="Four1", pays="France", continent="Europe", stock_produit={1: 3, 2: 50})  # Stock critique pour Prod1
        ]
        
        alertes = self.service._calculer_alertes_produits(produits_critiques, fournisseurs_critiques)
        
        assert alertes['produits_prix_critique'] == 1  # 1 produit avec prix = 0
        assert alertes['produits_stock_critique'] == 1  # 1 produit avec stock ≤ 5
        assert alertes['produits_demande_critique'] == 2  # 0 demande pour les deux produits
    
    def test_historique_max_tours(self):
        """Test de la limite de l'historique"""
        # Ajouter plus de tours que la limite
        for i in range(PRODUCT_HISTORY_MAX_TOURS + 10):
            self.service.ajouter_tour(self.produits, self.fournisseurs, i)
        
        # L'historique ne devrait pas dépasser la limite
        assert len(self.service.historique_produits) == PRODUCT_HISTORY_MAX_TOURS
        
        # Le premier tour devrait être le plus ancien
        assert self.service.historique_produits[0]['tour'] == 10  # Les 10 premiers ont été supprimés
    
    def test_cache_lru(self):
        """Test du cache LRU pour les calculs complexes"""
        produits_ids = tuple(produit.id for produit in self.produits)
        
        # Premier appel (pas en cache)
        stats1 = self.service._calculer_statistiques_produits(produits_ids)
        
        # Deuxième appel (en cache)
        stats2 = self.service._calculer_statistiques_produits(produits_ids)
        
        # Les résultats doivent être identiques
        assert stats1 == stats2
    
    def test_reset(self):
        """Test de la réinitialisation du service"""
        # Ajouter des données
        self.service.enregistrer_achat(1, {'montant_total': 1000.0})
        self.service.ajouter_tour(self.produits, self.fournisseurs, 1)
        
        # Réinitialiser
        self.service.reset()
        
        # Vérifier que tout est remis à zéro
        assert self.service.demandes_par_produit == {}
        assert self.service.achats_par_produit == {}
        assert self.service.prix_historique == {}
        assert self.service.tour_actuel == 0
        assert len(self.service.historique_produits) == 0
    
    def test_metriques_vides(self):
        """Test des métriques vides"""
        metrics = self.service._metriques_vides()
        
        # Vérifier que toutes les métriques sont à 0
        assert metrics['produits_total'] == 0
        assert metrics['produits_actifs'] == 0
        assert metrics['produits_count'] == 0
        assert metrics['total_demandes'] == 0
    
    def test_integration_complete(self):
        """Test d'intégration complète"""
        # Simuler une session complète
        for tour in range(1, 4):
            # Ajouter des achats
            self.service.enregistrer_achat(1, {'montant_total': 1000.0 * tour})
            self.service.enregistrer_achat(2, {'montant_total': 500.0 * tour})
            
            # Ajouter le tour
            self.service.ajouter_tour(self.produits, self.fournisseurs, tour)
            
            # Calculer les métriques
            metrics = self.service.calculer_metriques_produits(self.produits, self.fournisseurs)
            
            # Vérifications de base
            assert metrics['produits_total'] == 3
            assert metrics['produits_count'] == 3
            assert metrics['total_demandes'] == tour * 2
        
        # Vérifier l'historique
        assert len(self.service.historique_produits) == 3
        
        # Vérifier les demandes cumulées
        assert self.service.demandes_par_produit[1] == 3
        assert self.service.demandes_par_produit[2] == 3
        assert self.service.demandes_par_produit[3] == 0
    
    def test_produits_avec_prix_variables(self):
        """Test avec des produits ayant des prix variables"""
        # Ajouter plusieurs tours avec des prix différents
        for tour in range(1, 4):
            # Modifier les prix
            self.produits[0].prix = 100.0 + tour * 10
            self.produits[1].prix = 200.0 + tour * 5
            
            self.service.ajouter_tour(self.produits, self.fournisseurs, tour)
        
        metriques_comportement = self.service._calculer_metriques_comportement(self.produits)
        
        # Volatilité des prix devrait être > 0
        assert metriques_comportement['volatilite_prix'] > 0.0
        
        # Tendance des prix devrait être positive
        assert metriques_comportement['tendance_prix'] > 0.0
    
    def test_produits_inactifs(self):
        """Test avec des produits inactifs"""
        produits_mixtes = [
            Produit(id=1, nom="Actif", prix=100.0, type=TypeProduit.matiere_premiere, actif=True),
            Produit(id=2, nom="Inactif", prix=200.0, type=TypeProduit.produit_fini, actif=False)
        ]
        
        metriques_base = self.service._calculer_metriques_base(produits_mixtes, self.fournisseurs)
        
        assert metriques_base['actifs'] == 1  # Seulement un produit actif
        assert metriques_base['total'] == 2  # Deux produits au total


if __name__ == "__main__":
    # Instructions de lancement
    print("Tests unitaires pour ProductMetricsService")
    print("Lancement : pytest tests/unit/test_product_metrics.py -v")
    print("Couverture : pytest tests/unit/test_product_metrics.py --cov=services.product_metrics_service -v")
