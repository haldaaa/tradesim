#!/usr/bin/env python3
"""
Tests API pour les endpoints FastAPI de TradeSim
===============================================

Ce fichier teste tous les endpoints de l'API :
- GET / (root)
- GET /produits
- GET /fournisseurs
- GET /entreprises

Auteur: Assistant IA
Date: 2024-08-02
"""

import sys
import os
# Ajouter le dossier parent au path Python pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from fastapi.testclient import TestClient
from api.main import app
from data import (
    fake_produits_db, fake_fournisseurs_db, fake_entreprises_db,
    prix_par_fournisseur
)
from models import Produit, TypeProduit, Fournisseur, Entreprise
from services.game_manager import reset_game, generate_game_data


class TestAPIEndpoints:
    """Tests pour les endpoints API"""
    
    def setup_method(self):
        """Setup avant chaque test - configuration de test"""
        self.client = TestClient(app)
        
        # Configuration de test
        self.config_test = {
            "entreprises": {
                "nombre": 2,
                "budget_min": 500.0,
                "budget_max": 1500.0,
                "strategies": ["moins_cher", "par_type"],
                "types_preferes": ["matiere_premiere", "consommable", "produit_fini"]
            },
            "produits": {
                "nombre": 5,
                "prix_min": 10.0,
                "prix_max": 200.0,
                "actifs_min": 3,
                "actifs_max": 4,
                "types": ["matiere_premiere", "consommable", "produit_fini"]
            },
            "fournisseurs": {
                "nombre": 2,
                "produits_min": 2,
                "produits_max": 4,
                "stock_min": 20,
                "stock_max": 100
            }
        }
        
        # Reset et génération des données
        reset_game()
        generate_game_data(self.config_test)
    
    def test_root_endpoint(self):
        """Test de l'endpoint racine GET /"""
        response = self.client.get("/")
        
        # Vérifier le statut de la réponse
        assert response.status_code == 200
        
        # Vérifier le contenu de la réponse
        data = response.json()
        assert "message" in data
        assert data["message"] == "Bienvenue sur TradeSim"
        
        print("✅ Test endpoint racine - Réponse valide")
    
    def test_produits_endpoint(self):
        """Test de l'endpoint GET /produits"""
        response = self.client.get("/produits")
        
        # Vérifier le statut de la réponse
        assert response.status_code == 200
        
        # Vérifier le contenu de la réponse
        produits = response.json()
        assert isinstance(produits, list)
        
        # Vérifier que seuls les produits actifs sont retournés
        produits_actifs_api = [p for p in produits if p["actif"]]
        produits_actifs_db = [p for p in fake_produits_db if p.actif]
        
        assert len(produits_actifs_api) == len(produits_actifs_db)
        
        # Vérifier la structure des produits
        for produit in produits:
            assert "id" in produit
            assert "nom" in produit
            assert "prix" in produit
            assert "actif" in produit
            assert "type" in produit
            
            # Vérifier les types de données
            assert isinstance(produit["id"], int)
            assert isinstance(produit["nom"], str)
            assert isinstance(produit["prix"], (int, float))
            assert isinstance(produit["actif"], bool)
            assert isinstance(produit["type"], str)
            
            # Vérifier que le type est valide
            assert produit["type"] in ["matiere_premiere", "consommable", "produit_fini"]
        
        print("✅ Test endpoint produits - Données valides")
    
    def test_fournisseurs_endpoint(self):
        """Test de l'endpoint GET /fournisseurs"""
        response = self.client.get("/fournisseurs")
        
        # Vérifier le statut de la réponse
        assert response.status_code == 200
        
        # Vérifier le contenu de la réponse
        fournisseurs = response.json()
        assert isinstance(fournisseurs, list)
        assert len(fournisseurs) == len(fake_fournisseurs_db)
        
        # Vérifier la structure des fournisseurs
        for fournisseur in fournisseurs:
            assert "id" in fournisseur
            assert "nom_entreprise" in fournisseur
            assert "pays" in fournisseur
            assert "produits" in fournisseur
            
            # Vérifier les types de données
            assert isinstance(fournisseur["id"], int)
            assert isinstance(fournisseur["nom_entreprise"], str)
            assert isinstance(fournisseur["pays"], str)
            assert isinstance(fournisseur["produits"], list)
            
            # Vérifier la structure des produits chez le fournisseur
            for produit in fournisseur["produits"]:
                assert "produit_id" in produit
                assert "nom" in produit
                assert "stock" in produit
                assert "prix_unitaire" in produit
                
                # Vérifier les types de données
                assert isinstance(produit["produit_id"], int)
                assert isinstance(produit["nom"], str)
                assert isinstance(produit["stock"], int)
                assert isinstance(produit["prix_unitaire"], (int, float)) or produit["prix_unitaire"] is None
        
        print("✅ Test endpoint fournisseurs - Données valides")
    
    def test_entreprises_endpoint(self):
        """Test de l'endpoint GET /entreprises"""
        response = self.client.get("/entreprises")
        
        # Vérifier le statut de la réponse
        assert response.status_code == 200
        
        # Vérifier le contenu de la réponse
        entreprises = response.json()
        assert isinstance(entreprises, list)
        assert len(entreprises) == len(fake_entreprises_db)
        
        # Vérifier la structure des entreprises
        for entreprise in entreprises:
            assert "id" in entreprise
            assert "nom" in entreprise
            assert "pays" in entreprise
            assert "budget" in entreprise
            assert "budget_initial" in entreprise
            assert "types_preferes" in entreprise
            assert "strategie" in entreprise
            
            # Vérifier les types de données
            assert isinstance(entreprise["id"], int)
            assert isinstance(entreprise["nom"], str)
            assert isinstance(entreprise["pays"], str)
            assert isinstance(entreprise["budget"], (int, float))
            assert isinstance(entreprise["budget_initial"], (int, float))
            assert isinstance(entreprise["types_preferes"], list)
            assert isinstance(entreprise["strategie"], str)
            
            # Vérifier que les types préférés sont valides
            for type_pref in entreprise["types_preferes"]:
                assert type_pref in ["matiere_premiere", "consommable", "produit_fini"]
            
            # Vérifier que la stratégie est valide
            assert entreprise["strategie"] in ["moins_cher", "par_type"]
        
        print("✅ Test endpoint entreprises - Données valides")
    
    def test_produits_filtering(self):
        """Test que l'endpoint /produits ne retourne que les produits actifs"""
        # Créer un produit inactif
        produit_inactif = Produit(
            id=999,
            nom="Produit Inactif",
            prix=100.0,
            actif=False,
            type=TypeProduit.matiere_premiere
        )
        fake_produits_db.append(produit_inactif)
        
        response = self.client.get("/produits")
        produits = response.json()
        
        # Vérifier que le produit inactif n'est pas dans la réponse
        produit_ids = [p["id"] for p in produits]
        assert 999 not in produit_ids
        
        print("✅ Test filtrage produits - Seuls les actifs retournés")
    
    def test_fournisseurs_data_consistency(self):
        """Test de cohérence des données des fournisseurs"""
        response = self.client.get("/fournisseurs")
        fournisseurs_api = response.json()
        
        # Vérifier que les données correspondent à la base
        for fournisseur_api in fournisseurs_api:
            fournisseur_db = next(f for f in fake_fournisseurs_db if f.id == fournisseur_api["id"])
            
            assert fournisseur_api["nom_entreprise"] == fournisseur_db.nom_entreprise
            assert fournisseur_api["pays"] == fournisseur_db.pays
            
            # Vérifier que les produits correspondent
            produits_api_ids = {p["produit_id"] for p in fournisseur_api["produits"]}
            produits_db_ids = set(fournisseur_db.stock_produit.keys())
            
            assert produits_api_ids == produits_db_ids
        
        print("✅ Test cohérence fournisseurs - Données cohérentes")
    
    def test_entreprises_data_consistency(self):
        """Test de cohérence des données des entreprises"""
        response = self.client.get("/entreprises")
        entreprises_api = response.json()
        
        # Vérifier que les données correspondent à la base
        for entreprise_api in entreprises_api:
            entreprise_db = next(e for e in fake_entreprises_db if e.id == entreprise_api["id"])
            
            assert entreprise_api["nom"] == entreprise_db.nom
            assert entreprise_api["pays"] == entreprise_db.pays
            assert entreprise_api["budget"] == entreprise_db.budget
            assert entreprise_api["budget_initial"] == entreprise_db.budget_initial
            assert entreprise_api["strategie"] == entreprise_db.strategie
            
            # Vérifier les types préférés
            types_api = set(entreprise_api["types_preferes"])
            types_db = set(t.value for t in entreprise_db.types_preferes)
            assert types_api == types_db
        
        print("✅ Test cohérence entreprises - Données cohérentes")


