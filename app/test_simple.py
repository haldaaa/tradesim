#!/usr/bin/env python3
"""
Test simple pour vérifier que l'application TradeSim fonctionne correctement.

Ce fichier contient des tests basiques pour :
- La création d'objets Produit
- L'import des modules de l'application
- La validation des modèles Pydantic

Auteur: Assistant IA
Date: 2024-08-02
"""

def test_produit_creation():
    """
    Test de création d'un produit avec tous ses attributs.
    
    Vérifie que :
    - Un objet Produit peut être créé avec tous ses paramètres
    - Les valeurs sont correctement assignées
    - Le type de produit est valide
    """
    from app.models import Produit, TypeProduit
    
    # Création d'un produit de test avec tous les attributs
    produit = Produit(
        id=1,
        nom="Test Produit",
        prix=100.0,
        actif=True,
        type=TypeProduit.matiere_premiere
    )
    
    # Vérifications des attributs
    assert produit.id == 1, "L'ID du produit doit être 1"
    assert produit.nom == "Test Produit", "Le nom du produit doit être 'Test Produit'"
    assert produit.prix == 100.0, "Le prix du produit doit être 100.0"
    assert produit.actif == True, "Le produit doit être actif"
    assert produit.type == TypeProduit.matiere_premiere, "Le type doit être matière première"
    
    print("✅ Test création produit réussi")

if __name__ == "__main__":
    """
    Point d'entrée pour exécuter les tests directement.
    Utile pour le développement et le debugging.
    """
    print("🚀 Démarrage des tests TradeSim...")
    test_produit_creation()
    print("�� Tests terminés !") 