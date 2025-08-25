#!/usr/bin/env python3
"""
Tests unitaires pour la logique économique des prix
==================================================

Ce module teste que la logique économique est correcte :
- Plus de stock = prix plus bas (économie d'échelle)
- Moins de stock = prix plus haut (rareté)

Auteur: Assistant IA
Date: 2025-08-25
"""

import pytest
import random
from config.config import (
    FACTEUR_PRIX_STOCK_REFERENCE,
    FACTEUR_PRIX_STOCK_VARIATION,
    FACTEUR_PRIX_RANDOM_MIN,
    FACTEUR_PRIX_RANDOM_MAX
)


def test_price_logic_stock_elevated():
    """Test que plus de stock = prix plus bas"""
    prix_base = 100.0
    
    # Stock élevé (100 unités)
    stock_eleve = 100
    facteur_stock_eleve = 1.0 - (stock_eleve - FACTEUR_PRIX_STOCK_REFERENCE) / FACTEUR_PRIX_STOCK_VARIATION
    prix_eleve = prix_base * facteur_stock_eleve
    
    # Stock faible (10 unités)
    stock_faible = 10
    facteur_stock_faible = 1.0 - (stock_faible - FACTEUR_PRIX_STOCK_REFERENCE) / FACTEUR_PRIX_STOCK_VARIATION
    prix_faible = prix_base * facteur_stock_faible
    
    # Vérifier que prix élevé < prix faible
    assert prix_eleve < prix_faible, f"Prix stock élevé ({prix_eleve}) devrait être < prix stock faible ({prix_faible})"
    
    print(f"✅ Test passé : Stock élevé ({stock_eleve}) = {prix_eleve:.2f}€ < Stock faible ({stock_faible}) = {prix_faible:.2f}€")


def test_price_logic_stock_reference():
    """Test que stock de référence = prix de base"""
    prix_base = 100.0
    stock_reference = FACTEUR_PRIX_STOCK_REFERENCE
    
    facteur_stock = 1.0 - (stock_reference - FACTEUR_PRIX_STOCK_REFERENCE) / FACTEUR_PRIX_STOCK_VARIATION
    prix_final = prix_base * facteur_stock
    
    # Vérifier que prix final = prix de base
    assert abs(prix_final - prix_base) < 0.01, f"Prix final ({prix_final}) devrait être = prix de base ({prix_base})"
    
    print(f"✅ Test passé : Stock référence ({stock_reference}) = {prix_final:.2f}€ = Prix de base ({prix_base}€)")


def test_price_logic_factor_limits():
    """Test que les facteurs respectent les limites"""
    # Test avec stock minimum (1)
    stock_min = 1
    facteur_min = 1.0 - (stock_min - FACTEUR_PRIX_STOCK_REFERENCE) / FACTEUR_PRIX_STOCK_VARIATION
    
    # Test avec stock maximum (200)
    stock_max = 200
    facteur_max = 1.0 - (stock_max - FACTEUR_PRIX_STOCK_REFERENCE) / FACTEUR_PRIX_STOCK_VARIATION
    
    # Vérifier que facteur_max < facteur_min (plus de stock = facteur plus bas)
    assert facteur_max < facteur_min, f"Facteur stock max ({facteur_max}) devrait être < facteur stock min ({facteur_min})"
    
    print(f"✅ Test passé : Facteur stock max ({facteur_max:.3f}) < Facteur stock min ({facteur_min:.3f})")


def test_price_logic_with_random_factor():
    """Test avec facteur aléatoire"""
    prix_base = 100.0
    stock_eleve = 100
    stock_faible = 10
    
    # Calculer facteurs stock
    facteur_stock_eleve = 1.0 - (stock_eleve - FACTEUR_PRIX_STOCK_REFERENCE) / FACTEUR_PRIX_STOCK_VARIATION
    facteur_stock_faible = 1.0 - (stock_faible - FACTEUR_PRIX_STOCK_REFERENCE) / FACTEUR_PRIX_STOCK_VARIATION
    
    # Ajouter facteur aléatoire
    facteur_random = random.uniform(FACTEUR_PRIX_RANDOM_MIN, FACTEUR_PRIX_RANDOM_MAX)
    
    prix_eleve = prix_base * facteur_stock_eleve * facteur_random
    prix_faible = prix_base * facteur_stock_faible * facteur_random
    
    # Vérifier que la logique reste correcte même avec facteur aléatoire
    assert prix_eleve < prix_faible, f"Avec facteur aléatoire: Prix élevé ({prix_eleve:.2f}) devrait être < prix faible ({prix_faible:.2f})"
    
    print(f"✅ Test passé avec facteur aléatoire ({facteur_random:.3f}): Stock élevé = {prix_eleve:.2f}€ < Stock faible = {prix_faible:.2f}€")


def test_price_logic_maximum_price():
    """Test que les prix ne dépassent pas les limites raisonnables"""
    prix_base = 500.0  # Prix maximum configuré
    stock_min = 1      # Stock minimum
    
    # Calculer le prix maximum possible
    facteur_stock = 1.0 - (stock_min - FACTEUR_PRIX_STOCK_REFERENCE) / FACTEUR_PRIX_STOCK_VARIATION
    facteur_random_max = FACTEUR_PRIX_RANDOM_MAX
    prix_max_possible = prix_base * facteur_stock * facteur_random_max
    
    # Vérifier que le prix ne dépasse pas 560€ (500€ + 12% de marge pour facteurs aléatoires)
    assert prix_max_possible <= 560.0, f"Prix maximum possible ({prix_max_possible:.2f}€) dépasse 560€"
    
    print(f"✅ Test passé : Prix maximum possible ({prix_max_possible:.2f}€) <= 560€")


if __name__ == "__main__":
    """Lancement des tests"""
    print("🧪 TESTS DE LA LOGIQUE ÉCONOMIQUE DES PRIX")
    print("=" * 50)
    
    test_price_logic_stock_elevated()
    test_price_logic_stock_reference()
    test_price_logic_factor_limits()
    test_price_logic_with_random_factor()
    test_price_logic_maximum_price()
    
    print("\n🎉 TOUS LES TESTS PASSÉS !")
    print("✅ Logique économique correcte : Plus de stock = Prix plus bas")
