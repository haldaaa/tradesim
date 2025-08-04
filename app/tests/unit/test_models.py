#!/usr/bin/env python3
"""
Tests unitaires pour les modèles Pydantic de TradeSim
====================================================

Ce fichier teste la validation et la création de tous les modèles :
- Produit (avec TypeProduit enum)
- Fournisseur (avec stock_produit dict)
- Entreprise (avec types_preferes et strategie)
- ProduitChezFournisseur
- FournisseurComplet
- Transaction

Auteur: Assistant IA
Date: 2024-08-02
"""

import pytest
from pydantic import ValidationError
from models import (
    Produit, TypeProduit, Fournisseur, Entreprise,
    ProduitChezFournisseur, FournisseurComplet, Transaction
)
from datetime import datetime, timezone


class TestTypeProduit:
    """Tests pour l'enum TypeProduit"""
    
    def test_type_produit_values(self):
        """Test que tous les types de produit sont valides"""
        assert TypeProduit.matiere_premiere == "matiere_premiere"
        assert TypeProduit.consommable == "consommable"
        assert TypeProduit.produit_fini == "produit_fini"
        
        # Test que les valeurs sont bien des strings
        assert isinstance(TypeProduit.matiere_premiere, str)
        assert isinstance(TypeProduit.consommable, str)
        assert isinstance(TypeProduit.produit_fini, str)
        
        print("✅ Test TypeProduit - Tous les types sont valides")


class TestProduit:
    """Tests pour le modèle Produit"""
    
    def test_produit_creation_valide(self):
        """Test création d'un produit avec tous les paramètres valides"""
        produit = Produit(
            id=1,
            nom="Test Produit",
            prix=100.0,
            actif=True,
            type=TypeProduit.matiere_premiere
        )
        
        assert produit.id == 1
        assert produit.nom == "Test Produit"
        assert produit.prix == 100.0
        assert produit.actif == True
        assert produit.type == TypeProduit.matiere_premiere
        
        print("✅ Test Produit - Création valide réussie")
    
    def test_produit_prix_negatif(self):
        """Test que le prix négatif est accepté (pas de contrainte dans le modèle)"""
        produit = Produit(
            id=1,
            nom="Test Produit",
            prix=-50.0,  # Prix négatif
            actif=True,
            type=TypeProduit.matiere_premiere
        )
        assert produit.prix == -50.0
        print("✅ Test Produit - Prix négatif accepté (pas de contrainte)")
    
    def test_produit_id_negatif(self):
        """Test que l'ID négatif est accepté (pas de contrainte dans le modèle)"""
        produit = Produit(
            id=-1,  # ID négatif
            nom="Test Produit",
            prix=100.0,
            actif=True,
            type=TypeProduit.matiere_premiere
        )
        assert produit.id == -1
        print("✅ Test Produit - ID négatif accepté (pas de contrainte)")
    
    def test_produit_nom_vide(self):
        """Test que le nom vide est accepté (pas de contrainte dans le modèle)"""
        produit = Produit(
            id=1,
            nom="",  # Nom vide
            prix=100.0,
            actif=True,
            type=TypeProduit.matiere_premiere
        )
        assert produit.nom == ""
        print("✅ Test Produit - Nom vide accepté (pas de contrainte)")
    
    def test_produit_tous_types(self):
        """Test création avec tous les types de produit"""
        types_testes = [TypeProduit.matiere_premiere, TypeProduit.consommable, TypeProduit.produit_fini]
        
        for i, type_produit in enumerate(types_testes):
            produit = Produit(
                id=i + 1,
                nom=f"Produit {type_produit.value}",
                prix=100.0,
                actif=True,
                type=type_produit
            )
            assert produit.type == type_produit
            
        print("✅ Test Produit - Tous les types fonctionnent")


