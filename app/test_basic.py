#!/usr/bin/env python3

def test_basic():
    """Test basique"""
    print("🧪 Test basique en cours...")
    assert 1 + 1 == 2
    print("✅ Test basique réussi !")

def test_import():
    """Test d'import"""
    print("🧪 Test d'import en cours...")
    try:
        from app.models import Produit, TypeProduit
        print("✅ Import réussi !")
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Démarrage des tests...")
    test_basic()
    test_import()
    print("�� Tests terminés !") 