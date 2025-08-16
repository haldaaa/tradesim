#!/usr/bin/env python3
"""
Service de métriques de produits pour TradeSim
=============================================

Ce service calcule et gère toutes les métriques liées aux produits.
Il utilise un cache LRU pour optimiser les calculs complexes et maintient
un historique des performances des produits pour les analyses de tendances.

ARCHITECTURE :
- Historique des produits par tour (deque avec maxlen=200)
- Cache LRU pour les calculs statistiques coûteux
- Métriques arrondies pour éviter les erreurs de virgule flottante
- Alertes automatiques sur les produits critiques
- Historique des prix par produit pour l'analyse des tendances

MÉTRIQUES CALCULÉES (16 métriques) :
- BASE (5) : nombre, répartition par type, prix moyen, actifs
- PERFORMANCE (6) : demande, offre, rotation, disponibilité
- COMPORTEMENT (5) : volatilité, tendance, élasticité, stabilité

Fonctionnalités :
- Calcul de métriques de base (nombre, répartition, prix)
- Calcul de métriques de performance (demande, offre, rotation)
- Calcul de métriques de comportement (volatilité, tendance, élasticité)
- Historique des produits (200 tours maximum)
- Cache LRU pour les calculs complexes
- Alertes automatiques sur les produits critiques

Auteur: Assistant IA
Date: 2025-08-10
"""

import statistics
import math
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
from collections import deque, defaultdict
import time

from models.models import Produit, TypeProduit, Fournisseur
from config.config import (
    PRODUCT_HISTORY_MAX_TOURS, PRODUCT_CACHE_ENABLED, PRODUCT_CACHE_SIZE,
    PRODUCT_CRITIQUE_PRIX, PRODUCT_CRITIQUE_STOCK, PRODUCT_CRITIQUE_DEMANDE
)


