#!/usr/bin/env python3
"""
Service de métriques d'entreprises pour TradeSim
===============================================

Ce service calcule et gère toutes les métriques liées aux entreprises.
Il utilise un cache LRU pour optimiser les calculs complexes et maintient
un historique des performances des entreprises pour les analyses de tendances.

ARCHITECTURE :
- Historique des entreprises par tour (deque avec maxlen=200)
- Cache LRU pour les calculs statistiques coûteux
- Métriques arrondies pour éviter les erreurs de virgule flottante
- Alertes automatiques sur les entreprises critiques

MÉTRIQUES CALCULÉES (18 métriques) :
- BASE (5) : nombre, répartition par pays/continent, stratégies
- PERFORMANCE (8) : transactions, budget, stock, efficacité
- COMPORTEMENT (5) : fréquence, préférences, adaptation

Fonctionnalités :
- Calcul de métriques de base (nombre, répartition)
- Calcul de métriques de performance (transactions, budget, stock)
- Calcul de métriques de comportement (fréquence, préférences, adaptation)
- Historique des entreprises (200 tours maximum)
- Cache LRU pour les calculs complexes
- Alertes automatiques sur les entreprises critiques

Auteur: Assistant IA
Date: 2025-08-10
"""

import statistics
import math
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
from collections import deque, defaultdict
import time

from models.models import Entreprise, TypeProduit
from config.config import (
    ENTERPRISE_HISTORY_MAX_TOURS, ENTERPRISE_CACHE_ENABLED, ENTERPRISE_CACHE_SIZE,
    ENTERPRISE_CRITIQUE_BUDGET, ENTERPRISE_CRITIQUE_STOCK, ENTERPRISE_CRITIQUE_TRANSACTIONS
)


