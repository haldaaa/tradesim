#!/usr/bin/env python3
"""
Service de métriques de budget pour TradeSim
===========================================

Ce service calcule et gère toutes les métriques liées aux budgets des entreprises.
Il utilise un cache LRU pour optimiser les calculs complexes et maintient
un historique des budgets pour les analyses de tendances.

ARCHITECTURE :
- Historique des budgets par tour (max 200 tours)
- Cache LRU pour les calculs statistiques coûteux
- Métriques arrondies pour éviter les erreurs de virgule flottante
- Alertes automatiques sur les budgets critiques

MÉTRIQUES CALCULÉES (14 métriques) :
1. Métriques de base (5) : total, moyenne, médiane, écart-type, coefficient variation
2. Métriques de variation (3) : variation totale, dépenses, gains
3. Métriques de santé (3) : ratio dépenses/revenus, entreprises critiques/faibles
4. Métriques de tendance (2) : évolution tour, tendance globale
5. Métriques avancées (1) : skewness (asymétrie)

UTILISATION :
- Appelé par SimulationService à chaque tour
- Métriques collectées dans logs/metrics.jsonl
- Exposées via Prometheus pour monitoring

Auteur: Assistant IA
Date: 2025-08-11
Version: 2.0 - Correction erreurs d'arrondi
"""

import statistics
import math
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
from collections import deque
import time

from models.models import Entreprise
from config.config import (
    BUDGET_HISTORY_MAX_TOURS, BUDGET_CACHE_ENABLED, BUDGET_CACHE_SIZE,
    BUDGET_CRITIQUE_SEUIL, BUDGET_FAIBLE_SEUIL, BUDGET_ELEVE_SEUIL
)


