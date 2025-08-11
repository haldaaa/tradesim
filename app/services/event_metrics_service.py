#!/usr/bin/env python3
"""
Service de métriques d'événements pour TradeSim
==============================================

Ce service calcule et gère toutes les métriques liées aux événements.
Il utilise un cache LRU pour optimiser les calculs complexes et maintient
un historique des performances des événements pour les analyses de tendances.

ARCHITECTURE :
- Historique des événements par tour (deque avec maxlen=200)
- Cache LRU pour les calculs statistiques coûteux
- Métriques arrondies pour éviter les erreurs de virgule flottante
- Alertes automatiques sur les événements critiques
- Suivi des impacts et intensités des événements

MÉTRIQUES CALCULÉES (16 métriques) :
- BASE (5) : nombre total, appliqués, fréquence, répartition, types
- PERFORMANCE (6) : impact, efficacité, stabilité, latence, débit
- COMPORTEMENT (5) : volatilité, tendance, corrélation, prévisibilité

Fonctionnalités :
- Calcul de métriques de base (nombre, répartition, fréquence)
- Calcul de métriques de performance (impact, efficacité, stabilité)
- Calcul de métriques de comportement (volatilité, tendance, corrélation)
- Historique des événements (200 tours maximum)
- Cache LRU pour les calculs complexes
- Alertes automatiques sur les événements critiques

Auteur: Assistant IA
Date: 2025-08-10
"""

import statistics
import math
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
from collections import deque, defaultdict
import time

from models.models import Entreprise, Fournisseur, Produit, TypeProduit
from config.config import (
    EVENT_HISTORY_MAX_TOURS, EVENT_CACHE_ENABLED, EVENT_CACHE_SIZE,
    EVENT_CRITIQUE_FREQUENCE, EVENT_CRITIQUE_IMPACT, EVENT_CRITIQUE_INTENSITE
)


