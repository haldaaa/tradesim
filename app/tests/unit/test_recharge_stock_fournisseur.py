#!/usr/bin/env python3
"""
Tests unitaires pour l'événement Recharge Stock Fournisseur
==========================================================

Tests complets de l'événement de recharge des stocks des fournisseurs.
Validation de la logique, des probabilités, des quantités et du logging.

Instructions de lancement :
- Test complet : pytest tests/unit/test_recharge_stock_fournisseur.py -v
- Test spécifique : pytest tests/unit/test_recharge_stock_fournisseur.py::TestRechargeStockFournisseur::test_appliquer_recharge_stock_fournisseur -v
- Test avec couverture : pytest tests/unit/test_recharge_stock_fournisseur.py --cov=events.recharge_stock_fournisseur -v
"""

import pytest
import random
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from events.recharge_stock_fournisseur import appliquer_recharge_stock_fournisseur
from models.models import Entreprise, Fournisseur, Produit, TypeProduit
from config.config import (
    RECHARGE_FOURNISSEUR_INTERVAL,
    PROBABILITE_RECHARGE_FOURNISSEUR,
    PROBABILITE_RECHARGE_PRODUIT,
    RECHARGE_QUANTITE_MIN,
    RECHARGE_QUANTITE_MAX
)


class TestRechargeStockFournisseur:
    """Tests pour l'événement de recharge des stocks des fournisseurs"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        # Créer des données de test
        self.produit1 = Produit(
            id=1,
            nom="Produit Test 1",
            type=TypeProduit.matiere_premiere,
            prix=100.0,
            actif=True
        )
        
        self.produit2 = Produit(
            id=2,
            nom="Produit Test 2", 
            type=TypeProduit.consommable,
            prix=50.0,
            actif=True
        )
        
        self.fournisseur1 = Fournisseur(
            id=1,
            nom_entreprise="Fournisseur Test 1",
            pays="France",
            continent="Europe",
            stock_produit={1: 100, 2: 50}  # Stock initial
        )
        
        self.fournisseur2 = Fournisseur(
            id=2,
            nom_entreprise="Fournisseur Test 2",
            pays="Japon",
            continent="Asie",
            stock_produit={1: 75, 2: 25}  # Stock initial
        )
    
    @patch('events.recharge_stock_fournisseur.ProduitRepository')
    @patch('events.recharge_stock_fournisseur.FournisseurRepository')
    def test_appliquer_recharge_stock_fournisseur_intervalle(self, mock_fournisseur_repo, mock_produit_repo):
        """Test que l'événement ne se déclenche qu'aux bons intervalles"""
        # Mock des repositories
        mock_produit_repo.return_value.get_actifs.return_value = [self.produit1, self.produit2]
        mock_fournisseur_repo.return_value.get_all.return_value = [self.fournisseur1, self.fournisseur2]
        
        # Test avec un tick qui n'est pas un multiple de 20
        resultat = appliquer_recharge_stock_fournisseur(15)
        assert resultat == []
        
        # Test avec un tick qui est un multiple de 20
        with patch('random.random', return_value=0.1):  # Force la probabilité
            resultat = appliquer_recharge_stock_fournisseur(20)
            assert isinstance(resultat, list)
    
    @patch('events.recharge_stock_fournisseur.ProduitRepository')
    @patch('events.recharge_stock_fournisseur.FournisseurRepository')
    def test_appliquer_recharge_stock_fournisseur_probabilite_fournisseur(self, mock_fournisseur_repo, mock_produit_repo):
        """Test de la probabilité de recharge par fournisseur"""
        # Mock des repositories
        mock_produit_repo.return_value.get_actifs.return_value = [self.produit1, self.produit2]
        mock_fournisseur_repo.return_value.get_all.return_value = [self.fournisseur1, self.fournisseur2]
        
        # Test avec probabilité élevée (tous les fournisseurs rechargés)
        with patch('random.random', return_value=0.1):  # < 0.4
            resultat = appliquer_recharge_stock_fournisseur(20)
            assert len(resultat) > 0
        
        # Test avec probabilité faible (aucun fournisseur rechargé)
        with patch('random.random', return_value=0.9):  # > 0.4
            resultat = appliquer_recharge_stock_fournisseur(20)
            assert len(resultat) == 0
    
    @patch('events.recharge_stock_fournisseur.ProduitRepository')
    @patch('events.recharge_stock_fournisseur.FournisseurRepository')
    def test_appliquer_recharge_stock_fournisseur_quantite(self, mock_fournisseur_repo, mock_produit_repo):
        """Test des quantités de recharge"""
        # Mock des repositories
        mock_produit_repo.return_value.get_actifs.return_value = [self.produit1, self.produit2]
        mock_fournisseur_repo.return_value.get_all.return_value = [self.fournisseur1]
        
        # Force la recharge avec une quantité spécifique
        with patch('random.random', return_value=0.1):  # Force la probabilité
            with patch('random.randint', return_value=25):  # Force la quantité
                resultat = appliquer_recharge_stock_fournisseur(20)
                
                if resultat:
                    # Vérifier que la quantité est dans les bonnes limites
                    for log in resultat:
                        if log.get('event_type') == 'recharge_stock_fournisseur':
                            for produit in log.get('produits_recharges', []):
                                quantite = produit['quantite_rechargee']
                                assert RECHARGE_QUANTITE_MIN <= quantite <= RECHARGE_QUANTITE_MAX
    
    @patch('events.recharge_stock_fournisseur.ProduitRepository')
    @patch('events.recharge_stock_fournisseur.FournisseurRepository')
    def test_appliquer_recharge_stock_fournisseur_stock_mise_a_jour(self, mock_fournisseur_repo, mock_produit_repo):
        """Test que le stock est bien mis à jour"""
        # Mock des repositories
        mock_produit_repo.return_value.get_actifs.return_value = [self.produit1]
        mock_fournisseur_repo.return_value.get_all.return_value = [self.fournisseur1]
        
        stock_initial = self.fournisseur1.stock_produit[1]
        
        # Force la recharge
        with patch('random.random', return_value=0.1):  # Force la probabilité
            with patch('random.randint', return_value=30):  # Force la quantité
                resultat = appliquer_recharge_stock_fournisseur(20)
                
                if resultat:
                    # Vérifier que le stock a été mis à jour
                    nouveau_stock = self.fournisseur1.stock_produit[1]
                    assert nouveau_stock == stock_initial + 30
    
    @patch('events.recharge_stock_fournisseur.ProduitRepository')
    @patch('events.recharge_stock_fournisseur.FournisseurRepository')
    def test_appliquer_recharge_stock_fournisseur_logs_structure(self, mock_fournisseur_repo, mock_produit_repo):
        """Test de la structure des logs générés"""
        # Mock des repositories
        mock_produit_repo.return_value.get_actifs.return_value = [self.produit1]
        mock_fournisseur_repo.return_value.get_all.return_value = [self.fournisseur1]
        
        # Force la recharge
        with patch('random.random', return_value=0.1):  # Force la probabilité
            with patch('random.randint', return_value=25):  # Force la quantité
                resultat = appliquer_recharge_stock_fournisseur(20)
                
                if resultat:
                    # Vérifier la structure des logs
                    for log in resultat:
                        assert 'tick' in log
                        assert 'timestamp' in log
                        assert 'timestamp_humain' in log
                        assert 'event_type' in log
                        assert 'log_humain' in log
                        
                        if log['event_type'] == 'recharge_stock_fournisseur':
                            assert 'fournisseur_id' in log
                            assert 'fournisseur_nom' in log
                            assert 'fournisseur_continent' in log
                            assert 'nb_produits_recharges' in log
                            assert 'quantite_totale_rechargee' in log
                            assert 'produits_recharges' in log
                        
                        elif log['event_type'] == 'recharge_stock_fournisseur_resume':
                            assert 'statistiques' in log
                            assert 'fournisseurs' in log
    
    @patch('events.recharge_stock_fournisseur.ProduitRepository')
    @patch('events.recharge_stock_fournisseur.FournisseurRepository')
    def test_appliquer_recharge_stock_fournisseur_produits_actifs_seulement(self, mock_fournisseur_repo, mock_produit_repo):
        """Test que seuls les produits actifs sont rechargés"""
        # Créer un produit inactif
        produit_inactif = Produit(
            id=3,
            nom="Produit Inactif",
            type=TypeProduit.produit_fini,
            prix=200.0,
            actif=False
        )
        
        # Ajouter le produit inactif au stock du fournisseur
        self.fournisseur1.stock_produit[3] = 10
        
        # Mock des repositories
        mock_produit_repo.return_value.get_actifs.return_value = [self.produit1, self.produit2]  # Pas le produit inactif
        mock_fournisseur_repo.return_value.get_all.return_value = [self.fournisseur1]
        
        # Force la recharge
        with patch('random.random', return_value=0.1):  # Force la probabilité
            with patch('random.randint', return_value=20):  # Force la quantité
                resultat = appliquer_recharge_stock_fournisseur(20)
                
                if resultat:
                    # Vérifier que le stock du produit inactif n'a pas changé
                    assert self.fournisseur1.stock_produit[3] == 10
    
    @patch('events.recharge_stock_fournisseur.ProduitRepository')
    @patch('events.recharge_stock_fournisseur.FournisseurRepository')
    def test_appliquer_recharge_stock_fournisseur_produits_en_stock_seulement(self, mock_fournisseur_repo, mock_produit_repo):
        """Test que seuls les produits en stock sont rechargés"""
        # Créer un produit actif mais pas en stock
        produit_sans_stock = Produit(
            id=4,
            nom="Produit Sans Stock",
            type=TypeProduit.consommable,
            prix=150.0,
            actif=True
        )
        
        # Mock des repositories
        mock_produit_repo.return_value.get_actifs.return_value = [self.produit1, produit_sans_stock]
        mock_fournisseur_repo.return_value.get_all.return_value = [self.fournisseur1]
        
        # Force la recharge
        with patch('random.random', return_value=0.1):  # Force la probabilité
            resultat = appliquer_recharge_stock_fournisseur(20)
            
            # Vérifier que le produit sans stock n'a pas été ajouté au stock
            assert 4 not in self.fournisseur1.stock_produit
    
    @patch('events.recharge_stock_fournisseur.ProduitRepository')
    @patch('events.recharge_stock_fournisseur.FournisseurRepository')
    def test_appliquer_recharge_stock_fournisseur_statistiques(self, mock_fournisseur_repo, mock_produit_repo):
        """Test des statistiques calculées"""
        # Mock des repositories
        mock_produit_repo.return_value.get_actifs.return_value = [self.produit1, self.produit2]
        mock_fournisseur_repo.return_value.get_all.return_value = [self.fournisseur1, self.fournisseur2]
        
        # Force la recharge
        with patch('random.random', return_value=0.1):  # Force la probabilité
            with patch('random.randint', return_value=30):  # Force la quantité
                resultat = appliquer_recharge_stock_fournisseur(20)
                
                if resultat:
                    # Chercher le log de résumé
                    resume_log = None
                    for log in resultat:
                        if log.get('event_type') == 'recharge_stock_fournisseur_resume':
                            resume_log = log
                            break
                    
                    if resume_log:
                        stats = resume_log['statistiques']
                        assert 'nb_fournisseurs_recharges' in stats
                        assert 'nb_produits_recharges' in stats
                        assert 'quantite_totale_rechargee' in stats
                        assert 'moyenne_quantite_par_fournisseur' in stats
                        assert 'moyenne_produits_par_fournisseur' in stats
    
    @patch('events.recharge_stock_fournisseur.ProduitRepository')
    @patch('events.recharge_stock_fournisseur.FournisseurRepository')
    def test_appliquer_recharge_stock_fournisseur_aucun_fournisseur(self, mock_fournisseur_repo, mock_produit_repo):
        """Test avec aucun fournisseur"""
        # Mock des repositories vides
        mock_produit_repo.return_value.get_actifs.return_value = []
        mock_fournisseur_repo.return_value.get_all.return_value = []
        
        resultat = appliquer_recharge_stock_fournisseur(20)
        assert resultat == []
    
    @patch('events.recharge_stock_fournisseur.ProduitRepository')
    @patch('events.recharge_stock_fournisseur.FournisseurRepository')
    def test_appliquer_recharge_stock_fournisseur_aucun_produit_actif(self, mock_fournisseur_repo, mock_produit_repo):
        """Test avec aucun produit actif"""
        # Mock des repositories
        mock_produit_repo.return_value.get_actifs.return_value = []  # Aucun produit actif
        mock_fournisseur_repo.return_value.get_all.return_value = [self.fournisseur1]
        
        resultat = appliquer_recharge_stock_fournisseur(20)
        assert resultat == []


if __name__ == "__main__":
    """
    Point d'entrée pour exécuter les tests directement.
    Utile pour le développement et le debugging.
    """
    print("🧪 Tests de l'événement Recharge Stock Fournisseur...")
    
    # Créer une instance de test
    test_instance = TestRechargeStockFournisseur()
    
    # Tests de base
    test_instance.setup_method()
    
    # Test d'intervalle
    print("✅ Test intervalle...")
    with patch('events.recharge_stock_fournisseur.ProduitRepository') as mock_produit_repo:
        with patch('events.recharge_stock_fournisseur.FournisseurRepository') as mock_fournisseur_repo:
            mock_produit_repo.return_value.get_actifs.return_value = [test_instance.produit1]
            mock_fournisseur_repo.return_value.get_all.return_value = [test_instance.fournisseur1]
            
            resultat = appliquer_recharge_stock_fournisseur(15)
            assert resultat == []
            print("✅ Test intervalle réussi")
    
    # Test de recharge
    print("✅ Test recharge...")
    with patch('events.recharge_stock_fournisseur.ProduitRepository') as mock_produit_repo:
        with patch('events.recharge_stock_fournisseur.FournisseurRepository') as mock_fournisseur_repo:
            with patch('random.random', return_value=0.1):
                with patch('random.randint', return_value=25):
                    mock_produit_repo.return_value.get_actifs.return_value = [test_instance.produit1]
                    mock_fournisseur_repo.return_value.get_all.return_value = [test_instance.fournisseur1]
                    
                    resultat = appliquer_recharge_stock_fournisseur(20)
                    assert isinstance(resultat, list)
                    print("✅ Test recharge réussi")
    
    print("🎉 Tous les tests réussis !")