class BudgetMetricsService:
    """
    Service de métriques de budget avec cache LRU et historique
    
    ARCHITECTURE :
    - Historique des budgets par tour (deque avec maxlen=200)
    - Cache LRU pour les calculs statistiques coûteux
    - Métriques arrondies pour éviter les erreurs de virgule flottante
    - Alertes automatiques sur les budgets critiques
    
    RESPONSABILITÉS :
    - Calcul des métriques de base des budgets (total, moyenne, médiane, etc.)
    - Calcul des métriques de variation et tendance (évolution, dépenses, gains)
    - Gestion de l'historique des budgets (200 tours maximum)
    - Cache LRU pour optimiser les calculs statistiques complexes
    - Alertes sur les budgets critiques (entreprises en difficulté)
    
    MÉTRIQUES PRODUITES (14 métriques) :
    - budget_total_entreprises : Somme de tous les budgets
    - budget_moyen_entreprises : Moyenne arithmétique des budgets
    - budget_median_entreprises : Médiane des budgets
    - budget_ecart_type_entreprises : Écart-type des budgets
    - budget_coefficient_variation : Coefficient de variation (CV = σ/μ)
    - budget_variation_totale : Variation totale depuis le début
    - budget_depenses_totales : Dépenses cumulées
    - budget_gains_totaux : Gains cumulés
    - budget_ratio_depenses_revenus : Ratio dépenses/gains
    - budget_entreprises_critiques : Nombre d'entreprises critiques
    - budget_entreprises_faibles : Nombre d'entreprises faibles
    - budget_evolution_tour : Évolution depuis le tour précédent
    - budget_tendance_globale : Tendance sur l'historique
    - budget_skewness : Asymétrie de la distribution
    
    UTILISATION :
    - Appelé par SimulationService.ajouter_tour() à chaque tour
    - Métriques calculées via calculer_metriques_budget()
    - Données stockées dans logs/metrics.jsonl
    - Exposées via Prometheus pour monitoring temps réel
    """
    
    def __init__(self):
        """Initialise le service de métriques de budget"""
        self.historique_budgets: deque = deque(maxlen=BUDGET_HISTORY_MAX_TOURS)
        self.depenses_totales: float = 0.0
        self.gains_totaux: float = 0.0
        self.transactions_count: int = 0
        self.tour_actuel: int = 0
        
        # Cache LRU pour les calculs complexes
        if BUDGET_CACHE_ENABLED:
            # Convertir la liste en tuple pour le cache (tuples sont hashables)
            self._calculer_statistiques_cached = lru_cache(maxsize=BUDGET_CACHE_SIZE)(self._calculer_statistiques_cached)
    
    def ajouter_tour(self, entreprises: List[Entreprise], tour: int) -> None:
        """
        Ajoute un tour à l'historique des budgets
        
        Args:
            entreprises: Liste des entreprises
            tour: Numéro du tour
        """
        self.tour_actuel = tour
        
        # Collecter les budgets actuels
        budgets_tour = {
            'tour': tour,
            'timestamp': time.time(),
            'budgets': [entreprise.budget for entreprise in entreprises],
            'budgets_initiaux': [entreprise.budget_initial for entreprise in entreprises],
            'entreprises_count': len(entreprises)
        }
        
        self.historique_budgets.append(budgets_tour)
    
    def enregistrer_transaction(self, montant: float, type_transaction: str = "achat") -> None:
        """
        Enregistre une transaction pour le calcul des dépenses/gains
        
        Args:
            montant: Montant de la transaction
            type_transaction: Type de transaction ("achat" ou "vente")
        """
        self.transactions_count += 1
        
        if type_transaction == "achat":
            self.depenses_totales += montant
        elif type_transaction == "vente":
            self.gains_totaux += montant
    
    def calculer_metriques_budget(self, entreprises: List[Entreprise]) -> Dict[str, Any]:
        """
        Calcule toutes les métriques de budget
        
        Args:
            entreprises: Liste des entreprises
            
        Returns:
            Dictionnaire contenant toutes les métriques de budget
        """
        if not entreprises:
            return self._metriques_vides()
        
        # Budgets actuels
        budgets_actuels = [entreprise.budget for entreprise in entreprises]
        budgets_initiaux = [entreprise.budget_initial for entreprise in entreprises]
        
        # Calculs statistiques de base
        stats_actuels = self._calculer_statistiques(budgets_actuels)
        stats_initiaux = self._calculer_statistiques(budgets_initiaux)
        
        # Calculs de variation
        variations = self._calculer_variations(budgets_actuels, budgets_initiaux)
        
        # Calculs de tendance
        tendances = self._calculer_tendances()
        
        # Métriques de santé financière
        sante_financiere = self._calculer_sante_financiere(budgets_actuels)
        
        # Métriques d'alerte
        alertes = self._calculer_alertes(budgets_actuels)
        
        return {
            # Métriques de base (5 métriques) - Arrondies à 2 décimales pour éviter les erreurs de virgule flottante
            'budget_total_entreprises': round(sum(budgets_actuels), 2),  # Somme de tous les budgets
            'budget_moyen_entreprises': round(stats_actuels['moyenne'], 2),  # Moyenne arithmétique des budgets
            'budget_median_entreprises': round(stats_actuels['mediane'], 2),  # Médiane des budgets
            'budget_ecart_type_entreprises': round(stats_actuels['ecart_type'], 2),  # Écart-type des budgets
            'budget_coefficient_variation': round(stats_actuels['coefficient_variation'], 4),  # CV = écart-type/moyenne
            
            # Métriques de variation (3 métriques)
            'budget_variation_totale': round(variations['variation_totale'], 2),  # Somme des variations
            'budget_depenses_totales': round(self.depenses_totales, 2),  # Dépenses cumulées
            'budget_gains_totaux': round(self.gains_totaux, 2),  # Gains cumulés
            
            # Métriques de santé financière (3 métriques)
            'budget_ratio_depenses_revenus': round(self._calculer_ratio_depenses_revenus(), 4),  # Ratio dépenses/gains
            'budget_entreprises_critiques': alertes['entreprises_critiques'],  # Nombre d'entreprises critiques
            'budget_entreprises_faibles': alertes['entreprises_faibles'],  # Nombre d'entreprises faibles
            
            # Métriques de tendance (2 métriques)
            'budget_evolution_tour': round(tendances['evolution_tour'], 2),  # Évolution depuis le tour précédent
            'budget_tendance_globale': round(tendances['tendance_globale'], 2),  # Tendance sur l'historique
            
            # Métriques avancées (1 métrique)
            'budget_skewness': round(stats_actuels['skewness'], 4),  # Asymétrie de la distribution
            
            # Métadonnées
            'entreprises_count': len(entreprises),
            'tour_actuel': self.tour_actuel,
            'transactions_count': self.transactions_count
        }
    
    def _calculer_statistiques_cached(self, budgets_tuple: tuple) -> Dict[str, float]:
        """
        Version cachée de _calculer_statistiques (utilise des tuples)
        
        Args:
            budgets_tuple: Tuple des budgets (hashable pour le cache)
            
        Returns:
            Dictionnaire avec moyenne, médiane, écart-type, CV, skewness
        """
        budgets = list(budgets_tuple)
        return self._calculer_statistiques_impl(budgets)
    
    def _calculer_statistiques(self, budgets: List[float]) -> Dict[str, float]:
        """
        Calcule les statistiques de base d'une liste de budgets
        
        Args:
            budgets: Liste des budgets
            
        Returns:
            Dictionnaire avec moyenne, médiane, écart-type, CV, skewness
        """
        if not budgets:
            return {
                'moyenne': 0.0, 'mediane': 0.0, 'ecart_type': 0.0,
                'coefficient_variation': 0.0, 'skewness': 0.0
            }
        
        # Utiliser le cache si activé
        if BUDGET_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_cached'):
            return self._calculer_statistiques_cached(tuple(budgets))
        
        return self._calculer_statistiques_impl(budgets)
    
    def _calculer_statistiques_impl(self, budgets: List[float]) -> Dict[str, float]:
        """
        Implémentation réelle du calcul des statistiques
        
        Args:
            budgets: Liste des budgets
            
        Returns:
            Dictionnaire avec moyenne, médiane, écart-type, CV, skewness
        """
        if not budgets:
            return {
                'moyenne': 0.0, 'mediane': 0.0, 'ecart_type': 0.0,
                'coefficient_variation': 0.0, 'skewness': 0.0
            }
        
        n = len(budgets)
        moyenne = statistics.mean(budgets)
        mediane = statistics.median(budgets)
        
        # Écart-type
        if n > 1:
            ecart_type = statistics.stdev(budgets)
        else:
            ecart_type = 0.0
        
        # Coefficient de variation (CV = σ/μ)
        coefficient_variation = (ecart_type / moyenne) if moyenne > 0 else 0.0
        
        # Skewness (asymétrie) - formule simplifiée
        if n > 2 and ecart_type > 0:
            skewness = sum(((x - moyenne) / ecart_type) ** 3 for x in budgets) / n
        else:
            skewness = 0.0
        
        return {
            'moyenne': moyenne,
            'mediane': mediane,
            'ecart_type': ecart_type,
            'coefficient_variation': coefficient_variation,
            'skewness': skewness
        }
    
    def _calculer_variations(self, budgets_actuels: List[float], budgets_initiaux: List[float]) -> Dict[str, float]:
        """
        Calcule les variations entre budgets actuels et initiaux
        
        Args:
            budgets_actuels: Budgets actuels des entreprises
            budgets_initiaux: Budgets initiaux des entreprises
            
        Returns:
            Dictionnaire avec les variations calculées
        """
        if len(budgets_actuels) != len(budgets_initiaux):
            return {'variation_totale': 0.0}
        
        variations = [actuel - initial for actuel, initial in zip(budgets_actuels, budgets_initiaux)]
        variation_totale = sum(variations)
        
        return {
            'variation_totale': variation_totale
        }
    
    def _calculer_tendances(self) -> Dict[str, float]:
        """
        Calcule les tendances basées sur l'historique
        
        Returns:
            Dictionnaire avec les tendances calculées
        """
        if len(self.historique_budgets) < 2:
            return {
                'evolution_tour': 0.0,
                'tendance_globale': 0.0
            }
        
        # Évolution depuis le tour précédent
        tour_precedent = self.historique_budgets[-2]
        tour_actuel = self.historique_budgets[-1]
        
        budget_precedent = sum(tour_precedent['budgets'])
        budget_actuel = sum(tour_actuel['budgets'])
        
        evolution_tour = budget_actuel - budget_precedent
        
        # Tendance globale (sur les 10 derniers tours)
        if len(self.historique_budgets) >= 10:
            tours_recents = list(self.historique_budgets)[-10:]
            budgets_recents = [sum(tour['budgets']) for tour in tours_recents]
            
            # Calcul de la pente (tendance linéaire)
            n = len(budgets_recents)
            x_values = list(range(n))
            y_values = budgets_recents
            
            # Formule de régression linéaire simplifiée
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            
            if n * sum_x2 - sum_x * sum_x != 0:
                pente = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                tendance_globale = pente
            else:
                tendance_globale = 0.0
        else:
            tendance_globale = evolution_tour
        
        return {
            'evolution_tour': evolution_tour,
            'tendance_globale': tendance_globale
        }
    
    def _calculer_sante_financiere(self, budgets: List[float]) -> Dict[str, float]:
        """
        Calcule les métriques de santé financière
        
        Args:
            budgets: Liste des budgets actuels
            
        Returns:
            Dictionnaire avec les métriques de santé financière
        """
        if not budgets:
            return {'ratio_depenses_revenus': 0.0}
        
        # Ratio dépenses/revenus
        ratio_depenses_revenus = self._calculer_ratio_depenses_revenus()
        
        return {
            'ratio_depenses_revenus': ratio_depenses_revenus
        }
    
    def _calculer_ratio_depenses_revenus(self) -> float:
        """
        Calcule le ratio dépenses/revenus
        
        Returns:
            Ratio dépenses/revenus (0 si pas de revenus, 999999 si infini)
        """
        if self.gains_totaux > 0:
            return self.depenses_totales / self.gains_totaux
        elif self.depenses_totales > 0:
            return 999999.0  # Dépenses mais pas de revenus (évite l'infini)
        else:
            return 0.0  # Aucune activité
    
    def _calculer_alertes(self, budgets: List[float]) -> Dict[str, int]:
        """
        Calcule les alertes basées sur les seuils de budget
        
        Args:
            budgets: Liste des budgets actuels
            
        Returns:
            Dictionnaire avec le nombre d'entreprises dans chaque catégorie
        """
        entreprises_critiques = sum(1 for budget in budgets if budget <= BUDGET_CRITIQUE_SEUIL)
        entreprises_faibles = sum(1 for budget in budgets if BUDGET_CRITIQUE_SEUIL < budget <= BUDGET_FAIBLE_SEUIL)
        entreprises_normales = sum(1 for budget in budgets if BUDGET_FAIBLE_SEUIL < budget <= BUDGET_ELEVE_SEUIL)
        entreprises_elevees = sum(1 for budget in budgets if budget > BUDGET_ELEVE_SEUIL)
        
        return {
            'entreprises_critiques': entreprises_critiques,
            'entreprises_faibles': entreprises_faibles,
            'entreprises_normales': entreprises_normales,
            'entreprises_elevees': entreprises_elevees
        }
    
    def _metriques_vides(self) -> Dict[str, Any]:
        """
        Retourne des métriques vides quand il n'y a pas d'entreprises
        
        Returns:
            Dictionnaire avec toutes les métriques à 0
        """
        return {
            'budget_total_entreprises': 0.0,
            'budget_moyen_entreprises': 0.0,
            'budget_median_entreprises': 0.0,
            'budget_ecart_type_entreprises': 0.0,
            'budget_coefficient_variation': 0.0,
            'budget_variation_totale': 0.0,
            'budget_depenses_totales': self.depenses_totales,
            'budget_gains_totaux': self.gains_totaux,
            'budget_ratio_depenses_revenus': 0.0,
            'budget_entreprises_critiques': 0,
            'budget_entreprises_faibles': 0,
            'budget_evolution_tour': 0.0,
            'budget_tendance_globale': 0.0,
            'budget_skewness': 0.0,
            'entreprises_count': 0,
            'tour_actuel': self.tour_actuel,
            'transactions_count': self.transactions_count
        }
    
    def reset(self) -> None:
        """Réinitialise le service (pour les tests)"""
        self.historique_budgets.clear()
        self.depenses_totales = 0.0
        self.gains_totaux = 0.0
        self.transactions_count = 0
        self.tour_actuel = 0
        
        # Vider le cache LRU
        if BUDGET_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_cached'):
            self._calculer_statistiques_cached.cache_clear()
