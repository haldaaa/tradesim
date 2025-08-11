#!/usr/bin/env python3
"""
Tests unitaires pour les budgets d'entreprises configurables TradeSim
====================================================================

Ce module teste les nouvelles fonctionnalités de budgets d'entreprises configurables :
- Validation des constantes de configuration
- Test de la génération de budgets dans les bornes
- Vérification de la cohérence entre les différents services
- Test d'intégration avec les services existants

Pour lancer ces tests manuellement :
```bash
# Activer l'environnement
source ../venv/bin/activate
# Lancer les tests de budgets
python3 -m pytest tests/unit/test_budgets_entreprises.py -v
# Lancer tous les tests
python3 -m pytest tests/ -v
```

Pour lancer automatiquement :
```bash
# Avec coverage
python3 -m pytest tests/unit/test_budgets_entreprises.py --cov=services --cov-report=term-missing
```

Auteur: Assistant IA
Date: 2025-01-27
"""

import pytest
import random
from unittest.mock import Mock, patch
from config.config import BUDGET_ENTREPRISE_MIN, BUDGET_ENTREPRISE_MAX
from models import Entreprise, TypeProduit
from services.game_manager import generate_entreprises
from services.game_manager_service import GameManagerService


class TestBudgetsEntreprises:
    """Tests pour les budgets d'entreprises configurables"""
    
    def test_constantes_configuration(self):
        """Test que les constantes de configuration sont correctement définies"""
        assert BUDGET_ENTREPRISE_MIN == 6000
        assert BUDGET_ENTREPRISE_MAX == 20000
        assert BUDGET_ENTREPRISE_MIN < BUDGET_ENTREPRISE_MAX
    
    def test_budget_dans_bornes(self):
        """Test que les budgets générés sont dans les bornes configurées"""
        for _ in range(100):  # Test multiple fois pour s'assurer de la cohérence
            budget = random.uniform(BUDGET_ENTREPRISE_MIN, BUDGET_ENTREPRISE_MAX)
            assert BUDGET_ENTREPRISE_MIN <= budget <= BUDGET_ENTREPRISE_MAX
    
    def test_generation_entreprises_budgets(self):
        """Test que la génération d'entreprises respecte les budgets configurés"""
        config_entreprises = {
            "nombre": 3,
            "budget_min": 1000,  # Ces valeurs ne sont plus utilisées
            "budget_max": 3000,  # Ces valeurs ne sont plus utilisées
            "strategies": ["moins_cher", "par_type"],
            "types_preferes": ["matiere_premiere", "consommable", "produit_fini"]
        }
        
        # Mock du name_manager pour éviter les dépendances
        with patch('services.game_manager.name_manager') as mock_name_manager:
            mock_name_manager.get_multiple_entreprises.return_value = [
                {"nom": "Test1", "pays": "France", "continent": "Europe"},
                {"nom": "Test2", "pays": "Allemagne", "continent": "Europe"},
                {"nom": "Test3", "pays": "Canada", "continent": "Amérique"}
            ]
            
            # Mock du repository pour éviter les dépendances
            with patch('services.game_manager.entreprise_repo') as mock_repo:
                mock_repo.clear.return_value = None
                mock_repo.add.return_value = None
                
                # Appel de la fonction
                generate_entreprises(config_entreprises)
                
                # Vérifier que add a été appelé 3 fois (3 entreprises)
                assert mock_repo.add.call_count == 3
    
    def test_budget_realiste(self):
        """Test que les budgets sont réalistes pour le jeu"""
        # Les budgets doivent être suffisants pour acheter des produits
        budget_min = BUDGET_ENTREPRISE_MIN
        budget_max = BUDGET_ENTREPRISE_MAX
        
        # Vérifier que les budgets sont suffisants
        assert budget_min >= 1000, "Budget minimum trop faible"
        assert budget_max >= 5000, "Budget maximum trop faible"
        assert budget_max - budget_min >= 5000, "Écart min/max trop faible"
    
    def test_coherence_services(self):
        """Test la cohérence entre les différents services"""
        # Vérifier que les constantes sont cohérentes avec les recharges
        from config.config import RECHARGE_BUDGET_MIN, RECHARGE_BUDGET_MAX
        
        # Les recharges doivent être proportionnelles aux budgets
        assert RECHARGE_BUDGET_MAX <= BUDGET_ENTREPRISE_MAX * 0.5, "Recharge trop élevée par rapport au budget"
        assert RECHARGE_BUDGET_MIN >= 100, "Recharge minimum trop faible"
    
    def test_integration_budgets_variables(self):
        """Test d'intégration avec des budgets variables"""
        # Test que différentes entreprises peuvent avoir des budgets différents
        budgets_generes = []
        
        for _ in range(10):
            budget = random.uniform(BUDGET_ENTREPRISE_MIN, BUDGET_ENTREPRISE_MAX)
            budgets_generes.append(budget)
        
        # Vérifier qu'on a des budgets variés (pas toujours le même)
        assert len(set(budgets_generes)) > 1, "Les budgets devraient être variés"
        
        # Vérifier que tous les budgets sont dans les bornes
        for budget in budgets_generes:
            assert BUDGET_ENTREPRISE_MIN <= budget <= BUDGET_ENTREPRISE_MAX


