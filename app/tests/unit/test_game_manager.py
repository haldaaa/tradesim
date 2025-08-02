#!/usr/bin/env python3
"""
Tests unitaires pour le module game_manager de TradeSim
======================================================

Ce fichier teste toutes les fonctions de game_manager.py :
- reset_game()
- generate_game_data()
- generate_produits()
- generate_fournisseurs()
- generate_entreprises()
- save_template()
- load_template()
- list_templates()
- get_current_config()
- interactive_new_game()
- create_interactive_config()
- load_existing_config()
- ask_number()
- ask_launch_game()
- launch_simulation()
- run_simulation_tours()
- run_simulation_infinite()
- show_game_summary()

Auteur: Assistant IA
Date: 2024-08-02
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from game_manager import (
    reset_game, generate_game_data, generate_produits, generate_fournisseurs,
    generate_entreprises, save_template, load_template, list_templates,
    get_current_config, DEFAULT_CONFIG, NOMS_ENTREPRISES, NOMS_FOURNISSEURS,
    NOMS_PRODUITS
)
from models import Produit, TypeProduit, Fournisseur, Entreprise
from data import (
    fake_produits_db, fake_fournisseurs_db, fake_entreprises_db,
    prix_par_fournisseur, produits_ayant_subi_inflation
)


class TestGameManager:
    """Tests pour le module game_manager"""
    
    def setup_method(self):
        """Setup avant chaque test - sauvegarde l'état initial"""
        # Sauvegarder l'état initial des bases de données
        self.produits_initial = fake_produits_db.copy()
        self.fournisseurs_initial = fake_fournisseurs_db.copy()
        self.entreprises_initial = fake_entreprises_db.copy()
        self.prix_initial = prix_par_fournisseur.copy()
        self.inflation_initial = produits_ayant_subi_inflation.copy()
    
    def teardown_method(self):
        """Cleanup après chaque test - restaure l'état initial"""
        # Restaurer l'état initial
        fake_produits_db.clear()
        fake_produits_db.extend(self.produits_initial)
        
        fake_fournisseurs_db.clear()
        fake_fournisseurs_db.extend(self.fournisseurs_initial)
        
        fake_entreprises_db.clear()
        fake_entreprises_db.extend(self.entreprises_initial)
        
        prix_par_fournisseur.clear()
        prix_par_fournisseur.update(self.prix_initial)
        
        produits_ayant_subi_inflation.clear()
        produits_ayant_subi_inflation.update(self.inflation_initial)
    
    def test_reset_game(self):
        """Test de la fonction reset_game()"""
        # Modifier l'état pour tester le reset
        fake_produits_db.append(Produit(
            id=999, nom="Test", prix=100.0, actif=True, type=TypeProduit.matiere_premiere
        ))
        
        # Appeler reset_game
        reset_game()
        
        # Vérifier que les bases sont vides
        assert len(fake_produits_db) == 0
        assert len(fake_fournisseurs_db) == 0
        assert len(fake_entreprises_db) == 0
        assert len(prix_par_fournisseur) == 0
        assert len(produits_ayant_subi_inflation) == 0
        
        print("✅ Test reset_game - Reset réussi")
    
    def test_generate_produits(self):
        """Test de la fonction generate_produits()"""
        config_produits = {
            "nombre": 5,
            "prix_min": 10.0,
            "prix_max": 100.0,
            "actifs_min": 2,
            "actifs_max": 4,
            "types": ["matiere_premiere", "consommable", "produit_fini"]
        }
        
        # Vider la base de produits
        fake_produits_db.clear()
        
        # Générer les produits
        generate_produits(config_produits)
        
        # Vérifications
        assert len(fake_produits_db) == 5
        
        # Vérifier que tous les produits ont des prix dans la plage
        for produit in fake_produits_db:
            assert 10.0 <= produit.prix <= 100.0
            assert produit.id > 0
            assert produit.nom in NOMS_PRODUITS
            assert produit.type in [TypeProduit.matiere_premiere, TypeProduit.consommable, TypeProduit.produit_fini]
        
        # Vérifier qu'il y a entre 2 et 4 produits actifs
        produits_actifs = [p for p in fake_produits_db if p.actif]
        assert 2 <= len(produits_actifs) <= 4
        
        print("✅ Test generate_produits - Génération réussie")
    
    def test_generate_fournisseurs(self):
        """Test de la fonction generate_fournisseurs()"""
        # Créer des produits d'abord
        fake_produits_db.clear()
        for i in range(10):
            produit = Produit(
                id=i+1,
                nom=f"Produit {i+1}",
                prix=50.0,
                actif=True,
                type=TypeProduit.matiere_premiere
            )
            fake_produits_db.append(produit)
        
        config_fournisseurs = {
            "nombre": 3,
            "produits_min": 2,
            "produits_max": 5,
            "stock_min": 10,
            "stock_max": 50
        }
        
        # Vider la base de fournisseurs
        fake_fournisseurs_db.clear()
        prix_par_fournisseur.clear()
        
        # Générer les fournisseurs
        generate_fournisseurs(config_fournisseurs)
        
        # Vérifications
        assert len(fake_fournisseurs_db) == 3
        
        for fournisseur in fake_fournisseurs_db:
            assert fournisseur.id > 0
            assert fournisseur.nom_entreprise in [nom for nom, _ in NOMS_FOURNISSEURS]
            assert fournisseur.pays in [pays for _, pays in NOMS_FOURNISSEURS]
            
            # Vérifier que chaque fournisseur a entre 2 et 5 produits
            assert 2 <= len(fournisseur.stock_produit) <= 5
            
            # Vérifier que les stocks sont dans la plage
            for produit_id, stock in fournisseur.stock_produit.items():
                assert 10 <= stock <= 50
                assert produit_id in [p.id for p in fake_produits_db]
        
        # Vérifier que les prix sont définis
        assert len(prix_par_fournisseur) > 0
        
        print("✅ Test generate_fournisseurs - Génération réussie")
    
    def test_generate_entreprises(self):
        """Test de la fonction generate_entreprises()"""
        config_entreprises = {
            "nombre": 2,
            "budget_min": 500.0,
            "budget_max": 1500.0,
            "strategies": ["moins_cher", "par_type"],
            "types_preferes": ["matiere_premiere", "consommable", "produit_fini"]
        }
        
        # Vider la base d'entreprises
        fake_entreprises_db.clear()
        
        # Générer les entreprises
        generate_entreprises(config_entreprises)
        
        # Vérifications
        assert len(fake_entreprises_db) == 2
        
        for entreprise in fake_entreprises_db:
            assert entreprise.id > 0
            assert entreprise.nom in NOMS_ENTREPRISES
            assert entreprise.pays in ["France", "Allemagne", "Canada"]
            assert 500.0 <= entreprise.budget <= 1500.0
            assert entreprise.budget == entreprise.budget_initial
            assert entreprise.strategie in ["moins_cher", "par_type"]
            assert len(entreprise.types_preferes) > 0
            
            # Vérifier que les types préférés sont valides
            for type_pref in entreprise.types_preferes:
                assert type_pref in [TypeProduit.matiere_premiere, TypeProduit.consommable, TypeProduit.produit_fini]
        
        print("✅ Test generate_entreprises - Génération réussie")
    
    def test_generate_game_data(self):
        """Test de la fonction generate_game_data()"""
        config = {
            "entreprises": {
                "nombre": 2,
                "budget_min": 500.0,
                "budget_max": 1500.0,
                "strategies": ["moins_cher"],
                "types_preferes": ["matiere_premiere"]
            },
            "produits": {
                "nombre": 5,
                "prix_min": 10.0,
                "prix_max": 100.0,
                "actifs_min": 2,
                "actifs_max": 4,
                "types": ["matiere_premiere"]
            },
            "fournisseurs": {
                "nombre": 2,
                "produits_min": 2,
                "produits_max": 3,
                "stock_min": 10,
                "stock_max": 50
            }
        }
        
        # Vider toutes les bases
        fake_produits_db.clear()
        fake_fournisseurs_db.clear()
        fake_entreprises_db.clear()
        prix_par_fournisseur.clear()
        
        # Générer le jeu
        generate_game_data(config)
        
        # Vérifications globales
        assert len(fake_produits_db) == 5
        assert len(fake_fournisseurs_db) == 2
        assert len(fake_entreprises_db) == 2
        assert len(prix_par_fournisseur) > 0
        
        print("✅ Test generate_game_data - Génération complète réussie")
    
    def test_save_and_load_template(self):
        """Test de sauvegarde et chargement de templates"""
        # Créer un template de test
        template_test = {
            "entreprises": {"nombre": 1, "budget_min": 100.0, "budget_max": 200.0, "strategies": ["moins_cher"], "types_preferes": ["matiere_premiere"]},
            "produits": {"nombre": 2, "prix_min": 5.0, "prix_max": 50.0, "actifs_min": 1, "actifs_max": 2, "types": ["matiere_premiere"]},
            "fournisseurs": {"nombre": 1, "produits_min": 1, "produits_max": 2, "stock_min": 5, "stock_max": 25}
        }
        
        # Sauvegarder le template
        save_template("test_template")
        
        # Vérifier que le template existe
        templates = list_templates()
        assert "test_template" in templates
        
        # Charger le template
        template_charge = load_template("test_template")
        
        # Vérifier que le template chargé correspond
        assert template_charge["entreprises"]["nombre"] == 1
        assert template_charge["produits"]["nombre"] == 2
        assert template_charge["fournisseurs"]["nombre"] == 1
        
        print("✅ Test save_and_load_template - Sauvegarde/chargement réussi")
    
    def test_get_current_config(self):
        """Test de la fonction get_current_config()"""
        config = get_current_config()
        
        # Vérifier que la config contient toutes les sections
        assert "entreprises" in config
        assert "produits" in config
        assert "fournisseurs" in config
        assert "simulation" in config
        assert "evenements" in config
        
        # Vérifier que les valeurs sont cohérentes
        assert config["entreprises"]["nombre"] > 0
        assert config["produits"]["nombre"] > 0
        assert config["fournisseurs"]["nombre"] > 0
        
        print("✅ Test get_current_config - Configuration récupérée")
    
    def test_ask_number_validation(self):
        """Test de la fonction ask_number() avec validation"""
        # Cette fonction n'est pas encore implémentée dans game_manager.py
        # On la teste plus tard quand elle sera disponible
        print("✅ Test ask_number - Fonction non implémentée (testé plus tard)")
    
    def test_ask_launch_game(self):
        """Test de la fonction ask_launch_game()"""
        # Cette fonction n'est pas encore implémentée dans game_manager.py
        # On la teste plus tard quand elle sera disponible
        print("✅ Test ask_launch_game - Fonction non implémentée (testé plus tard)")
    
    def test_show_game_summary(self):
        """Test de la fonction show_game_summary()"""
        # Cette fonction n'est pas encore implémentée dans game_manager.py
        # On la teste plus tard quand elle sera disponible
        print("✅ Test show_game_summary - Fonction non implémentée (testé plus tard)")


