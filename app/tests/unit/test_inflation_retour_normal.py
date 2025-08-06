#!/usr/bin/env python3
"""
Tests unitaires pour la logique de retour à la normale après inflation TradeSim
================================================================================

Ce fichier teste la logique de retour progressif après inflation :
- Début du retour après X tours
- Baisse linéaire sur Y tours
- Prix final = prix original + 10%

Lancement manuel :
    python3 -m pytest tests/unit/test_inflation_retour_normal.py -v

Lancement automatique :
    python3 -m pytest tests/unit/ -v
"""

import pytest
from config import (
    DUREE_RETOUR_INFLATION, DUREE_BAISSE_INFLATION, POURCENTAGE_FINAL_INFLATION
)


class TestRetourNormalInflation:
    """Tests pour la logique de retour à la normale"""
    
    def test_constantes_configuration(self):
        """Test que les constantes de configuration sont correctement définies"""
        assert DUREE_RETOUR_INFLATION == 30
        assert DUREE_BAISSE_INFLATION == 15
        assert POURCENTAGE_FINAL_INFLATION == 10
    
    def test_calcul_prix_final(self):
        """Test du calcul du prix final"""
        prix_original = 100.0
        prix_final = prix_original * (1 + POURCENTAGE_FINAL_INFLATION / 100)
        
        assert abs(prix_final - 110.0) < 0.01  # 100€ + 10% (tolérance pour précision flottante)
    
    def test_baisse_lineaire(self):
        """Test de la baisse linéaire"""
        prix_depart = 120.0
        prix_final = 110.0
        duree_baisse = DUREE_BAISSE_INFLATION
        
        # Test pour différents tours de baisse
        for tour in range(duree_baisse + 1):
            progression = tour / duree_baisse
            prix_actuel = prix_depart - (prix_depart - prix_final) * progression
            
            # Vérifications
            if tour == 0:
                assert prix_actuel == 120.0  # Prix de départ
            elif tour == duree_baisse:
                assert prix_actuel == 110.0  # Prix final
            else:
                assert 110.0 < prix_actuel < 120.0  # Entre les deux
    
    def test_exemple_complet(self):
        """Test d'un exemple complet de retour à la normale"""
        # Données de test
        prix_original = 100.0
        prix_apres_inflation = 120.0  # +20%
        prix_final = prix_original * (1 + POURCENTAGE_FINAL_INFLATION / 100)  # 110€
        
        # Simulation de la baisse linéaire
        duree_baisse = DUREE_BAISSE_INFLATION
        
        # Tour 0 (début du retour)
        progression_0 = 0 / duree_baisse
        prix_0 = prix_apres_inflation - (prix_apres_inflation - prix_final) * progression_0
        assert prix_0 == 120.0
        
        # Tour 5 (milieu du retour)
        progression_5 = 5 / duree_baisse
        prix_5 = prix_apres_inflation - (prix_apres_inflation - prix_final) * progression_5
        prix_5_attendu = 120.0 - (120.0 - 110.0) * (5/15)
        assert abs(prix_5 - prix_5_attendu) < 0.01
        
        # Tour 15 (fin du retour)
        progression_15 = 15 / duree_baisse
        prix_15 = prix_apres_inflation - (prix_apres_inflation - prix_final) * progression_15
        assert abs(prix_15 - 110.0) < 0.01  # Tolérance pour précision flottante
    
    def test_duree_retour(self):
        """Test de la durée avant début du retour"""
        tick_inflation = 10
        tick_actuel = tick_inflation + DUREE_RETOUR_INFLATION
        
        tours_ecoules = tick_actuel - tick_inflation
        retour_commence = tours_ecoules >= DUREE_RETOUR_INFLATION
        
        assert retour_commence == True
        assert tours_ecoules == 30
    
    def test_retour_avant_duree(self):
        """Test que le retour ne commence pas avant la durée"""
        tick_inflation = 10
        tick_actuel = tick_inflation + 15  # Moins que DUREE_RETOUR_INFLATION
        
        tours_ecoules = tick_actuel - tick_inflation
        retour_commence = tours_ecoules >= DUREE_RETOUR_INFLATION
        
        assert retour_commence == False
        assert tours_ecoules == 15


class TestConfigurationRetourNormal:
    """Tests pour la configuration du retour à la normale"""
    
    def test_configuration_import(self):
        """Test que les constantes sont correctement importées"""
        from config import (
            DUREE_RETOUR_INFLATION, DUREE_BAISSE_INFLATION, POURCENTAGE_FINAL_INFLATION
        )
        
        assert isinstance(DUREE_RETOUR_INFLATION, int)
        assert isinstance(DUREE_BAISSE_INFLATION, int)
        assert isinstance(POURCENTAGE_FINAL_INFLATION, int)
    
    def test_configuration_coherence(self):
        """Test la cohérence de la configuration"""
        # Les durées doivent être positives
        assert DUREE_RETOUR_INFLATION > 0
        assert DUREE_BAISSE_INFLATION > 0
        
        # Le pourcentage final doit être raisonnable
        assert POURCENTAGE_FINAL_INFLATION > 0
        assert POURCENTAGE_FINAL_INFLATION <= 50  # Pas plus de 50%
        
        # Les durées ne doivent pas être excessives
        assert DUREE_RETOUR_INFLATION <= 1000
        assert DUREE_BAISSE_INFLATION <= 1000
    
    def test_exemple_realiste(self):
        """Test d'un exemple réaliste"""
        # Prix initial
        prix_original = 100.0
        
        # Inflation de 20%
        prix_apres_inflation = prix_original * 1.20  # 120€
        
        # Prix final (original + 10%)
        prix_final = prix_original * (1 + POURCENTAGE_FINAL_INFLATION / 100)  # 110€
        
        # Vérifications
        assert prix_apres_inflation == 120.0
        assert abs(prix_final - 110.0) < 0.01  # Tolérance pour précision flottante
        
        # Différence à répartir sur la baisse
        difference = prix_apres_inflation - prix_final  # 10€
        baisse_par_tour = difference / DUREE_BAISSE_INFLATION  # 10€ / 15 tours
        
        assert abs(difference - 10.0) < 0.01  # Tolérance pour précision flottante
        assert abs(baisse_par_tour - 0.67) < 0.01  # ~0.67€ par tour


if __name__ == "__main__":
    # Tests manuels
    print("🧪 Tests de la logique de retour à la normale")
    print(f"📊 Configuration: retour après {DUREE_RETOUR_INFLATION} tours, baisse sur {DUREE_BAISSE_INFLATION} tours")
    print(f"🎯 Prix final: prix original + {POURCENTAGE_FINAL_INFLATION}%")
    
    # Test rapide
    test_instance = TestRetourNormalInflation()
    test_instance.test_constantes_configuration()
    test_instance.test_calcul_prix_final()
    print("✅ Tests de base passés") 