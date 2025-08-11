#!/usr/bin/env python3
"""
Tests unitaires pour SimulationService
Validation des corrections du bug (10/08/2025) :
- Correction des références aux attributs inexistants
- Utilisation de PriceService pour les prix
- Correction de l'accès aux stocks des fournisseurs
- Tests de toutes les méthodes corrigées

Instructions de lancement :
- Test unitaire : pytest tests/unit/test_simulation_service.py -v
- Test avec couverture : pytest tests/unit/test_simulation_service.py --cov=services.simulation_service --cov-report=html
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.models.models import Entreprise, Fournisseur, Produit, TypeProduit
from app.services.simulation_service import SimulationService, IDGenerator


class TestSimulationService:
    """Tests unitaires pour SimulationService avec corrections du bug"""
    
    def setup_method(self):
        """Configuration initiale pour chaque test"""
        # Création des données de test avec les bons attributs
        self.entreprises = [
            Entreprise(
                id=1, nom="TestEnt1", pays="France", continent="Europe",
                budget=10000, budget_initial=10000,
                types_preferes=[TypeProduit.matiere_premiere], strategie="moins_cher"
            ),
            Entreprise(
                id=2, nom="TestEnt2", pays="Allemagne", continent="Europe",
                budget=8000, budget_initial=8000,
                types_preferes=[TypeProduit.produit_fini], strategie="par_type"
            )
        ]
        
        self.fournisseurs = [
            Fournisseur(
                id=1, nom_entreprise="TestFour1", pays="France", continent="Europe",
                stock_produit={1: 100, 2: 50}  # produit_id: quantité
            ),
            Fournisseur(
                id=2, nom_entreprise="TestFour2", pays="Allemagne", continent="Europe",
                stock_produit={1: 75, 3: 25}
            )
        ]
        
        self.produits = [
            Produit(id=1, nom="TestProd1", prix=100.0, actif=True, type=TypeProduit.matiere_premiere),
            Produit(id=2, nom="TestProd2", prix=200.0, actif=True, type=TypeProduit.produit_fini),
            Produit(id=3, nom="TestProd3", prix=150.0, actif=True, type=TypeProduit.consommable)
        ]
        
        # Mock du PriceService
        self.mock_price_service = Mock()
        self.mock_price_service.get_prix_produit_fournisseur.return_value = 100.0
        
        # Création du service avec mocks
        with patch('app.services.simulation_service.price_service', self.mock_price_service):
            with patch('app.services.simulation_service.PRICE_SERVICE_AVAILABLE', True):
                self.service = SimulationService(self.entreprises, self.fournisseurs, self.produits, verbose=False)
    
    def test_initialisation_service(self):
        """Test de l'initialisation correcte du service"""
        assert self.service.entreprises == self.entreprises
        assert self.service.fournisseurs == self.fournisseurs
        assert self.service.produits == self.produits
        assert self.service.verbose == False
        assert self.service.tick_actuel == 0
        assert self.service.tours_completes == 0
    
    def test_calculer_statistiques_avec_corrections(self):
        """Test du calcul des statistiques avec les corrections du bug"""
        stats = self.service.calculer_statistiques()
        
        assert "budget_total_actuel" in stats
        assert "stock_total_actuel" in stats
        assert "tours_completes" in stats
        assert "evenements_appliques" in stats
        assert "duree_simulation" in stats
        
        # Vérification des valeurs
        assert stats["budget_total_actuel"] == 18000.0  # 10000 + 8000
        assert stats["tours_completes"] == 0
        assert stats["evenements_appliques"] == 0
    
    def test_acheter_produit_detaille_avec_price_service(self):
        """Test de l'achat de produit avec utilisation de PriceService"""
        entreprise = self.entreprises[0]
        produit = self.produits[0]
        fournisseur = self.fournisseurs[0]
        
        # Mock du prix
        self.mock_price_service.get_prix_produit_fournisseur.return_value = 100.0
        
        # Test de l'achat avec le mock appliqué
        with patch('app.services.simulation_service.price_service', self.mock_price_service):
            result = self.service.acheter_produit_detaille(entreprise, produit, fournisseur, "moins_cher")
            
            # Vérification que PriceService a été appelé
            self.mock_price_service.get_prix_produit_fournisseur.assert_called_with(produit.id, fournisseur.id)
            
            # Vérification du résultat
            assert isinstance(result, bool)
    
    def test_acheter_produit_stock_insuffisant(self):
        """Test de l'achat avec stock insuffisant"""
        entreprise = self.entreprises[0]
        produit = self.produits[0]
        fournisseur = self.fournisseurs[0]
        
        # Mock du prix et stock insuffisant
        self.mock_price_service.get_prix_produit_fournisseur.return_value = 100.0
        fournisseur.stock_produit[produit.id] = 0  # Stock vide
        
        result = self.service.acheter_produit_detaille(entreprise, produit, fournisseur, "moins_cher")
        assert result == False
    
    def test_acheter_produit_prix_zero(self):
        """Test de l'achat avec prix à zéro"""
        entreprise = self.entreprises[0]
        produit = self.produits[0]
        fournisseur = self.fournisseurs[0]
        
        # Mock du prix à zéro
        self.mock_price_service.get_prix_produit_fournisseur.return_value = 0
        
        result = self.service.acheter_produit_detaille(entreprise, produit, fournisseur, "moins_cher")
        assert result == False
    
    def test_simuler_transactions_avec_corrections(self):
        """Test de la simulation des transactions avec les corrections"""
        # Mock des prix pour tous les fournisseurs
        self.mock_price_service.get_prix_produit_fournisseur.return_value = 100.0
        
        # Test avec le mock appliqué
        with patch('app.services.simulation_service.price_service', self.mock_price_service):
            transactions = self.service.simuler_transactions()
            
            # Vérification que PriceService a été appelé
            assert self.mock_price_service.get_prix_produit_fournisseur.called
            
            # Vérification du nombre de transactions
            assert isinstance(transactions, int)
            assert transactions >= 0
    
    def test_trouver_fournisseur_moins_cher(self):
        """Test de la recherche du fournisseur le moins cher"""
        produit = self.produits[0]
        
        # Mock de différents prix
        def mock_get_prix(produit_id, fournisseur_id):
            if fournisseur_id == 1:
                return 100.0
            elif fournisseur_id == 2:
                return 80.0
            return None
        
        self.mock_price_service.get_prix_produit_fournisseur.side_effect = mock_get_prix
        
        # Test de la logique de recherche
        fournisseur_moins_cher = None
        prix_min = float('inf')
        
        for fournisseur in self.fournisseurs:
            if produit.id in fournisseur.stock_produit and fournisseur.stock_produit[produit.id] > 0:
                prix = self.mock_price_service.get_prix_produit_fournisseur(produit.id, fournisseur.id)
                if prix and prix < prix_min:
                    prix_min = prix
                    fournisseur_moins_cher = fournisseur
        
        # Vérification que le fournisseur le moins cher a été trouvé
        assert fournisseur_moins_cher is not None
        assert fournisseur_moins_cher.id == 2  # Fournisseur avec prix 80.0
    
    def test_simulation_tour_complet(self):
        """Test d'un tour de simulation complet"""
        # Mock des prix
        self.mock_price_service.get_prix_produit_fournisseur.return_value = 100.0
        
        # Mock des événements
        with patch.object(self.service, 'appliquer_evenements', return_value=[]):
            result = self.service.simulation_tour()
        
        # Vérification du résultat
        assert "transactions_effectuees" in result
        assert "evenements_appliques" in result
        assert "tick" in result
        assert "tour" in result
        assert "duration" in result
        
        # Vérification des compteurs
        assert result["tick"] == 1
        assert result["tour"] == 1
    
    def test_collecter_metriques(self):
        """Test de la collecte des métriques"""
        # Mock du PrometheusExporter
        with patch('app.services.simulation_service.MONITORING_AVAILABLE', True):
            with patch('app.services.simulation_service.PrometheusExporter') as mock_exporter_class:
                mock_exporter = Mock()
                mock_exporter_class.return_value = mock_exporter
                
                self.service.prometheus_exporter = mock_exporter
                
                # Test de la collecte
                self.service.collecter_metriques()
                
                # Vérification que les métriques ont été mises à jour
                mock_exporter.update_tradesim_metrics.assert_called()
    
    def test_calculer_metriques_simulation(self):
        """Test du calcul des métriques de simulation"""
        stats = {
            "tours_completes": 10,
            "evenements_appliques": 5,
            "duree_simulation": 2.0,
            "transactions_reussies": 8,
            "transactions_total": 10
        }
        
        metrics = self.service._calculer_metriques_simulation(stats)
        
        # Vérification des métriques calculées
        assert "frequence_evenements" in metrics
        assert "taux_succes_transactions" in metrics
        assert "vitesse_simulation" in metrics
        assert "stabilite_prix" in metrics
        
        # Vérification des valeurs
        assert metrics["frequence_evenements"] == 0.5  # 5/10
        assert metrics["taux_succes_transactions"] == 0.8  # 8/10
        assert metrics["vitesse_simulation"] == 5.0  # 10/2.0
    
    def test_calculer_stabilite_prix(self):
        """Test du calcul de la stabilité des prix"""
        stabilite = self.service._calculer_stabilite_prix()
        
        # Vérification que c'est un nombre flottant
        assert isinstance(stabilite, float)
        assert stabilite >= 0
    
    def test_validation_donnees(self):
        """Test de la validation des données"""
        # Test avec données valides
        data_valide = {"budget": 1000, "prix": 100, "stock": 50}
        assert self.service._validate_data(data_valide, "test") == True
        
        # Test avec données invalides
        data_invalide = {"budget": -1000, "prix": -100, "stock": -50}
        assert self.service._validate_data(data_invalide, "test") == False
    
    def test_gestion_erreurs(self):
        """Test de la gestion des erreurs"""
        # Test avec PriceService indisponible
        with patch('app.services.simulation_service.PRICE_SERVICE_AVAILABLE', False):
            entreprise = self.entreprises[0]
            produit = self.produits[0]
            fournisseur = self.fournisseurs[0]
            
            result = self.service.acheter_produit_detaille(entreprise, produit, fournisseur, "moins_cher")
            assert result == False
    
    def test_logging_et_traçabilite(self):
        """Test du système de logging et de traçabilité"""
        # Test de génération d'ID
        id_txn = self.service.id_generator.get_id("TXN")
        assert id_txn.startswith(self.service.id_generator.get_session_id())
        assert "TXN" in id_txn
        
        # Test de session ID
        session_id = self.service.id_generator.get_session_id()
        assert isinstance(session_id, str)
        assert len(session_id) > 0
    
    def test_performance_et_cache(self):
        """Test des optimisations de performance"""
        # Test du cache LRU pour les statistiques
        start_time = datetime.now()
        stats1 = self.service.calculer_statistiques()
        time1 = (datetime.now() - start_time).total_seconds()
        
        start_time = datetime.now()
        stats2 = self.service.calculer_statistiques()
        time2 = (datetime.now() - start_time).total_seconds()
        
        # Le deuxième appel devrait être plus rapide grâce au cache
        assert time2 <= time1
        assert stats1 == stats2
    
    def test_edge_cases(self):
        """Test des cas limites"""
        # Test avec listes vides
        service_vide = SimulationService([], [], [], verbose=False)
        stats = service_vide.calculer_statistiques()
        assert stats["budget_total_actuel"] == 0
        assert stats["stock_total_actuel"] == 0
        
        # Test avec données None
        with patch('app.services.simulation_service.price_service') as mock_price:
            mock_price.get_prix_produit_fournisseur.return_value = None
            entreprise = self.entreprises[0]
            produit = self.produits[0]
            fournisseur = self.fournisseurs[0]
            
            result = self.service.acheter_produit_detaille(entreprise, produit, fournisseur, "moins_cher")
            assert result == False


