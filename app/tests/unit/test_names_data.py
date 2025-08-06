#!/usr/bin/env python3
"""
Tests unitaires pour le système de noms TradeSim
===============================================

Ce module teste le système de noms réalistes de TradeSim :
- Validation des données de noms (entreprises, fournisseurs, produits)
- Tests du NameManager (sélection aléatoire, gestion des doublons)
- Tests de cohérence géographique (pays/continent)

Tests inclus :
- Validation des listes de données
- Tests de sélection aléatoire
- Tests de gestion des doublons
- Tests de réinitialisation
- Tests de cohérence géographique

Pour lancer ces tests manuellement :
```bash
# Activer l'environnement
source ../venv/bin/activate

# Lancer les tests de noms
python3 -m pytest tests/unit/test_names_data.py -v

# Lancer tous les tests
python3 -m pytest tests/ -v
```

Auteur: Assistant IA
Date: 2025-01-27
"""

import pytest
from data.names_data import ENTREPRISES_DATA, FOURNISSEURS_DATA, PRODUITS_DATA
from services.name_manager import NameManager


class TestNamesData:
    """
    Tests pour les données de noms (names_data.py).
    
    Valide la structure et la cohérence des listes de noms.
    """
    
    def test_entreprises_data_structure(self):
        """Teste la structure des données d'entreprises."""
        assert len(ENTREPRISES_DATA) == 42, "Il doit y avoir exactement 42 entreprises"
        
        for entreprise in ENTREPRISES_DATA:
            assert "nom" in entreprise, "Chaque entreprise doit avoir un nom"
            assert "pays" in entreprise, "Chaque entreprise doit avoir un pays"
            assert "continent" in entreprise, "Chaque entreprise doit avoir un continent"
            assert isinstance(entreprise["nom"], str), "Le nom doit être une chaîne"
            assert isinstance(entreprise["pays"], str), "Le pays doit être une chaîne"
            assert isinstance(entreprise["continent"], str), "Le continent doit être une chaîne"
    
    def test_fournisseurs_data_structure(self):
        """Teste la structure des données de fournisseurs."""
        assert len(FOURNISSEURS_DATA) == 42, "Il doit y avoir exactement 42 fournisseurs"
        
        for fournisseur in FOURNISSEURS_DATA:
            assert "nom" in fournisseur, "Chaque fournisseur doit avoir un nom"
            assert "pays" in fournisseur, "Chaque fournisseur doit avoir un pays"
            assert "continent" in fournisseur, "Chaque fournisseur doit avoir un continent"
            assert isinstance(fournisseur["nom"], str), "Le nom doit être une chaîne"
            assert isinstance(fournisseur["pays"], str), "Le pays doit être une chaîne"
            assert isinstance(fournisseur["continent"], str), "Le continent doit être une chaîne"
    
    def test_produits_data_structure(self):
        """Teste la structure des données de produits."""
        assert len(PRODUITS_DATA) == 61, "Il doit y avoir exactement 61 produits"
        
        for produit in PRODUITS_DATA:
            assert "nom" in produit, "Chaque produit doit avoir un nom"
            assert "type" in produit, "Chaque produit doit avoir un type"
            assert isinstance(produit["nom"], str), "Le nom doit être une chaîne"
            assert isinstance(produit["type"], str), "Le type doit être une chaîne"
    
    def test_produits_types_distribution(self):
        """Teste la distribution des types de produits."""
        types_count = {}
        for produit in PRODUITS_DATA:
            type_produit = produit["type"]
            types_count[type_produit] = types_count.get(type_produit, 0) + 1
        
        assert types_count["produit_fini"] == 21, "Il doit y avoir 21 produits finis"
        assert types_count["consommable"] == 20, "Il doit y avoir 20 consommables"
        assert types_count["matiere_premiere"] == 20, "Il doit y avoir 20 matières premières"
    
    def test_geographic_consistency(self):
        """Teste la cohérence géographique pays/continent."""
        # Test entreprises
        for entreprise in ENTREPRISES_DATA:
            pays = entreprise["pays"]
            continent = entreprise["continent"]
            self._assert_geographic_consistency(pays, continent)
        
        # Test fournisseurs
        for fournisseur in FOURNISSEURS_DATA:
            pays = fournisseur["pays"]
            continent = fournisseur["continent"]
            self._assert_geographic_consistency(pays, continent)
    
    def _assert_geographic_consistency(self, pays: str, continent: str):
        """Vérifie la cohérence géographique pays/continent."""
        # Mapping géographique de base
        europe_pays = ["France", "Allemagne", "Espagne", "Italie", "Pays-Bas", "Belgique", 
                      "Suède", "Norvège", "Danemark", "Pologne", "République tchèque", 
                      "Autriche", "Finlande", "Suisse"]
        asie_pays = ["Chine", "Japon", "Corée du Sud", "Inde", "Singapour", "Thaïlande",
                    "Vietnam", "Malaisie", "Indonésie", "Taïwan", "Philippines"]
        amerique_nord_pays = ["États-Unis", "Canada", "Mexique"]
        amerique_sud_pays = ["Brésil", "Argentine", "Chili", "Colombie", "Pérou"]
        afrique_pays = ["Afrique du Sud", "Égypte", "Maroc", "Nigeria", "Kenya"]
        oceanie_pays = ["Australie", "Nouvelle-Zélande"]
        
        if pays in europe_pays:
            assert continent == "Europe", f"{pays} doit être en Europe"
        elif pays in asie_pays:
            assert continent == "Asie", f"{pays} doit être en Asie"
        elif pays in amerique_nord_pays:
            assert continent == "Amérique du Nord", f"{pays} doit être en Amérique du Nord"
        elif pays in amerique_sud_pays:
            assert continent == "Amérique du Sud", f"{pays} doit être en Amérique du Sud"
        elif pays in afrique_pays:
            assert continent == "Afrique", f"{pays} doit être en Afrique"
        elif pays in oceanie_pays:
            assert continent == "Océanie", f"{pays} doit être en Océanie"
        else:
            pytest.fail(f"Pays non reconnu : {pays}")
    
    def test_unique_names(self):
        """Teste l'unicité des noms dans chaque liste."""
        # Test entreprises
        noms_entreprises = [e["nom"] for e in ENTREPRISES_DATA]
        assert len(noms_entreprises) == len(set(noms_entreprises)), "Noms d'entreprises non uniques"
        
        # Test fournisseurs
        noms_fournisseurs = [f["nom"] for f in FOURNISSEURS_DATA]
        assert len(noms_fournisseurs) == len(set(noms_fournisseurs)), "Noms de fournisseurs non uniques"
        
        # Test produits
        noms_produits = [p["nom"] for p in PRODUITS_DATA]
        assert len(noms_produits) == len(set(noms_produits)), "Noms de produits non uniques"