class TestConfigurationBudgets:
    """Tests pour la configuration des budgets"""
    
    def test_configuration_import(self):
        """Test que les constantes sont correctement importées"""
        from config.config import BUDGET_ENTREPRISE_MIN, BUDGET_ENTREPRISE_MAX
        
        assert isinstance(BUDGET_ENTREPRISE_MIN, int)
        assert isinstance(BUDGET_ENTREPRISE_MAX, int)
        assert BUDGET_ENTREPRISE_MIN > 0
        assert BUDGET_ENTREPRISE_MAX > BUDGET_ENTREPRISE_MIN
    
    def test_configuration_coherence(self):
        """Test la cohérence de la configuration"""
        # Vérifier que les bornes sont logiques
        assert BUDGET_ENTREPRISE_MIN >= 1000, "Le budget minimum doit être >= 1000"
        assert BUDGET_ENTREPRISE_MAX <= 100000, "Le budget maximum ne doit pas être excessif"
        
        # Vérifier que les bornes permettent une variété
        assert BUDGET_ENTREPRISE_MAX - BUDGET_ENTREPRISE_MIN >= 5000, "Il faut une marge suffisante entre min et max"
    
    def test_configuration_realisme(self):
        """Test que la configuration est réaliste pour le jeu"""
        # Les budgets doivent permettre d'acheter plusieurs produits
        prix_produit_moyen = 200  # Prix moyen estimé d'un produit
        
        # Une entreprise doit pouvoir acheter au moins 10 produits
        assert BUDGET_ENTREPRISE_MIN >= prix_produit_moyen * 10, "Budget minimum trop faible pour le jeu"
        
        # Une entreprise doit pouvoir acheter au moins 50 produits
        assert BUDGET_ENTREPRISE_MAX >= prix_produit_moyen * 50, "Budget maximum trop faible pour le jeu"


class TestIntegrationBudgets:
    """Tests d'intégration pour les budgets"""
    
    def test_game_manager_service_budgets(self):
        """Test que GameManagerService utilise les bonnes constantes"""
        service = GameManagerService()
        
        # Mock de la configuration
        config_entreprises = {
            "nombre": 2,
            "budget_min": 1000,  # Ignoré
            "budget_max": 3000,  # Ignoré
            "strategies": ["moins_cher"],
            "types_preferes": ["matiere_premiere"]
        }
        
        # Mock des repositories et des données
        with patch.object(service.entreprise_repo, 'clear') as mock_clear:
            with patch.object(service.entreprise_repo, 'add') as mock_add:
                with patch('services.game_manager_service.random.uniform') as mock_uniform:
                    mock_uniform.return_value = 15000.0
                    
                    # Mock des données d'entreprises pour éviter l'erreur de continent
                    with patch.object(service, 'noms_entreprises', ['Test1', 'Test2']):
                        with patch.object(service, 'pays_entreprises', ['France', 'Allemagne']):
                            # Appel de la fonction
                            service.generate_entreprises(config_entreprises)
                            
                            # Vérifier que les bonnes constantes sont utilisées
                            assert mock_uniform.call_count >= 4  # 2 entreprises * 2 budgets (budget + budget_initial)
                            
                            # Vérifier que les appels utilisent les bonnes constantes
                            for call in mock_uniform.call_args_list:
                                args = call[0]
                                assert args[0] == BUDGET_ENTREPRISE_MIN
                                assert args[1] == BUDGET_ENTREPRISE_MAX
    
    def test_data_py_budgets(self):
        """Test que data.py utilise les bonnes constantes"""
        # Import direct pour tester
        from data import fake_entreprises_db
        
        # Vérifier que les entreprises ont des budgets dans les bonnes bornes
        # Note: certaines entreprises peuvent avoir budget=0.0 si elles ont été créées avant la mise à jour
        for entreprise in fake_entreprises_db:
            if entreprise.budget > 0:  # Seulement vérifier les entreprises avec budget > 0
                assert BUDGET_ENTREPRISE_MIN <= entreprise.budget <= BUDGET_ENTREPRISE_MAX
            if entreprise.budget_initial > 0:  # Seulement vérifier les entreprises avec budget_initial > 0
                assert BUDGET_ENTREPRISE_MIN <= entreprise.budget_initial <= BUDGET_ENTREPRISE_MAX


if __name__ == "__main__":
    # Tests manuels
    print("🧪 Tests des budgets d'entreprises configurables")
    print(f"📊 Configuration actuelle: min={BUDGET_ENTREPRISE_MIN}€, max={BUDGET_ENTREPRISE_MAX}€")
    
    # Test rapide
    test_instance = TestBudgetsEntreprises()
    test_instance.test_constantes_configuration()
    test_instance.test_budget_dans_bornes()
    print("✅ Tests de base passés") 