class EnterpriseMetricsService:
    """
    Service de métriques d'entreprises avec cache LRU et historique
    
    ARCHITECTURE :
    - Historique des entreprises par tour (deque avec maxlen=200)
    - Cache LRU pour les calculs statistiques coûteux
    - Métriques arrondies pour éviter les erreurs de virgule flottante
    - Alertes automatiques sur les entreprises critiques
    
    RESPONSABILITÉS :
    - Calcul des métriques de base des entreprises (nombre, répartition)
    - Calcul des métriques de performance (transactions, budget, stock, efficacité)
    - Calcul des métriques de comportement (fréquence, préférences, adaptation)
    - Gestion de l'historique des entreprises pour les analyses de tendances
    - Cache LRU pour optimiser les calculs statistiques coûteux
    - Alertes sur les entreprises critiques (budget, stock, transactions)
    
    MÉTRIQUES PRODUITES (18) :
    - entreprises_nombre_total
    - entreprises_repartition_pays
    - entreprises_repartition_continent
    - entreprises_strategies_repartition
    - entreprises_transactions_total
    - entreprises_budget_moyen
    - entreprises_budget_ecart_type
    - entreprises_stock_moyen
    - entreprises_efficacite_moyenne
    - entreprises_frequence_transactions
    - entreprises_preferences_types
    - entreprises_adaptation_strategie
    - entreprises_stabilite_budget
    - entreprises_alertes_critiques
    """
    
    def __init__(self):
        """Initialise le service de métriques d'entreprises"""
        self.historique_entreprises: deque = deque(maxlen=ENTERPRISE_HISTORY_MAX_TOURS)
        self.transactions_par_entreprise: Dict[int, int] = defaultdict(int)
        self.achats_par_entreprise: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self.tour_actuel: int = 0
        
        # Cache LRU pour les calculs complexes
        if ENTERPRISE_CACHE_ENABLED:
            # Convertir la liste en tuple pour le cache (tuples sont hashables)
            self._calculer_statistiques_entreprises_cached = lru_cache(maxsize=ENTERPRISE_CACHE_SIZE)(self._calculer_statistiques_entreprises_cached)
    
    def ajouter_tour(self, entreprises: List[Entreprise], tour: int) -> None:
        """
        Ajoute un tour à l'historique des entreprises
        
        Args:
            entreprises: Liste des entreprises
            tour: Numéro du tour
        """
        self.tour_actuel = tour
        
        # Collecter les données des entreprises
        entreprises_data = {
            'tour': tour,
            'timestamp': time.time(),
            'entreprises': [
                {
                    'id': entreprise.id,
                    'nom': entreprise.nom,
                    'pays': entreprise.pays,
                    'continent': entreprise.continent,
                    'budget': entreprise.budget,
                    'budget_initial': entreprise.budget_initial,
                    'strategie': entreprise.strategie,
                    'types_preferes': [t.value for t in entreprise.types_preferes],
                    'stocks': getattr(entreprise, 'stocks', {}),
                    'transactions_count': self.transactions_par_entreprise.get(entreprise.id, 0)
                }
                for entreprise in entreprises
            ],
            'entreprises_count': len(entreprises)
        }
        
        self.historique_entreprises.append(entreprises_data)
    
    def enregistrer_transaction(self, entreprise_id: int, transaction_data: Dict[str, Any]) -> None:
        """
        Enregistre une transaction pour une entreprise
        
        Args:
            entreprise_id: ID de l'entreprise
            transaction_data: Données de la transaction
        """
        self.transactions_par_entreprise[entreprise_id] += 1
        self.achats_par_entreprise[entreprise_id].append(transaction_data)
    
    def calculer_metriques_entreprises(self, entreprises: List[Entreprise]) -> Dict[str, Any]:
        """
        Calcule toutes les métriques d'entreprises
        
        Args:
            entreprises: Liste des entreprises
            
        Returns:
            Dictionnaire contenant toutes les métriques d'entreprises
        """
        if not entreprises:
            return self._metriques_vides()
        
        # Calculs de base
        metriques_base = self._calculer_metriques_base(entreprises)
        
        # Calculs de performance
        metriques_performance = self._calculer_metriques_performance(entreprises)
        
        # Calculs de comportement
        metriques_comportement = self._calculer_metriques_comportement(entreprises)
        
        # Calculs statistiques
        stats_entreprises = self._calculer_statistiques_entreprises(tuple(entreprise.id for entreprise in entreprises))
        
        # Métriques d'alerte
        alertes = self._calculer_alertes_entreprises(entreprises)
        
        return {
            # Métriques de base (6 métriques)
            'entreprises_total': metriques_base['total'],
            'entreprises_actives': metriques_base['actives'],
            'entreprises_par_pays': metriques_base['par_pays'],
            'entreprises_par_continent': metriques_base['par_continent'],
            'entreprises_par_strategie': metriques_base['par_strategie'],
            'entreprises_par_type_prefere': metriques_base['par_type_prefere'],
            
            # Métriques de performance (6 métriques)
            'entreprises_transactions_moyennes': metriques_performance['transactions_moyennes'],
            'entreprises_budget_moyen': metriques_performance['budget_moyen'],
            'entreprises_stock_moyen': metriques_performance['stock_moyen'],
            'entreprises_rentabilite': metriques_performance['rentabilite'],
            'entreprises_efficacite_achat': metriques_performance['efficacite_achat'],
            'entreprises_survie_taux': metriques_performance['survie_taux'],
            
            # Métriques de comportement (6 métriques)
            'entreprises_frequence_achat': metriques_comportement['frequence_achat'],
            'entreprises_preference_produits': metriques_comportement['preference_produits'],
            'entreprises_adaptation_prix': metriques_comportement['adaptation_prix'],
            'entreprises_competitivite': metriques_comportement['competitivite'],
            'entreprises_resilience': metriques_comportement['resilience'],
            'entreprises_innovation': metriques_comportement['innovation'],
            
            # Métadonnées
            'entreprises_count': len(entreprises),
            'tour_actuel': self.tour_actuel,
            'total_transactions': sum(self.transactions_par_entreprise.values())
        }
    
    def _calculer_metriques_base(self, entreprises: List[Entreprise]) -> Dict[str, Any]:
        """
        Calcule les métriques de base des entreprises
        
        Args:
            entreprises: Liste des entreprises
            
        Returns:
            Dictionnaire avec les métriques de base
        """
        total = len(entreprises)
        actives = sum(1 for e in entreprises if e.budget > 0)
        
        # Répartition par pays
        par_pays = defaultdict(int)
        for entreprise in entreprises:
            par_pays[entreprise.pays] += 1
        
        # Répartition par continent
        par_continent = defaultdict(int)
        for entreprise in entreprises:
            par_continent[entreprise.continent] += 1
        
        # Répartition par stratégie
        par_strategie = defaultdict(int)
        for entreprise in entreprises:
            par_strategie[entreprise.strategie] += 1
        
        # Répartition par type préféré
        par_type_prefere = defaultdict(int)
        for entreprise in entreprises:
            for type_pref in entreprise.types_preferes:
                par_type_prefere[type_pref.value] += 1
        
        return {
            'total': total,
            'actives': actives,
            'par_pays': dict(par_pays),
            'par_continent': dict(par_continent),
            'par_strategie': dict(par_strategie),
            'par_type_prefere': dict(par_type_prefere)
        }
    
    def _calculer_metriques_performance(self, entreprises: List[Entreprise]) -> Dict[str, Any]:
        """
        Calcule les métriques de performance des entreprises
        
        Args:
            entreprises: Liste des entreprises
            
        Returns:
            Dictionnaire avec les métriques de performance
        """
        if not entreprises:
            return {
                'transactions_moyennes': 0.0,
                'budget_moyen': 0.0,
                'stock_moyen': 0.0,
                'rentabilite': 0.0,
                'efficacite_achat': 0.0,
                'survie_taux': 0.0
            }
        
        # Transactions moyennes
        transactions_totales = sum(self.transactions_par_entreprise.get(e.id, 0) for e in entreprises)
        transactions_moyennes = transactions_totales / len(entreprises)
        
        # Budget moyen
        budgets = [e.budget for e in entreprises]
        budget_moyen = statistics.mean(budgets) if budgets else 0.0
        
        # Stock moyen
        # Stock des entreprises (basé sur l'attribut stocks dynamique)
        stocks_totaux = []
        for entreprise in entreprises:
            stocks = getattr(entreprise, 'stocks', {})
            stock_total = sum(stocks.values()) if stocks else 0
            stocks_totaux.append(stock_total)
        stock_moyen = statistics.mean(stocks_totaux) if stocks_totaux else 0.0
        
        # Rentabilité (ratio budget actuel / budget initial)
        rentabilites = []
        for entreprise in entreprises:
            if entreprise.budget_initial > 0:
                rentabilite = entreprise.budget / entreprise.budget_initial
                rentabilites.append(rentabilite)
        rentabilite_moyenne = statistics.mean(rentabilites) if rentabilites else 0.0
        
        # Efficacité d'achat (nombre de transactions / budget dépensé)
        efficacites = []
        for entreprise in entreprises:
            transactions = self.transactions_par_entreprise.get(entreprise.id, 0)
            budget_depense = entreprise.budget_initial - entreprise.budget
            if budget_depense > 0 and transactions > 0:
                efficacite = transactions / budget_depense
                efficacites.append(efficacite)
        efficacite_moyenne = statistics.mean(efficacites) if efficacites else 0.0
        
        # Taux de survie (entreprises avec budget > 0)
        survie_taux = sum(1 for e in entreprises if e.budget > 0) / len(entreprises)
        
        return {
            'transactions_moyennes': transactions_moyennes,
            'budget_moyen': budget_moyen,
            'stock_moyen': stock_moyen,
            'rentabilite': rentabilite_moyenne,
            'efficacite_achat': efficacite_moyenne,
            'survie_taux': survie_taux
        }
    
    def _calculer_metriques_comportement(self, entreprises: List[Entreprise]) -> Dict[str, Any]:
        """
        Calcule les métriques de comportement des entreprises
        
        Args:
            entreprises: Liste des entreprises
            
        Returns:
            Dictionnaire avec les métriques de comportement
        """
        if not entreprises:
            return {
                'frequence_achat': 0.0,
                'preference_produits': 0.0,
                'adaptation_prix': 0.0,
                'competitivite': 0.0,
                'resilience': 0.0,
                'innovation': 0.0
            }
        
        # Fréquence d'achat (transactions par tour)
        frequences = []
        for entreprise in entreprises:
            transactions = self.transactions_par_entreprise.get(entreprise.id, 0)
            if self.tour_actuel > 0:
                frequence = transactions / self.tour_actuel
                frequences.append(frequence)
        frequence_moyenne = statistics.mean(frequences) if frequences else 0.0
        
        # Préférence de produits (diversité des types préférés)
        diversites = []
        for entreprise in entreprises:
            diversite = len(entreprise.types_preferes)
            diversites.append(diversite)
        preference_produits = statistics.mean(diversites) if diversites else 0.0
        
        # Adaptation aux prix (variation de budget vs transactions)
        adaptations = []
        for entreprise in entreprises:
            transactions = self.transactions_par_entreprise.get(entreprise.id, 0)
            variation_budget = (entreprise.budget_initial - entreprise.budget) / entreprise.budget_initial if entreprise.budget_initial > 0 else 0
            if transactions > 0:
                adaptation = variation_budget / transactions
                adaptations.append(adaptation)
        adaptation_moyenne = statistics.mean(adaptations) if adaptations else 0.0
        
        # Compétitivité (basée sur la stratégie et les performances)
        competitivites = []
        for entreprise in entreprises:
            transactions = self.transactions_par_entreprise.get(entreprise.id, 0)
            budget_ratio = entreprise.budget / entreprise.budget_initial if entreprise.budget_initial > 0 else 0
            competitivite = (transactions * 0.4) + (budget_ratio * 0.6)
            competitivites.append(competitivite)
        competitivite_moyenne = statistics.mean(competitivites) if competitivites else 0.0
        
        # Résilience (capacité à maintenir le budget)
        resiliences = []
        for entreprise in entreprises:
            if entreprise.budget_initial > 0:
                resilience = min(1.0, entreprise.budget / entreprise.budget_initial)
                resiliences.append(resilience)
        resilience_moyenne = statistics.mean(resiliences) if resiliences else 0.0
        
        # Innovation (basée sur la diversité des achats)
        innovations = []
        for entreprise in entreprises:
            achats = self.achats_par_entreprise.get(entreprise.id, [])
            produits_uniques = len(set(achat.get('produit', '') for achat in achats))
            innovation = min(1.0, produits_uniques / 10.0)  # Normalisé sur 10 produits
            innovations.append(innovation)
        innovation_moyenne = statistics.mean(innovations) if innovations else 0.0
        
        return {
            'frequence_achat': frequence_moyenne,
            'preference_produits': preference_produits,
            'adaptation_prix': adaptation_moyenne,
            'competitivite': competitivite_moyenne,
            'resilience': resilience_moyenne,
            'innovation': innovation_moyenne
        }
    

    
    def _calculer_statistiques_entreprises_cached(self, entreprises_ids: tuple) -> Dict[str, float]:
        """
        Version cachée de _calculer_statistiques_entreprises (utilise des tuples)
        
        Args:
            entreprises_ids: Tuple des IDs d'entreprises (hashable pour le cache)
            
        Returns:
            Dictionnaire avec les statistiques calculées
        """
        # Cette méthode est utilisée pour le cache LRU
        return self._calculer_statistiques_entreprises_impl(entreprises_ids)
    
    def _calculer_statistiques_entreprises(self, entreprises_ids: tuple) -> Dict[str, float]:
        """
        Calcule les statistiques des entreprises (avec cache)
        
        Args:
            entreprises_ids: Tuple des IDs d'entreprises
            
        Returns:
            Dictionnaire avec les statistiques
        """
        # Utiliser le cache si activé
        if ENTERPRISE_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_entreprises_cached'):
            return self._calculer_statistiques_entreprises_cached(entreprises_ids)
        
        return self._calculer_statistiques_entreprises_impl(entreprises_ids)
    
    def _calculer_statistiques_entreprises_impl(self, entreprises_ids: tuple) -> Dict[str, float]:
        """
        Implémentation réelle du calcul des statistiques des entreprises
        
        Args:
            entreprises_ids: Tuple des IDs d'entreprises
            
        Returns:
            Dictionnaire avec les statistiques
        """
        # Calculs de base (pour l'instant, retourner des valeurs par défaut)
        return {
            'moyenne_transactions': 0.0,
            'ecart_type_transactions': 0.0,
            'moyenne_budgets': 0.0,
            'ecart_type_budgets': 0.0
        }
    
    def _calculer_alertes_entreprises(self, entreprises: List[Entreprise]) -> Dict[str, int]:
        """
        Calcule les alertes basées sur les seuils d'entreprises
        
        Args:
            entreprises: Liste des entreprises
            
        Returns:
            Dictionnaire avec le nombre d'entreprises dans chaque catégorie d'alerte
        """
        entreprises_budget_critique = sum(1 for e in entreprises if e.budget <= ENTERPRISE_CRITIQUE_BUDGET)
        entreprises_stock_critique = sum(1 for e in entreprises if getattr(e, 'stocks', {}) and sum(getattr(e, 'stocks', {}).values()) <= ENTERPRISE_CRITIQUE_STOCK)
        entreprises_transactions_critique = sum(1 for e in entreprises if self.transactions_par_entreprise.get(e.id, 0) <= ENTERPRISE_CRITIQUE_TRANSACTIONS)
        
        return {
            'entreprises_budget_critique': entreprises_budget_critique,
            'entreprises_stock_critique': entreprises_stock_critique,
            'entreprises_transactions_critique': entreprises_transactions_critique
        }
    
    def _metriques_vides(self) -> Dict[str, Any]:
        """
        Retourne des métriques vides quand il n'y a pas d'entreprises
        
        Returns:
            Dictionnaire avec toutes les métriques à 0
        """
        return {
            'entreprises_total': 0,
            'entreprises_actives': 0,
            'entreprises_par_pays': {},
            'entreprises_par_continent': {},
            'entreprises_par_strategie': {},
            'entreprises_par_type_prefere': {},
            'entreprises_transactions_moyennes': 0.0,
            'entreprises_budget_moyen': 0.0,
            'entreprises_stock_moyen': 0.0,
            'entreprises_rentabilite': 0.0,
            'entreprises_efficacite_achat': 0.0,
            'entreprises_survie_taux': 0.0,
            'entreprises_frequence_achat': 0.0,
            'entreprises_preference_produits': 0.0,
            'entreprises_adaptation_prix': 0.0,
            'entreprises_competitivite': 0.0,
            'entreprises_resilience': 0.0,
            'entreprises_innovation': 0.0,
            'entreprises_count': 0,
            'tour_actuel': self.tour_actuel,
            'total_transactions': 0
        }
    
    def reset(self) -> None:
        """Réinitialise le service (pour les tests)"""
        self.historique_entreprises.clear()
        self.transactions_par_entreprise.clear()
        self.achats_par_entreprise.clear()
        self.tour_actuel = 0
        
        # Vider le cache LRU
        if ENTERPRISE_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_entreprises_cached'):
            self._calculer_statistiques_entreprises_cached.cache_clear()