class TestNameManager:
    """
    Tests pour le NameManager.
    
    Valide la sélection aléatoire et la gestion des doublons.
    """
    
    def setup_method(self):
        """Initialise un nouveau NameManager pour chaque test."""
        self.name_manager = NameManager()
    
    def test_initial_state(self):
        """Teste l'état initial du NameManager."""
        stats = self.name_manager.get_stats()
        assert stats["entreprises_utilisees"] == 0
        assert stats["fournisseurs_utilises"] == 0
        assert stats["produits_utilises"] == 0
    
    def test_get_unique_entreprise(self):
        """Teste la sélection d'entreprises uniques."""
        # Sélectionner plusieurs entreprises
        entreprises = []
        for _ in range(5):
            entreprise = self.name_manager.get_unique_entreprise()
            entreprises.append(entreprise)
        
        # Vérifier qu'elles sont toutes différentes
        noms = [e["nom"] for e in entreprises]
        assert len(noms) == len(set(noms)), "Noms d'entreprises non uniques"
        
        # Vérifier la structure
        for entreprise in entreprises:
            assert "nom" in entreprise
            assert "pays" in entreprise
            assert "continent" in entreprise
    
    def test_get_unique_fournisseur(self):
        """Teste la sélection de fournisseurs uniques."""
        # Sélectionner plusieurs fournisseurs
        fournisseurs = []
        for _ in range(5):
            fournisseur = self.name_manager.get_unique_fournisseur()
            fournisseurs.append(fournisseur)
        
        # Vérifier qu'elles sont toutes différentes
        noms = [f["nom"] for f in fournisseurs]
        assert len(noms) == len(set(noms)), "Noms de fournisseurs non uniques"
        
        # Vérifier la structure
        for fournisseur in fournisseurs:
            assert "nom" in fournisseur
            assert "pays" in fournisseur
            assert "continent" in fournisseur
    
    def test_get_unique_produit(self):
        """Teste la sélection de produits uniques."""
        # Sélectionner plusieurs produits
        produits = []
        for _ in range(10):
            produit = self.name_manager.get_unique_produit()
            produits.append(produit)
        
        # Vérifier qu'elles sont toutes différentes
        noms = [p["nom"] for p in produits]
        assert len(noms) == len(set(noms)), "Noms de produits non uniques"
        
        # Vérifier la structure
        for produit in produits:
            assert "nom" in produit
            assert "type" in produit
    
    def test_get_unique_produit_by_type(self):
        """Teste la sélection de produits par type."""
        # Test par type
        for type_produit in ["produit_fini", "consommable", "matiere_premiere"]:
            produit = self.name_manager.get_unique_produit(type_produit)
            assert produit["type"] == type_produit
    
    def test_reset_functionality(self):
        """Teste la fonctionnalité de réinitialisation."""
        # Utiliser quelques noms
        self.name_manager.get_unique_entreprise()
        self.name_manager.get_unique_fournisseur()
        self.name_manager.get_unique_produit()
        
        # Vérifier qu'ils sont utilisés
        stats_before = self.name_manager.get_stats()
        assert stats_before["entreprises_utilisees"] == 1
        assert stats_before["fournisseurs_utilises"] == 1
        assert stats_before["produits_utilises"] == 1
        
        # Réinitialiser
        self.name_manager.reset()
        
        # Vérifier que tout est réinitialisé
        stats_after = self.name_manager.get_stats()
        assert stats_after["entreprises_utilisees"] == 0
        assert stats_after["fournisseurs_utilises"] == 0
        assert stats_after["produits_utilises"] == 0
    
    def test_multiple_selection(self):
        """Teste la sélection multiple."""
        # Test entreprises
        entreprises = self.name_manager.get_multiple_entreprises(3)
        assert len(entreprises) == 3
        noms = [e["nom"] for e in entreprises]
        assert len(noms) == len(set(noms))
        
        # Test fournisseurs
        fournisseurs = self.name_manager.get_multiple_fournisseurs(3)
        assert len(fournisseurs) == 3
        noms = [f["nom"] for f in fournisseurs]
        assert len(noms) == len(set(noms))
        
        # Test produits
        produits = self.name_manager.get_multiple_produits(5)
        assert len(produits) == 5
        noms = [p["nom"] for p in produits]
        assert len(noms) == len(set(noms))
    
    def test_multiple_selection_by_type(self):
        """Teste la sélection multiple par type."""
        # Test produits finis
        produits_finis = self.name_manager.get_multiple_produits(5, "produit_fini")
        assert len(produits_finis) == 5
        for produit in produits_finis:
            assert produit["type"] == "produit_fini"
    
    def test_error_handling(self):
        """Teste la gestion d'erreurs."""
        # Essayer de sélectionner plus d'entreprises que disponibles
        with pytest.raises(ValueError, match="Demande de 50 entreprises"):
            self.name_manager.get_multiple_entreprises(50)
        
        # Essayer de sélectionner plus de fournisseurs que disponibles
        with pytest.raises(ValueError, match="Demande de 50 fournisseurs"):
            self.name_manager.get_multiple_fournisseurs(50)
        
        # Essayer de sélectionner plus de produits que disponibles
        with pytest.raises(ValueError, match="Demande de 100 produits"):
            self.name_manager.get_multiple_produits(100)
    
    def test_stats_functionality(self):
        """Teste la fonctionnalité de statistiques."""
        # État initial
        stats = self.name_manager.get_stats()
        assert stats["entreprises_utilisees"] == 0
        assert stats["entreprises_disponibles"] == 42
        assert stats["fournisseurs_utilises"] == 0
        assert stats["fournisseurs_disponibles"] == 42
        assert stats["produits_utilises"] == 0
        assert stats["produits_disponibles"] == 61
        
        # Après utilisation
        self.name_manager.get_unique_entreprise()
        self.name_manager.get_unique_fournisseur()
        self.name_manager.get_unique_produit()
        
        stats = self.name_manager.get_stats()
        assert stats["entreprises_utilisees"] == 1
        assert stats["fournisseurs_utilises"] == 1
        assert stats["produits_utilises"] == 1 