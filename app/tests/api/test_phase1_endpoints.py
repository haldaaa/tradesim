#!/usr/bin/env python3
"""
Tests pour les endpoints Phase 1 - TradeSim API
===============================================

Tests des nouveaux endpoints ajoutés dans la Phase 1 :
- /health
- /config (GET/POST)
- /simulation (POST)
- /metrics (GET)
- /ws (WebSocket)

Auteur: Assistant IA
Date: 2024-09-04
"""

import pytest
import json
import asyncio
from fastapi.testclient import TestClient
from api.main import app

# Client de test
client = TestClient(app)

class TestHealthEndpoint:
    """Tests pour l'endpoint /health"""
    
    def test_health_check(self):
        """Test du health check"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"
        assert "timestamp" in data

class TestConfigEndpoints:
    """Tests pour les endpoints /config"""
    
    def test_get_config(self):
        """Test de récupération de la configuration"""
        response = client.get("/config")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "config" in data
        assert isinstance(data["config"], dict)
    
    def test_update_config(self):
        """Test de mise à jour de la configuration"""
        config_data = {
            "key": "test_key",
            "value": "test_value"
        }
        
        response = client.post("/config", json=config_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "Configuration test_key mise à jour" in data["message"]
        assert data["updated"]["key"] == "test_key"
        assert data["updated"]["value"] == "test_value"

class TestSimulationEndpoint:
    """Tests pour l'endpoint /simulation"""
    
    def test_simulation_basic(self):
        """Test de simulation basique"""
        simulation_data = {
            "tours": 5,
            "verbose": False,
            "with_metrics": True
        }
        
        response = client.post("/simulation", json=simulation_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "result" in data
        assert "metrics" in data
    
    def test_simulation_without_metrics(self):
        """Test de simulation sans métriques"""
        simulation_data = {
            "tours": 3,
            "verbose": True,
            "with_metrics": False
        }
        
        response = client.post("/simulation", json=simulation_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "result" in data
        assert data["metrics"] is None
    
    def test_simulation_invalid_params(self):
        """Test avec des paramètres invalides"""
        simulation_data = {
            "tours": -1,  # Nombre de tours invalide
            "verbose": False,
            "with_metrics": True
        }
        
        response = client.post("/simulation", json=simulation_data)
        # L'API devrait accepter mais la simulation pourrait échouer
        # On teste juste que l'endpoint répond
        assert response.status_code in [200, 422]

class TestMetricsEndpoint:
    """Tests pour l'endpoint /metrics"""
    
    def test_get_metrics(self):
        """Test de récupération des métriques"""
        response = client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "metrics" in data
        
        metrics = data["metrics"]
        assert "tours_completes" in metrics
        assert "entreprises_actives" in metrics
        assert "produits_actifs" in metrics
        assert "fournisseurs_actifs" in metrics
        
        # Vérifier que les valeurs sont des nombres
        assert isinstance(metrics["tours_completes"], int)
        assert isinstance(metrics["entreprises_actives"], int)
        assert isinstance(metrics["produits_actifs"], int)
        assert isinstance(metrics["fournisseurs_actifs"], int)

class TestWebSocketEndpoint:
    """Tests pour l'endpoint WebSocket /ws"""
    
    def test_websocket_connection(self):
        """Test de connexion WebSocket"""
        with client.websocket_connect("/ws") as websocket:
            # Test de connexion
            assert websocket is not None
    
    def test_websocket_ping_pong(self):
        """Test du ping-pong WebSocket"""
        with client.websocket_connect("/ws") as websocket:
            # Envoyer un ping
            websocket.send_text(json.dumps({"type": "ping"}))
            
            # Recevoir le pong
            data = websocket.receive_text()
            message = json.loads(data)
            
            assert message["type"] == "pong"
            assert "timestamp" in message
    
    def test_websocket_subscribe(self):
        """Test de l'abonnement WebSocket"""
        with client.websocket_connect("/ws") as websocket:
            # S'abonner
            websocket.send_text(json.dumps({"type": "subscribe"}))
            
            # Recevoir la confirmation
            data = websocket.receive_text()
            message = json.loads(data)
            
            assert message["type"] == "subscribed"
            assert "Abonnement aux mises à jour temps réel activé" in message["message"]

class TestExistingEndpoints:
    """Tests pour les endpoints existants (rétrocompatibilité)"""
    
    def test_root_endpoint(self):
        """Test de l'endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_produits_endpoint(self):
        """Test de l'endpoint produits"""
        response = client.get("/produits")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_fournisseurs_endpoint(self):
        """Test de l'endpoint fournisseurs"""
        response = client.get("/fournisseurs")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_entreprises_endpoint(self):
        """Test de l'endpoint entreprises"""
        response = client.get("/entreprises")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)

class TestCORS:
    """Tests pour la configuration CORS"""
    
    def test_cors_headers(self):
        """Test des headers CORS"""
        response = client.options("/config")
        assert response.status_code == 200
        
        # Vérifier les headers CORS
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
