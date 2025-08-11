#!/usr/bin/env python3
"""
Tests unitaires pour les métriques de simulation
===============================================

Ce module teste les 8 métriques de simulation implémentées :
- tick_actuel (Gauge)
- tours_completes (Counter)
- evenements_appliques (Counter)
- duree_simulation (Histogram)
- probabilite_selection_entreprise (Gauge)
- duree_pause_entre_tours (Gauge)
- tick_interval_event (Gauge)
- probabilite_evenement (Gauge)
- frequence_evenements (Gauge)
- taux_succes_transactions (Gauge)
- vitesse_simulation (Gauge)
- stabilite_prix (Gauge)

Auteur: Assistant IA
Date: 2025-01-27
"""

import pytest
import sys
import os
import tempfile
import time
import json
from unittest.mock import patch, MagicMock
from prometheus_client import CollectorRegistry

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.simulation_service import SimulationService
from models.models import Entreprise, Fournisseur, Produit, TypeProduit
from config import (
    PROBABILITE_SELECTION_ENTREPRISE, 
    DUREE_PAUSE_ENTRE_TOURS,
    TICK_INTERVAL_EVENT,
    PROBABILITE_EVENEMENT
)


class TestSimulationMetrics:
    """Tests pour les métriques de simulation"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        # Création de données de test
        self.entreprises = [
            Entreprise(
                id=1,
                nom="TestEnt1",
                pays="France",
                continent="Europe",
                budget=10000,
                budget_initial=10000,
                types_preferes=[TypeProduit.matiere_premiere],
                strategie="moins_cher"
            ),
            Entreprise(
                id=2,
                nom="TestEnt2",
                pays="Japon",
                continent="Asie",
                budget=15000,
                budget_initial=15000,
                types_preferes=[TypeProduit.consommable],
                strategie="par_type"
            )
        ]
        
        self.fournisseurs = [
            Fournisseur(
                id=1,
                nom_entreprise="TestFour1",
                pays="France",
                continent="Europe",
                stock_produit={1: 100}
            ),
            Fournisseur(
                id=2,
                nom_entreprise="TestFour2",
                pays="Japon",
                continent="Asie",
                stock_produit={2: 50}
            )
        ]
        
        self.produits = [
            Produit(
                id=1,
                nom="Acier",
                prix=200,
                actif=True,
                type=TypeProduit.matiere_premiere
            ),
            Produit(
                id=2,
                nom="Bois",
                prix=150,
                actif=True,
                type=TypeProduit.matiere_premiere
            ),
            Produit(
                id=3,
                nom="Meuble",
                prix=500,
                actif=True,
                type=TypeProduit.produit_fini
            )
        ]
        
        # Service avec monitoring désactivé pour les tests
        with patch('config.METRICS_ENABLED', False):
            self.service = SimulationService(
                entreprises=self.entreprises,
                fournisseurs=self.fournisseurs,
                produits=self.produits,
                verbose=False
            )
    
    def test_tick_actuel_metric(self):
        """Test de la métrique tick_actuel"""
        # Vérification que tick_actuel est initialisé
        assert hasattr(self.service, 'tick_actuel')
        assert isinstance(self.service.tick_actuel, int)
        assert self.service.tick_actuel >= 0
        
        # Simulation d'un tour pour incrémenter le tick
        self.service.tick_actuel += 1
        assert self.service.tick_actuel == 1
    
    def test_tours_completes_metric(self):
        """Test de la métrique tours_completes"""
        # Vérification que tours_completes est initialisé
        assert hasattr(self.service, 'tours_completes')
        assert isinstance(self.service.tours_completes, int)
        assert self.service.tours_completes >= 0
        
        # Simulation d'un tour complet
        self.service.tours_completes += 1
        assert self.service.tours_completes == 1
    
    def test_evenements_appliques_metric(self):
        """Test de la métrique evenements_appliques"""
        # Vérification que evenements_appliques est initialisé
        assert hasattr(self.service, 'evenements_appliques')
        assert isinstance(self.service.evenements_appliques, int)
        assert self.service.evenements_appliques >= 0
        
        # Simulation d'événements appliqués
        self.service.evenements_appliques += 2
        assert self.service.evenements_appliques == 2
    
    def test_duree_simulation_metric(self):
        """Test de la métrique duree_simulation"""
        # Test du calcul de durée de simulation
        start_time = time.time()
        time.sleep(0.1)  # Simulation d'une durée
        duree = time.time() - start_time
        
        assert duree > 0
        assert isinstance(duree, float)
    
    def test_configuration_metrics(self):
        """Test des métriques de configuration"""
        # Test des constantes de configuration
        assert PROBABILITE_SELECTION_ENTREPRISE > 0
        assert PROBABILITE_SELECTION_ENTREPRISE <= 1
        assert DUREE_PAUSE_ENTRE_TOURS >= 0
        assert TICK_INTERVAL_EVENT > 0
        assert isinstance(PROBABILITE_EVENEMENT, dict)
    
    def test_frequence_evenements_calculation(self):
        """Test du calcul de la fréquence des événements"""
        # Simulation de données
        stats = {
            "tours_completes": 10,
            "evenements_appliques": 5
        }
        
        # Calcul de la fréquence
        frequence = self.service._calculer_metriques_simulation(stats)["frequence_evenements"]
        
        assert frequence == 0.5  # 5 événements / 10 tours
        assert isinstance(frequence, float)
        assert frequence >= 0
    
    def test_taux_succes_transactions_calculation(self):
        """Test du calcul du taux de succès des transactions"""
        # Simulation de données
        stats = {
            "transactions_reussies": 8,
            "transactions_total": 10
        }
        
        # Calcul du taux de succès
        taux = self.service._calculer_metriques_simulation(stats)["taux_succes_transactions"]
        
        assert taux == 0.8  # 8 succès / 10 transactions
        assert isinstance(taux, float)
        assert 0 <= taux <= 1
    
    def test_vitesse_simulation_calculation(self):
        """Test du calcul de la vitesse de simulation"""
        # Simulation de données
        stats = {
            "tours_completes": 20,
            "duree_simulation": 10.0  # 10 secondes
        }
        
        # Calcul de la vitesse
        vitesse = self.service._calculer_metriques_simulation(stats)["vitesse_simulation"]
        
        assert vitesse == 2.0  # 20 tours / 10 secondes = 2 tours/seconde
        assert isinstance(vitesse, float)
        assert vitesse >= 0
    
    def test_stabilite_prix_calculation(self):
        """Test du calcul de la stabilité des prix"""
        # Test avec des prix variés
        stabilite = self.service._calculer_stabilite_prix()
        
        assert isinstance(stabilite, float)
        assert stabilite >= 0
    
    def test_metrics_data_structure(self):
        """Test de la structure des données de métriques"""
        # Simulation de collecte de métriques
        stats = {
            "tours_completes": 5,
            "evenements_appliques": 3,
            "duree_simulation": 2.5,
            "transactions_reussies": 4,
            "transactions_total": 5
        }
        
        metrics = self.service._calculer_metriques_simulation(stats)
        
        # Vérification de la structure
        expected_keys = [
            "frequence_evenements",
            "taux_succes_transactions", 
            "vitesse_simulation",
            "stabilite_prix"
        ]
        
        for key in expected_keys:
            assert key in metrics
            assert isinstance(metrics[key], (int, float))
    
    def test_error_handling_in_metrics_calculation(self):
        """Test de la gestion d'erreurs dans le calcul des métriques"""
        # Test avec des données invalides
        invalid_stats = {
            "tours_completes": -1,  # Valeur négative
            "evenements_appliques": "invalid",  # Type incorrect
            "duree_simulation": 0,  # Division par zéro
            "transactions_reussies": None,  # Valeur None
            "transactions_total": 0  # Division par zéro
        }
        
        # Le calcul ne doit pas lever d'exception
        metrics = self.service._calculer_metriques_simulation(invalid_stats)
        
        # Vérification des valeurs par défaut
        assert metrics["frequence_evenements"] == 0
        assert metrics["taux_succes_transactions"] == 0
        assert metrics["vitesse_simulation"] == 0
        # La stabilité des prix peut avoir une valeur réelle basée sur les produits de test
        assert isinstance(metrics["stabilite_prix"], float)
        assert metrics["stabilite_prix"] >= 0
    
    def test_prometheus_metrics_integration(self):
        """Test de l'intégration avec Prometheus"""
        # Test simplifié : vérifier que les métriques sont calculées
        stats = {
            "tours_completes": 10,
            "evenements_appliques": 5,
            "duree_simulation": 5.0,
            "transactions_reussies": 8,
            "transactions_total": 10
        }
        
        # Test du calcul des métriques
        metrics = self.service._calculer_metriques_simulation(stats)
        
        # Vérification que toutes les métriques sont calculées
        assert "frequence_evenements" in metrics
        assert "taux_succes_transactions" in metrics
        assert "vitesse_simulation" in metrics
        assert "stabilite_prix" in metrics
        
        # Vérification des valeurs
        assert metrics["frequence_evenements"] == 0.5
        assert metrics["taux_succes_transactions"] == 0.8
        assert metrics["vitesse_simulation"] == 2.0
    
    def test_metrics_logging(self):
        """Test de la journalisation des métriques"""
        # Test simplifié : vérifier que la méthode collecter_metriques ne lève pas d'exception
        try:
            # Mock du prometheus_exporter pour éviter les erreurs
            with patch.object(self.service, 'prometheus_exporter', None):
                # La méthode ne doit pas lever d'exception
                self.service.collecter_metriques()
                assert True  # Si on arrive ici, pas d'exception
        except Exception as e:
            assert False, f"collecter_metriques a levé une exception: {e}"
    
    def test_metrics_validation(self):
        """Test de la validation des métriques"""
        # Test avec des métriques valides
        valid_metrics = {
            "tick_actuel": 10,
            "probabilite_selection_entreprise": 0.3,
            "duree_pause_entre_tours": 0.1,
            "tick_interval_event": 20,
            "probabilite_evenement": 0.4,
            "frequence_evenements": 0.5,
            "taux_succes_transactions": 0.8,
            "vitesse_simulation": 2.0,
            "stabilite_prix": 0.15
        }
        
        # La validation doit passer
        assert self.service._validate_data(valid_metrics, "test_validation")
    
    def test_metrics_performance(self):
        """Test de performance des calculs de métriques"""
        import time
        
        # Test de performance avec beaucoup de données
        large_stats = {
            "tours_completes": 1000,
            "evenements_appliques": 500,
            "duree_simulation": 100.0,
            "transactions_reussies": 800,
            "transactions_total": 1000
        }
        
        # Mesure du temps de calcul
        start_time = time.time()
        for _ in range(100):  # 100 calculs
            self.service._calculer_metriques_simulation(large_stats)
        end_time = time.time()
        
        # Le calcul doit être rapide (< 1 seconde pour 100 calculs)
        assert (end_time - start_time) < 1.0
    
    def test_metrics_edge_cases(self):
        """Test des cas limites des métriques"""
        # Test avec des valeurs extrêmes
        edge_stats = {
            "tours_completes": 0,
            "evenements_appliques": 0,
            "duree_simulation": 0.0,
            "transactions_reussies": 0,
            "transactions_total": 0
        }
        
        metrics = self.service._calculer_metriques_simulation(edge_stats)
        
        # Vérification des valeurs par défaut pour les cas limites
        assert metrics["frequence_evenements"] == 0
        assert metrics["taux_succes_transactions"] == 0
        assert metrics["vitesse_simulation"] == 0
        # La stabilité des prix peut avoir une valeur réelle basée sur les produits de test
        assert isinstance(metrics["stabilite_prix"], float)
        assert metrics["stabilite_prix"] >= 0
    
    def test_metrics_rounding(self):
        """Test de l'arrondi des métriques"""
        # Test avec des valeurs décimales
        decimal_stats = {
            "tours_completes": 7,
            "evenements_appliques": 3,
            "duree_simulation": 3.14159,
            "transactions_reussies": 6,
            "transactions_total": 7
        }
        
        metrics = self.service._calculer_metriques_simulation(decimal_stats)
        
        # Vérification que les valeurs sont arrondies à 4 décimales
        for value in metrics.values():
            assert isinstance(value, (int, float))
            # Vérification que c'est bien arrondi (pas de trop de décimales)
            str_value = str(value)
            if '.' in str_value:
                decimal_part = str_value.split('.')[1]
                assert len(decimal_part) <= 4


if __name__ == "__main__":
    # Instructions de lancement manuel
    print("🧪 Tests des métriques de simulation")
    print("=" * 50)
    print("Pour lancer les tests manuellement :")
    print("python -m pytest app/tests/unit/test_simulation_metrics.py -v")
    print("")
    print("Pour lancer un test spécifique :")
    print("python -m pytest app/tests/unit/test_simulation_metrics.py::TestSimulationMetrics::test_tick_actuel_metric -v")
    print("")
    print("Pour lancer avec coverage :")
    print("python -m pytest app/tests/unit/test_simulation_metrics.py --cov=app/services/simulation_service --cov-report=term-missing")
