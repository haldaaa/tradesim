import pytest

def test_simple():
    """Test simple pour vérifier que pytest fonctionne"""
    assert 1 + 1 == 2
    print("✅ Test simple réussi")

def test_import_app():
    """Test d'import de l'application"""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tradesim', 'app'))
    
    try:
        from models import Produit, TypeProduit
        print("✅ Import des modèles réussi")
        assert True
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        assert False

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 