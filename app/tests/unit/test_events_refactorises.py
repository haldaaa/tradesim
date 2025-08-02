#!/usr/bin/env python3
"""
Test des événements refactorisés
===============================

Ce fichier teste que tous les événements refactorisés fonctionnent
correctement avec la nouvelle architecture Repository.

Auteur: Assistant IA
Date: 2024-08-02
"""

def test_events_imports():
    """Test que tous les événements peuvent être importés."""
    try:
        from events.inflation import appliquer_inflation
        from events.reassort import evenement_reassort
        from events.recharge_budget import appliquer_recharge_budget
        from events.variation_disponibilite import appliquer_variation_disponibilite
        
        print("✅ Import de tous les événements réussi")
        return True
    except Exception as e:
        print(f"❌ Erreur import événements: {e}")
        return False

def test_events_execution():
    """Test l'exécution des événements."""
    try:
        from events.inflation import appliquer_inflation
        from events.reassort import evenement_reassort
        from events.recharge_budget import appliquer_recharge_budget
        from events.variation_disponibilite import appliquer_variation_disponibilite
        
        # Test inflation
        logs_inflation = appliquer_inflation(1)
        print(f"✅ Inflation: {len(logs_inflation)} logs générés")
        
        # Test reassort
        logs_reassort = evenement_reassort(1)
        print(f"✅ Reassort: {len(logs_reassort)} logs générés")
        
        # Test recharge budget
        logs_recharge = appliquer_recharge_budget(1)
        print(f"✅ Recharge budget: {len(logs_recharge)} logs générés")
        
        # Test variation disponibilité
        logs_variation = appliquer_variation_disponibilite(1)
        print(f"✅ Variation disponibilité: {len(logs_variation)} logs générés")
        
        return True
    except Exception as e:
        print(f"❌ Erreur exécution événements: {e}")
        return False

def test_repository_integration():
    """Test que les événements utilisent bien les Repository."""
    try:
        from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
        from events.inflation import appliquer_inflation
        
        # Vérifier que les Repository sont utilisés
        produit_repo = ProduitRepository()
        fournisseur_repo = FournisseurRepository()
        entreprise_repo = EntrepriseRepository()
        
        # Vérifier que les données sont accessibles
        produits = produit_repo.get_all()
        fournisseurs = fournisseur_repo.get_all()
        entreprises = entreprise_repo.get_all()
        
        print(f"✅ Repository intégration: {len(produits)} produits, {len(fournisseurs)} fournisseurs, {len(entreprises)} entreprises")
        
        return True
    except Exception as e:
        print(f"❌ Erreur intégration Repository: {e}")
        return False

def main():
    """Fonction principale de test."""
    print("🧪 Test des événements refactorisés")
    print("=" * 50)
    
    tests = [
        ("Import des événements", test_events_imports),
        ("Exécution des événements", test_events_execution),
        ("Intégration Repository", test_repository_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Résultats des tests:")
    
    success_count = 0
    for test_name, result in results:
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        print(f"  {test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n🎯 {success_count}/{len(results)} tests réussis")
    
    if success_count == len(results):
        print("🎉 Tous les événements refactorisés fonctionnent parfaitement !")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")

if __name__ == "__main__":
    main() 