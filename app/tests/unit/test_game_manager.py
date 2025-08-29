#!/usr/bin/env python3
"""
Test Game Manager - Tests pour le module game_manager
====================================================

Ce fichier teste le module game_manager avec la nouvelle architecture Repository.
Les tests utilisent les Repository au lieu d'accès directs aux fake_db.

Auteur: Assistant IA
Date: 2024-08-02
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Imports corrigés pour la nouvelle structure
from services.game_manager import (
    reset_game, generate_game_data, generate_produits, generate_fournisseurs,
    generate_entreprises, save_template, load_template, list_templates,
    get_current_config, ask_number, ask_launch_game, show_game_summary,
    get_default_config, NOMS_ENTREPRISES, NOMS_FOURNISSEURS,
    NOMS_PRODUITS
)
from models import Produit, TypeProduit, Fournisseur, Entreprise
from config.config import BUDGET_ENTREPRISE_MIN, BUDGET_ENTREPRISE_MAX

# Imports des Repository (nouvelle architecture)
from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository


class TestGameManager:
    """Tests pour le module game_manager avec architecture Repository"""
    
    def setup_method(self):
        """Setup avant chaque test - sauvegarde l'état initial via Repository"""
        # Initialiser les Repository
        self.produit_repo = ProduitRepository()
        self.fournisseur_repo = FournisseurRepository()
        self.entreprise_repo = EntrepriseRepository()
        
        # Sauvegarder l'état initial via Repository
        self.produits_initial = self.produit_repo.get_all().copy()
        self.fournisseurs_initial = self.fournisseur_repo.get_all().copy()
        self.entreprises_initial = self.entreprise_repo.get_all().copy()
    
    def teardown_method(self):
        """Cleanup après chaque test - restaure l'état initial via Repository"""
        # Vider les Repository
        self.produit_repo.clear()
        self.fournisseur_repo.clear()
        self.entreprise_repo.clear()
        
        # Restaurer l'état initial via Repository
        for produit in self.produits_initial:
            self.produit_repo.add(produit)
        
        for fournisseur in self.fournisseurs_initial:
            self.fournisseur_repo.add(fournisseur)
        
        for entreprise in self.entreprises_initial:
            self.entreprise_repo.add(entreprise)
    
    def test_reset_game(self):
        """Test de la fonction reset_game() avec Repository"""
        # Appeler reset_game d'abord pour s'assurer que les repositories sont vides
        reset_game()
        
        # Vérifier que les Repository sont vides
        assert len(self.produit_repo.get_all()) == 0
        assert len(self.fournisseur_repo.get_all()) == 0
        assert len(self.entreprise_repo.get_all()) == 0
        
        # Modifier l'état pour tester le reset
        produit_test = Produit(
            id=999, nom="Test", prix=100.0, actif=True, type=TypeProduit.matiere_premiere
        )
        self.produit_repo.add(produit_test)
        
        # Appeler reset_game à nouveau
        reset_game()
        
        # Vérifier que les Repository sont vides après le reset
        assert len(self.produit_repo.get_all()) == 0
        assert len(self.fournisseur_repo.get_all()) == 0
        assert len(self.entreprise_repo.get_all()) == 0
        
        print("✅ Test reset_game - Reset réussi avec Repository")
    
    def test_generate_produits(self):
        """Test de la fonction generate_produits() avec Repository"""
        config_produits = {
            "nombre": 5,
            "prix_min": 10.0,
            "prix_max": 100.0,
            "actifs_min": 2,
            "actifs_max": 4,
            "types": ["matiere_premiere", "consommable", "produit_fini"]
        }
        
        # Vider le Repository de produits
        self.produit_repo.clear()
        
        # Générer les produits
        generate_produits(config_produits)
        
        # Vérifications via Repository
        produits = self.produit_repo.get_all()
        assert len(produits) == 5
        
        # Vérifier que tous les produits ont des prix dans la plage
        for produit in produits:
            assert 10.0 <= produit.prix <= 100.0
            assert produit.id > 0
            # Vérifier que le nom est dans les données de noms
            from data.names_data import PRODUITS_DATA
            noms_produits = [p["nom"] for p in PRODUITS_DATA]
            assert produit.nom in noms_produits
            assert produit.type in [TypeProduit.matiere_premiere, TypeProduit.consommable, TypeProduit.produit_fini]
        
        # Vérifier qu'il y a entre 2 et 4 produits actifs
        produits_actifs = self.produit_repo.get_actifs()
        assert 2 <= len(produits_actifs) <= 4
        
        print("✅ Test generate_produits - Génération réussie avec Repository")
    
    def test_generate_fournisseurs(self):
        """Test de la fonction generate_fournisseurs() avec Repository"""
        # D'abord générer des produits pour que les fournisseurs puissent les utiliser
        config_produits = {
            "nombre": 5,
            "prix_min": 10.0,
            "prix_max": 100.0,
            "actifs_min": 2,
            "actifs_max": 4,
            "types": ["matiere_premiere", "consommable", "produit_fini"]
        }
        generate_produits(config_produits)
        
        config_fournisseurs = {
            "nombre": 3,
            "produits_min": 2,
            "produits_max": 5,
            "stock_min": 10,
            "stock_max": 100
        }
        
        # Vider le Repository de fournisseurs
        self.fournisseur_repo.clear()
        
        # Générer les fournisseurs
        generate_fournisseurs(config_fournisseurs)
        
        # Vérifications via Repository
        fournisseurs = self.fournisseur_repo.get_all()
        assert len(fournisseurs) == 3
        
        for fournisseur in fournisseurs:
            # Vérifier que le nom est dans les données de noms
            from data.names_data import FOURNISSEURS_DATA
            noms_fournisseurs = [f["nom"] for f in FOURNISSEURS_DATA]
            assert fournisseur.nom_entreprise in noms_fournisseurs
            # Vérifier que le pays est dans les données de noms
            pays_fournisseurs = [f["pays"] for f in FOURNISSEURS_DATA]
            assert fournisseur.pays in pays_fournisseurs
            assert 2 <= len(fournisseur.stock_produit) <= 5
            
            # Vérifier les stocks
            for stock in fournisseur.stock_produit.values():
                assert 10 <= stock <= 100
        
        print("✅ Test generate_fournisseurs - Génération réussie avec Repository")
    
    def test_generate_entreprises(self):
        """Test de la fonction generate_entreprises() avec Repository"""
        config_entreprises = {
            "nombre": 2,
            "budget_min": 1000.0,
            "budget_max": 3000.0,
            "strategies": ["moins_cher", "par_type"],
            "types_preferes": ["matiere_premiere", "consommable", "produit_fini"]
        }
        
        # Vider le Repository d'entreprises
        self.entreprise_repo.clear()
        
        # Générer les entreprises
        generate_entreprises(config_entreprises)
        
        # Vérifications via Repository
        entreprises = self.entreprise_repo.get_all()
        assert len(entreprises) == 2
        
        for entreprise in entreprises:
            # Vérifier que le nom est dans les données de noms
            from data.names_data import ENTREPRISES_DATA
            noms_entreprises = [e["nom"] for e in ENTREPRISES_DATA]
            assert entreprise.nom in noms_entreprises
            # Vérifier que le pays est dans les données de noms
            pays_entreprises = [e["pays"] for e in ENTREPRISES_DATA]
            assert entreprise.pays in pays_entreprises
            assert BUDGET_ENTREPRISE_MIN <= entreprise.budget <= BUDGET_ENTREPRISE_MAX
            assert entreprise.strategie in ["moins_cher", "par_type"]
            assert len(entreprise.types_preferes) > 0
        
        print("✅ Test generate_entreprises - Génération réussie avec Repository")
    
    def test_generate_game_data(self):
        """Test de la fonction generate_game_data() avec Repository"""
        config = {
            "produits": {
                "nombre": 3,
                "prix_min": 10.0,
                "prix_max": 50.0,
                "actifs_min": 1,
                "actifs_max": 2,
                "types": ["matiere_premiere", "consommable", "produit_fini"]
            },
            "fournisseurs": {
                "nombre": 2,
                "produits_min": 1,
                "produits_max": 3,
                "stock_min": 10,
                "stock_max": 50
            },
            "entreprises": {
                "nombre": 1,
                "budget_min": 1000.0,
                "budget_max": 2000.0,
                "strategies": ["moins_cher", "par_type"],
                "types_preferes": ["matiere_premiere", "consommable", "produit_fini"]
            }
        }
        
        # Vider tous les Repository
        self.produit_repo.clear()
        self.fournisseur_repo.clear()
        self.entreprise_repo.clear()
        
        # Générer les données de jeu
        generate_game_data(config)
        
        # Vérifications via Repository
        assert len(self.produit_repo.get_all()) == 3
        assert len(self.fournisseur_repo.get_all()) == 2
        assert len(self.entreprise_repo.get_all()) == 1
        
        # Vérifier qu'il y a au moins un produit actif
        produits_actifs = self.produit_repo.get_actifs()
        assert len(produits_actifs) >= 1
        
        print("✅ Test generate_game_data - Génération complète réussie avec Repository")
    
    def test_save_and_load_template(self):
        """Test de sauvegarde et chargement de template avec Repository"""
        
        # Sauvegarder un template
        save_template("test_template")
        
        # Vérifier que le template existe
        templates = list_templates()
        assert "test_template" in templates
        
        # Charger le template
        loaded_config = load_template("test_template")
        # Vérifier que la configuration chargée contient les sections attendues
        assert "entreprises" in loaded_config
        assert "produits" in loaded_config
        assert "fournisseurs" in loaded_config
        
        print("✅ Test save_and_load_template - Template sauvegardé et chargé avec Repository")
    
    def test_get_current_config(self):
        """Test de récupération de la configuration actuelle avec Repository"""
        config = get_current_config()
        
        # Vérifier que la configuration contient les sections attendues
        assert "produits" in config
        assert "fournisseurs" in config
        assert "entreprises" in config
        
        print("✅ Test get_current_config - Configuration récupérée avec Repository")
    
    def test_ask_number_validation(self):
        """Test de validation des nombres"""
        # Test avec l'option 'choix' et un nombre valide
        with patch('builtins.input', side_effect=['c', '5']):
            result = ask_number("Test", 5, 1, 10)
            assert result == 5
        
        # Test avec l'option 'défaut'
        with patch('builtins.input', return_value='d'):
            result = ask_number("Test", 5, 1, 10)
            assert result == 5
        
        print("✅ Test ask_number_validation - Validation réussie")
    
    def test_ask_launch_game(self):
        """Test de la demande de lancement de jeu"""
        # Test avec choix '1' (lancer la simulation)
        with patch('builtins.input', return_value='1'):
            result = ask_launch_game()
            assert result is True
        
        print("✅ Test ask_launch_game - Lancement confirmé")
    
    def test_show_game_summary(self):
        """Test d'affichage du résumé de jeu avec Repository"""
        # Vider les repositories pour éviter les conflits d'ID
        self.produit_repo.clear()
        self.fournisseur_repo.clear()
        self.entreprise_repo.clear()
        
        # Générer quelques données de test
        produit = Produit(id=1, nom="Test", prix=100.0, actif=True, type=TypeProduit.matiere_premiere)
        self.produit_repo.add(produit)
        
        # Ajouter un fournisseur avec le produit
        fournisseur = Fournisseur(id=1, nom_entreprise="TestFournisseur", pays="France", continent="Europe", stock_produit={1: 10})
        self.fournisseur_repo.add(fournisseur)
        
        # Tester l'affichage du résumé
        show_game_summary()  # La fonction affiche mais ne retourne rien
        
        # Vérifier que les données sont bien présentes
        assert len(self.produit_repo.get_all()) > 0
        assert len(self.fournisseur_repo.get_all()) > 0
        
        print("✅ Test show_game_summary - Résumé affiché avec Repository")


