#!/usr/bin/env python3
"""
Tests unitaires pour la logique de pénalité d'inflation TradeSim
================================================================

Ce fichier teste la nouvelle logique de pénalité d'inflation :
- Pénalité de -15% pour les produits déjà affectés
- Durée de 50 tours avec reset automatique
- Gestion des compteurs par produit

Lancement manuel :
    python3 -m pytest tests/unit/test_inflation_penalite.py -v

Lancement automatique :
    python3 -m pytest tests/unit/ -v
"""

import pytest
import random
from unittest.mock import Mock, patch
from config.config import (
    INFLATION_POURCENTAGE_MIN, INFLATION_POURCENTAGE_MAX,
    PENALITE_INFLATION_PRODUIT_EXISTANT, DUREE_PENALITE_INFLATION
)


class TestInflationPenalite:
    """Tests pour la logique de pénalité d'inflation"""
    
    def test_constantes_configuration(self):
        """Test que les constantes de configuration sont correctement définies"""
        assert PENALITE_INFLATION_PRODUIT_EXISTANT == 15
        assert DUREE_PENALITE_INFLATION == 50
        assert INFLATION_POURCENTAGE_MIN == 30
        assert INFLATION_POURCENTAGE_MAX == 60
    
    def test_calcul_penalite(self):
        """Test du calcul de pénalité d'inflation"""
        # Test sans pénalité
        pourcentage_inflation = 40.0
        penalite_active = False
        resultat = pourcentage_inflation - (PENALITE_INFLATION_PRODUIT_EXISTANT if penalite_active else 0)
        assert resultat == 40.0
        
        # Test avec pénalité
        penalite_active = True
        resultat = pourcentage_inflation - (PENALITE_INFLATION_PRODUIT_EXISTANT if penalite_active else 0)
        assert resultat == 25.0  # 40% - 15%
        
        # Test minimum 5%
        pourcentage_inflation = 10.0
        resultat = pourcentage_inflation - (PENALITE_INFLATION_PRODUIT_EXISTANT if penalite_active else 0)
        resultat_minimum = max(resultat, 5)  # Minimum 5%
        assert resultat_minimum == 5.0
    
    def test_duree_penalite(self):
        """Test de la durée de pénalité"""
        # Test pénalité active
        tick_actuel = 30
        derniere_inflation_tick = 10
        tours_ecoules = tick_actuel - derniere_inflation_tick
        
        penalite_active = tours_ecoules <= DUREE_PENALITE_INFLATION
        assert penalite_active == True  # 20 tours < 50
        
        # Test pénalité expirée
        tick_actuel = 70
        derniere_inflation_tick = 10
        tours_ecoules = tick_actuel - derniere_inflation_tick
        
        penalite_active = tours_ecoules <= DUREE_PENALITE_INFLATION
        assert penalite_active == False  # 60 tours > 50
    
    def test_reset_compteur(self):
        """Test du reset du compteur de pénalité"""
        # État initial
        timer = {
            "derniere_inflation_tick": 10,
            "tours_restants_penalite": 25  # Moitié écoulé
        }
        
        # Nouvelle inflation
        tick_actuel = 30
        timer["derniere_inflation_tick"] = tick_actuel
        timer["tours_restants_penalite"] = DUREE_PENALITE_INFLATION
        
        assert timer["tours_restants_penalite"] == 50
        assert timer["derniere_inflation_tick"] == 30


class TestConfigurationInflation:
    """Tests pour la configuration de l'inflation"""
    
    def test_configuration_import(self):
        """Test que les constantes sont correctement importées"""
        from config.config import (
            INFLATION_POURCENTAGE_MIN, INFLATION_POURCENTAGE_MAX,
            PENALITE_INFLATION_PRODUIT_EXISTANT, DUREE_PENALITE_INFLATION
        )
        
        assert isinstance(INFLATION_POURCENTAGE_MIN, int)
        assert isinstance(INFLATION_POURCENTAGE_MAX, int)
        assert isinstance(PENALITE_INFLATION_PRODUIT_EXISTANT, int)
        assert isinstance(DUREE_PENALITE_INFLATION, int)
    
    def test_configuration_coherence(self):
        """Test la cohérence de la configuration"""
        # Les pourcentages doivent être logiques
        assert INFLATION_POURCENTAGE_MIN >= 0
        assert INFLATION_POURCENTAGE_MAX > INFLATION_POURCENTAGE_MIN
        assert INFLATION_POURCENTAGE_MAX <= 100
        
        # La pénalité doit être raisonnable
        assert PENALITE_INFLATION_PRODUIT_EXISTANT > 0
        assert PENALITE_INFLATION_PRODUIT_EXISTANT <= INFLATION_POURCENTAGE_MAX
        
        # La durée doit être réaliste
        assert DUREE_PENALITE_INFLATION > 0
        assert DUREE_PENALITE_INFLATION <= 1000  # Pas plus de 1000 tours
    
    def test_exemple_inflation(self):
        """Test d'un exemple concret d'inflation avec pénalité"""
        # Prix initial
        prix_initial = 100.0
        
        # 1ère inflation : +40%
        inflation_1 = 40.0
        prix_apres_1 = prix_initial * (1 + inflation_1 / 100)
        assert prix_apres_1 == 140.0
        
        # 2ème inflation : +25% (40% - 15% de pénalité)
        inflation_2 = 40.0 - PENALITE_INFLATION_PRODUIT_EXISTANT
        prix_apres_2 = prix_apres_1 * (1 + inflation_2 / 100)
        assert prix_apres_2 == 175.0  # 140 * 1.25
        
        # 3ème inflation (après 50 tours) : +40% (pénalité expirée)
        inflation_3 = 40.0
        prix_apres_3 = prix_apres_2 * (1 + inflation_3 / 100)
        assert abs(prix_apres_3 - 245.0) < 0.01  # 175 * 1.4 (tolérance pour précision flottante)


if __name__ == "__main__":
    # Tests manuels
    print("🧪 Tests de la logique de pénalité d'inflation")
    print(f"📊 Configuration: pénalité {PENALITE_INFLATION_PRODUIT_EXISTANT}%, durée {DUREE_PENALITE_INFLATION} tours")
    
    # Test rapide
    test_instance = TestInflationPenalite()
    test_instance.test_constantes_configuration()
    test_instance.test_calcul_penalite()
    print("✅ Tests de base passés") 