class TestFournisseur:
    """Tests pour le modèle Fournisseur"""
    
    def test_fournisseur_creation_valide(self):
        """Test création d'un fournisseur avec stock valide"""
        fournisseur = Fournisseur(
            id=1,
            nom_entreprise="Test Fournisseur",
            pays="France",
            stock_produit={1: 100, 2: 50}
        )
        
        assert fournisseur.id == 1
        assert fournisseur.nom_entreprise == "Test Fournisseur"
        assert fournisseur.pays == "France"
        assert fournisseur.stock_produit == {1: 100, 2: 50}
        
        print("✅ Test Fournisseur - Création valide réussie")
    
    def test_fournisseur_stock_negatif(self):
        """Test que le stock négatif est accepté (pas de contrainte dans le modèle)"""
        fournisseur = Fournisseur(
            id=1,
            nom_entreprise="Test Fournisseur",
            pays="France",
            stock_produit={1: -10}  # Stock négatif
        )
        assert fournisseur.stock_produit[1] == -10
        print("✅ Test Fournisseur - Stock négatif accepté (pas de contrainte)")
    
    def test_fournisseur_stock_vide(self):
        """Test fournisseur sans stock (valide)"""
        fournisseur = Fournisseur(
            id=1,
            nom_entreprise="Test Fournisseur",
            pays="France",
            stock_produit={}
        )
        
        assert fournisseur.stock_produit == {}
        print("✅ Test Fournisseur - Stock vide accepté")


class TestEntreprise:
    """Tests pour le modèle Entreprise"""
    
    def test_entreprise_creation_valide(self):
        """Test création d'une entreprise avec tous les paramètres"""
        entreprise = Entreprise(
            id=1,
            nom="Test Entreprise",
            pays="France",
            budget=1000.0,
            budget_initial=1000.0,
            types_preferes=[TypeProduit.matiere_premiere, TypeProduit.consommable],
            strategie="moins_cher"
        )
        
        assert entreprise.id == 1
        assert entreprise.nom == "Test Entreprise"
        assert entreprise.pays == "France"
        assert entreprise.budget == 1000.0
        assert entreprise.budget_initial == 1000.0
        assert entreprise.types_preferes == [TypeProduit.matiere_premiere, TypeProduit.consommable]
        assert entreprise.strategie == "moins_cher"
        
        print("✅ Test Entreprise - Création valide réussie")
    
    def test_entreprise_budget_negatif(self):
        """Test que le budget négatif est accepté (pas de contrainte dans le modèle)"""
        entreprise = Entreprise(
            id=1,
            nom="Test Entreprise",
            pays="France",
            budget=-100.0,  # Budget négatif
            budget_initial=1000.0,
            types_preferes=[TypeProduit.matiere_premiere],
            strategie="moins_cher"
        )
        assert entreprise.budget == -100.0
        print("✅ Test Entreprise - Budget négatif accepté (pas de contrainte)")
    
    def test_entreprise_strategie_invalide(self):
        """Test que la stratégie invalide est acceptée (pas de contrainte dans le modèle)"""
        entreprise = Entreprise(
            id=1,
            nom="Test Entreprise",
            pays="France",
            budget=1000.0,
            budget_initial=1000.0,
            types_preferes=[TypeProduit.matiere_premiere],
            strategie="strategie_invalide"  # Stratégie invalide
        )
        assert entreprise.strategie == "strategie_invalide"
        print("✅ Test Entreprise - Stratégie invalide acceptée (pas de contrainte)")
    
    def test_entreprise_types_preferes_vide(self):
        """Test entreprise sans types préférés (valide)"""
        entreprise = Entreprise(
            id=1,
            nom="Test Entreprise",
            pays="France",
            budget=1000.0,
            budget_initial=1000.0,
            types_preferes=[],  # Liste vide
            strategie="moins_cher"
        )
        
        assert entreprise.types_preferes == []
        print("✅ Test Entreprise - Types préférés vides acceptés")


class TestProduitChezFournisseur:
    """Tests pour le modèle ProduitChezFournisseur"""
    
    def test_produit_chez_fournisseur_creation(self):
        """Test création d'un produit chez fournisseur"""
        produit_fournisseur = ProduitChezFournisseur(
            produit_id=1,
            nom="Test Produit",
            stock=100,
            prix_unitaire=50.0
        )
        
        assert produit_fournisseur.produit_id == 1
        assert produit_fournisseur.nom == "Test Produit"
        assert produit_fournisseur.stock == 100
        assert produit_fournisseur.prix_unitaire == 50.0
        
        print("✅ Test ProduitChezFournisseur - Création réussie")


