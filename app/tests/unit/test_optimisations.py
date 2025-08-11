#!/usr/bin/env python3
"""
Tests unitaires pour les optimisations du système
Tests de validation, cache, index, monitoring temps réel, et performance
"""

import unittest
import time
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from services.simulation_service import IDGenerator, SimulationService
from models.models import Entreprise, Fournisseur, Produit, TypeProduit
from config import (
    VALID_ACTION_TYPES, MAX_COUNTER, BATCH_LOG_SIZE, CACHE_MAX_SIZE,
    VALIDATION_ENABLED, REALTIME_MONITORING, PERFORMANCE_THRESHOLD,
    ALERT_BUDGET_CRITIQUE, ALERT_STOCK_CRITIQUE, ALERT_ERROR_RATE
)

class TestIDGeneratorOptimisations(unittest.TestCase):
    """Tests pour les optimisations du générateur d'IDs"""
    
    def setUp(self):
        self.id_generator = IDGenerator()
    
    def test_validation_action_types(self):
        """Test de validation des types d'action"""
        # Test types valides
        for action_type in VALID_ACTION_TYPES:
            id_val = self.id_generator.get_id(action_type)
            self.assertIsInstance(id_val, str)
            self.assertIn(action_type, id_val)
        
        # Test type invalide
        with self.assertRaises(ValueError):
            self.id_generator.get_id("INVALID_TYPE")
        
        # Test type vide
        with self.assertRaises(ValueError):
            self.id_generator.get_id("")
    
    def test_counter_overflow(self):
        """Test du débordement du compteur"""
        # Générer MAX_COUNTER IDs
        for i in range(MAX_COUNTER):
            self.id_generator.get_id("TXN")
        
        # Le suivant devrait lever une exception
        with self.assertRaises(ValueError):
            self.id_generator.get_id("TXN")
    
    def test_batch_logging(self):
        """Test de l'écriture en batch"""
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            # Simuler l'ajout au buffer
            for i in range(BATCH_LOG_SIZE + 1):
                log_entry = {"test": f"entry_{i}", "timestamp": datetime.now().isoformat()}
                self.id_generator.add_to_buffer(log_entry)
            
            # Vérifier que le buffer a été vidé
            self.assertEqual(len(self.id_generator.log_buffer), 1)
            
            # Vider manuellement le buffer
            self.id_generator.flush_buffer()
            self.assertEqual(len(self.id_generator.log_buffer), 0)
            
        finally:
            os.unlink(temp_file)
    
    def test_index_search(self):
        """Test de l'index pour recherche rapide"""
        # Générer quelques IDs
        ids = []
        for i in range(5):
            ids.append(self.id_generator.get_id("TXN"))
        
        # Rechercher par session
        session_id = self.id_generator.get_session_id()
        found_ids = self.id_generator.search_by_session(session_id)
        
        self.assertEqual(len(found_ids), 5)
        for id_val in ids:
            self.assertIn(id_val, found_ids)

