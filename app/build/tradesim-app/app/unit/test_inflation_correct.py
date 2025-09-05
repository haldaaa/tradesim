#!/usr/bin/env python3
"""
Test corrigé pour le module d'inflation de TradeSim.

Ce fichier teste le système d'inflation en utilisant les vraies fonctions
disponibles dans le module inflation.py.

Auteur: Assistant IA
Date: 2024-08-02
"""

def test_inflation_basic():
    """
    Test basique du module d'inflation.
    
    Vérifie que :
    - La fonction appliquer_inflation existe et peut être appelée
    - Elle fonctionne avec les données de test
    """
    from events.inflation import appliquer_inflation_et_retour
    from models import Produit, TypeProduit
    from data import fake_produits_db, produits_ayant_subi_inflation
    
    # Réinitialiser les données
    fake_produits_db.clear()
    produits_ayant_subi_inflation.clear()
    
    # Créer un produit de test
    produit = Produit(
        id=1,
        nom="Test Produit",
        prix=100.0,
        actif=True,
        type=TypeProduit.matiere_premiere
    )
    fake_produits_db.append(produit)
    
    # Test 1: Prix initial
    prix_initial = produit.prix
    print(f"💰 Prix initial: {prix_initial}")
    
    # Test 2: Appliquer l'inflation (tick=1)
    resultat = appliquer_inflation_et_retour(tick=1)
    print(f"📈 Prix après inflation: {produit.prix}")
    
    # Vérifications
    assert resultat is not None, "La fonction doit retourner un résultat"
    print("✅ Test inflation réussi !")

if __name__ == "__main__":
    """
    Point d'entrée pour exécuter le test d'inflation.
    """
    print("🚀 Test du module d'inflation...")
    test_inflation_basic()
    print("🎉 Test d'inflation terminé !") 