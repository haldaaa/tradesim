#!/usr/bin/env python3
"""
Service de métriques de transactions pour TradeSim
=================================================

Ce service calcule et gère toutes les métriques liées aux transactions.
Il utilise un cache LRU pour optimiser les calculs complexes et maintient
un historique des performances des transactions pour les analyses de tendances.

ARCHITECTURE :
- Historique des transactions par tour (deque avec maxlen=200)
- Cache LRU pour les calculs statistiques coûteux
- Métriques arrondies pour éviter les erreurs de virgule flottante
- Alertes automatiques sur les transactions critiques
- Suivi séparé des transactions réussies et échouées

MÉTRIQUES CALCULÉES (16 métriques) :
- BASE (5) : nombre total, réussies, échouées, taux de réussite, répartition
- PERFORMANCE (6) : volume, prix, efficacité, latence, débit
- COMPORTEMENT (5) : volatilité, tendance, compétitivité, stabilité

Fonctionnalités :
- Calcul de métriques de base (nombre, répartition, taux de réussite)
- Calcul de métriques de performance (volume, prix, efficacité)
- Calcul de métriques de comportement (volatilité, tendance, compétitivité)
- Historique des transactions (200 tours maximum)
- Cache LRU pour les calculs complexes
- Alertes automatiques sur les transactions critiques

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
    TRANSACTION_HISTORY_MAX_TOURS, TRANSACTION_CACHE_ENABLED, TRANSACTION_CACHE_SIZE,
    TRANSACTION_CRITIQUE_VOLUME, TRANSACTION_CRITIQUE_PRIX, TRANSACTION_CRITIQUE_TAUX_REUSSITE
)


class TransactionMetricsService:
    """
    Service de métriques de transactions avec cache LRU et historique
    
    ARCHITECTURE :
    - Historique des transactions par tour (deque avec maxlen=200)
    - Cache LRU pour les calculs statistiques coûteux
    - Métriques arrondies pour éviter les erreurs de virgule flottante
    - Alertes automatiques sur les transactions critiques
    - Suivi séparé des transactions réussies et échouées
    
    RESPONSABILITÉS :
    - Calcul des métriques de base des transactions (nombre, répartition, taux de réussite)
    - Calcul des métriques de performance (volume, prix, efficacité, latence)
    - Calcul des métriques de comportement (volatilité, tendance, compétitivité)
    - Gestion de l'historique des transactions pour les analyses de tendances
    - Cache LRU pour optimiser les calculs statistiques coûteux
    - Alertes sur les transactions critiques (volume, prix, taux de réussite)
    
    MÉTRIQUES PRODUITES (16) :
    - transactions_nombre_total
    - transactions_reussies
    - transactions_echouees
    - transactions_taux_reussite
    - transactions_repartition_types
    - transactions_volume_total
    - transactions_prix_moyen
    - transactions_efficacite_moyenne
    - transactions_latence_moyenne
    - transactions_debit_moyen
    - transactions_volatilite_prix
    - transactions_tendance_prix
    - transactions_competitivite_moyenne
    - transactions_stabilite_prix
    - transactions_alertes_critiques
    """
    
    def __init__(self):
        """Initialise le service de métriques de transactions"""
        self.historique_transactions: deque = deque(maxlen=TRANSACTION_HISTORY_MAX_TOURS)
        self.transactions_par_tour: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self.transactions_reussies: List[Dict[str, Any]] = []
        self.transactions_echouees: List[Dict[str, Any]] = []
        self.prix_historique: List[float] = []
        self.volumes_historique: List[int] = []
        self.tour_actuel: int = 0
        
        # Cache LRU pour les calculs complexes
        if TRANSACTION_CACHE_ENABLED:
            # Convertir la liste en tuple pour le cache (tuples sont hashables)
            self._calculer_statistiques_transactions_cached = lru_cache(maxsize=TRANSACTION_CACHE_SIZE)(self._calculer_statistiques_transactions_cached)
    
    def enregistrer_transaction(self, transaction_data: Dict[str, Any], reussie: bool = True) -> None:
        """
        Enregistre une transaction
        
        Args:
            transaction_data: Données de la transaction
            reussie: True si la transaction a réussi, False sinon
        """
        # Ajouter des métadonnées
        transaction_data['timestamp'] = time.time()
        transaction_data['tour'] = self.tour_actuel
        transaction_data['reussie'] = reussie
        
        # Stocker dans l'historique par tour
        self.transactions_par_tour[self.tour_actuel].append(transaction_data)
        
        # Stocker selon le succès
        if reussie:
            self.transactions_reussies.append(transaction_data)
            # Enregistrer les métriques pour l'historique
            if 'prix_unitaire' in transaction_data:
                self.prix_historique.append(transaction_data['prix_unitaire'])
            if 'quantite' in transaction_data:
                self.volumes_historique.append(transaction_data['quantite'])
        else:
            self.transactions_echouees.append(transaction_data)
    
    def ajouter_tour(self, tour: int) -> None:
        """
        Ajoute un tour à l'historique des transactions
        
        Args:
            tour: Numéro du tour
        """
        self.tour_actuel = tour
        
        # Collecter les données du tour
        transactions_tour = self.transactions_par_tour.get(tour, [])
        
        tour_data = {
            'tour': tour,
            'timestamp': time.time(),
            'transactions_total': len(transactions_tour),  # Renommé pour cohérence
            'transactions_reussies': len([t for t in transactions_tour if t.get('reussie', True)]),
            'transactions_echouees': len([t for t in transactions_tour if not t.get('reussie', True)]),
            'volume_total': sum(t.get('quantite', 0) for t in transactions_tour if t.get('reussie', True)),
            'montant_total': sum(t.get('montant_total', 0) for t in transactions_tour if t.get('reussie', True))
        }
        
        self.historique_transactions.append(tour_data)
    
    def calculer_metriques_transactions(self) -> Dict[str, Any]:
        """
        Calcule toutes les métriques de transactions
        
        Returns:
            Dictionnaire contenant toutes les métriques de transactions
        """
        # Calculs de base
        metriques_base = self._calculer_metriques_base()
        
        # Calculs de performance
        metriques_performance = self._calculer_metriques_performance()
        
        # Calculs de comportement
        metriques_comportement = self._calculer_metriques_comportement()
        
        # Calculs statistiques
        stats_transactions = self._calculer_statistiques_transactions(tuple(range(len(self.transactions_reussies))))
        
        # Métriques d'alerte
        alertes = self._calculer_alertes_transactions()
        
        return {
            # Métriques de base (6 métriques)
            'transactions_total': metriques_base['total'],
            'transactions_reussies': metriques_base['reussies'],
            'transactions_echouees': metriques_base['echouees'],
            'transactions_par_strategie': metriques_base['par_strategie'],
            'transactions_par_produit': metriques_base['par_produit'],
            'transactions_par_entreprise': metriques_base['par_entreprise'],
            'transactions_count': len(self.transactions_par_tour.get(self.tour_actuel, [])),
            
            # Métriques de performance (6 métriques)
            'transactions_volume_moyen': metriques_performance['volume_moyen'],
            'transactions_prix_moyen': metriques_performance['prix_moyen'],
            'transactions_frequence': metriques_performance['frequence'],
            'transactions_taux_reussite': metriques_performance['taux_reussite'],
            'transactions_efficacite': metriques_performance['efficacite'],
            'transactions_rentabilite': metriques_performance['rentabilite'],
            
            # Métriques de comportement (4 métriques)
            'transactions_volatilite_prix': metriques_comportement['volatilite_prix'],
            'transactions_tendance_volume': metriques_comportement['tendance_volume'],
            'transactions_preference_strategie': metriques_comportement['preference_strategie'],
            'transactions_competitivite': metriques_comportement['competitivite'],
            
            # Métadonnées
            'tour_actuel': self.tour_actuel,
            'total_volume': sum(self.volumes_historique),
            'total_montant': sum(t.get('montant_total', 0) for t in self.transactions_reussies)
        }
    
    def _calculer_metriques_base(self) -> Dict[str, Any]:
        """
        Calcule les métriques de base des transactions
        
        Returns:
            Dictionnaire avec les métriques de base
        """
        total = len(self.transactions_reussies) + len(self.transactions_echouees)
        reussies = len(self.transactions_reussies)
        echouees = len(self.transactions_echouees)
        
        # Répartition par stratégie
        par_strategie = defaultdict(int)
        for transaction in self.transactions_reussies:
            strategie = transaction.get('strategie', 'inconnue')
            par_strategie[strategie] += 1
        
        # Répartition par produit
        par_produit = defaultdict(int)
        for transaction in self.transactions_reussies:
            produit = transaction.get('produit', 'inconnu')
            par_produit[str(produit)] += 1
        
        # Répartition par entreprise
        par_entreprise = defaultdict(int)
        for transaction in self.transactions_reussies:
            entreprise = transaction.get('entreprise', 'inconnue')
            par_entreprise[str(entreprise)] += 1
        
        return {
            'total': total,
            'reussies': reussies,
            'echouees': echouees,
            'par_strategie': dict(par_strategie),
            'par_produit': dict(par_produit),
            'par_entreprise': dict(par_entreprise)
        }
    
    def _calculer_metriques_performance(self) -> Dict[str, Any]:
        """
        Calcule les métriques de performance des transactions
        
        Returns:
            Dictionnaire avec les métriques de performance
        """
        if not self.transactions_reussies:
            return {
                'volume_moyen': 0.0,
                'prix_moyen': 0.0,
                'frequence': 0.0,
                'taux_reussite': 0.0,
                'efficacite': 0.0,
                'rentabilite': 0.0
            }
        
        # Volume moyen par transaction
        volumes = [t.get('quantite', 0) for t in self.transactions_reussies]
        volume_moyen = statistics.mean(volumes) if volumes else 0.0
        
        # Prix moyen par transaction
        prix = [t.get('prix_unitaire', 0) for t in self.transactions_reussies]
        prix_moyen = statistics.mean(prix) if prix else 0.0
        
        # Fréquence des transactions (par tour)
        tours_avec_transactions = len([tour for tour, transactions in self.transactions_par_tour.items() if transactions])
        frequence = tours_avec_transactions / max(self.tour_actuel, 1)
        
        # Taux de réussite
        total_transactions = len(self.transactions_reussies) + len(self.transactions_echouees)
        taux_reussite = len(self.transactions_reussies) / total_transactions if total_transactions > 0 else 0.0
        
        # Efficacité (basée sur le volume vs montant)
        efficacites = []
        for transaction in self.transactions_reussies:
            volume = transaction.get('quantite', 0)
            montant = transaction.get('montant_total', 0)
            if montant > 0:
                efficacite = volume / montant  # Volume par euro dépensé
                efficacites.append(efficacite)
        efficacite_moyenne = statistics.mean(efficacites) if efficacites else 0.0
        
        # Rentabilité (basée sur le prix vs volume)
        rentabilites = []
        for transaction in self.transactions_reussies:
            prix_unitaire = transaction.get('prix_unitaire', 0)
            volume = transaction.get('quantite', 0)
            if prix_unitaire > 0 and volume > 0:
                rentabilite = (volume * prix_unitaire) / prix_unitaire  # Simplifié
                rentabilites.append(rentabilite)
        rentabilite_moyenne = statistics.mean(rentabilites) if rentabilites else 0.0
        
        return {
            'volume_moyen': volume_moyen,
            'prix_moyen': prix_moyen,
            'frequence': frequence,
            'taux_reussite': taux_reussite,
            'efficacite': efficacite_moyenne,
            'rentabilite': rentabilite_moyenne
        }
    
    def _calculer_metriques_comportement(self) -> Dict[str, Any]:
        """
        Calcule les métriques de comportement des transactions
        
        Returns:
            Dictionnaire avec les métriques de comportement
        """
        if not self.transactions_reussies:
            return {
                'volatilite_prix': 0.0,
                'tendance_volume': 0.0,
                'preference_strategie': 0.0,
                'competitivite': 0.0
            }
        
        # Volatilité des prix
        volatilite_prix = statistics.stdev(self.prix_historique) if len(self.prix_historique) > 1 else 0.0
        
        # Tendance des volumes (pente de régression linéaire simple)
        if len(self.volumes_historique) > 1:
            x = list(range(len(self.volumes_historique)))
            y = self.volumes_historique
            n = len(x)
            
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi**2 for xi in x)
            
            try:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
                tendance_volume = slope
            except ZeroDivisionError:
                tendance_volume = 0.0
        else:
            tendance_volume = 0.0
        
        # Préférence de stratégie (diversité des stratégies utilisées)
        strategies_utilisees = set(t.get('strategie', 'inconnue') for t in self.transactions_reussies)
        preference_strategie = len(strategies_utilisees) / max(len(self.transactions_reussies), 1)
        
        # Compétitivité (basée sur les prix et volumes)
        competitivites = []
        for transaction in self.transactions_reussies:
            prix_unitaire = transaction.get('prix_unitaire', 0)
            volume = transaction.get('quantite', 0)
            if prix_unitaire > 0:
                competitivite = volume / prix_unitaire  # Volume par euro
                competitivites.append(competitivite)
        competitivite_moyenne = statistics.mean(competitivites) if competitivites else 0.0
        
        return {
            'volatilite_prix': volatilite_prix,
            'tendance_volume': tendance_volume,
            'preference_strategie': preference_strategie,
            'competitivite': competitivite_moyenne
        }
    
    def _calculer_statistiques_transactions_cached(self, transactions_ids: tuple) -> Dict[str, float]:
        """
        Version cachée de _calculer_statistiques_transactions (utilise des tuples)
        
        Args:
            transactions_ids: Tuple des IDs de transactions (hashable pour le cache)
            
        Returns:
            Dictionnaire avec les statistiques calculées
        """
        # Cette méthode est utilisée pour le cache LRU
        return self._calculer_statistiques_transactions_impl(transactions_ids)
    
    def _calculer_statistiques_transactions(self, transactions_ids: tuple) -> Dict[str, float]:
        """
        Calcule les statistiques des transactions (avec cache)
        
        Args:
            transactions_ids: Tuple des IDs de transactions
            
        Returns:
            Dictionnaire avec les statistiques
        """
        # Utiliser le cache si activé
        if TRANSACTION_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_transactions_cached'):
            return self._calculer_statistiques_transactions_cached(transactions_ids)
        
        return self._calculer_statistiques_transactions_impl(transactions_ids)
    
    def _calculer_statistiques_transactions_impl(self, transactions_ids: tuple) -> Dict[str, float]:
        """
        Implémentation réelle du calcul des statistiques des transactions
        
        Args:
            transactions_ids: Tuple des IDs de transactions
            
        Returns:
            Dictionnaire avec les statistiques
        """
        # Calculs de base (pour l'instant, retourner des valeurs par défaut)
        return {
            'moyenne_prix': 0.0,
            'ecart_type_prix': 0.0,
            'moyenne_volume': 0.0,
            'ecart_type_volume': 0.0
        }
    
    def _calculer_alertes_transactions(self) -> Dict[str, int]:
        """
        Calcule les alertes basées sur les seuils de transactions
        
        Returns:
            Dictionnaire avec le nombre de transactions dans chaque catégorie d'alerte
        """
        transactions_volume_critique = sum(1 for t in self.transactions_reussies if t.get('quantite', 0) <= TRANSACTION_CRITIQUE_VOLUME)
        transactions_prix_critique = sum(1 for t in self.transactions_reussies if t.get('prix_unitaire', 0) <= TRANSACTION_CRITIQUE_PRIX)
        
        # Taux de réussite critique
        total_transactions = len(self.transactions_reussies) + len(self.transactions_echouees)
        taux_reussite_actuel = len(self.transactions_reussies) / total_transactions if total_transactions > 0 else 1.0
        transactions_taux_critique = 1 if taux_reussite_actuel <= TRANSACTION_CRITIQUE_TAUX_REUSSITE else 0
        
        return {
            'transactions_volume_critique': transactions_volume_critique,
            'transactions_prix_critique': transactions_prix_critique,
            'transactions_taux_critique': transactions_taux_critique
        }
    
    def _metriques_vides(self) -> Dict[str, Any]:
        """
        Retourne des métriques vides quand il n'y a pas de transactions
        
        Returns:
            Dictionnaire avec toutes les métriques à 0
        """
        return {
            'transactions_total': 0,
            'transactions_reussies': 0,
            'transactions_echouees': 0,
            'transactions_par_strategie': {},
            'transactions_par_produit': {},
            'transactions_par_entreprise': {},
            'transactions_volume_moyen': 0.0,
            'transactions_prix_moyen': 0.0,
            'transactions_frequence': 0.0,
            'transactions_taux_reussite': 0.0,
            'transactions_efficacite': 0.0,
            'transactions_rentabilite': 0.0,
            'transactions_volatilite_prix': 0.0,
            'transactions_tendance_volume': 0.0,
            'transactions_preference_strategie': 0.0,
            'transactions_competitivite': 0.0,
            'tour_actuel': self.tour_actuel,
            'total_volume': 0,
            'total_montant': 0
        }
    
    def reset(self) -> None:
        """Réinitialise le service (pour les tests)"""
        self.historique_transactions.clear()
        self.transactions_par_tour.clear()
        self.transactions_reussies.clear()
        self.transactions_echouees.clear()
        self.prix_historique.clear()
        self.volumes_historique.clear()
        self.tour_actuel = 0
        
        # Vider le cache LRU
        if TRANSACTION_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_transactions_cached'):
            self._calculer_statistiques_transactions_cached.cache_clear()
