#!/usr/bin/env python3
"""
Test des progrès de refactorisation
===================================

Ce fichier teste les progrès de la refactorisation vers l'architecture Repository.

Auteur: Assistant IA
Date: 2024-08-02
"""

def test_architecture_complete():
    """Test que l'architecture de base fonctionne."""
    try:
        from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
        from models import Produit, Fournisseur, Entreprise, TypeProduit
        from config import NOMBRE_TOURS, DEBUG_MODE, TICK_INTERVAL_EVENT
        
        print("✅ Architecture de base fonctionnelle")
        assert True, "Architecture de base fonctionnelle"
    except Exception as e:
        print(f"❌ Erreur architecture: {e}")
        assert False, f"Erreur architecture: {e}"

def test_events_refactorised():
    """Test que tous les événements sont refactorisés."""
    try:
        from events.inflation import appliquer_inflation
        from events.reassort import evenement_reassort
        from events.recharge_budget import appliquer_recharge_budget
        from events.variation_disponibilite import appliquer_variation_disponibilite
        
        # Test rapide d'exécution
        logs_inflation = appliquer_inflation(1)
        logs_reassort = evenement_reassort(1)
        logs_recharge = appliquer_recharge_budget(1)
        logs_variation = appliquer_variation_disponibilite(1)
        
        print(f"✅ Événements refactorisés: {len(logs_inflation)} + {len(logs_reassort)} + {len(logs_recharge)} + {len(logs_variation)} logs")
        assert True, "Événements refactorisés"
    except Exception as e:
        print(f"❌ Erreur événements: {e}")
        assert False, f"Erreur événements: {e}"

def test_services_partial():
    """Test que les services commencent à être refactorisés."""
    try:
        from services.simulateur import simulation_tour, produit_repo, fournisseur_repo, entreprise_repo
        
        # Vérifier que les Repository sont utilisés
        produits = produit_repo.get_all()
        fournisseurs = fournisseur_repo.get_all()
        entreprises = entreprise_repo.get_all()
        
        print(f"✅ Services partiellement refactorisés: {len(produits)} produits, {len(fournisseurs)} fournisseurs, {len(entreprises)} entreprises")
        assert True, "Services partiellement refactorisés"
    except Exception as e:
        print(f"❌ Erreur services: {e}")
        assert False, f"Erreur services: {e}"

def test_repository_usage():
    """Test que les Repository sont bien utilisés partout."""
    try:
        from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
        
        # Test des Repository
        produit_repo = ProduitRepository()
        fournisseur_repo = FournisseurRepository()
        entreprise_repo = EntrepriseRepository()
        
        # Test des méthodes
        produits = produit_repo.get_actifs()
        fournisseurs = fournisseur_repo.get_all()
        entreprises = entreprise_repo.get_all()
        
        print(f"✅ Repository usage: {len(produits)} produits actifs, {len(fournisseurs)} fournisseurs, {len(entreprises)} entreprises")
        assert True, "Repository usage"
    except Exception as e:
        print(f"❌ Erreur Repository usage: {e}")
        assert False, f"Erreur Repository usage: {e}"

def main():
    """Fonction principale de test."""
    print("🧪 Test des progrès de refactorisation")
    print("=" * 50)
    
    tests = [
        ("Architecture de base", test_architecture_complete),
        ("Événements refactorisés", test_events_refactorised),
        ("Services partiels", test_services_partial),
        ("Usage Repository", test_repository_usage),
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
        print("🎉 La refactorisation progresse bien !")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    # Calcul du pourcentage de progression
    progression = (success_count / len(results)) * 100
    print(f"📈 Progression estimée: {progression:.0f}%")

if __name__ == "__main__":
    main() 