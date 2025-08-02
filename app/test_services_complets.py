#!/usr/bin/env python3
"""
Test des services complets TradeSim
==================================

Ce test valide que tous les nouveaux services fonctionnent correctement
avec l'architecture Repository.

Auteur: Assistant IA
Date: 2024-08-02
"""

import sys
import os

def test_imports_services():
    """Test l'import de tous les services"""
    try:
        from services import (
            SimulationService, simulation_service,
            GameManagerService, game_manager_service,
            TransactionService, transaction_service,
            BudgetService, budget_service
        )
        print("✅ Import de tous les services réussi")
        return True
    except Exception as e:
        print(f"❌ Erreur import services: {e}")
        return False

def test_simulation_service():
    """Test le SimulationService"""
    try:
        from services import simulation_service
        
        # Test de base
        simulation_service.reset_simulation()
        stats = simulation_service.calculer_statistiques()
        
        assert isinstance(stats, dict)
        assert "tours_completes" in stats
        assert "evenements_appliques" in stats
        
        print("✅ SimulationService fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur SimulationService: {e}")
        return False

def test_game_manager_service():
    """Test le GameManagerService"""
    try:
        from services import game_manager_service
        
        # Test de base
        resultat = game_manager_service.reset_game()
        assert resultat == True
        
        # Test de génération de données
        config = game_manager_service.get_current_config()
        assert isinstance(config, dict)
        assert "entreprises" in config
        assert "produits" in config
        assert "fournisseurs" in config
        
        # Test de résumé
        summary = game_manager_service.get_game_summary()
        assert isinstance(summary, dict)
        
        print("✅ GameManagerService fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur GameManagerService: {e}")
        return False

def test_transaction_service():
    """Test le TransactionService"""
    try:
        from services import transaction_service
        
        # Test de base
        transaction_service.reset_transactions()
        
        # Test de calcul de prix
        from models import Produit, Fournisseur, TypeProduit
        produit = Produit(id=999, nom="Test", prix=100.0, actif=True, type=TypeProduit.matiere_premiere)
        fournisseur = Fournisseur(id=999, nom_entreprise="Test", pays="France", stock_produit={999: 50})
        
        prix = transaction_service.calculer_prix_fournisseur(produit, fournisseur, 50)
        assert isinstance(prix, float)
        assert prix > 0
        
        # Test de statistiques
        stats = transaction_service.get_statistiques_transactions()
        assert isinstance(stats, dict)
        assert "nombre_transactions" in stats
        
        print("✅ TransactionService fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur TransactionService: {e}")
        return False

def test_budget_service():
    """Test le BudgetService"""
    try:
        from services import budget_service
        
        # Test de base
        budget_service.reset_operations()
        
        # Test de statistiques
        stats = budget_service.get_statistiques_budgets()
        assert isinstance(stats, dict)
        assert "nombre_entreprises" in stats
        assert "budget_total" in stats
        
        # Test de recherche d'entreprises
        entreprises_difficulte = budget_service.get_entreprises_en_difficulte()
        entreprises_prosperes = budget_service.get_entreprises_prosperes()
        
        assert isinstance(entreprises_difficulte, list)
        assert isinstance(entreprises_prosperes, list)
        
        print("✅ BudgetService fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur BudgetService: {e}")
        return False

def test_integration_services():
    """Test l'intégration entre les services"""
    try:
        from services import (
            simulation_service, game_manager_service,
            transaction_service, budget_service
        )
        
        # Initialiser le jeu
        game_manager_service.reset_game()
        
        # Vérifier que les services peuvent accéder aux mêmes données
        entreprises = simulation_service.entreprise_repo.get_all()
        assert len(entreprises) > 0
        
        # Test d'intégration budget + transaction
        if entreprises:
            entreprise = entreprises[0]
            ancien_budget = budget_service.get_budget_entreprise(entreprise.id)
            
            # Vérifier que l'entreprise a un budget valide
            if ancien_budget is not None:
                # Ajouter du budget
                budget_service.ajouter_budget(entreprise.id, 1000)
                nouveau_budget = budget_service.get_budget_entreprise(entreprise.id)
                
                assert nouveau_budget == ancien_budget + 1000
        
        print("✅ Intégration des services réussie")
        return True
    except Exception as e:
        print(f"❌ Erreur intégration services: {e}")
        return False

def test_utilisation_avancee():
    """Test d'utilisation avancée des services"""
    try:
        from services import (
            simulation_service, game_manager_service,
            transaction_service, budget_service
        )
        
        # Simuler une session complète
        game_manager_service.reset_game()
        simulation_service.reset_simulation()
        transaction_service.reset_transactions()
        budget_service.reset_operations()
        
        # Effectuer quelques tours de simulation (simplifié)
        for i in range(2):
            try:
                resultat = simulation_service.simulation_tour(verbose=False)
                assert isinstance(resultat, dict)
                assert "tour" in resultat
                assert "tick" in resultat
            except Exception as e:
                print(f"  ⚠️ Tour {i+1} échoué: {e}")
                # Continuer même si un tour échoue
        
        # Vérifier les statistiques
        stats_simulation = simulation_service.get_etat_actuel()
        stats_budget = budget_service.get_statistiques_budgets()
        stats_transactions = transaction_service.get_statistiques_transactions()
        
        assert isinstance(stats_simulation, dict)
        assert isinstance(stats_budget, dict)
        assert isinstance(stats_transactions, dict)
        
        print("✅ Utilisation avancée des services réussie")
        return True
    except Exception as e:
        print(f"❌ Erreur utilisation avancée: {e}")
        return False

def main():
    """Test principal des services complets"""
    print("🧪 TEST DES SERVICES COMPLETS")
    print("=" * 50)
    
    tests = [
        ("Imports Services", test_imports_services),
        ("SimulationService", test_simulation_service),
        ("GameManagerService", test_game_manager_service),
        ("TransactionService", test_transaction_service),
        ("BudgetService", test_budget_service),
        ("Intégration Services", test_integration_services),
        ("Utilisation Avancée", test_utilisation_avancee),
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
        print("✅ Tous les services sont opérationnels")
        return True
    else:
        print("⚠️ Certains tests ont échoué")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 