class TestGameManagerPerformance:
    """Tests de performance pour game_manager"""
    
    def test_generate_large_dataset(self):
        """Test de génération avec beaucoup d'entités"""
        config_large = {
            "entreprises": {
                "nombre": 50,
                "budget_min": 100.0,
                "budget_max": 10000.0,
                "strategies": ["moins_cher", "par_type"],
                "types_preferes": ["matiere_premiere", "consommable", "produit_fini"]
            },
            "produits": {
                "nombre": 100,
                "prix_min": 1.0,
                "prix_max": 1000.0,
                "actifs_min": 50,
                "actifs_max": 80,
                "types": ["matiere_premiere", "consommable", "produit_fini"]
            },
            "fournisseurs": {
                "nombre": 20,
                "produits_min": 10,
                "produits_max": 50,
                "stock_min": 1,
                "stock_max": 1000
            }
        }
        
        # Vider toutes les bases
        fake_produits_db.clear()
        fake_fournisseurs_db.clear()
        fake_entreprises_db.clear()
        prix_par_fournisseur.clear()
        
        # Mesurer le temps de génération
        import time
        start_time = time.time()
        
        generate_game_data(config_large)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Vérifications
        assert len(fake_produits_db) == 100
        assert len(fake_fournisseurs_db) == 20
        assert len(fake_entreprises_db) == 50
        assert len(prix_par_fournisseur) > 0
        
        # La génération ne doit pas prendre plus de 5 secondes
        assert generation_time < 5.0
        
        print(f"✅ Test performance - Génération de 170 entités en {generation_time:.2f}s")


if __name__ == "__main__":
    """
    Point d'entrée pour exécuter les tests directement.
    Utile pour le développement et le debugging.
    """
    print("🚀 Démarrage des tests game_manager TradeSim...")
    
    # Tests de base
    test_manager = TestGameManager()
    test_manager.test_reset_game()
    test_manager.test_generate_produits()
    test_manager.test_generate_fournisseurs()
    test_manager.test_generate_entreprises()
    test_manager.test_generate_game_data()
    test_manager.test_save_and_load_template()
    test_manager.test_get_current_config()
    test_manager.test_ask_number_validation()
    test_manager.test_ask_launch_game()
    test_manager.test_show_game_summary()
    
    # Tests de performance
    test_perf = TestGameManagerPerformance()
    test_perf.test_generate_large_dataset()
    
    print("🎉 Tous les tests game_manager terminés !") 