class TestAPIErrorHandling:
    """Tests de gestion d'erreurs pour l'API"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.client = TestClient(app)
        
        # Configuration minimale
        config_min = {
            "entreprises": {"nombre": 1, "budget_min": 100.0, "budget_max": 200.0, "strategies": ["moins_cher"], "types_preferes": ["matiere_premiere"]},
            "produits": {"nombre": 2, "prix_min": 10.0, "prix_max": 50.0, "actifs_min": 1, "actifs_max": 2, "types": ["matiere_premiere"]},
            "fournisseurs": {"nombre": 1, "produits_min": 1, "produits_max": 2, "stock_min": 10, "stock_max": 50}
        }
        
        reset_game()
        generate_game_data(config_min)
    
    def test_invalid_endpoint(self):
        """Test d'un endpoint inexistant"""
        response = self.client.get("/endpoint_inexistant")
        
        # Vérifier que l'erreur 404 est retournée
        assert response.status_code == 404
        
        print("✅ Test endpoint inexistant - Erreur 404")
    
    def test_method_not_allowed(self):
        """Test d'une méthode HTTP non autorisée"""
        response = self.client.post("/produits")
        
        # Vérifier que l'erreur 405 est retournée
        assert response.status_code == 405
        
        print("✅ Test méthode non autorisée - Erreur 405")