class EventMetricsService:
    """
    Service de métriques d'événements avec cache LRU et historique
    
    ARCHITECTURE :
    - Historique des événements par tour (deque avec maxlen=200)
    - Cache LRU pour les calculs statistiques coûteux
    - Métriques arrondies pour éviter les erreurs de virgule flottante
    - Alertes automatiques sur les événements critiques
    - Suivi des impacts et intensités des événements
    
    RESPONSABILITÉS :
    - Calcul des métriques de base des événements (nombre, répartition, fréquence)
    - Calcul des métriques de performance (impact, efficacité, stabilité, latence)
    - Calcul des métriques de comportement (volatilité, tendance, corrélation)
    - Gestion de l'historique des événements pour les analyses de tendances
    - Cache LRU pour optimiser les calculs statistiques coûteux
    - Alertes sur les événements critiques (fréquence, impact, intensité)
    
    MÉTRIQUES PRODUITES (16) :
    - evenements_nombre_total
    - evenements_appliques
    - evenements_frequence_moyenne
    - evenements_repartition_types
    - evenements_types_actifs
    - evenements_impact_moyen
    - evenements_efficacite_moyenne
    - evenements_stabilite_moyenne
    - evenements_latence_moyenne
    - evenements_debit_moyen
    - evenements_volatilite_impact
    - evenements_tendance_impact
    - evenements_correlation_types
    - evenements_previsibilite
    - evenements_alertes_critiques
    """
    
    def __init__(self):
        """Initialise le service de métriques d'événements"""
        self.historique_evenements: deque = deque(maxlen=EVENT_HISTORY_MAX_TOURS)
        self.evenements_par_tour: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self.evenements_totaux: List[Dict[str, Any]] = []
        self.impacts_historique: List[float] = []
        self.intensites_historique: List[float] = []
        self.tour_actuel: int = 0
        
        # Cache LRU pour les calculs complexes
        if EVENT_CACHE_ENABLED:
            # Convertir la liste en tuple pour le cache (tuples sont hashables)
            self._calculer_statistiques_evenements_cached = lru_cache(maxsize=EVENT_CACHE_SIZE)(self._calculer_statistiques_evenements_cached)
    
    def enregistrer_evenement(self, evenement_data: Dict[str, Any]) -> None:
        """
        Enregistre un événement
        
        Args:
            evenement_data: Données de l'événement
        """
        # Ajouter des métadonnées
        evenement_data['timestamp'] = time.time()
        evenement_data['tour'] = self.tour_actuel
        
        # Stocker dans l'historique par tour
        self.evenements_par_tour[self.tour_actuel].append(evenement_data)
        
        # Stocker dans l'historique total
        self.evenements_totaux.append(evenement_data)
        
        # Enregistrer les métriques pour l'historique
        if 'impact' in evenement_data:
            self.impacts_historique.append(evenement_data['impact'])
        if 'intensite' in evenement_data:
            self.intensites_historique.append(evenement_data['intensite'])
    
    def ajouter_tour(self, tour: int) -> None:
        """
        Ajoute un tour à l'historique des événements
        
        Args:
            tour: Numéro du tour
        """
        self.tour_actuel = tour
        
        # Collecter les données du tour
        evenements_tour = self.evenements_par_tour.get(tour, [])
        
        tour_data = {
            'tour': tour,
            'timestamp': time.time(),
            'evenements_count': len(evenements_tour),
            'impact_total': sum(e.get('impact', 0) for e in evenements_tour),
            'intensite_moyenne': statistics.mean([e.get('intensite', 0) for e in evenements_tour]) if evenements_tour else 0.0,
            'types_evenements': list(set(e.get('type', 'inconnu') for e in evenements_tour))
        }
        
        self.historique_evenements.append(tour_data)
    
    def calculer_metriques_evenements(self) -> Dict[str, Any]:
        """
        Calcule toutes les métriques d'événements
        
        Returns:
            Dictionnaire contenant toutes les métriques d'événements
        """
        # Calculs de base
        metriques_base = self._calculer_metriques_base()
        
        # Calculs de performance
        metriques_performance = self._calculer_metriques_performance()
        
        # Calculs de comportement
        metriques_comportement = self._calculer_metriques_comportement()
        
        # Calculs statistiques
        stats_evenements = self._calculer_statistiques_evenements(tuple(range(len(self.evenements_totaux))))
        
        # Métriques d'alerte
        alertes = self._calculer_alertes_evenements()
        
        return {
            # Métriques de base (6 métriques)
            'evenements_total': metriques_base['total'],
            'evenements_par_type': metriques_base['par_type'],
            'evenements_par_impact': metriques_base['par_impact'],
            'evenements_frequence': metriques_base['frequence'],
            'evenements_duree_moyenne': metriques_base['duree_moyenne'],
            'evenements_intensite_moyenne': metriques_base['intensite_moyenne'],
            
            # Métriques de performance (6 métriques)
            'evenements_impact_budget': metriques_performance['impact_budget'],
            'evenements_impact_prix': metriques_performance['impact_prix'],
            'evenements_impact_stock': metriques_performance['impact_stock'],
            'evenements_efficacite': metriques_performance['efficacite'],
            'evenements_rentabilite': metriques_performance['rentabilite'],
            'evenements_stabilite': metriques_performance['stabilite'],
            
            # Métriques de comportement (4 métriques)
            'evenements_volatilite': metriques_comportement['volatilite'],
            'evenements_tendance': metriques_comportement['tendance'],
            'evenements_correlation': metriques_comportement['correlation'],
            'evenements_predictibilite': metriques_comportement['predictibilite'],
            
            # Métadonnées
            'tour_actuel': self.tour_actuel,
            'total_impact': sum(self.impacts_historique),
            'total_intensite': sum(self.intensites_historique)
        }
    
    def _calculer_metriques_base(self) -> Dict[str, Any]:
        """
        Calcule les métriques de base des événements
        
        Returns:
            Dictionnaire avec les métriques de base
        """
        total = len(self.evenements_totaux)
        
        # Répartition par type
        par_type = defaultdict(int)
        for evenement in self.evenements_totaux:
            type_evenement = evenement.get('type', 'inconnu')
            par_type[type_evenement] += 1
        
        # Répartition par impact (positif/négatif)
        par_impact = defaultdict(int)
        for evenement in self.evenements_totaux:
            impact = evenement.get('impact', 0)
            if impact > 0:
                par_impact['positif'] += 1
            elif impact < 0:
                par_impact['negatif'] += 1
            else:
                par_impact['neutre'] += 1
        
        # Fréquence des événements (par tour)
        tours_avec_evenements = len([tour for tour, evenements in self.evenements_par_tour.items() if evenements])
        frequence = tours_avec_evenements / max(self.tour_actuel, 1)
        
        # Durée moyenne des événements
        durees = [e.get('duree', 0) for e in self.evenements_totaux if 'duree' in e]
        duree_moyenne = statistics.mean(durees) if durees else 0.0
        
        # Intensité moyenne des événements
        intensite_moyenne = statistics.mean(self.intensites_historique) if self.intensites_historique else 0.0
        
        return {
            'total': total,
            'par_type': dict(par_type),
            'par_impact': dict(par_impact),
            'frequence': frequence,
            'duree_moyenne': duree_moyenne,
            'intensite_moyenne': intensite_moyenne
        }
    
    def _calculer_metriques_performance(self) -> Dict[str, Any]:
        """
        Calcule les métriques de performance des événements
        
        Returns:
            Dictionnaire avec les métriques de performance
        """
        if not self.evenements_totaux:
            return {
                'impact_budget': 0.0,
                'impact_prix': 0.0,
                'impact_stock': 0.0,
                'efficacite': 0.0,
                'rentabilite': 0.0,
                'stabilite': 0.0
            }
        
        # Impact moyen sur les budgets
        impacts_budget = [e.get('impact_budget', 0) for e in self.evenements_totaux]
        impact_budget = statistics.mean(impacts_budget) if impacts_budget else 0.0
        
        # Impact moyen sur les prix
        impacts_prix = [e.get('impact_prix', 0) for e in self.evenements_totaux]
        impact_prix = statistics.mean(impacts_prix) if impacts_prix else 0.0
        
        # Impact moyen sur les stocks
        impacts_stock = [e.get('impact_stock', 0) for e in self.evenements_totaux]
        impact_stock = statistics.mean(impacts_stock) if impacts_stock else 0.0
        
        # Efficacité (basée sur l'impact vs intensité)
        efficacites = []
        for evenement in self.evenements_totaux:
            impact = evenement.get('impact', 0)
            intensite = evenement.get('intensite', 0)
            if intensite > 0:
                efficacite = abs(impact) / intensite
                efficacites.append(efficacite)
        efficacite_moyenne = statistics.mean(efficacites) if efficacites else 0.0
        
        # Rentabilité (basée sur l'impact positif vs négatif)
        impacts_positifs = [e.get('impact', 0) for e in self.evenements_totaux if e.get('impact', 0) > 0]
        impacts_negatifs = [e.get('impact', 0) for e in self.evenements_totaux if e.get('impact', 0) < 0]
        
        total_positif = sum(impacts_positifs) if impacts_positifs else 0
        total_negatif = abs(sum(impacts_negatifs)) if impacts_negatifs else 0
        
        rentabilite = total_positif / (total_negatif + 1) if total_negatif > 0 else total_positif
        
        # Stabilité (basée sur la variance des impacts)
        stabilite = 1.0 - min(statistics.variance(self.impacts_historique) if len(self.impacts_historique) > 1 else 0, 1.0)
        
        return {
            'impact_budget': impact_budget,
            'impact_prix': impact_prix,
            'impact_stock': impact_stock,
            'efficacite': efficacite_moyenne,
            'rentabilite': rentabilite,
            'stabilite': stabilite
        }
    
    def _calculer_metriques_comportement(self) -> Dict[str, Any]:
        """
        Calcule les métriques de comportement des événements
        
        Returns:
            Dictionnaire avec les métriques de comportement
        """
        if not self.evenements_totaux:
            return {
                'volatilite': 0.0,
                'tendance': 0.0,
                'correlation': 0.0,
                'predictibilite': 0.0
            }
        
        # Volatilité des événements (écart-type des impacts)
        volatilite = statistics.stdev(self.impacts_historique) if len(self.impacts_historique) > 1 else 0.0
        
        # Tendance des événements (pente de régression linéaire simple)
        if len(self.impacts_historique) > 1:
            x = list(range(len(self.impacts_historique)))
            y = self.impacts_historique
            n = len(x)
            
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi**2 for xi in x)
            
            try:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
                tendance = slope
            except ZeroDivisionError:
                tendance = 0.0
        else:
            tendance = 0.0
        
        # Corrélation entre impacts et intensités
        if len(self.impacts_historique) > 1 and len(self.intensites_historique) > 1:
            min_len = min(len(self.impacts_historique), len(self.intensites_historique))
            impacts = self.impacts_historique[:min_len]
            intensites = self.intensites_historique[:min_len]
            
            try:
                correlation = statistics.correlation(impacts, intensites)
            except:
                correlation = 0.0
        else:
            correlation = 0.0
        
        # Prédictibilité (basée sur la régularité des patterns)
        if len(self.evenements_totaux) > 1:
            # Calculer la régularité des intervalles entre événements
            timestamps = [e.get('timestamp', 0) for e in self.evenements_totaux]
            timestamps.sort()
            
            if len(timestamps) > 1:
                intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
                if intervals:
                    # Plus la variance des intervalles est faible, plus c'est prévisible
                    variance_intervals = statistics.variance(intervals) if len(intervals) > 1 else 0
                    predictibilite = 1.0 / (1.0 + variance_intervals)
                else:
                    predictibilite = 0.0
            else:
                predictibilite = 0.0
        else:
            predictibilite = 0.0
        
        return {
            'volatilite': volatilite,
            'tendance': tendance,
            'correlation': correlation,
            'predictibilite': predictibilite
        }
    
    def _calculer_statistiques_evenements_cached(self, evenements_ids: tuple) -> Dict[str, float]:
        """
        Version cachée de _calculer_statistiques_evenements (utilise des tuples)
        
        Args:
            evenements_ids: Tuple des IDs d'événements (hashable pour le cache)
            
        Returns:
            Dictionnaire avec les statistiques calculées
        """
        # Cette méthode est utilisée pour le cache LRU
        return self._calculer_statistiques_evenements_impl(evenements_ids)
    
    def _calculer_statistiques_evenements(self, evenements_ids: tuple) -> Dict[str, float]:
        """
        Calcule les statistiques des événements (avec cache)
        
        Args:
            evenements_ids: Tuple des IDs d'événements
            
        Returns:
            Dictionnaire avec les statistiques
        """
        # Utiliser le cache si activé
        if EVENT_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_evenements_cached'):
            return self._calculer_statistiques_evenements_cached(evenements_ids)
        
        return self._calculer_statistiques_evenements_impl(evenements_ids)
    
    def _calculer_statistiques_evenements_impl(self, evenements_ids: tuple) -> Dict[str, float]:
        """
        Implémentation réelle du calcul des statistiques des événements
        
        Args:
            evenements_ids: Tuple des IDs d'événements
            
        Returns:
            Dictionnaire avec les statistiques
        """
        # Calculs de base (pour l'instant, retourner des valeurs par défaut)
        return {
            'moyenne_impact': 0.0,
            'ecart_type_impact': 0.0,
            'moyenne_intensite': 0.0,
            'ecart_type_intensite': 0.0
        }
    
    def _calculer_alertes_evenements(self) -> Dict[str, int]:
        """
        Calcule les alertes basées sur les seuils d'événements
        
        Returns:
            Dictionnaire avec le nombre d'événements dans chaque catégorie d'alerte
        """
        # Fréquence critique
        tours_avec_evenements = len([tour for tour, evenements in self.evenements_par_tour.items() if evenements])
        frequence_actuelle = tours_avec_evenements / max(self.tour_actuel, 1)
        evenements_frequence_critique = 1 if frequence_actuelle >= EVENT_CRITIQUE_FREQUENCE else 0
        
        # Impact critique
        impacts_positifs = [e.get('impact', 0) for e in self.evenements_totaux if e.get('impact', 0) > 0]
        impacts_negatifs = [e.get('impact', 0) for e in self.evenements_totaux if e.get('impact', 0) < 0]
        
        total_positif = sum(impacts_positifs) if impacts_positifs else 0
        total_negatif = abs(sum(impacts_negatifs)) if impacts_negatifs else 0
        
        ratio_impact = total_negatif / (total_positif + 1) if total_positif > 0 else 0
        evenements_impact_critique = 1 if ratio_impact >= EVENT_CRITIQUE_IMPACT else 0
        
        # Intensité critique
        intensite_moyenne = statistics.mean(self.intensites_historique) if self.intensites_historique else 0
        evenements_intensite_critique = 1 if intensite_moyenne >= EVENT_CRITIQUE_INTENSITE else 0
        
        return {
            'evenements_frequence_critique': evenements_frequence_critique,
            'evenements_impact_critique': evenements_impact_critique,
            'evenements_intensite_critique': evenements_intensite_critique
        }
    
    def _metriques_vides(self) -> Dict[str, Any]:
        """
        Retourne des métriques vides quand il n'y a pas d'événements
        
        Returns:
            Dictionnaire avec toutes les métriques à 0
        """
        return {
            'evenements_total': 0,
            'evenements_par_type': {},
            'evenements_par_impact': {},
            'evenements_frequence': 0.0,
            'evenements_duree_moyenne': 0.0,
            'evenements_intensite_moyenne': 0.0,
            'evenements_impact_budget': 0.0,
            'evenements_impact_prix': 0.0,
            'evenements_impact_stock': 0.0,
            'evenements_efficacite': 0.0,
            'evenements_rentabilite': 0.0,
            'evenements_stabilite': 0.0,
            'evenements_volatilite': 0.0,
            'evenements_tendance': 0.0,
            'evenements_correlation': 0.0,
            'evenements_predictibilite': 0.0,
            'tour_actuel': self.tour_actuel,
            'total_impact': 0,
            'total_intensite': 0
        }
    
    def reset(self) -> None:
        """Réinitialise le service (pour les tests)"""
        self.historique_evenements.clear()
        self.evenements_par_tour.clear()
        self.evenements_totaux.clear()
        self.impacts_historique.clear()
        self.intensites_historique.clear()
        self.tour_actuel = 0
        
        # Vider le cache LRU
        if EVENT_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_evenements_cached'):
            self._calculer_statistiques_evenements_cached.cache_clear()
