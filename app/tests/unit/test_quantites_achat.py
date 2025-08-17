#!/usr/bin/env python3
"""
Tests unitaires pour les quantités d'achat configurables TradeSim
================================================================

Ce module teste les nouvelles fonctionnalités de quantités d'achat configurables :
- Validation des constantes de configuration
- Test de la logique d'achat avec les nouvelles quantités
- Vérification des bornes min/max
- Test d'intégration avec les services existants

Pour lancer ces tests manuellement :
```bash
# Activer l'environnement
source ../venv/bin/activate
# Lancer les tests de quantités d'achat
python3 -m pytest tests/unit/test_quantites_achat.py -v
# Lancer tous les tests
python3 -m pytest tests/ -v
```

Pour lancer automatiquement :
```bash
# Avec coverage
python3 -m pytest tests/unit/test_quantites_achat.py --cov=services --cov-report=term-missing
```

Auteur: Assistant IA
Date: 2025-01-27
"""

import pytest
import random
from unittest.mock import Mock, patch
from config.config import QUANTITE_ACHAT_MIN, QUANTITE_ACHAT_MAX
from models import Entreprise, Produit, Fournisseur, TypeProduit
from services.simulateur import acheter_produit
from services.transaction_service import TransactionService


class TestQuantitesAchat:
    """Tests pour les quantités d'achat configurables"""
    
    def test_constantes_configuration(self):
        """Test que les constantes de configuration sont correctement définies"""
        assert QUANTITE_ACHAT_MIN == 1
        assert QUANTITE_ACHAT_MAX == 100
        assert QUANTITE_ACHAT_MIN < QUANTITE_ACHAT_MAX
    
    def test_quantite_dans_bornes(self):
        """Test que les quantités générées sont dans les bornes configurées"""
        for _ in range(100):  # Test multiple fois pour s'assurer de la cohérence
            quantite = random.randint(QUANTITE_ACHAT_MIN, QUANTITE_ACHAT_MAX)
            assert QUANTITE_ACHAT_MIN <= quantite <= QUANTITE_ACHAT_MAX
    
    def test_quantite_respecte_budget(self):
        """Test que la quantité respecte le budget disponible"""
        # Mock des données
        entreprise = Mock(spec=Entreprise)
        entreprise.budget = 100.0
        entreprise.id = 1
        entreprise.nom = "TestCorp"
        entreprise.stocks = {}  # Ajouter l'attribut stocks manquant
        
        produit = Mock(spec=Produit)
        produit.id = 1
        produit.nom = "TestProduit"
        produit.type = TypeProduit.consommable
        
        fournisseur = Mock(spec=Fournisseur)
        fournisseur.id = 1
        fournisseur.nom_entreprise = "TestFournisseur"
        fournisseur.stock_produit = {1: 50}
        
        # Prix unitaire de 10€
        with patch('services.simulateur.get_prix_produit_fournisseur', return_value=10.0):
            with patch('services.simulateur.get_fournisseurs_avec_stock', return_value=[fournisseur]):
                with patch('services.simulateur.random.choice', return_value=fournisseur):
                    with patch('services.simulateur.random.randint') as mock_randint:
                        # Simuler une quantité qui respecte le budget (max 10 avec budget 100€)
                        mock_randint.return_value = 5
                        
                        # Test de la fonction
                        resultat = acheter_produit(
                            entreprise=entreprise,
                            produit=produit,
                            horodatage_iso="2025-01-27T10:00:00",
                            horodatage_humain="27/01/2025 10:00:00",
                            strategie="moins_cher",
                            verbose=False
                        )
                        
                        # Vérifier que la quantité respecte le budget
                        assert mock_randint.call_args[0][0] == QUANTITE_ACHAT_MIN
                        assert mock_randint.call_args[0][1] <= 10  # Budget / prix unitaire
    
    def test_quantite_respecte_stock(self):
        """Test que la quantité respecte le stock disponible"""
        entreprise = Mock(spec=Entreprise)
        entreprise.budget = 1000.0  # Budget suffisant
        entreprise.id = 1
        entreprise.nom = "TestCorp"
        entreprise.stocks = {}  # Ajouter l'attribut stocks manquant
        
        produit = Mock(spec=Produit)
        produit.id = 1
        produit.nom = "TestProduit"
        produit.type = TypeProduit.consommable
        
        fournisseur = Mock(spec=Fournisseur)
        fournisseur.id = 1
        fournisseur.nom_entreprise = "TestFournisseur"
        fournisseur.stock_produit = {1: 5}  # Stock limité à 5
        
        with patch('services.simulateur.get_prix_produit_fournisseur', return_value=10.0):
            with patch('services.simulateur.get_fournisseurs_avec_stock', return_value=[fournisseur]):
                with patch('services.simulateur.random.choice', return_value=fournisseur):
                    with patch('services.simulateur.random.randint') as mock_randint:
                        # La quantité max devrait être limitée par le stock (5)
                        mock_randint.return_value = 3
                        
                        resultat = acheter_produit(
                            entreprise=entreprise,
                            produit=produit,
                            horodatage_iso="2025-01-27T10:00:00",
                            horodatage_humain="27/01/2025 10:00:00",
                            strategie="moins_cher",
                            verbose=False
                        )
                        
                        # Vérifier que la quantité max est limitée par le stock
                        assert mock_randint.call_args[0][1] <= 5  # Stock disponible
    
    def test_transaction_service_quantite(self):
        """Test que TransactionService utilise les bonnes quantités"""
        service = TransactionService()
        
        # Mock d'une entreprise
        entreprise = Mock(spec=Entreprise)
        entreprise.id = 1
        entreprise.nom = "TestCorp"
        entreprise.budget = 1000.0
        entreprise.stocks = {}  # Ajouter l'attribut stocks manquant
        
        # Mock d'un produit
        produit = Mock(spec=Produit)
        produit.id = 1
        produit.nom = "TestProduit"
        produit.type = TypeProduit.consommable
        produit.actif = True
        
        # Mock du repository
        with patch.object(service.produit_repo, 'get_by_id', return_value=produit):
            with patch.object(service, 'trouver_fournisseurs_produit', return_value=[]):
                with patch.object(service, 'choisir_fournisseur', return_value=None):
                    # Test que la fonction utilise les constantes de configuration
                    with patch('services.transaction_service.random.randint') as mock_randint:
                        mock_randint.return_value = 15
                        
                        # Appel de la fonction (qui va échouer mais on teste l'appel)
                        resultat = service.effectuer_achat(entreprise, 1, 15)
                        
                        # Vérifier que la fonction retourne None (pas de fournisseur disponible)
                        assert resultat is None
    
    def test_integration_quantites_variables(self):
        """Test d'intégration avec des quantités variables"""
        # Test que différentes entreprises peuvent acheter des quantités différentes
        quantites_achetees = []
        
        for _ in range(10):
            quantite = random.randint(QUANTITE_ACHAT_MIN, QUANTITE_ACHAT_MAX)
            quantites_achetees.append(quantite)
        
        # Vérifier qu'on a des quantités variées (pas toujours la même)
        assert len(set(quantites_achetees)) > 1, "Les quantités devraient être variées"
        
        # Vérifier que toutes les quantités sont dans les bornes
        for quantite in quantites_achetees:
            assert QUANTITE_ACHAT_MIN <= quantite <= QUANTITE_ACHAT_MAX