class TestAPIPerformance:
    """Tests de performance pour l'API"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.client = TestClient(app)
        
        # Configuration avec beaucoup d'entités
        config_large = {
            "entreprises": {
                "nombre": 20,
                "budget_min": 100.0,
                "budget_max": 5000.0,
                "strategies": ["moins_cher", "par_type"],
                "types_preferes": ["matiere_premiere", "consommable", "produit_fini"]
            },
            "produits": {
                "nombre": 50,
                "prix_min": 1.0,
                "prix_max": 1000.0,
                "actifs_min": 20,
                "actifs_max": 40,
                "types": ["matiere_premiere", "consommable", "produit_fini"]
            },
            "fournisseurs": {
                "nombre": 10,
                "produits_min": 10,
                "produits_max": 30,
                "stock_min": 10,
                "stock_max": 500
            }
        }
        
        reset_game()
        generate_game_data(config_large)
    
    def test_api_response_time(self):
        """Test du temps de réponse de l'API"""
        import time
        
        # Mesurer le temps de réponse pour chaque endpoint
        endpoints = ["/", "/produits", "/fournisseurs", "/entreprises"]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Vérifier que la réponse est rapide (< 1 seconde)
            assert response_time < 1.0
            assert response.status_code == 200
            
            print(f"✅ Test performance {endpoint} - {response_time:.3f}s")
    
    def test_large_dataset_handling(self):
        """Test de gestion d'un grand volume de données"""
        # Vérifier que l'API peut gérer beaucoup d'entités
        response = self.client.get("/produits")
        produits = response.json()
        assert len(produits) >= 20  # Au moins 20 produits actifs
        
        response = self.client.get("/fournisseurs")
        fournisseurs = response.json()
        assert len(fournisseurs) == 10
        
        response = self.client.get("/entreprises")
        entreprises = response.json()
        assert len(entreprises) == 20
        
        print("✅ Test grand volume - API performante")


if __name__ == "__main__":
    """
    Point d'entrée pour exécuter les tests directement.
    Utile pour le développement et le debugging.
    """
    print("🚀 Démarrage des tests API TradeSim...")
    
    # Tests de base
    test_api = TestAPIEndpoints()
    test_api.test_root_endpoint()
    test_api.test_produits_endpoint()
    test_api.test_fournisseurs_endpoint()
    test_api.test_entreprises_endpoint()
    test_api.test_produits_filtering()
    test_api.test_fournisseurs_data_consistency()
    test_api.test_entreprises_data_consistency()
    
    # Tests de gestion d'erreurs
    test_errors = TestAPIErrorHandling()
    test_errors.test_invalid_endpoint()
    test_errors.test_method_not_allowed()
    
    # Tests de performance
    test_perf = TestAPIPerformance()
    test_perf.test_api_response_time()
    test_perf.test_large_dataset_handling()
    
    print("🎉 Tous les tests API terminés !") 