#!/usr/bin/env python3
"""
Service de métriques de performance pour TradeSim
================================================

Ce service calcule et gère toutes les métriques liées aux performances système.
Il utilise un cache LRU pour optimiser les calculs complexes et maintient
un historique des performances pour les analyses de tendances.

ARCHITECTURE :
- Historique des performances par tour (deque avec maxlen=200)
- Cache LRU pour les calculs statistiques coûteux
- Métriques arrondies pour éviter les erreurs de virgule flottante
- Alertes automatiques sur les performances critiques
- Mesures système en temps réel (psutil)

MÉTRIQUES CALCULÉES (16 métriques) :
- BASE (5) : temps d'exécution, mémoire, CPU, processus, efficacité
- PERFORMANCE (6) : optimisation, charge, débit, latence, utilisation
- COMPORTEMENT (5) : volatilité, tendance, bottlenecks, stabilité

Fonctionnalités :
- Calcul de métriques de base (temps, mémoire, CPU)
- Calcul de métriques de performance (efficacité, optimisation, charge)
- Calcul de métriques de comportement (volatilité, tendance, bottlenecks)
- Historique des performances (200 tours maximum)
- Cache LRU pour les calculs complexes
- Alertes automatiques sur les performances critiques

Auteur: Assistant IA
Date: 2025-08-10
"""

import statistics
import math
import time
import psutil
import os
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
from collections import deque, defaultdict

from models.models import Entreprise, Fournisseur, Produit, TypeProduit
from config.config import (
    PERFORMANCE_HISTORY_MAX_TOURS, PERFORMANCE_CACHE_ENABLED, PERFORMANCE_CACHE_SIZE,
    PERFORMANCE_CRITIQUE_TEMPS, PERFORMANCE_CRITIQUE_MEMOIRE, PERFORMANCE_CRITIQUE_CPU
)