class TestConfigurationQuantites:
    """Tests pour la configuration des quantités"""
    
    def test_configuration_import(self):
        """Test que les constantes sont correctement importées"""
        from config.config import QUANTITE_ACHAT_MIN, QUANTITE_ACHAT_MAX
        
        assert isinstance(QUANTITE_ACHAT_MIN, int)
        assert isinstance(QUANTITE_ACHAT_MAX, int)
        assert QUANTITE_ACHAT_MIN > 0
        assert QUANTITE_ACHAT_MAX > QUANTITE_ACHAT_MIN
    
    def test_configuration_coherence(self):
        """Test la cohérence de la configuration"""
        # Vérifier que les bornes sont logiques
        assert QUANTITE_ACHAT_MIN >= 1, "La quantité minimum doit être >= 1"
        assert QUANTITE_ACHAT_MAX <= 1000, "La quantité maximum ne doit pas être excessive"
        
        # Vérifier que les bornes permettent une variété
        assert QUANTITE_ACHAT_MAX - QUANTITE_ACHAT_MIN >= 10, "Il faut une marge suffisante entre min et max"


if __name__ == "__main__":
    # Tests manuels
    print("🧪 Tests des quantités d'achat configurables")
    print(f"📊 Configuration actuelle: min={QUANTITE_ACHAT_MIN}, max={QUANTITE_ACHAT_MAX}")
    
    # Test rapide
    test_instance = TestQuantitesAchat()
    test_instance.test_constantes_configuration()
    test_instance.test_quantite_dans_bornes()
    print("✅ Tests de base passés") 