class TestGameManagerPerformance:
    """Tests de performance pour le module game_manager avec Repository"""
    
    def test_generate_large_dataset(self):
        """Test de génération d'un grand dataset avec Repository"""
        config = {
            "produits": {
                "nombre": 50,  # Réduit pour éviter de dépasser la limite
                "prix_min": 1.0,
                "prix_max": 1000.0,
                "actifs_min": 25,
                "actifs_max": 40,
                "types": ["matiere_premiere", "consommable", "produit_fini"]
            },
            "fournisseurs": {
                "nombre": 20,
                "produits_min": 10,
                "produits_max": 50,
                "stock_min": 1,
                "stock_max": 1000
            },
            "entreprises": {
                "nombre": 10, 
                "budget_min": 1000.0, 
                "budget_max": 10000.0,
                "strategies": ["moins_cher", "par_type"],
                "types_preferes": ["matiere_premiere", "consommable", "produit_fini"]
            }
        }
        
        # Initialiser les Repository
        produit_repo = ProduitRepository()
        fournisseur_repo = FournisseurRepository()
        entreprise_repo = EntrepriseRepository()
        
        # Vider les Repository
        produit_repo.clear()
        fournisseur_repo.clear()
        entreprise_repo.clear()
        
        # Générer le grand dataset
        generate_game_data(config)
        
        # Vérifications
        assert len(produit_repo.get_all()) == 50
        assert len(fournisseur_repo.get_all()) == 20
        assert len(entreprise_repo.get_all()) == 10
        
        print("✅ Test generate_large_dataset - Performance OK avec Repository") 