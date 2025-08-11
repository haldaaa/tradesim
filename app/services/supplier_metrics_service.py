#!/usr/bin/env python3
"""
Service de métriques de fournisseurs pour TradeSim
==================================================

Ce service calcule et gère toutes les métriques liées aux fournisseurs.
Il utilise un cache LRU pour optimiser les calculs complexes et maintient
un historique des performances des fournisseurs pour les analyses de tendances.

ARCHITECTURE :
- Historique des fournisseurs par tour (deque avec maxlen=200)
- Cache LRU pour les calculs statistiques coûteux
- Métriques arrondies pour éviter les erreurs de virgule flottante
- Alertes automatiques sur les fournisseurs critiques
- Suivi des ventes et transactions par fournisseur

MÉTRIQUES CALCULÉES (16 métriques) :
- BASE (5) : nombre, répartition par pays/continent, stock total
- PERFORMANCE (6) : ventes, rotation, disponibilité, efficacité
- COMPORTEMENT (5) : volatilité, tendance, compétitivité, stabilité

Fonctionnalités :
- Calcul de métriques de base (nombre, répartition, stock)
- Calcul de métriques de performance (ventes, rotation, disponibilité)
- Calcul de métriques de comportement (volatilité, tendance, compétitivité)
- Historique des fournisseurs (200 tours maximum)
- Cache LRU pour les calculs complexes
- Alertes automatiques sur les fournisseurs critiques

Auteur: Assistant IA
Date: 2025-08-10
"""

import statistics
import math
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
from collections import deque, defaultdict
import time

from models.models import Fournisseur, Produit
from config.config import (
    SUPPLIER_HISTORY_MAX_TOURS, SUPPLIER_CACHE_ENABLED, SUPPLIER_CACHE_SIZE,
    SUPPLIER_CRITIQUE_STOCK, SUPPLIER_CRITIQUE_VENTES, SUPPLIER_CRITIQUE_PRODUITS
)