class TestFournisseurComplet:
    """Tests pour le modèle FournisseurComplet"""
    
    def test_fournisseur_complet_creation(self):
        """Test création d'un fournisseur complet avec produits"""
        produits = [
            ProduitChezFournisseur(
                produit_id=1,
                nom="Produit 1",
                stock=100,
                prix_unitaire=50.0
            ),
            ProduitChezFournisseur(
                produit_id=2,
                nom="Produit 2",
                stock=50,
                prix_unitaire=25.0
            )
        ]
        
        fournisseur_complet = FournisseurComplet(
            id=1,
            nom_entreprise="Test Fournisseur",
            pays="France",
            produits=produits
        )
        
        assert fournisseur_complet.id == 1
        assert fournisseur_complet.nom_entreprise == "Test Fournisseur"
        assert fournisseur_complet.pays == "France"
        assert len(fournisseur_complet.produits) == 2
        
        print("✅ Test FournisseurComplet - Création réussie")


class TestTransaction:
    """Tests pour le modèle Transaction"""
    
    def test_transaction_creation_valide(self):
        """Test création d'une transaction valide"""
        timestamp = datetime.now(timezone.utc)
        transaction = Transaction(
            timestamp=timestamp,
            entreprise_id=1,
            fournisseur_id=1,
            produit_id=1,
            produit_nom="Test Produit",
            quantite=5,
            prix_unitaire=100.0,
            total=500.0,
            succes=True
        )
        
        assert transaction.entreprise_id == 1
        assert transaction.fournisseur_id == 1
        assert transaction.produit_id == 1
        assert transaction.produit_nom == "Test Produit"
        assert transaction.quantite == 5
        assert transaction.prix_unitaire == 100.0
        assert transaction.total == 500.0
        assert transaction.succes == True
        assert transaction.raison_echec is None
        
        print("✅ Test Transaction - Création valide réussie")
    
    def test_transaction_echec(self):
        """Test création d'une transaction échouée"""
        timestamp = datetime.now(timezone.utc)
        transaction = Transaction(
            timestamp=timestamp,
            entreprise_id=1,
            fournisseur_id=1,
            produit_id=1,
            produit_nom="Test Produit",
            quantite=0,
            prix_unitaire=100.0,
            total=0.0,
            succes=False,
            raison_echec="Budget insuffisant"
        )
        
        assert transaction.succes == False
        assert transaction.raison_echec == "Budget insuffisant"
        
        print("✅ Test Transaction - Échec avec raison")


if __name__ == "__main__":
    """
    Point d'entrée pour exécuter les tests directement.
    Utile pour le développement et le debugging.
    """
    print("🚀 Démarrage des tests de modèles TradeSim...")
    
    # Tests TypeProduit
    test_type = TestTypeProduit()
    test_type.test_type_produit_values()
    
    # Tests Produit
    test_produit = TestProduit()
    test_produit.test_produit_creation_valide()
    test_produit.test_produit_prix_negatif()
    test_produit.test_produit_id_negatif()
    test_produit.test_produit_nom_vide()
    test_produit.test_produit_tous_types()
    
    # Tests Fournisseur
    test_fournisseur = TestFournisseur()
    test_fournisseur.test_fournisseur_creation_valide()
    test_fournisseur.test_fournisseur_stock_negatif()
    test_fournisseur.test_fournisseur_stock_vide()
    
    # Tests Entreprise
    test_entreprise = TestEntreprise()
    test_entreprise.test_entreprise_creation_valide()
    test_entreprise.test_entreprise_budget_negatif()
    test_entreprise.test_entreprise_strategie_invalide()
    test_entreprise.test_entreprise_types_preferes_vide()
    
    # Tests ProduitChezFournisseur
    test_produit_fournisseur = TestProduitChezFournisseur()
    test_produit_fournisseur.test_produit_chez_fournisseur_creation()
    
    # Tests FournisseurComplet
    test_fournisseur_complet = TestFournisseurComplet()
    test_fournisseur_complet.test_fournisseur_complet_creation()
    
    # Tests Transaction
    test_transaction = TestTransaction()
    test_transaction.test_transaction_creation_valide()
    test_transaction.test_transaction_echec()
    
    print("🎉 Tous les tests de modèles terminés !") 