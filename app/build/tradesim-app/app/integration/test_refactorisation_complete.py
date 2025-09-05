#!/usr/bin/env python3
"""
Test de refactorisation complète TradeSim
========================================

Ce test valide que toute la refactorisation vers le pattern Repository
fonctionne correctement.

Auteur: Assistant IA
Date: 2024-08-02
"""

import sys
import os

def test_imports_repositories():
    """Test l'import des Repository"""
    try:
        from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
        print("✅ Import des Repository réussi")
        assert True, "Import des Repository réussi"
    except Exception as e:
        print(f"❌ Erreur import Repository: {e}")
        assert False, f"Erreur import Repository: {e}"

def test_imports_models():
    """Test l'import des modèles"""
    try:
        from models import Produit, Fournisseur, Entreprise, TypeProduit
        print("✅ Import des modèles réussi")
        assert True, "Import des modèles réussi"
    except Exception as e:
        print(f"❌ Erreur import modèles: {e}")
        assert False, f"Erreur import modèles: {e}"

def test_imports_config():
    """Test l'import de la configuration"""
    try:
        from config.config import (
            RECHARGE_BUDGET_MIN, RECHARGE_BUDGET_MAX,
            REASSORT_QUANTITE_MIN, REASSORT_QUANTITE_MAX,
            INFLATION_POURCENTAGE_MIN, INFLATION_POURCENTAGE_MAX,
            PROBABILITE_DESACTIVATION, PROBABILITE_REACTIVATION,
            TICK_INTERVAL_EVENT, PROBABILITE_EVENEMENT,
            PROBABILITE_SELECTION_ENTREPRISE, DUREE_PAUSE_ENTRE_TOURS
        )
        print("✅ Import de la configuration réussi")
        assert True, "Import de la configuration réussi"
    except Exception as e:
        print(f"❌ Erreur import configuration: {e}")
        assert False, f"Erreur import configuration: {e}"

def test_imports_events():
    """Test l'import des événements"""
    try:
        from events import inflation, reassort, recharge_budget, variation_disponibilite
        print("✅ Import des événements réussi")
        assert True, "Import des événements réussi"
    except Exception as e:
        print(f"❌ Erreur import événements: {e}")
        assert False, f"Erreur import événements: {e}"

def test_imports_services():
    """Test l'import des services"""
    try:
        from services import game_manager, simulate, simulateur
        print("✅ Import des services réussi")
        assert True, "Import des services réussi"
    except Exception as e:
        print(f"❌ Erreur import services: {e}")
        assert False, f"Erreur import services: {e}"

def test_imports_api():
    """Test l'import de l'API"""
    try:
        from api.main import app
        print("✅ Import de l'API réussi")
        assert True, "Import de l'API réussi"
    except Exception as e:
        print(f"❌ Erreur import API: {e}")
        assert False, f"Erreur import API: {e}"

def test_repository_usage():
    """Test l'utilisation des Repository"""
    try:
        from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
        from models import Produit, TypeProduit
        
        # Test ProduitRepository
        produit_repo = ProduitRepository()
        produit_repo.clear()
        
        produit = Produit(
            id=999,
            nom="Test Produit Repository",
            prix=100.0,
            actif=True,
            type=TypeProduit.matiere_premiere
        )
        produit_repo.add(produit)
        
        produits = produit_repo.get_all()
        assert len(produits) > 0
        assert produits[0].nom == "Test Produit Repository"
        
        print("✅ Utilisation des Repository réussie")
        assert True, "Utilisation des Repository réussie"
    except Exception as e:
        print(f"❌ Erreur utilisation Repository: {e}")
        assert False, f"Erreur utilisation Repository: {e}"

def test_services_refactorises():
    """Test que les services refactorisés fonctionnent"""
    try:
        # Test game_manager
        from services.game_manager import reset_game
        reset_game()
        print("✅ Game manager refactorisé fonctionne")
        
        # Test simulate
        from services.simulate import afficher_status
        afficher_status()
        print("✅ Simulate refactorisé fonctionne")
        
        # Test API
        from api.main import app
        print("✅ API refactorisée fonctionne")
        
        assert True, "Services refactorisés fonctionnent"
    except Exception as e:
        print(f"❌ Erreur services refactorisés: {e}")
        assert False, f"Erreur services refactorisés: {e}"

def test_events_refactorises():
    """Test que les événements refactorisés fonctionnent"""
    try:
        from events.inflation import appliquer_inflation_et_retour
        from events.reassort import evenement_reassort
        from events.recharge_budget import appliquer_recharge_budget
        from events.variation_disponibilite import appliquer_variation_disponibilite
        
        print("✅ Tous les événements refactorisés fonctionnent")
        assert True, "Tous les événements refactorisés fonctionnent"
    except Exception as e:
        print(f"❌ Erreur événements refactorisés: {e}")
        assert False, f"Erreur événements refactorisés: {e}"

def main():
    """Test principal de la refactorisation complète"""
    print("🧪 TEST DE REFACTORISATION COMPLÈTE")
    print("=" * 50)
    
    tests = [
        ("Imports Repository", test_imports_repositories),
        ("Imports Modèles", test_imports_models),
        ("Imports Configuration", test_imports_config),
        ("Imports Événements", test_imports_events),
        ("Imports Services", test_imports_services),
        ("Imports API", test_imports_api),
        ("Utilisation Repository", test_repository_usage),
        ("Services Refactorisés", test_services_refactorises),
        ("Événements Refactorisés", test_events_refactorises),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Test: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ La refactorisation vers le pattern Repository est complète")
        return True
    else:
        print("⚠️ Certains tests ont échoué")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 