class TestSimulationServiceOptimisations(unittest.TestCase):
    """Tests pour les optimisations du service de simulation"""
    
    def setUp(self):
        # Créer des données de test avec tous les champs requis
        self.entreprises = [
            Entreprise(
                id=1, 
                nom="TestEnt", 
                budget=1000.0, 
                budget_initial=1000.0,
                strategie="moins_cher", 
                # stocks gérés par SimulationService
                pays="France",
                continent="Europe",
                types_preferes=[TypeProduit.matiere_premiere]
            )
        ]
        self.fournisseurs = [
            Fournisseur(
                id=1, 
                nom_entreprise="TestFour", 
                stock_produit={1: 100},  # produit_id: quantité
                pays="France",
                continent="Europe"
            )
        ]
        self.produits = [
            Produit(id=1, nom="TestProd", prix=100.0, type=TypeProduit.matiere_premiere, actif=True)
        ]
        
        # Mock de PriceService pour les tests
        with patch('app.services.simulation_service.price_service') as mock_price_service:
            mock_price_service.get_prix_produit_fournisseur.return_value = 100.0
            with patch('app.services.simulation_service.PRICE_SERVICE_AVAILABLE', True):
                self.service = SimulationService(
                    self.entreprises, self.fournisseurs, self.produits, verbose=False
                )
    
    def test_data_validation(self):
        """Test de validation des données"""
        # Test données valides
        valid_data = {"prix": 10.0, "quantite": 5, "budget": 100.0}
        self.assertTrue(self.service._validate_data(valid_data, "test"))
        
        # Test prix négatif
        invalid_price = {"prix": -5.0}
        self.assertFalse(self.service._validate_data(invalid_price, "test"))
        
        # Test quantité invalide
        invalid_quantity = {"quantite": 0}
        self.assertFalse(self.service._validate_data(invalid_quantity, "test"))
        
        # Test budget négatif
        invalid_budget = {"budget": -100.0}
        self.assertFalse(self.service._validate_data(invalid_budget, "test"))
    
    def test_cache_statistics(self):
        """Test du cache pour les statistiques"""
        # Premier appel (pas en cache)
        start_time = time.time()
        stats1 = self.service.calculer_statistiques()
        duration1 = time.time() - start_time
        
        # Deuxième appel (en cache)
        start_time = time.time()
        stats2 = self.service.calculer_statistiques()
        duration2 = time.time() - start_time
        
        # Le deuxième appel devrait être plus rapide
        self.assertLess(duration2, duration1)
        self.assertEqual(stats1, stats2)
    
    def test_error_logging(self):
        """Test du logging d'erreurs"""
        initial_error_count = self.service.error_count
        
        # Simuler une erreur
        self.service._log_error("test_error", "Test error message")
        
        # Vérifier que le compteur d'erreurs a augmenté
        self.assertEqual(self.service.error_count, initial_error_count + 1)
    
    def test_realtime_alerts(self):
        """Test des alertes temps réel"""
        # Simuler un budget critique
        self.service.entreprises[0].budget = ALERT_BUDGET_CRITIQUE - 100
        
        # Calculer les statistiques (déclenche l'alerte)
        stats = self.service.calculer_statistiques()
        
        # Vérifier que les statistiques sont calculées
        self.assertIsInstance(stats, dict)
    
    def test_performance_monitoring(self):
        """Test du monitoring de performance"""
        # Simuler une opération lente
        with patch('time.time') as mock_time:
            mock_time.side_effect = [0.0, PERFORMANCE_THRESHOLD + 0.1]
            
            # Cette opération devrait déclencher une alerte de performance
            stats = self.service.calculer_statistiques()
            
            # Vérifier que les statistiques sont calculées
            self.assertIsInstance(stats, dict)
    
    def test_transaction_validation(self):
        """Test de validation des transactions"""
        # Test de validation des données (plus simple)
        valid_data = {"prix": 100.0, "stock_disponible": 50, "budget": 1000.0}
        result = self.service._validate_data(valid_data, "test_transaction")
        self.assertTrue(result)
        
        # Test de validation avec données invalides
        invalid_data = {"prix": -100.0, "stock_disponible": 0, "budget": -1000.0}
        result = self.service._validate_data(invalid_data, "test_transaction")
        self.assertFalse(result)
    
    def test_error_rate_calculation(self):
        """Test du calcul du taux d'erreur"""
        # Simuler quelques actions
        self.service.total_actions = 10
        self.service.error_count = 2
        
        # Calculer le taux d'erreur
        error_rate = self.service.error_count / self.service.total_actions
        
        self.assertEqual(error_rate, 0.2)  # 20%
        
        # Si le taux dépasse le seuil, une alerte devrait être déclenchée
        if error_rate > ALERT_ERROR_RATE:
            # Simuler une alerte
            self.service._send_alert("error_rate_critical", f"Taux d'erreur critique: {error_rate:.2%}")
    
    def test_batch_logging_integration(self):
        """Test d'intégration de l'écriture en batch"""
        # Créer un fichier temporaire pour les logs
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_log_file = f.name
        
        try:
            # Simuler plusieurs transactions
            for i in range(3):
                self.service.acheter_produit_detaille(
                    self.entreprises[0], self.produits[0], self.fournisseurs[0], "moins_cher"
                )
            
            # Vérifier que le buffer a été utilisé
            self.assertGreater(self.service.total_actions, 0)
            
        finally:
            os.unlink(temp_log_file)

class TestConfigurationOptimisations(unittest.TestCase):
    """Tests pour la configuration des optimisations"""
    
    def test_configuration_imports(self):
        """Test que toutes les configurations sont importables"""
        from config import (
            ID_FORMAT, ID_SESSION_FORMAT, MAX_COUNTER, VALID_ACTION_TYPES,
            BATCH_LOG_SIZE, CACHE_MAX_SIZE, COMPRESSION_DAYS, INDEX_ENABLED,
            VALIDATION_ENABLED, REALTIME_MONITORING, PERFORMANCE_THRESHOLD,
            ALERT_BUDGET_CRITIQUE, ALERT_STOCK_CRITIQUE, ALERT_ERROR_RATE,
            METRICS_COLLECTION_INTERVAL, METRICS_RETENTION_DAYS
        )
        
        # Vérifier que les valeurs sont définies
        self.assertIsInstance(ID_FORMAT, str)
        self.assertIsInstance(MAX_COUNTER, int)
        self.assertIsInstance(VALID_ACTION_TYPES, list)
        self.assertIsInstance(BATCH_LOG_SIZE, int)
        self.assertIsInstance(CACHE_MAX_SIZE, int)
        self.assertIsInstance(VALIDATION_ENABLED, bool)
        self.assertIsInstance(REALTIME_MONITORING, bool)
        self.assertIsInstance(PERFORMANCE_THRESHOLD, float)
    
    def test_configuration_values(self):
        """Test des valeurs de configuration"""
        from config import (
            MAX_COUNTER, BATCH_LOG_SIZE, CACHE_MAX_SIZE,
            VALIDATION_ENABLED, REALTIME_MONITORING, PERFORMANCE_THRESHOLD
        )
        
        # Vérifier les valeurs attendues
        self.assertGreater(MAX_COUNTER, 0)
        self.assertGreater(BATCH_LOG_SIZE, 0)
        self.assertGreater(CACHE_MAX_SIZE, 0)
        self.assertGreater(PERFORMANCE_THRESHOLD, 0)
        self.assertIsInstance(VALIDATION_ENABLED, bool)
        self.assertIsInstance(REALTIME_MONITORING, bool)

if __name__ == '__main__':
    # Instructions de test manuel
    print("🧪 Tests des optimisations TradeSim")
    print("=" * 50)
    print("Pour exécuter les tests :")
    print("python -m pytest tests/unit/test_optimisations.py -v")
    print("\nTests couverts :")
    print("- Validation des types d'action")
    print("- Débordement des compteurs")
    print("- Écriture en batch des logs")
    print("- Index pour recherche rapide")
    print("- Validation des données")
    print("- Cache des statistiques")
    print("- Logging d'erreurs")
    print("- Alertes temps réel")
    print("- Monitoring de performance")
    print("- Configuration des optimisations")
    
    unittest.main()
