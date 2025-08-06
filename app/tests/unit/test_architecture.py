#!/usr/bin/env python3
"""
Test de la nouvelle architecture Repository
==========================================

Ce fichier teste que la nouvelle architecture avec les Repository
fonctionne correctement.

Auteur: Assistant IA
Date: 2024-08-02
"""

def test_repository_imports():
    """Test que les Repository peuvent être importés."""
    try:
        from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
        print("✅ Import des Repository réussi")
        assert True, "Import des Repository réussi"
    except Exception as e:
        print(f"❌ Erreur import Repository: {e}")
        assert False, f"Erreur import Repository: {e}"

def test_models_imports():
    """Test que les modèles peuvent être importés."""
    try:
        from models import Produit, Fournisseur, Entreprise, TypeProduit
        print("✅ Import des modèles réussi")
        assert True, "Import des modèles réussi"
    except Exception as e:
        print(f"❌ Erreur import modèles: {e}")
        assert False, f"Erreur import modèles: {e}"

def test_repository_usage():
    """Test l'utilisation des Repository."""
    try:
        from repositories import ProduitRepository
        from models import Produit, TypeProduit
        
        # Créer un repository
        repo = ProduitRepository()
        
        # Vider le repository pour le test
        repo.clear()
        
        # Créer un produit avec un ID unique
        produit = Produit(
            id=999,  # ID unique pour éviter les conflits
            nom="Test Produit Repository",
            prix=100.0,
            actif=True,
            type=TypeProduit.matiere_premiere
        )
        
        # Ajouter le produit
        repo.add(produit)
        
        # Récupérer tous les produits
        produits = repo.get_all()
        
        # Vérifier que le produit est là
        assert len(produits) > 0
        assert produits[0].nom == "Test Produit Repository"
        
        print("✅ Utilisation des Repository réussie")
        assert True, "Utilisation des Repository réussie"
        
    except Exception as e:
        print(f"❌ Erreur utilisation Repository: {e}")
        assert False, f"Erreur utilisation Repository: {e}"

def test_config_imports():
    """Test que la configuration peut être importée."""
    try:
        from config import NOMBRE_TOURS, DEBUG_MODE
        print("✅ Import de la configuration réussi")
        assert True, "Import de la configuration réussi"
    except Exception as e:
        print(f"❌ Erreur import configuration: {e}")
        assert False, f"Erreur import configuration: {e}"

def main():
    """Fonction principale de test."""
    print("🧪 Test de la nouvelle architecture TradeSim")
    print("=" * 50)
    
    tests = [
        ("Import des Repository", test_repository_imports),
        ("Import des modèles", test_models_imports),
        ("Utilisation des Repository", test_repository_usage),
        ("Import de la configuration", test_config_imports),
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
        print("🎉 Tous les tests sont passés ! L'architecture est prête.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")

if __name__ == "__main__":
    main() 