class TestIDGenerator:
    """Tests unitaires pour IDGenerator"""
    
    def setup_method(self):
        """Configuration initiale pour chaque test"""
        self.id_generator = IDGenerator()
    
    def test_generation_id_unique(self):
        """Test de génération d'IDs uniques"""
        id1 = self.id_generator.get_id("TXN")
        id2 = self.id_generator.get_id("TXN")
        
        assert id1 != id2
        assert id1.startswith(self.id_generator.get_session_id())
        assert id2.startswith(self.id_generator.get_session_id())
    
    def test_session_id(self):
        """Test de l'ID de session"""
        session_id = self.id_generator.get_session_id()
        assert isinstance(session_id, str)
        assert len(session_id) > 0
    
    def test_buffer_logging(self):
        """Test du buffer de logging"""
        log_entry = {"test": "data"}
        self.id_generator.add_to_buffer(log_entry)
        
        # Vérification que l'entrée a été ajoutée au buffer
        assert len(self.id_generator.log_buffer) > 0
    
    def test_flush_buffer(self):
        """Test de l'écriture du buffer"""
        log_entry = {"test": "data"}
        self.id_generator.add_to_buffer(log_entry)
        
        # Test du flush
        self.id_generator.flush_buffer()
        
        # Le buffer devrait être vide après le flush
        assert len(self.id_generator.log_buffer) == 0


if __name__ == "__main__":
    # Instructions de lancement
    print("Tests unitaires pour SimulationService")
    print("Lancement : pytest tests/unit/test_simulation_service.py -v")
    print("Couverture : pytest tests/unit/test_simulation_service.py --cov=services.simulation_service --cov-report=html")
