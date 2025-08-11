#!/usr/bin/env python3
"""
Tests unitaires pour GameStateService
====================================

Tests pour vérifier le bon fonctionnement du service de persistance
de l'état du jeu.

Auteur: Assistant IA
Date: 2025-08-04
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from services.game_state_service import GameStateService
from models import Produit, Fournisseur, Entreprise, TypeProduit
from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository


class TestGameStateService:
    """
    Tests unitaires pour GameStateService.
    """
    
    def setup_method(self):
        """Initialise les données de test avant chaque test."""
        # Créer un dossier temporaire pour les tests
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Créer des données de test
        self.produit_test = Produit(
            id=1,
            nom="Test Produit",
            prix=100.0,
            actif=True,
            type=TypeProduit.consommable
        )
        
        self.fournisseur_test = Fournisseur(
            id=1,
            nom_entreprise="Test Fournisseur",
            pays="France",
            continent="Europe",
            stock_produit={1: 50}
        )
        
        self.entreprise_test = Entreprise(
            id=1,
            nom="Test Entreprise",
            pays="France",
            continent="Europe",
            budget=1000.0,
            budget_initial=1000.0,
            types_preferes=[TypeProduit.consommable],
            strategie="moins_cher"
        )
        
        # Créer le service avec le dossier temporaire
        with patch('services.game_state_service.Path') as mock_path:
            mock_path.return_value = self.data_dir
            self.service = GameStateService()
        
        # Vider les repositories pour éviter les conflits d'ID
        self.service.produit_repo.clear()
        self.service.fournisseur_repo.clear()
        self.service.entreprise_repo.clear()
    
    def teardown_method(self):
        """Nettoie après chaque test."""
        # Supprimer le dossier temporaire
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_game_state_success(self):
        """Test de sauvegarde réussie de l'état du jeu."""
        # Ajouter des données aux repositories
        self.service.produit_repo.add(self.produit_test)
        self.service.fournisseur_repo.add(self.fournisseur_test)
        self.service.entreprise_repo.add(self.entreprise_test)
        
        # Sauvegarder l'état
        filename = self.service.save_game_state("test_save.json")
        
        # Vérifier que le fichier a été créé
        filepath = self.data_dir / "test_save.json"
        assert filepath.exists(), "Le fichier de sauvegarde doit être créé"
        
        # Vérifier le contenu du fichier
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert "metadata" in data, "Le fichier doit contenir les métadonnées"
        assert "produits" in data, "Le fichier doit contenir les produits"
        assert "fournisseurs" in data, "Le fichier doit contenir les fournisseurs"
        assert "entreprises" in data, "Le fichier doit contenir les entreprises"
        assert "prix" in data, "Le fichier doit contenir les prix"
        
        print(f"✅ Test sauvegarde - Fichier créé: {filename}")
    
    def test_load_game_state_success(self):
        """Test de chargement réussi de l'état du jeu."""
        # Créer un fichier JSON de test
        test_data = {
            "metadata": {
                "date_creation": "2025-08-04T15:00:00",
                "version": "0.1"
            },
            "produits": [self.produit_test.model_dump()],
            "fournisseurs": [self.fournisseur_test.model_dump()],
            "entreprises": [self.entreprise_test.model_dump()],
            "prix": {"1_1": 100.0}
        }
        
        test_file = self.data_dir / "test_load.json"
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Charger l'état
        success = self.service.load_game_state("test_load.json")
        
        # Vérifier que le chargement a réussi
        assert success, "Le chargement doit réussir"
        
        # Vérifier que les données ont été chargées
        produits = self.service.produit_repo.get_all()
        fournisseurs = self.service.fournisseur_repo.get_all()
        entreprises = self.service.entreprise_repo.get_all()
        
        assert len(produits) == 1, "Un produit doit être chargé"
        assert len(fournisseurs) == 1, "Un fournisseur doit être chargé"
        assert len(entreprises) == 1, "Une entreprise doit être chargée"
        
        print("✅ Test chargement - Données chargées avec succès")
    
    def test_load_game_state_file_not_found(self):
        """Test de gestion d'erreur quand le fichier n'existe pas."""
        with pytest.raises(Exception) as exc_info:
            self.service.load_game_state("fichier_inexistant.json")
        
        assert "introuvable" in str(exc_info.value), "L'erreur doit mentionner que le fichier est introuvable"
        print("✅ Test erreur fichier introuvable")
    
    def test_load_game_state_corrupted_json(self):
        """Test de gestion d'erreur avec JSON corrompu."""
        # Créer un fichier JSON corrompu
        test_file = self.data_dir / "corrupted.json"
        with open(test_file, 'w') as f:
            f.write('{"invalid": json}')
        
        with pytest.raises(Exception) as exc_info:
            self.service.load_game_state("corrupted.json")
        
        # L'erreur JSON peut être dans le message d'erreur original
        error_msg = str(exc_info.value)
        assert "Expecting value" in error_msg or "JSON" in error_msg or "json" in error_msg, "L'erreur doit mentionner le JSON"
        print("✅ Test erreur JSON corrompu")
    
    def test_load_game_state_missing_keys(self):
        """Test de gestion d'erreur avec clés manquantes."""
        # Créer un fichier JSON incomplet
        test_data = {
            "metadata": {"date_creation": "2025-08-04T15:00:00"},
            # Clés manquantes: produits, fournisseurs, entreprises, prix
        }
        
        test_file = self.data_dir / "incomplete.json"
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        with pytest.raises(Exception) as exc_info:
            self.service.load_game_state("incomplete.json")
        
        assert "Clé manquante" in str(exc_info.value), "L'erreur doit mentionner les clés manquantes"
        print("✅ Test erreur clés manquantes")
    
    def test_get_latest_game_file(self):
        """Test de récupération du fichier de partie active."""
        # Créer le fichier de partie active
        test_data = {
            "metadata": {"date_creation": "2025-08-04T15:00:00", "version": "0.1"},
            "produits": [],
            "fournisseurs": [],
            "entreprises": [],
            "prix": {}
        }
        
        filepath = self.data_dir / "partie_active.json"
        with open(filepath, 'w') as f:
            json.dump(test_data, f)
        
        # Récupérer le fichier de partie active
        latest_file = self.service.get_latest_game_file()
        
        # Vérifier que le fichier de partie active est retourné
        assert latest_file == "partie_active.json", "Le fichier de partie active doit être retourné"
        print(f"✅ Test fichier de partie active - {latest_file}")
    
    def test_get_latest_game_file_no_files(self):
        """Test quand aucun fichier de partie n'existe."""
        latest_file = self.service.get_latest_game_file()
        
        assert latest_file is None, "Aucun fichier ne doit être retourné"
        print("✅ Test aucun fichier trouvé")
    
    def test_delete_game_file_success(self):
        """Test de suppression réussie d'un fichier."""
        # Créer un fichier de test
        test_file = self.data_dir / "test_delete.json"
        with open(test_file, 'w') as f:
            json.dump({"test": "data"}, f)
        
        # Supprimer le fichier
        success = self.service.delete_game_file("test_delete.json")
        
        assert success, "La suppression doit réussir"
        assert not test_file.exists(), "Le fichier doit être supprimé"
        print("✅ Test suppression fichier")
    
    def test_delete_game_file_not_found(self):
        """Test de suppression d'un fichier inexistant."""
        success = self.service.delete_game_file("fichier_inexistant.json")
        
        assert not success, "La suppression doit échouer pour un fichier inexistant"
        print("✅ Test suppression fichier inexistant")
    
    def test_save_and_load_integration(self):
        """Test d'intégration sauvegarde puis chargement."""
        # Ajouter des données
        self.service.produit_repo.add(self.produit_test)
        self.service.fournisseur_repo.add(self.fournisseur_test)
        self.service.entreprise_repo.add(self.entreprise_test)
        
        # Sauvegarder
        filename = self.service.save_game_state("integration_test.json")
        
        # Vider les repositories
        self.service.produit_repo.clear()
        self.service.fournisseur_repo.clear()
        self.service.entreprise_repo.clear()
        
        # Vérifier qu'ils sont vides
        assert len(self.service.produit_repo.get_all()) == 0, "Le repository doit être vide"
        
        # Recharger
        success = self.service.load_game_state("integration_test.json")
        
        # Vérifier que les données sont restaurées
        produits = self.service.produit_repo.get_all()
        fournisseurs = self.service.fournisseur_repo.get_all()
        entreprises = self.service.entreprise_repo.get_all()
        
        assert len(produits) == 1, "Le produit doit être restauré"
        assert len(fournisseurs) == 1, "Le fournisseur doit être restauré"
        assert len(entreprises) == 1, "L'entreprise doit être restaurée"
        
        # Vérifier que les données sont identiques
        produit_restaure = produits[0]
        assert produit_restaure.nom == self.produit_test.nom, "Le nom du produit doit être identique"
        assert produit_restaure.prix == self.produit_test.prix, "Le prix du produit doit être identique"
        
        print("✅ Test intégration sauvegarde/chargement")


if __name__ == "__main__":
    """
    Point d'entrée pour exécuter les tests directement.
    """
    pytest.main([__file__, "-v"]) 