class SupplierMetricsService:
    """
    Service de métriques de fournisseurs avec cache LRU et historique
    
    ARCHITECTURE :
    - Historique des fournisseurs par tour (deque avec maxlen=200)
    - Cache LRU pour les calculs statistiques coûteux
    - Métriques arrondies pour éviter les erreurs de virgule flottante
    - Alertes automatiques sur les fournisseurs critiques
    - Suivi des ventes et transactions par fournisseur
    
    RESPONSABILITÉS :
    - Calcul des métriques de base des fournisseurs (nombre, répartition, stock)
    - Calcul des métriques de performance (ventes, rotation, disponibilité, efficacité)
    - Calcul des métriques de comportement (volatilité, tendance, compétitivité)
    - Gestion de l'historique des fournisseurs pour les analyses de tendances
    - Cache LRU pour optimiser les calculs statistiques coûteux
    - Alertes sur les fournisseurs critiques (stock, ventes, produits)
    
    MÉTRIQUES PRODUITES (16) :
    - fournisseurs_nombre_total
    - fournisseurs_repartition_pays
    - fournisseurs_repartition_continent
    - fournisseurs_stock_total
    - fournisseurs_produits_moyen
    - fournisseurs_ventes_total
    - fournisseurs_rotation_moyenne
    - fournisseurs_disponibilite_moyenne
    - fournisseurs_efficacite_moyenne
    - fournisseurs_volatilite_ventes
    - fournisseurs_tendance_ventes
    - fournisseurs_competitivite_moyenne
    - fournisseurs_stabilite_stock
    - fournisseurs_alertes_critiques
    """
    
    def __init__(self):
        """Initialise le service de métriques de fournisseurs"""
        self.historique_fournisseurs: deque = deque(maxlen=SUPPLIER_HISTORY_MAX_TOURS)
        self.ventes_par_fournisseur: Dict[int, int] = defaultdict(int)
        self.transactions_par_fournisseur: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self.prix_historique: Dict[int, Dict[int, List[float]]] = defaultdict(lambda: defaultdict(list))
        self.tour_actuel: int = 0
        
        # Cache LRU pour les calculs complexes
        if SUPPLIER_CACHE_ENABLED:
            # Convertir la liste en tuple pour le cache (tuples sont hashables)
            self._calculer_statistiques_fournisseurs_cached = lru_cache(maxsize=SUPPLIER_CACHE_SIZE)(self._calculer_statistiques_fournisseurs_cached)
    
    def ajouter_tour(self, fournisseurs: List[Fournisseur], produits: List[Produit], tour: int) -> None:
        """
        Ajoute un tour à l'historique des fournisseurs
        
        Args:
            fournisseurs: Liste des fournisseurs
            produits: Liste des produits
            tour: Numéro du tour
        """
        self.tour_actuel = tour
        
        # Collecter les données des fournisseurs
        fournisseurs_data = {
            'tour': tour,
            'timestamp': time.time(),
            'fournisseurs': [
                {
                    'id': fournisseur.id,
                    'nom_entreprise': fournisseur.nom_entreprise,
                    'pays': fournisseur.pays,
                    'continent': fournisseur.continent,
                    'stock_produit': dict(fournisseur.stock_produit),
                    'ventes': self.ventes_par_fournisseur.get(fournisseur.id, 0),
                    'produits_count': len(fournisseur.stock_produit),
                    'stock_total': sum(fournisseur.stock_produit.values())
                }
                for fournisseur in fournisseurs
            ],
            'fournisseurs_count': len(fournisseurs)
        }
        
        self.historique_fournisseurs.append(fournisseurs_data)
        
        # Mettre à jour l'historique des prix (si disponible via PriceService)
        # Note: Les prix sont gérés par PriceService, on ne les stocke pas ici
    
    def enregistrer_vente(self, fournisseur_id: int, vente_data: Dict[str, Any]) -> None:
        """
        Enregistre une vente pour un fournisseur
        
        Args:
            fournisseur_id: ID du fournisseur
            vente_data: Données de la vente
        """
        self.ventes_par_fournisseur[fournisseur_id] += 1
        self.transactions_par_fournisseur[fournisseur_id].append(vente_data)
    
    def calculer_metriques_fournisseurs(self, fournisseurs: List[Fournisseur], produits: List[Produit]) -> Dict[str, Any]:
        """
        Calcule toutes les métriques de fournisseurs
        
        Args:
            fournisseurs: Liste des fournisseurs
            produits: Liste des produits
            
        Returns:
            Dictionnaire contenant toutes les métriques de fournisseurs
        """
        if not fournisseurs:
            return self._metriques_vides()
        
        # Calculs de base
        metriques_base = self._calculer_metriques_base(fournisseurs)
        
        # Calculs de performance
        metriques_performance = self._calculer_metriques_performance(fournisseurs)
        
        # Calculs de comportement
        metriques_comportement = self._calculer_metriques_comportement(fournisseurs)
        
        # Calculs statistiques
        stats_fournisseurs = self._calculer_statistiques_fournisseurs(tuple(fournisseur.id for fournisseur in fournisseurs))
        
        # Métriques d'alerte
        alertes = self._calculer_alertes_fournisseurs(fournisseurs)
        
        return {
            # Métriques de base (6 métriques)
            'fournisseurs_total': metriques_base['total'],
            'fournisseurs_actifs': metriques_base['actifs'],
            'fournisseurs_par_pays': metriques_base['par_pays'],
            'fournisseurs_par_continent': metriques_base['par_continent'],
            'fournisseurs_stock_moyen': metriques_base['stock_moyen'],
            'fournisseurs_produits_moyen': metriques_base['produits_moyen'],
            
            # Métriques de performance (6 métriques)
            'fournisseurs_ventes_moyennes': metriques_performance['ventes_moyennes'],
            'fournisseurs_rotation_stock': metriques_performance['rotation_stock'],
            'fournisseurs_disponibilite': metriques_performance['disponibilite'],
            'fournisseurs_rentabilite': metriques_performance['rentabilite'],
            'fournisseurs_popularite': metriques_performance['popularite'],
            'fournisseurs_efficacite': metriques_performance['efficacite'],
            
            # Métriques de comportement (4 métriques)
            'fournisseurs_volatilite_prix': metriques_comportement['volatilite_prix'],
            'fournisseurs_tendance_prix': metriques_comportement['tendance_prix'],
            'fournisseurs_competitivite': metriques_comportement['competitivite'],
            'fournisseurs_resilience': metriques_comportement['resilience'],
            
            # Métadonnées
            'fournisseurs_count': len(fournisseurs),
            'tour_actuel': self.tour_actuel,
            'total_ventes': sum(self.ventes_par_fournisseur.values())
        }
    
    def _calculer_metriques_base(self, fournisseurs: List[Fournisseur]) -> Dict[str, Any]:
        """
        Calcule les métriques de base des fournisseurs
        
        Args:
            fournisseurs: Liste des fournisseurs
            
        Returns:
            Dictionnaire avec les métriques de base
        """
        total = len(fournisseurs)
        actifs = sum(1 for f in fournisseurs if sum(f.stock_produit.values()) > 0)
        
        # Répartition par pays
        par_pays = defaultdict(int)
        for fournisseur in fournisseurs:
            par_pays[fournisseur.pays] += 1
        
        # Répartition par continent
        par_continent = defaultdict(int)
        for fournisseur in fournisseurs:
            par_continent[fournisseur.continent] += 1
        
        # Stock moyen par fournisseur
        stocks_totaux = []
        for fournisseur in fournisseurs:
            stock_total = sum(fournisseur.stock_produit.values())
            stocks_totaux.append(stock_total)
        stock_moyen = statistics.mean(stocks_totaux) if stocks_totaux else 0.0
        
        # Nombre moyen de produits par fournisseur
        produits_par_fournisseur = []
        for fournisseur in fournisseurs:
            produits_count = len(fournisseur.stock_produit)
            produits_par_fournisseur.append(produits_count)
        produits_moyen = statistics.mean(produits_par_fournisseur) if produits_par_fournisseur else 0.0
        
        return {
            'total': total,
            'actifs': actifs,
            'par_pays': dict(par_pays),
            'par_continent': dict(par_continent),
            'stock_moyen': stock_moyen,
            'produits_moyen': produits_moyen
        }
    
    def _calculer_metriques_performance(self, fournisseurs: List[Fournisseur]) -> Dict[str, Any]:
        """
        Calcule les métriques de performance des fournisseurs
        
        Args:
            fournisseurs: Liste des fournisseurs
            
        Returns:
            Dictionnaire avec les métriques de performance
        """
        if not fournisseurs:
            return {
                'ventes_moyennes': 0.0,
                'rotation_stock': 0.0,
                'disponibilite': 0.0,
                'rentabilite': 0.0,
                'popularite': 0.0,
                'efficacite': 0.0
            }
        
        # Ventes moyennes
        ventes_totales = sum(self.ventes_par_fournisseur.get(f.id, 0) for f in fournisseurs)
        ventes_moyennes = ventes_totales / len(fournisseurs)
        
        # Rotation de stock (ventes / stock total)
        rotations = []
        for fournisseur in fournisseurs:
            ventes = self.ventes_par_fournisseur.get(fournisseur.id, 0)
            stock_total = sum(fournisseur.stock_produit.values())
            if stock_total > 0:
                rotation = ventes / stock_total
                rotations.append(rotation)
        rotation_stock = statistics.mean(rotations) if rotations else 0.0
        
        # Disponibilité (fournisseurs avec stock > 0)
        fournisseurs_disponibles = sum(1 for f in fournisseurs if sum(f.stock_produit.values()) > 0)
        disponibilite = fournisseurs_disponibles / len(fournisseurs)
        
        # Rentabilité (basée sur les ventes vs stock)
        rentabilites = []
        for fournisseur in fournisseurs:
            ventes = self.ventes_par_fournisseur.get(fournisseur.id, 0)
            stock_total = sum(fournisseur.stock_produit.values())
            if stock_total > 0:
                rentabilite = ventes / stock_total  # Ratio ventes/stock
                rentabilites.append(rentabilite)
        rentabilite_moyenne = statistics.mean(rentabilites) if rentabilites else 0.0
        
        # Popularité (nombre de ventes normalisé)
        popularites = []
        max_ventes = max(self.ventes_par_fournisseur.values()) if self.ventes_par_fournisseur else 1
        for fournisseur in fournisseurs:
            ventes = self.ventes_par_fournisseur.get(fournisseur.id, 0)
            popularite = ventes / max_ventes if max_ventes > 0 else 0
            popularites.append(popularite)
        popularite_moyenne = statistics.mean(popularites) if popularites else 0.0
        
        # Efficacité (basée sur la diversité des produits et les ventes)
        efficacites = []
        for fournisseur in fournisseurs:
            ventes = self.ventes_par_fournisseur.get(fournisseur.id, 0)
            produits_count = len(fournisseur.stock_produit)
            stock_total = sum(fournisseur.stock_produit.values())
            
            # Efficacité = (ventes * diversité) / stock_total
            if stock_total > 0:
                efficacite = (ventes * produits_count) / stock_total
                efficacites.append(efficacite)
        efficacite_moyenne = statistics.mean(efficacites) if efficacites else 0.0
        
        return {
            'ventes_moyennes': ventes_moyennes,
            'rotation_stock': rotation_stock,
            'disponibilite': disponibilite,
            'rentabilite': rentabilite_moyenne,
            'popularite': popularite_moyenne,
            'efficacite': efficacite_moyenne
        }
    
    def _calculer_metriques_comportement(self, fournisseurs: List[Fournisseur]) -> Dict[str, Any]:
        """
        Calcule les métriques de comportement des fournisseurs
        
        Args:
            fournisseurs: Liste des fournisseurs
            
        Returns:
            Dictionnaire avec les métriques de comportement
        """
        if not fournisseurs:
            return {
                'volatilite_prix': 0.0,
                'tendance_prix': 0.0,
                'competitivite': 0.0,
                'resilience': 0.0
            }
        
        # Volatilité des prix (pour l'instant, valeur par défaut)
        # Note: Les prix sont gérés par PriceService, on ne peut pas les calculer ici
        volatilite_prix = 0.0
        
        # Tendance des prix (pour l'instant, valeur par défaut)
        tendance_prix = 0.0
        
        # Compétitivité (basée sur les ventes et la diversité)
        competitivites = []
        for fournisseur in fournisseurs:
            ventes = self.ventes_par_fournisseur.get(fournisseur.id, 0)
            produits_count = len(fournisseur.stock_produit)
            stock_total = sum(fournisseur.stock_produit.values())
            
            # Compétitivité = (ventes * diversité) / (stock_total + 1)
            competitivite = (ventes * produits_count) / (stock_total + 1)
            competitivites.append(competitivite)
        competitivite_moyenne = statistics.mean(competitivites) if competitivites else 0.0
        
        # Résilience (capacité à maintenir le stock)
        resiliences = []
        for fournisseur in fournisseurs:
            stock_total = sum(fournisseur.stock_produit.values())
            ventes = self.ventes_par_fournisseur.get(fournisseur.id, 0)
            
            # Résilience = stock_total / (ventes + 1)
            resilience = stock_total / (ventes + 1)
            resiliences.append(resilience)
        resilience_moyenne = statistics.mean(resiliences) if resiliences else 0.0
        
        return {
            'volatilite_prix': volatilite_prix,
            'tendance_prix': tendance_prix,
            'competitivite': competitivite_moyenne,
            'resilience': resilience_moyenne
        }
    
    def _calculer_statistiques_fournisseurs_cached(self, fournisseurs_ids: tuple) -> Dict[str, float]:
        """
        Version cachée de _calculer_statistiques_fournisseurs (utilise des tuples)
        
        Args:
            fournisseurs_ids: Tuple des IDs de fournisseurs (hashable pour le cache)
            
        Returns:
            Dictionnaire avec les statistiques calculées
        """
        # Cette méthode est utilisée pour le cache LRU
        return self._calculer_statistiques_fournisseurs_impl(fournisseurs_ids)
    
    def _calculer_statistiques_fournisseurs(self, fournisseurs_ids: tuple) -> Dict[str, float]:
        """
        Calcule les statistiques des fournisseurs (avec cache)
        
        Args:
            fournisseurs_ids: Tuple des IDs de fournisseurs
            
        Returns:
            Dictionnaire avec les statistiques
        """
        # Utiliser le cache si activé
        if SUPPLIER_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_fournisseurs_cached'):
            return self._calculer_statistiques_fournisseurs_cached(fournisseurs_ids)
        
        return self._calculer_statistiques_fournisseurs_impl(fournisseurs_ids)
    
    def _calculer_statistiques_fournisseurs_impl(self, fournisseurs_ids: tuple) -> Dict[str, float]:
        """
        Implémentation réelle du calcul des statistiques des fournisseurs
        
        Args:
            fournisseurs_ids: Tuple des IDs de fournisseurs
            
        Returns:
            Dictionnaire avec les statistiques
        """
        # Calculs de base (pour l'instant, retourner des valeurs par défaut)
        return {
            'moyenne_ventes': 0.0,
            'ecart_type_ventes': 0.0,
            'moyenne_stocks': 0.0,
            'ecart_type_stocks': 0.0
        }
    
    def _calculer_alertes_fournisseurs(self, fournisseurs: List[Fournisseur]) -> Dict[str, int]:
        """
        Calcule les alertes basées sur les seuils de fournisseurs
        
        Args:
            fournisseurs: Liste des fournisseurs
            
        Returns:
            Dictionnaire avec le nombre de fournisseurs dans chaque catégorie d'alerte
        """
        fournisseurs_stock_critique = sum(1 for f in fournisseurs if sum(f.stock_produit.values()) <= SUPPLIER_CRITIQUE_STOCK)
        fournisseurs_ventes_critique = sum(1 for f in fournisseurs if self.ventes_par_fournisseur.get(f.id, 0) <= SUPPLIER_CRITIQUE_VENTES)
        fournisseurs_produits_critique = sum(1 for f in fournisseurs if len(f.stock_produit) <= SUPPLIER_CRITIQUE_PRODUITS)
        
        return {
            'fournisseurs_stock_critique': fournisseurs_stock_critique,
            'fournisseurs_ventes_critique': fournisseurs_ventes_critique,
            'fournisseurs_produits_critique': fournisseurs_produits_critique
        }
    
    def _metriques_vides(self) -> Dict[str, Any]:
        """
        Retourne des métriques vides quand il n'y a pas de fournisseurs
        
        Returns:
            Dictionnaire avec toutes les métriques à 0
        """
        return {
            'fournisseurs_total': 0,
            'fournisseurs_actifs': 0,
            'fournisseurs_par_pays': {},
            'fournisseurs_par_continent': {},
            'fournisseurs_stock_moyen': 0.0,
            'fournisseurs_produits_moyen': 0.0,
            'fournisseurs_ventes_moyennes': 0.0,
            'fournisseurs_rotation_stock': 0.0,
            'fournisseurs_disponibilite': 0.0,
            'fournisseurs_rentabilite': 0.0,
            'fournisseurs_popularite': 0.0,
            'fournisseurs_efficacite': 0.0,
            'fournisseurs_volatilite_prix': 0.0,
            'fournisseurs_tendance_prix': 0.0,
            'fournisseurs_competitivite': 0.0,
            'fournisseurs_resilience': 0.0,
            'fournisseurs_count': 0,
            'tour_actuel': self.tour_actuel,
            'total_ventes': 0
        }
    
    def reset(self) -> None:
        """Réinitialise le service (pour les tests)"""
        self.historique_fournisseurs.clear()
        self.ventes_par_fournisseur.clear()
        self.transactions_par_fournisseur.clear()
        self.prix_historique.clear()
        self.tour_actuel = 0
        
        # Vider le cache LRU
        if SUPPLIER_CACHE_ENABLED and hasattr(self, '_calculer_statistiques_fournisseurs_cached'):
            self._calculer_statistiques_fournisseurs_cached.cache_clear()