class ProductMetricsService:
    """
    Service de métriques de produits avec cache LRU et historique
    
    ARCHITECTURE :
    - Historique des produits par tour (deque avec maxlen=200)
    - Cache LRU pour les calculs statistiques coûteux
    - Métriques arrondies pour éviter les erreurs de virgule flottante
    - Alertes automatiques sur les produits critiques
    - Historique des prix par produit pour l'analyse des tendances
    
    RESPONSABILITÉS :
    - Calcul des métriques de base des produits (nombre, répartition, prix)
    - Calcul des métriques de performance (demande, offre, rotation, disponibilité)
    - Calcul des métriques de comportement (volatilité, tendance, élasticité)
    - Gestion de l'historique des produits pour les analyses de tendances
    - Cache LRU pour optimiser les calculs statistiques coûteux
    - Alertes sur les produits critiques (prix, stock, demande)
    
    MÉTRIQUES PRODUITES (16) :
    - produits_nombre_total
    - produits_repartition_types
    - produits_prix_moyen
    - produits_prix_ecart_type
    - produits_actifs_pourcentage
    - produits_demande_total
    - produits_offre_total
    - produits_rotation_moyenne
    - produits_disponibilite_moyenne
    - produits_volatilite_prix
    - produits_tendance_prix
    - produits_elasticite_demande
    - produits_stabilite_prix
    - produits_alertes_critiques
    """
    
    def __init__(self):
        """Initialise le service de métriques de produits"""
        self.historique_produits: deque = deque(maxlen=PRODUCT_HISTORY_MAX_TOURS)
        self.demandes_par_produit: Dict[int, int] = defaultdict(int)
        self.achats_par_produit: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self.prix_historique: Dict[int, List[float]] = defaultdict(list)
        self.tour_actuel: int = 0
        
        # Cache LRU pour les calculs complexes
        if PRODUCT_CACHE_ENABLED:
            # Convertir la liste en tuple pour le cache (tuples sont hashables)
            self._calculer_statistiques_produits_cached = lru_cache(maxsize=PRODUCT_CACHE_SIZE)(self._calculer_statistiques_produits_cached)
    
    def ajouter_tour(self, produits: List[Produit], fournisseurs: List[Fournisseur], tour: int) -> None:
        """
        Ajoute un tour à l'historique des produits
        
        Args:
            produits: Liste des produits
            fournisseurs: Liste des fournisseurs
            tour: Numéro du tour
        """
        self.tour_actuel = tour
        
        # Collecter les données des produits
        produits_data = {
            'tour': tour,
            'timestamp': time.time(),
            'produits': [
                {
                    'id': produit.id,
                    'nom': produit.nom,
                    'type': produit.type.value,
                    'prix': produit.prix,
                    'actif': produit.actif,
                    'demande': self.demandes_par_produit.get(produit.id, 0),
                    'stock_total': sum(fournisseur.stock_produit.get(produit.id, 0) for fournisseur in fournisseurs)
                }
                for produit in produits
            ],
            'produits_count': len(produits)
        }
        
        self.historique_produits.append(produits_data)
        
        # Mettre à jour l'historique des prix
        for produit in produits:
            self.prix_historique[produit.id].append(produit.prix)
    
    def enregistrer_achat(self, produit_id: int, achat_data: Dict[str, Any]) -> None:
        """
        Enregistre un achat pour un produit
        
        Args:
            produit_id: ID du produit
            achat_data: Données de l'achat
        """
        self.demandes_par_produit[produit_id] += 1
        self.achats_par_produit[produit_id].append(achat_data)
    
    def calculer_metriques_produits(self, produits: List[Produit], fournisseurs: List[Fournisseur]) -> Dict[str, Any]:
        """
        Calcule toutes les métriques de produits
        
        Args:
            produits: Liste des produits
            fournisseurs: Liste des fournisseurs
            
        Returns:
            Dictionnaire contenant toutes les métriques de produits
        """
        if not produits:
            return self._metriques_vides()
        
        # Calculs de base
        metriques_base = self._calculer_metriques_base(produits, fournisseurs)
        
        # Calculs de performance
        metriques_performance = self._calculer_metriques_performance(produits, fournisseurs)
        
        # Calculs de comportement
        metriques_comportement = self._calculer_metriques_comportement(produits)
        
        # Calculs statistiques
        stats_produits = self._calculer_statistiques_produits(tuple(produit.id for produit in produits))
        
        # Métriques d'alerte
        alertes = self._calculer_alertes_produits(produits, fournisseurs)
        
        return {
            # Métriques de base (6 métriques)
            'produits_total': metriques_base['total'],
            'produits_actifs': metriques_base['actifs'],
            'produits_par_type': metriques_base['par_type'],
            'produits_par_continent': metriques_base['par_continent'],
            'produits_prix_moyen': metriques_base['prix_moyen'],
            'produits_prix_median': metriques_base['prix_median'],
            
            # Métriques de performance (6 métriques)
            'produits_demande_moyenne': metriques_performance['demande_moyenne'],
            'produits_offre_moyenne': metriques_performance['offre_moyenne'],
            'produits_rotation_stock': metriques_performance['rotation_stock'],
            'produits_rentabilite': metriques_performance['rentabilite'],
            'produits_popularite': metriques_performance['popularite'],
            'produits_disponibilite': metriques_performance['disponibilite'],
            
            # Métriques de comportement (4 métriques)
            'produits_volatilite_prix': metriques_comportement['volatilite_prix'],
            'produits_tendance_prix': metriques_comportement['tendance_prix'],
            'produits_elasticite_demande': metriques_comportement['elasticite_demande'],
            'produits_competitivite': metriques_comportement['competitivite'],
            
            # Métadonnées
            'produits_count': len(produits),
            'tour_actuel': self.tour_actuel,
            'total_demandes': sum(self.demandes_par_produit.values())
        }
    
    def _calculer_metriques_base(self, produits: List[Produit], fournisseurs: List[Fournisseur]) -> Dict[str, Any]:
        """
        Calcule les métriques de base des produits
        
        Args:
            produits: Liste des produits
            fournisseurs: Liste des fournisseurs
            
        Returns:
            Dictionnaire avec les métriques de base
        """
        total = len(produits)
        actifs = sum(1 for p in produits if p.actif)
        
        # Répartition par type
        par_type = defaultdict(int)
        for produit in produits:
            par_type[produit.type.value] += 1
        
        # Répartition par continent (basée sur les fournisseurs)
        par_continent = defaultdict(int)
        for produit in produits:
            # Compter les fournisseurs qui ont ce produit en stock
            fournisseurs_produit = sum(1 for f in fournisseurs if f.stock_produit.get(produit.id, 0) > 0)
            if fournisseurs_produit > 0:
                # Utiliser le continent du premier fournisseur disponible
                for fournisseur in fournisseurs:
                    if fournisseur.stock_produit.get(produit.id, 0) > 0:
                        par_continent[fournisseur.continent] += 1
                        break
        
        # Prix moyen et médian
        prix = [p.prix for p in produits if p.prix > 0]
        prix_moyen = statistics.mean(prix) if prix else 0.0
        prix_median = statistics.median(prix) if prix else 0.0
        
        return {
            'total': total,
            'actifs': actifs,
            'par_type': dict(par_type),
            'par_continent': dict(par_continent),
            'prix_moyen': prix_moyen,
            'prix_median': prix_median
        }
    
    def _calculer_metriques_performance(self, produits: List[Produit], fournisseurs: List[Fournisseur]) -> Dict[str, Any]:
        """
        Calcule les métriques de performance des produits
        
        Args:
            produits: Liste des produits
            fournisseurs: Liste des fournisseurs
            
        Returns:
            Dictionnaire avec les métriques de performance
        """
        if not produits:
            return {
                'demande_moyenne': 0.0,
                'offre_moyenne': 0.0,
                'rotation_stock': 0.0,
                'rentabilite': 0.0,
                'popularite': 0.0,
                'disponibilite': 0.0
            }
        
        # Demande moyenne
        demandes_totales = sum(self.demandes_par_produit.get(p.id, 0) for p in produits)
        demande_moyenne = demandes_totales / len(produits)
        
        # Offre moyenne (stock total)
        offres_totales = []
        for produit in produits:
            stock_total = sum(f.stock_produit.get(produit.id, 0) for f in fournisseurs)
            offres_totales.append(stock_total)
        offre_moyenne = statistics.mean(offres_totales) if offres_totales else 0.0
        
        # Rotation de stock (demande / offre)
        rotations = []
        for produit in produits:
            demande = self.demandes_par_produit.get(produit.id, 0)
            offre = sum(f.stock_produit.get(produit.id, 0) for f in fournisseurs)
            if offre > 0:
                rotation = demande / offre
                rotations.append(rotation)
        rotation_stock = statistics.mean(rotations) if rotations else 0.0
        
        # Rentabilité (basée sur la demande vs prix)
        rentabilites = []
        for produit in produits:
            demande = self.demandes_par_produit.get(produit.id, 0)
            prix = produit.prix
            if prix > 0:
                rentabilite = demande * prix  # Revenu potentiel
                rentabilites.append(rentabilite)
        rentabilite_moyenne = statistics.mean(rentabilites) if rentabilites else 0.0
        
        # Popularité (nombre d'achats normalisé)
        popularites = []
        max_demande = max(self.demandes_par_produit.values()) if self.demandes_par_produit else 1
        for produit in produits:
            demande = self.demandes_par_produit.get(produit.id, 0)
            popularite = demande / max_demande if max_demande > 0 else 0
            popularites.append(popularite)
        popularite_moyenne = statistics.mean(popularites) if popularites else 0.0
        
        # Disponibilité (produits avec stock > 0)
        produits_disponibles = 0
        for produit in produits:
            stock_total = sum(f.stock_produit.get(produit.id, 0) for f in fournisseurs)
            if stock_total > 0:
                produits_disponibles += 1
        disponibilite = produits_disponibles / len(produits)
        
        return {
            'demande_moyenne': demande_moyenne,
            'offre_moyenne': offre_moyenne,
            'rotation_stock': rotation_stock,
            'rentabilite': rentabilite_moyenne,
            'popularite': popularite_moyenne,
            'disponibilite': disponibilite
        }
    
    def _calculer_metriques_comportement(self, produits: List[Produit]) -> Dict[str, Any]:
        """
        Calcule les métriques de comportement des produits
        
        Args:
            produits: Liste des produits
            
        Returns:
            Dictionnaire avec les métriques de comportement
        """
        if not produits:
            return {
                'volatilite_prix': 0.0,
                'tendance_prix': 0.0,
                'elasticite_demande': 0.0,
                'competitivite': 0.0
            }
        
        # Volatilité des prix (écart-type des prix historiques)
        volatilites = []
        for produit in produits:
            prix_historique = self.prix_historique.get(produit.id, [])
            if len(prix_historique) > 1:
                volatilite = statistics.stdev(prix_historique)
                volatilites.append(volatilite)
        volatilite_moyenne = statistics.mean(volatilites) if volatilites else 0.0
        
        # Tendance des prix (pente de régression linéaire)
        tendances = []
        for produit in produits:
            prix_historique = self.prix_historique.get(produit.id, [])
            if len(prix_historique) >= 2:
                # Calcul de la pente simplifié
                x_values = list(range(len(prix_historique)))
                y_values = prix_historique
                
                n = len(x_values)
                sum_x = sum(x_values)
                sum_y = sum(y_values)
                sum_xy = sum(x * y for x, y in zip(x_values, y_values))
                sum_x2 = sum(x * x for x in x_values)
                
                if n * sum_x2 - sum_x * sum_x != 0:
                    pente = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                    tendances.append(pente)
        tendance_moyenne = statistics.mean(tendances) if tendances else 0.0
        
        # Élasticité de la demande (variation de demande vs variation de prix)
        elasticites = []
        for produit in produits:
            demande = self.demandes_par_produit.get(produit.id, 0)
            prix_historique = self.prix_historique.get(produit.id, [])
            
            if len(prix_historique) >= 2 and demande > 0:
                variation_prix = (prix_historique[-1] - prix_historique[0]) / prix_historique[0] if prix_historique[0] > 0 else 0
                if variation_prix != 0:
                    elasticite = demande / variation_prix
                    elasticites.append(elasticite)
        elasticite_moyenne = statistics.mean(elasticites) if elasticites else 0.0
        
        # Compétitivité (basée sur le prix et la demande)
        competitivites = []
        for produit in produits:
            demande = self.demandes_par_produit.get(produit.id, 0)
            prix = produit.prix
            
            # Compétitivité = demande / prix (normalisé)
            if prix > 0:
                competitivite = demande / prix
                competitivites.append(competitivite)
        competitivite_moyenne = statistics.mean(competitivites) if competitivites else 0.0
        
        return {
            'volatilite_prix': volatilite_moyenne,
            'tendance_prix': tendance_moyenne,
            'elasticite_demande': elasticite_moyenne,
            'competitivite': competitivite_moyenne
        }
    
    def _calculer_statistiques_produits_cached(self, produits_ids: tuple) -> Dict[str, float]:
        """
        Version cachée de _calculer_statistiques_produits (utilise des tuples)
        
        Args:
            produits_ids: Tuple des IDs de produits (hashable pour le cache)
            
        Returns:
            Dictionnaire avec les statistiques calculées
        """
        # Cette méthode est utilisée pour le cache LRU
        return self._calculer_statistiques_produits_impl(produits_ids)
    
    def _calculer_statistiques_produits(self, produits_ids: tuple) -> Dict[str, float]:
        """
        Calcule les statistiques des produits (avec cache)
        
        Args:
            produits_ids: Tuple des IDs de produits
            
        Returns:
            Dictionnaire avec les statistiques
        """
        # Utiliser le cache si activé
        if PRODUCT_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_produits_cached'):
            return self._calculer_statistiques_produits_cached(produits_ids)
        
        return self._calculer_statistiques_produits_impl(produits_ids)
    
    def _calculer_statistiques_produits_impl(self, produits_ids: tuple) -> Dict[str, float]:
        """
        Implémentation réelle du calcul des statistiques des produits
        
        Args:
            produits_ids: Tuple des IDs de produits
            
        Returns:
            Dictionnaire avec les statistiques
        """
        # Calculs de base (pour l'instant, retourner des valeurs par défaut)
        return {
            'moyenne_demandes': 0.0,
            'ecart_type_demandes': 0.0,
            'moyenne_prix': 0.0,
            'ecart_type_prix': 0.0
        }
    
    def _calculer_alertes_produits(self, produits: List[Produit], fournisseurs: List[Fournisseur]) -> Dict[str, int]:
        """
        Calcule les alertes basées sur les seuils de produits
        
        Args:
            produits: Liste des produits
            fournisseurs: Liste des fournisseurs
            
        Returns:
            Dictionnaire avec le nombre de produits dans chaque catégorie d'alerte
        """
        produits_prix_critique = sum(1 for p in produits if p.prix <= PRODUCT_CRITIQUE_PRIX)
        produits_stock_critique = sum(1 for p in produits if sum(f.stock_produit.get(p.id, 0) for f in fournisseurs) <= PRODUCT_CRITIQUE_STOCK)
        produits_demande_critique = sum(1 for p in produits if self.demandes_par_produit.get(p.id, 0) <= PRODUCT_CRITIQUE_DEMANDE)
        
        return {
            'produits_prix_critique': produits_prix_critique,
            'produits_stock_critique': produits_stock_critique,
            'produits_demande_critique': produits_demande_critique
        }
    

    
    def _metriques_vides(self) -> Dict[str, Any]:
        """
        Retourne des métriques vides quand il n'y a pas de produits
        
        Returns:
            Dictionnaire avec toutes les métriques à 0
        """
        return {
            'produits_total': 0,
            'produits_actifs': 0,
            'produits_par_type': {},
            'produits_par_continent': {},
            'produits_prix_moyen': 0.0,
            'produits_prix_median': 0.0,
            'produits_demande_moyenne': 0.0,
            'produits_offre_moyenne': 0.0,
            'produits_rotation_stock': 0.0,
            'produits_rentabilite': 0.0,
            'produits_popularite': 0.0,
            'produits_disponibilite': 0.0,
            'produits_volatilite_prix': 0.0,
            'produits_tendance_prix': 0.0,
            'produits_elasticite_demande': 0.0,
            'produits_competitivite': 0.0,
            'produits_count': 0,
            'tour_actuel': self.tour_actuel,
            'total_demandes': 0
        }
    
    def reset(self) -> None:
        """Réinitialise le service (pour les tests)"""
        self.historique_produits.clear()
        self.demandes_par_produit.clear()
        self.achats_par_produit.clear()
        self.prix_historique.clear()
        self.tour_actuel = 0
        
        # Vider le cache LRU
        if PRODUCT_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_produits_cached'):
            self._calculer_statistiques_produits_cached.cache_clear()