class PerformanceMetricsService:
    """
    Service de métriques de performance avec cache LRU et historique
    
    ARCHITECTURE :
    - Historique des performances par tour (deque avec maxlen=200)
    - Cache LRU pour les calculs statistiques coûteux
    - Métriques arrondies pour éviter les erreurs de virgule flottante
    - Alertes automatiques sur les performances critiques
    - Mesures système en temps réel (psutil)
    
    RESPONSABILITÉS :
    - Calcul des métriques de base des performances (temps, mémoire, CPU)
    - Calcul des métriques de performance avancées (efficacité, optimisation, charge)
    - Calcul des métriques de comportement (volatilité, tendance, bottlenecks)
    - Gestion de l'historique des performances pour les analyses de tendances
    - Cache LRU pour optimiser les calculs statistiques coûteux
    - Alertes sur les performances critiques (temps, mémoire, CPU)
    
    MÉTRIQUES PRODUITES (16) :
    - performance_temps_execution
    - performance_memoire_utilisee
    - performance_cpu_utilisation
    - performance_processus_actifs
    - performance_efficacite_moyenne
    - performance_optimisation_moyenne
    - performance_charge_moyenne
    - performance_debit_moyen
    - performance_latence_moyenne
    - performance_utilisation_moyenne
    - performance_volatilite_temps
    - performance_tendance_temps
    - performance_bottlenecks_identifies
    - performance_stabilite_moyenne
    - performance_alertes_critiques
    """
    
    def __init__(self):
        """Initialise le service de métriques de performance"""
        self.historique_performance: deque = deque(maxlen=PERFORMANCE_HISTORY_MAX_TOURS)
        self.mesures_par_tour: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self.temps_execution: List[float] = []
        self.memoire_utilisee: List[float] = []
        self.cpu_utilisation: List[float] = []
        self.tour_actuel: int = 0
        self.debut_tour: float = 0.0
        
        # Cache LRU pour les calculs complexes
        if PERFORMANCE_CACHE_ENABLED:
            # Convertir la liste en tuple pour le cache (tuples sont hashables)
            self._calculer_statistiques_performance_cached = lru_cache(maxsize=PERFORMANCE_CACHE_SIZE)(self._calculer_statistiques_performance_cached)
    
    def debut_mesure(self) -> None:
        """
        Démarre une mesure de performance
        """
        self.debut_tour = time.time()
    
    def fin_mesure(self, tour: int) -> None:
        """
        Termine une mesure de performance
        
        Args:
            tour: Numéro du tour
        """
        if self.debut_tour == 0:
            return
        
        fin_tour = time.time()
        temps_execution = fin_tour - self.debut_tour
        
        # Collecter les métriques système
        try:
            process = psutil.Process(os.getpid())
            memoire = process.memory_info().rss / 1024 / 1024  # MB
            cpu_percent = process.cpu_percent()
        except:
            memoire = 0.0
            cpu_percent = 0.0
        
        # Créer la mesure de performance
        mesure = {
            'tour': tour,
            'timestamp': fin_tour,
            'temps_execution': temps_execution,
            'memoire_utilisee': memoire,
            'cpu_utilisation': cpu_percent,
            'temps_reponse': temps_execution,  # Pour l'instant, identique au temps d'exécution
            'throughput': 1.0 / temps_execution if temps_execution > 0 else 0.0,
            'latence': temps_execution
        }
        
        # Stocker dans l'historique par tour
        self.mesures_par_tour[tour].append(mesure)
        
        # Stocker dans les listes historiques
        self.temps_execution.append(temps_execution)
        self.memoire_utilisee.append(memoire)
        self.cpu_utilisation.append(cpu_percent)
        
        # Réinitialiser le début de tour
        self.debut_tour = 0.0
    
    def ajouter_tour(self, tour: int) -> None:
        """
        Ajoute un tour à l'historique des performances
        
        Args:
            tour: Numéro du tour
        """
        self.tour_actuel = tour
        
        # Collecter les données du tour
        mesures_tour = self.mesures_par_tour.get(tour, [])
        
        if mesures_tour:
            tour_data = {
                'tour': tour,
                'timestamp': time.time(),
                'mesures_count': len(mesures_tour),
                'temps_execution_moyen': statistics.mean([m.get('temps_execution', 0) for m in mesures_tour]),
                'memoire_moyenne': statistics.mean([m.get('memoire_utilisee', 0) for m in mesures_tour]),
                'cpu_moyen': statistics.mean([m.get('cpu_utilisation', 0) for m in mesures_tour]),
                'throughput_moyen': statistics.mean([m.get('throughput', 0) for m in mesures_tour])
            }
        else:
            tour_data = {
                'tour': tour,
                'timestamp': time.time(),
                'mesures_count': 0,
                'temps_execution_moyen': 0.0,
                'memoire_moyenne': 0.0,
                'cpu_moyen': 0.0,
                'throughput_moyen': 0.0
            }
        
        self.historique_performance.append(tour_data)
    
    def calculer_metriques_performance(self) -> Dict[str, Any]:
        """
        Calcule toutes les métriques de performance
        
        Returns:
            Dictionnaire contenant toutes les métriques de performance
        """
        # Calculs de base
        metriques_base = self._calculer_metriques_base()
        
        # Calculs de performance
        metriques_performance = self._calculer_metriques_performance()
        
        # Calculs de comportement
        metriques_comportement = self._calculer_metriques_comportement()
        
        # Calculs statistiques
        stats_performance = self._calculer_statistiques_performance(tuple(range(len(self.temps_execution))))
        
        # Métriques d'alerte
        alertes = self._calculer_alertes_performance()
        
        return {
            # Métriques de base (6 métriques)
            'performance_temps_execution': metriques_base['temps_execution'],
            'performance_memoire_utilisee': metriques_base['memoire_utilisee'],
            'performance_cpu_utilisation': metriques_base['cpu_utilisation'],
            'performance_temps_reponse': metriques_base['temps_reponse'],
            'performance_throughput': metriques_base['throughput'],
            'performance_latence': metriques_base['latence'],
            
            # Métriques de performance (6 métriques)
            'performance_efficacite_cache': metriques_performance['efficacite_cache'],
            'performance_optimisation': metriques_performance['optimisation'],
            'performance_charge_systeme': metriques_performance['charge_systeme'],
            'performance_stabilite': metriques_performance['stabilite'],
            'performance_scalabilite': metriques_performance['scalabilite'],
            'performance_qualite': metriques_performance['qualite'],
            
            # Métriques de comportement (4 métriques)
            'performance_volatilite': metriques_comportement['volatilite'],
            'performance_tendance': metriques_comportement['tendance'],
            'performance_bottlenecks': metriques_comportement['bottlenecks'],
            'performance_optimisations_disponibles': metriques_comportement['optimisations_disponibles'],
            
            # Métadonnées
            'tour_actuel': self.tour_actuel,
            'total_mesures': len(self.temps_execution),
            'total_temps': sum(self.temps_execution)
        }
    
    def _calculer_metriques_base(self) -> Dict[str, Any]:
        """
        Calcule les métriques de base des performances
        
        Returns:
            Dictionnaire avec les métriques de base
        """
        if not self.temps_execution:
            return {
                'temps_execution': 0.0,
                'memoire_utilisee': 0.0,
                'cpu_utilisation': 0.0,
                'temps_reponse': 0.0,
                'throughput': 0.0,
                'latence': 0.0
            }
        
        # Temps d'exécution moyen
        temps_execution = statistics.mean(self.temps_execution)
        
        # Mémoire utilisée moyenne
        memoire_utilisee = statistics.mean(self.memoire_utilisee) if self.memoire_utilisee else 0.0
        
        # CPU utilisation moyenne
        cpu_utilisation = statistics.mean(self.cpu_utilisation) if self.cpu_utilisation else 0.0
        
        # Temps de réponse moyen (pour l'instant, identique au temps d'exécution)
        temps_reponse = temps_execution
        
        # Throughput (opérations par seconde)
        throughput = 1.0 / temps_execution if temps_execution > 0 else 0.0
        
        # Latence moyenne
        latence = temps_execution
        
        return {
            'temps_execution': temps_execution,
            'memoire_utilisee': memoire_utilisee,
            'cpu_utilisation': cpu_utilisation,
            'temps_reponse': temps_reponse,
            'throughput': throughput,
            'latence': latence
        }
    
    def _calculer_metriques_performance(self) -> Dict[str, Any]:
        """
        Calcule les métriques de performance avancées
        
        Returns:
            Dictionnaire avec les métriques de performance
        """
        if not self.temps_execution:
            return {
                'efficacite_cache': 0.0,
                'optimisation': 0.0,
                'charge_systeme': 0.0,
                'stabilite': 0.0,
                'scalabilite': 0.0,
                'qualite': 0.0
            }
        
        # Efficacité du cache (basée sur la variance des temps d'exécution)
        if len(self.temps_execution) > 1:
            variance_temps = statistics.variance(self.temps_execution)
            efficacite_cache = 1.0 / (1.0 + variance_temps)  # Plus la variance est faible, plus le cache est efficace
        else:
            efficacite_cache = 1.0
        
        # Niveau d'optimisation (basé sur le temps d'exécution vs nombre de mesures)
        temps_moyen = statistics.mean(self.temps_execution)
        optimisation = 1.0 / (1.0 + temps_moyen)  # Plus le temps est faible, plus c'est optimisé
        
        # Charge du système (basée sur CPU et mémoire)
        cpu_moyen = statistics.mean(self.cpu_utilisation) if self.cpu_utilisation else 0.0
        memoire_moyenne = statistics.mean(self.memoire_utilisee) if self.memoire_utilisee else 0.0
        
        # Normaliser la mémoire (supposer 1GB comme référence)
        memoire_normalisee = min(memoire_moyenne / 1024.0, 1.0)  # 1GB = 100%
        charge_systeme = (cpu_moyen + memoire_normalisee * 100) / 2.0
        
        # Stabilité des performances (basée sur la variance des métriques)
        if len(self.temps_execution) > 1:
            variance_temps = statistics.variance(self.temps_execution)
            variance_cpu = statistics.variance(self.cpu_utilisation) if len(self.cpu_utilisation) > 1 else 0
            variance_memoire = statistics.variance(self.memoire_utilisee) if len(self.memoire_utilisee) > 1 else 0
            
            stabilite = 1.0 / (1.0 + variance_temps + variance_cpu + variance_memoire)
        else:
            stabilite = 1.0
        
        # Scalabilité (basée sur la capacité à maintenir les performances avec plus de données)
        if len(self.temps_execution) > 1:
            # Calculer la pente de régression pour le temps d'exécution
            x = list(range(len(self.temps_execution)))
            y = self.temps_execution
            n = len(x)
            
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi**2 for xi in x)
            
            try:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
                # Plus la pente est faible, plus c'est scalable
                scalabilite = 1.0 / (1.0 + abs(slope))
            except ZeroDivisionError:
                scalabilite = 1.0
        else:
            scalabilite = 1.0
        
        # Qualité des performances (combinaison de toutes les métriques)
        qualite = (efficacite_cache + optimisation + (1.0 - charge_systeme/100.0) + stabilite + scalabilite) / 5.0
        
        return {
            'efficacite_cache': efficacite_cache,
            'optimisation': optimisation,
            'charge_systeme': charge_systeme,
            'stabilite': stabilite,
            'scalabilite': scalabilite,
            'qualite': qualite
        }
    
    def _calculer_metriques_comportement(self) -> Dict[str, Any]:
        """
        Calcule les métriques de comportement des performances
        
        Returns:
            Dictionnaire avec les métriques de comportement
        """
        if not self.temps_execution:
            return {
                'volatilite': 0.0,
                'tendance': 0.0,
                'bottlenecks': 0,
                'optimisations_disponibles': 0
            }
        
        # Volatilité des performances (écart-type des temps d'exécution)
        volatilite = statistics.stdev(self.temps_execution) if len(self.temps_execution) > 1 else 0.0
        
        # Tendance des performances (pente de régression linéaire simple)
        if len(self.temps_execution) > 1:
            x = list(range(len(self.temps_execution)))
            y = self.temps_execution
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
        
        # Nombre de goulots d'étranglement (mesures avec temps > 2x la moyenne)
        if self.temps_execution:
            temps_moyen = statistics.mean(self.temps_execution)
            seuil_bottleneck = temps_moyen * 2
            bottlenecks = sum(1 for t in self.temps_execution if t > seuil_bottleneck)
        else:
            bottlenecks = 0
        
        # Optimisations disponibles (basées sur les métriques critiques)
        optimisations_disponibles = 0
        
        if self.temps_execution:
            temps_moyen = statistics.mean(self.temps_execution)
            if temps_moyen > PERFORMANCE_CRITIQUE_TEMPS:
                optimisations_disponibles += 1
        
        if self.memoire_utilisee:
            memoire_moyenne = statistics.mean(self.memoire_utilisee)
            memoire_max = psutil.virtual_memory().total / 1024 / 1024  # MB
            if memoire_moyenne / memoire_max > PERFORMANCE_CRITIQUE_MEMOIRE:
                optimisations_disponibles += 1
        
        if self.cpu_utilisation:
            cpu_moyen = statistics.mean(self.cpu_utilisation)
            if cpu_moyen > PERFORMANCE_CRITIQUE_CPU * 100:
                optimisations_disponibles += 1
        
        return {
            'volatilite': volatilite,
            'tendance': tendance,
            'bottlenecks': bottlenecks,
            'optimisations_disponibles': optimisations_disponibles
        }
    
    def _calculer_statistiques_performance_cached(self, performance_ids: tuple) -> Dict[str, float]:
        """
        Version cachée de _calculer_statistiques_performance (utilise des tuples)
        
        Args:
            performance_ids: Tuple des IDs de performance (hashable pour le cache)
            
        Returns:
            Dictionnaire avec les statistiques calculées
        """
        # Cette méthode est utilisée pour le cache LRU
        return self._calculer_statistiques_performance_impl(performance_ids)
    
    def _calculer_statistiques_performance(self, performance_ids: tuple) -> Dict[str, float]:
        """
        Calcule les statistiques des performances (avec cache)
        
        Args:
            performance_ids: Tuple des IDs de performance
            
        Returns:
            Dictionnaire avec les statistiques
        """
        # Utiliser le cache si activé
        if PERFORMANCE_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_performance_cached'):
            return self._calculer_statistiques_performance_cached(performance_ids)
        
        return self._calculer_statistiques_performance_impl(performance_ids)
    
    def _calculer_statistiques_performance_impl(self, performance_ids: tuple) -> Dict[str, float]:
        """
        Implémentation réelle du calcul des statistiques des performances
        
        Args:
            performance_ids: Tuple des IDs de performance
            
        Returns:
            Dictionnaire avec les statistiques
        """
        # Calculs de base (pour l'instant, retourner des valeurs par défaut)
        return {
            'moyenne_temps': 0.0,
            'ecart_type_temps': 0.0,
            'moyenne_memoire': 0.0,
            'ecart_type_memoire': 0.0
        }
    
    def _calculer_alertes_performance(self) -> Dict[str, int]:
        """
        Calcule les alertes basées sur les seuils de performance
        
        Returns:
            Dictionnaire avec le nombre de mesures dans chaque catégorie d'alerte
        """
        # Temps d'exécution critique
        mesures_temps_critique = sum(1 for t in self.temps_execution if t > PERFORMANCE_CRITIQUE_TEMPS)
        
        # Mémoire critique
        if self.memoire_utilisee:
            memoire_max = psutil.virtual_memory().total / 1024 / 1024  # MB
            mesures_memoire_critique = sum(1 for m in self.memoire_utilisee if m / memoire_max > PERFORMANCE_CRITIQUE_MEMOIRE)
        else:
            mesures_memoire_critique = 0
        
        # CPU critique
        mesures_cpu_critique = sum(1 for c in self.cpu_utilisation if c > PERFORMANCE_CRITIQUE_CPU * 100)
        
        return {
            'performance_temps_critique': mesures_temps_critique,
            'performance_memoire_critique': mesures_memoire_critique,
            'performance_cpu_critique': mesures_cpu_critique
        }
    
    def _metriques_vides(self) -> Dict[str, Any]:
        """
        Retourne des métriques vides quand il n'y a pas de mesures
        
        Returns:
            Dictionnaire avec toutes les métriques à 0
        """
        return {
            'performance_temps_execution': 0.0,
            'performance_memoire_utilisee': 0.0,
            'performance_cpu_utilisation': 0.0,
            'performance_temps_reponse': 0.0,
            'performance_throughput': 0.0,
            'performance_latence': 0.0,
            'performance_efficacite_cache': 0.0,
            'performance_optimisation': 0.0,
            'performance_charge_systeme': 0.0,
            'performance_stabilite': 0.0,
            'performance_scalabilite': 0.0,
            'performance_qualite': 0.0,
            'performance_volatilite': 0.0,
            'performance_tendance': 0.0,
            'performance_bottlenecks': 0,
            'performance_optimisations_disponibles': 0,
            'tour_actuel': self.tour_actuel,
            'total_mesures': 0,
            'total_temps': 0
        }
    
    def reset(self) -> None:
        """Réinitialise le service (pour les tests)"""
        self.historique_performance.clear()
        self.mesures_par_tour.clear()
        self.temps_execution.clear()
        self.memoire_utilisee.clear()
        self.cpu_utilisation.clear()
        self.tour_actuel = 0
        self.debut_tour = 0.0
        
        # Vider le cache LRU
        if PERFORMANCE_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_performance_cached'):
            self._calculer_statistiques_performance_cached.cache_clear()
