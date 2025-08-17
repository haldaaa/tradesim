#!/usr/bin/env python3
"""
Tests d'intégration pour Prometheus
Validation que les métriques sont correctement exposées et mises à jour

Instructions de lancement :
- Test d'intégration : pytest tests/integration/test_prometheus_integration.py -v
- Test avec monitoring : python -m pytest tests/integration/test_prometheus_integration.py -v --capture=no
"""

import pytest
import requests
import time
import json
import subprocess
import signal
import os
from typing import Dict, Any

from models.models import Entreprise, Fournisseur, Produit, TypeProduit
from services.simulation_service import SimulationService
from monitoring.prometheus_exporter import PrometheusExporter


class TestPrometheusIntegration:
    """Tests d'intégration pour Prometheus"""
    
    def setup_method(self):
        """Configuration initiale pour chaque test"""
        # Données de test
        self.entreprises = [
            Entreprise(
                id=1, nom="TestEnt1", pays="France", continent="Europe",
                budget=10000, budget_initial=10000,
                types_preferes=[TypeProduit.matiere_premiere], strategie="moins_cher"
            )
        ]
        
        self.fournisseurs = [
            Fournisseur(
                id=1, nom_entreprise="TestFour1", pays="France", continent="Europe",
                stock_produit={1: 100}
            )
        ]
        
        self.produits = [
            Produit(id=1, nom="TestProd1", prix=100.0, actif=True, type=TypeProduit.matiere_premiere)
        ]
        
        # Port de test
        self.test_port = 8001
        
    def teardown_method(self):
        """Nettoyage après chaque test"""
        # Arrêter l'exporter s'il est en cours
        try:
            requests.get(f"http://localhost:{self.test_port}/health", timeout=1)
        except:
            pass
    
    def test_prometheus_exporter_startup(self):
        """Test du démarrage de l'exporteur Prometheus"""
        exporter = PrometheusExporter(port=self.test_port)
        
        # Test que l'exporter peut être créé
        assert exporter is not None
        assert exporter.port == self.test_port
        assert exporter.app is not None
    
    def test_metrics_endpoint_available(self):
        """Test que l'endpoint /metrics est disponible"""
        # Démarrer l'exporter en arrière-plan
        exporter = PrometheusExporter(port=self.test_port)
        
        # Démarrer dans un thread séparé
        import threading
        thread = threading.Thread(target=exporter.start)
        thread.daemon = True
        thread.start()
        
        # Attendre que l'exporter démarre
        time.sleep(2)
        
        try:
            # Tester l'endpoint /metrics
            response = requests.get(f"http://localhost:{self.test_port}/metrics", timeout=5)
            assert response.status_code == 200
            assert "tradesim_" in response.text
            
        finally:
            # Arrêter l'exporter
            try:
                requests.get(f"http://localhost:{self.test_port}/health", timeout=1)
            except:
                pass
    
    def test_metrics_update(self):
        """Test de la mise à jour des métriques"""
        # Démarrer l'exporter
        exporter = PrometheusExporter(port=self.test_port)
        
        import threading
        thread = threading.Thread(target=exporter.start)
        thread.daemon = True
        thread.start()
        
        # Attendre que l'exporter démarre
        time.sleep(2)
        
        try:
            # Données de test
            test_metrics = {
                "tick_actuel": 5,
                "evenements_appliques": 3,
                "tours_completes": 2,
                "budget_total_entreprises": 5000.0,
                "probabilite_selection_entreprise": 0.3,
                "duree_pause_entre_tours": 0.1,
                "tick_interval_event": 20,
                "probabilite_evenement": 0.4,
                "frequence_evenements": 1.5,
                "taux_succes_transactions": 0.8,
                "vitesse_simulation": 2.0,
                "stabilite_prix": 0.5
            }
            
            # Mettre à jour les métriques
            exporter.update_tradesim_metrics(test_metrics)
            
            # Attendre que les métriques soient mises à jour
            time.sleep(1)
            
            # Vérifier les métriques
            response = requests.get(f"http://localhost:{self.test_port}/metrics", timeout=5)
            metrics_text = response.text
            
            # Vérifier que les métriques sont présentes
            assert "tradesim_tick_actuel" in metrics_text
            assert "tradesim_evenements_appliques" in metrics_text
            assert "tradesim_tours_completes" in metrics_text
            assert "tradesim_budget_total_entreprises" in metrics_text
            
            # Vérifier les valeurs (les métriques doivent être > 0)
            assert "tradesim_tick_actuel 5.0" in metrics_text
            assert "tradesim_evenements_appliques 3.0" in metrics_text
            assert "tradesim_tours_completes 2.0" in metrics_text
            assert "tradesim_budget_total_entreprises 5000.0" in metrics_text
            
        finally:
            # Arrêter l'exporter
            try:
                requests.get(f"http://localhost:{self.test_port}/health", timeout=1)
            except:
                pass
    
    def test_simulation_service_with_prometheus(self):
        """Test de l'intégration SimulationService + Prometheus"""
        # Démarrer l'exporter
        exporter = PrometheusExporter(port=self.test_port)
        
        import threading
        thread = threading.Thread(target=exporter.start)
        thread.daemon = True
        thread.start()
        
        # Attendre que l'exporter démarre
        time.sleep(2)
        
        try:
            # Créer le service de simulation avec l'exporter
            service = SimulationService(
                self.entreprises, 
                self.fournisseurs, 
                self.produits, 
                verbose=False
            )
            service.prometheus_exporter = exporter
            
            # Exécuter un tour de simulation
            result = service.simulation_tour()
            
            # Vérifier que le tour s'est bien passé
            assert "transactions_effectuees" in result
            assert "tick" in result
            assert "tour" in result
            
            # Forcer la collecte des métriques
            service.collecter_metriques()
            
            # Attendre que les métriques soient mises à jour
            time.sleep(1)
            
            # Vérifier les métriques Prometheus
            response = requests.get(f"http://localhost:{self.test_port}/metrics", timeout=5)
            metrics_text = response.text
            
            # Vérifier que les métriques de base sont présentes
            assert "tradesim_tick_actuel" in metrics_text
            assert "tradesim_tours_completes" in metrics_text
            
            # Vérifier que les valeurs ne sont plus à 0
            # Note: Les valeurs exactes dépendent de la simulation
            assert "tradesim_tick_actuel 0.0" not in metrics_text or "tradesim_tick_actuel 1.0" in metrics_text
            
        finally:
            # Arrêter l'exporter
            try:
                requests.get(f"http://localhost:{self.test_port}/health", timeout=1)
            except:
                pass
    
    def test_metrics_persistence(self):
        """Test de la persistance des métriques entre les appels"""
        # Démarrer l'exporter
        exporter = PrometheusExporter(port=self.test_port)
        
        import threading
        thread = threading.Thread(target=exporter.start)
        thread.daemon = True
        thread.start()
        
        # Attendre que l'exporter démarre
        time.sleep(2)
        
        try:
            # Première mise à jour
            metrics1 = {
                "tick_actuel": 1,
                "evenements_appliques": 1,
                "tours_completes": 1,
                "budget_total_entreprises": 1000.0
            }
            exporter.update_tradesim_metrics(metrics1)
            time.sleep(1)
            
            # Vérifier les métriques
            response1 = requests.get(f"http://localhost:{self.test_port}/metrics", timeout=5)
            assert "tradesim_tick_actuel 1.0" in response1.text
            
            # Deuxième mise à jour
            metrics2 = {
                "tick_actuel": 2,
                "evenements_appliques": 2,
                "tours_completes": 2,
                "budget_total_entreprises": 2000.0
            }
            exporter.update_tradesim_metrics(metrics2)
            time.sleep(1)
            
            # Vérifier que les métriques ont été mises à jour
            response2 = requests.get(f"http://localhost:{self.test_port}/metrics", timeout=5)
            assert "tradesim_tick_actuel 2.0" in response2.text
            assert "tradesim_budget_total_entreprises 2000.0" in response2.text
            
        finally:
            # Arrêter l'exporter
            try:
                requests.get(f"http://localhost:{self.test_port}/health", timeout=1)
            except:
                pass
    
    def test_metrics_jsonl_storage(self):
        """Test du stockage JSONL des métriques"""
        # Fichier de test
        test_file = "logs/test_metrics.jsonl"
        
        # Démarrer l'exporter avec un fichier de test
        exporter = PrometheusExporter(port=self.test_port)
        exporter.metrics_file = test_file
        
        import threading
        thread = threading.Thread(target=exporter.start)
        thread.daemon = True
        thread.start()
        
        # Attendre que l'exporter démarre
        time.sleep(2)
        
        try:
            # Données de test
            test_metrics = {
                "tick_actuel": 10,
                "evenements_appliques": 5,
                "tours_completes": 3,
                "budget_total_entreprises": 7500.0
            }
            
            # Mettre à jour les métriques
            exporter.update_tradesim_metrics(test_metrics)
            time.sleep(1)
            
            # Vérifier que le fichier JSONL a été créé
            assert os.path.exists(test_file)
            
            # Vérifier le contenu du fichier
            with open(test_file, 'r') as f:
                lines = f.readlines()
                assert len(lines) > 0
                
                # Vérifier la dernière ligne
                last_line = json.loads(lines[-1])
                assert "timestamp" in last_line
                assert "metrics" in last_line
                assert last_line["metrics"]["tick_actuel"] == 10
                assert last_line["metrics"]["budget_total_entreprises"] == 7500.0
                
        finally:
            # Nettoyer
            if os.path.exists(test_file):
                os.remove(test_file)
            
            # Arrêter l'exporter
            try:
                requests.get(f"http://localhost:{self.test_port}/health", timeout=1)
            except:
                pass


if __name__ == "__main__":
    # Instructions de lancement
    print("Tests d'intégration pour Prometheus")
    print("Lancement : pytest tests/integration/test_prometheus_integration.py -v")
    print("Note : Ces tests nécessitent que le port 8001 soit disponible")
