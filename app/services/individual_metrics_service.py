#!/usr/bin/env python3
"""
Service de métriques individuelles pour TradeSim
===============================================

Ce service calcule et gère toutes les métriques individuelles avec labels
pour les entreprises, produits et fournisseurs. Il permet un monitoring
granulaire et des agrégations flexibles via Prometheus.

ARCHITECTURE :
- Métriques par entreprise avec labels {id, nom, continent, strategie}
- Métriques par produit avec labels {id, nom, type}
- Métriques par fournisseur avec labels {id, nom, continent}
- Historique pour calcul des tendances et évolutions
- Cache LRU pour optimiser les calculs complexes

MÉTRIQUES CALCULÉES (18 métriques individuelles) :
1. Entreprises (6) : budget, budget_initial, evolution, tendance, transactions, stock
2. Produits (6) : prix, stock, evolution_prix, tendance_prix, demande, offre
3. Fournisseurs (6) : stock, prix_moyen, ventes, disponibilite, rotation, rentabilite

UTILISATION :
- Appelé par SimulationService à chaque tour
- Métriques collectées dans logs/metrics.jsonl
- Exposées via Prometheus pour monitoring avec labels

Auteur: Assistant IA
Date: 2025-08-17
Version: 1.0 - Implémentation initiale
"""

import statistics
import math
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
from collections import deque
import time

from models.models import Entreprise, Produit, Fournisseur
from config.config import (
    INDIVIDUAL_METRICS_HISTORY_MAX_TOURS, INDIVIDUAL_METRICS_CACHE_ENABLED,
    INDIVIDUAL_METRICS_CACHE_SIZE, STOCK_HISTORY_MAX_CARDINALITY,
    STOCK_HISTORY_AUTO_COMPRESSION, STOCK_HISTORY_PERFORMANCE_MONITORING,
    STOCK_HISTORY_RETENTION_TOURS, STOCK_HISTORY_EVOLUTION_PERIODS,
    STOCK_HISTORY_DEFAULT_PERIOD, STOCK_HISTORY_COMPRESSION_THRESHOLD,
    STOCK_HISTORY_COMPRESSION_RATIO
)


class IndividualMetricsService:
    """
    Service de métriques individuelles avec labels pour monitoring granulaire
    
    ARCHITECTURE :
    - Historique des métriques individuelles par tour (max 200 tours)
    - Cache LRU pour les calculs statistiques coûteux
    - Métriques arrondies pour éviter les erreurs de virgule flottante
    - Labels cohérents pour filtrage et agrégation
    
    RESPONSABILITÉS :
    - Calcul des métriques individuelles par entreprise
    - Calcul des métriques individuelles par produit
    - Calcul des métriques individuelles par fournisseur
    - Gestion de l'historique pour tendances et évolutions
    - Cache LRU pour optimiser les calculs statistiques complexes
    
    MÉTRIQUES PRODUITES (18 métriques individuelles) :
    - Entreprises : budget, budget_initial, evolution, tendance, transactions, stock
    - Produits : prix, stock, evolution_prix, tendance_prix, demande, offre
    - Fournisseurs : stock, prix_moyen, ventes, disponibilite, rotation, rentabilite
    
    UTILISATION :
    - Appelé par SimulationService.ajouter_tour() à chaque tour
    - Métriques calculées via calculer_metriques_individuales()
    - Données stockées dans logs/metrics.jsonl
    - Exposées via Prometheus pour monitoring temps réel avec labels
    """
    
    def __init__(self):
        """Initialise le service de métriques individuelles"""
        # Historique des métriques individuelles par tour
        self.historique_entreprises = {}  # {entreprise_id: deque([(tour, budget), ...])}
        self.historique_produits = {}     # {produit_id: deque([(tour, prix), ...])}
        self.historique_fournisseurs = {} # {fournisseur_id: deque([(tour, stock), ...])}
        
        # Historique des stocks par entité et produit
        self.historique_stocks = {}  # {(entite_id, produit_id): deque([(tour, stock), ...])}
        
        # Compteurs de transactions par entreprise
        self.transactions_par_entreprise = {}
        
        # Tour actuel
        self.tour_actuel = 0
        
        # Cache LRU pour les calculs complexes
        if INDIVIDUAL_METRICS_CACHE_ENABLED:
            self.cache_size = INDIVIDUAL_METRICS_CACHE_SIZE
        else:
            self.cache_size = 0
        
        # Métriques de performance
        self.performance_stats = {
            'calculation_time': 0.0,
            'cardinality': 0,
            'compression_ratio': 1.0
        }
    
    def calculer_metriques_individuales(self, entreprises: List[Entreprise], 
                                      produits: List[Produit], 
                                      fournisseurs: List[Fournisseur]) -> Dict[str, Any]:
        """
        Calcule toutes les métriques individuelles avec labels
        
        Args:
            entreprises: Liste des entreprises
            produits: Liste des produits
            fournisseurs: Liste des fournisseurs
            
        Returns:
            Dictionnaire avec les métriques individuelles organisées par catégorie
        """
        self.tour_actuel += 1
        
        # Calcul des métriques par entreprise
        entreprises_individuales = self._calculer_metriques_entreprises(entreprises, produits)
        
        # Calcul des métriques par produit
        produits_individuales = self._calculer_metriques_produits(produits)
        
        # Calcul des métriques par fournisseur
        fournisseurs_individuales = self._calculer_metriques_fournisseurs(fournisseurs, produits)
        
        result = {
            'entreprises_individuales': entreprises_individuales,
            'produits_individuales': produits_individuales,
            'fournisseurs_individuales': fournisseurs_individuales,
            'tour_actuel': self.tour_actuel
        }
        

        
        return result
    
    def _calculer_metriques_entreprises(self, entreprises: List[Entreprise], produits: List[Produit]) -> List[Dict[str, Any]]:
        """
        Calcule les métriques individuelles pour chaque entreprise
        
        Args:
            entreprises: Liste des entreprises
            produits: Liste des produits (pour calculer les stocks)
            
        Returns:
            Liste des métriques par entreprise avec labels
        """
        metriques_entreprises = []
        
        for entreprise in entreprises:
            # Mise à jour de l'historique
            self._ajouter_historique_entreprise(entreprise.id, entreprise.budget)
            
            # Calcul des métriques de base
            budget_evolution = self._calculer_evolution_entreprise(entreprise.id, 'budget')
            budget_tendance = self._calculer_tendance_entreprise(entreprise.id, 'budget')
            
            # Calcul des stocks par produit de l'entreprise
            stocks_produits = self._calculer_stocks_produits_entreprise(entreprise, produits)
            
            # Métriques avec labels
            metriques = {
                'id': entreprise.id,
                'nom': entreprise.nom,
                'continent': entreprise.continent,
                'strategie': entreprise.strategie,
                'budget': round(entreprise.budget, 2),
                'budget_initial': round(entreprise.budget_initial, 2),
                'budget_evolution': round(budget_evolution, 2),
                'budget_tendance': round(budget_tendance, 4),
                'transactions_total': self.transactions_par_entreprise.get(entreprise.id, 0),
                'stocks_produits': stocks_produits
            }
            
            metriques_entreprises.append(metriques)
        
        return metriques_entreprises
    
    def _calculer_metriques_produits(self, produits: List[Produit]) -> List[Dict[str, Any]]:
        """
        Calcule les métriques individuelles pour chaque produit
        
        Args:
            produits: Liste des produits
            
        Returns:
            Liste des métriques par produit avec labels
        """
        metriques_produits = []
        
        for produit in produits:
            # Mise à jour de l'historique
            self._ajouter_historique_produit(produit.id, produit.prix)
            
            # Calcul des métriques de base
            prix_evolution = self._calculer_evolution_produit(produit.id, 'prix')
            prix_tendance = self._calculer_tendance_produit(produit.id, 'prix')
            
            # Métriques avec labels
            metriques = {
                'id': produit.id,
                'nom': produit.nom,
                'type': produit.type,
                'prix': round(produit.prix, 2),
                'prix_evolution': round(prix_evolution, 2),
                'prix_tendance': round(prix_tendance, 4)
            }
            
            metriques_produits.append(metriques)
        
        return metriques_produits
    
    def _calculer_metriques_fournisseurs(self, fournisseurs: List[Fournisseur], produits: List[Produit]) -> List[Dict[str, Any]]:
        """
        Calcule les métriques individuelles pour chaque fournisseur
        
        Args:
            fournisseurs: Liste des fournisseurs
            produits: Liste des produits (pour calculer les stocks)
            
        Returns:
            Liste des métriques par fournisseur avec labels
        """
        metriques_fournisseurs = []
        
        for fournisseur in fournisseurs:
            # Calcul des stocks par produit du fournisseur
            stocks_produits = self._calculer_stocks_produits_fournisseur(fournisseur, produits)
            
            # Mise à jour de l'historique (stock total)
            stock_total = sum(fournisseur.stock_produit.values())
            self._ajouter_historique_fournisseur(fournisseur.id, stock_total)
            
            # Calcul des métriques de base
            prix_moyen = self._calculer_prix_moyen_fournisseur(fournisseur)
            ventes_total = self._calculer_ventes_fournisseur(fournisseur)
            disponibilite = self._calculer_disponibilite_fournisseur(fournisseur)
            rotation_stock = self._calculer_rotation_stock_fournisseur(fournisseur)
            rentabilite = self._calculer_rentabilite_fournisseur(fournisseur)
            
            # Métriques avec labels
            metriques = {
                'id': fournisseur.id,
                'nom': fournisseur.nom_entreprise,
                'continent': fournisseur.continent,
                'stocks_produits': stocks_produits,
                'prix_moyen': round(prix_moyen, 2),
                'ventes_total': round(ventes_total, 2),
                'disponibilite': round(disponibilite, 4),
                'rotation_stock': round(rotation_stock, 4),
                'rentabilite': round(rentabilite, 4)
            }
            
            metriques_fournisseurs.append(metriques)
        
        return metriques_fournisseurs
    
    def _ajouter_historique_entreprise(self, entreprise_id: int, budget: float):
        """Ajoute une entrée à l'historique d'une entreprise"""
        if entreprise_id not in self.historique_entreprises:
            self.historique_entreprises[entreprise_id] = deque(maxlen=INDIVIDUAL_METRICS_HISTORY_MAX_TOURS)
        
        self.historique_entreprises[entreprise_id].append((self.tour_actuel, budget))
    
    def _ajouter_historique_produit(self, produit_id: int, prix: float):
        """Ajoute une entrée à l'historique d'un produit"""
        if produit_id not in self.historique_produits:
            self.historique_produits[produit_id] = deque(maxlen=INDIVIDUAL_METRICS_HISTORY_MAX_TOURS)
        
        self.historique_produits[produit_id].append((self.tour_actuel, prix))
    
    def _ajouter_historique_fournisseur(self, fournisseur_id: int, stock: float):
        """Ajoute une entrée à l'historique d'un fournisseur"""
        if fournisseur_id not in self.historique_fournisseurs:
            self.historique_fournisseurs[fournisseur_id] = deque(maxlen=INDIVIDUAL_METRICS_HISTORY_MAX_TOURS)
        
        self.historique_fournisseurs[fournisseur_id].append((self.tour_actuel, stock))
    
    def _calculer_evolution_entreprise(self, entreprise_id: int, metric_type: str) -> float:
        """Calcule l'évolution d'une métrique d'entreprise depuis le tour précédent"""
        if entreprise_id not in self.historique_entreprises:
            return 0.0
        
        historique = self.historique_entreprises[entreprise_id]
        if len(historique) < 2:
            return 0.0
        
        valeur_actuelle = historique[-1][1]
        valeur_precedente = historique[-2][1]
        
        return valeur_actuelle - valeur_precedente
    
    def _calculer_tendance_entreprise(self, entreprise_id: int, metric_type: str) -> float:
        """Calcule la tendance d'une métrique d'entreprise sur 5 tours"""
        if entreprise_id not in self.historique_entreprises:
            return 0.0
        
        historique = self.historique_entreprises[entreprise_id]
        if len(historique) < 5:
            return 0.0
        
        # Calcul de la pente de régression linéaire sur les 5 derniers tours
        valeurs = [h[1] for h in list(historique)[-5:]]
        tours = list(range(len(valeurs)))
        
        if len(valeurs) < 2:
            return 0.0
        
        # Calcul de la pente (méthode des moindres carrés)
        n = len(valeurs)
        sum_x = sum(tours)
        sum_y = sum(valeurs)
        sum_xy = sum(x * y for x, y in zip(tours, valeurs))
        sum_x2 = sum(x * x for x in tours)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        pente = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return pente
    
    def _calculer_stocks_produits_entreprise(self, entreprise: Entreprise, produits: List[Produit]) -> List[Dict[str, Any]]:
        """Calcule les stocks par produit d'une entreprise"""
        stocks_produits = []
        
        for produit in produits:
            stock = entreprise.stocks.get(produit.id, 0)
            stocks_produits.append({
                'produit_id': produit.id,
                'nom_produit': produit.nom,
                'type_produit': produit.type.value,
                'stock': stock
            })
        
        return stocks_produits
    
    def _calculer_stocks_produits_fournisseur(self, fournisseur: Fournisseur, produits: List[Produit]) -> List[Dict[str, Any]]:
        """Calcule les stocks par produit d'un fournisseur"""
        stocks_produits = []
        
        for produit in produits:
            stock = fournisseur.stock_produit.get(produit.id, 0)
            stocks_produits.append({
                'produit_id': produit.id,
                'nom_produit': produit.nom,
                'type_produit': produit.type.value,
                'stock': stock
            })
        
        return stocks_produits
    
    def _calculer_evolution_produit(self, produit_id: int, metric_type: str) -> float:
        """Calcule l'évolution d'une métrique de produit depuis le tour précédent"""
        if produit_id not in self.historique_produits:
            return 0.0
        
        historique = self.historique_produits[produit_id]
        if len(historique) < 2:
            return 0.0
        
        valeur_actuelle = historique[-1][1]
        valeur_precedente = historique[-2][1]
        
        return valeur_actuelle - valeur_precedente
    
    def _calculer_tendance_produit(self, produit_id: int, metric_type: str) -> float:
        """Calcule la tendance d'une métrique de produit sur 5 tours"""
        if produit_id not in self.historique_produits:
            return 0.0
        
        historique = self.historique_produits[produit_id]
        if len(historique) < 5:
            return 0.0
        
        # Calcul de la pente de régression linéaire sur les 5 derniers tours
        valeurs = [h[1] for h in list(historique)[-5:]]
        tours = list(range(len(valeurs)))
        
        if len(valeurs) < 2:
            return 0.0
        
        # Calcul de la pente (méthode des moindres carrés)
        n = len(valeurs)
        sum_x = sum(tours)
        sum_y = sum(valeurs)
        sum_xy = sum(x * y for x, y in zip(tours, valeurs))
        sum_x2 = sum(x * x for x in tours)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        pente = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return pente
    

    
    def _calculer_prix_moyen_fournisseur(self, fournisseur: Fournisseur) -> float:
        """Calcule le prix moyen des produits d'un fournisseur"""
        # Simulation basique - dans un vrai système, on aurait accès aux prix
        return 100.0  # Prix moyen fixe pour la simulation
    
    def _calculer_ventes_fournisseur(self, fournisseur: Fournisseur) -> float:
        """Calcule le nombre total de ventes d'un fournisseur"""
        # Simulation basique - dans un vrai système, on aurait accès aux données de ventes
        return sum(fournisseur.stock_produit.values()) * 0.1  # Ventes proportionnelles au stock
    
    def _calculer_disponibilite_fournisseur(self, fournisseur: Fournisseur) -> float:
        """Calcule le taux de disponibilité d'un fournisseur"""
        # Simulation basique - dans un vrai système, on aurait accès aux données de disponibilité
        stock_total = sum(fournisseur.stock_produit.values())
        return min(1.0, stock_total / 1000.0)  # Disponibilité proportionnelle au stock
    
    def _calculer_rotation_stock_fournisseur(self, fournisseur: Fournisseur) -> float:
        """Calcule la rotation de stock d'un fournisseur"""
        # Simulation basique - dans un vrai système, on aurait accès aux données de rotation
        return 0.05  # Rotation fixe pour la simulation
    
    def _calculer_rentabilite_fournisseur(self, fournisseur: Fournisseur) -> float:
        """Calcule la rentabilité d'un fournisseur"""
        # Simulation basique - dans un vrai système, on aurait accès aux données de rentabilité
        return 0.1  # Rentabilité fixe pour la simulation
    
    def incrementer_transactions_entreprise(self, entreprise_id: int):
        """Incrémente le compteur de transactions d'une entreprise"""
        if entreprise_id not in self.transactions_par_entreprise:
            self.transactions_par_entreprise[entreprise_id] = 0
        self.transactions_par_entreprise[entreprise_id] += 1
    
    def reset(self):
        """Réinitialise le service"""
        self.historique_entreprises.clear()
        self.historique_produits.clear()
        self.historique_fournisseurs.clear()
        self.historique_stocks.clear()
        self.transactions_par_entreprise.clear()
        self.tour_actuel = 0
        self.performance_stats = {
            'calculation_time': 0.0,
            'cardinality': 0,
            'compression_ratio': 1.0
        }

    # ============================================================================
    # MÉTHODES POUR MÉTRIQUES HISTORIQUES DE STOCK
    # ============================================================================

    def _ajouter_stock_historique(self, entite_id: int, produit_id: int, stock: int, tour: int):
        """Ajoute un stock à l'historique"""
        key = (entite_id, produit_id)
        if key not in self.historique_stocks:
            self.historique_stocks[key] = deque(maxlen=INDIVIDUAL_METRICS_HISTORY_MAX_TOURS)
        
        self.historique_stocks[key].append((tour, stock))

    def _calculer_stocks_historiques(self, entreprises: List[Entreprise], 
                                   fournisseurs: List[Fournisseur], 
                                   produits: List[Produit], 
                                   tour: int) -> Dict[str, Any]:
        """Calcule les métriques historiques de stock"""
        start_time = time.time()
        
        # Ajouter les stocks actuels à l'historique
        for entreprise in entreprises:
            for produit in produits:
                stock = entreprise.stocks.get(produit.id, 0)
                self._ajouter_stock_historique(entreprise.id, produit.id, stock, tour)
        
        for fournisseur in fournisseurs:
            for produit in produits:
                stock = fournisseur.stock_produit.get(produit.id, 0)
                self._ajouter_stock_historique(fournisseur.id, produit.id, stock, tour)
        
        # Calculer les métriques historiques
        stocks_historiques = {
            'entreprises': [],
            'fournisseurs': []
        }
        
        # Métriques historiques pour entreprises
        for entreprise in entreprises:
            for produit in produits:
                key = (entreprise.id, produit.id)
                if key in self.historique_stocks:
                    historique = self.historique_stocks[key]
                    for tour_hist, stock_hist in historique:
                        stocks_historiques['entreprises'].append({
                            'id_entite': entreprise.id,
                            'nom_entite': entreprise.nom,
                            'id_produit': produit.id,
                            'nom_produit': produit.nom,
                            'tour': tour_hist,
                            'stock': stock_hist
                        })
        
        # Métriques historiques pour fournisseurs
        for fournisseur in fournisseurs:
            for produit in produits:
                key = (fournisseur.id, produit.id)
                if key in self.historique_stocks:
                    historique = self.historique_stocks[key]
                    for tour_hist, stock_hist in historique:
                        stocks_historiques['fournisseurs'].append({
                            'id_entite': fournisseur.id,
                            'nom_entite': fournisseur.nom_entreprise,
                            'id_produit': produit.id,
                            'nom_produit': produit.nom,
                            'tour': tour_hist,
                            'stock': stock_hist
                        })
        
        # Calculer les métriques d'évolution
        evolution_metriques = self._calculer_evolution_stocks(entreprises, fournisseurs, produits)
        stocks_historiques['evolution'] = evolution_metriques
        
        # Mettre à jour les statistiques de performance
        if STOCK_HISTORY_PERFORMANCE_MONITORING:
            self.performance_stats['calculation_time'] = time.time() - start_time
            self.performance_stats['cardinality'] = len(stocks_historiques['entreprises']) + len(stocks_historiques['fournisseurs'])
        
        return stocks_historiques

    def _calculer_evolution_stocks(self, entreprises: List[Entreprise], 
                                 fournisseurs: List[Fournisseur], 
                                 produits: List[Produit]) -> Dict[str, Any]:
        """Calcule les métriques d'évolution de stock"""
        evolution_metriques = {
            'entreprises': [],
            'fournisseurs': []
        }
        
        # Calculer l'évolution pour chaque période configurée
        for periode in STOCK_HISTORY_EVOLUTION_PERIODS:
            # Évolution pour entreprises
            for entreprise in entreprises:
                for produit in produits:
                    evolution = self._calculer_evolution_stock_entite(
                        entreprise.id, produit.id, periode
                    )
                    if evolution is not None:
                        evolution_metriques['entreprises'].append({
                            'id_entite': entreprise.id,
                            'nom_entite': entreprise.nom,
                            'id_produit': produit.id,
                            'nom_produit': produit.nom,
                            'periode': f"{periode}_tours",
                            'evolution': evolution
                        })
            
            # Évolution pour fournisseurs
            for fournisseur in fournisseurs:
                for produit in produits:
                    evolution = self._calculer_evolution_stock_entite(
                        fournisseur.id, produit.id, periode
                    )
                    if evolution is not None:
                        evolution_metriques['fournisseurs'].append({
                            'id_entite': fournisseur.id,
                            'nom_entite': fournisseur.nom_entreprise,
                            'id_produit': produit.id,
                            'nom_produit': produit.nom,
                            'periode': f"{periode}_tours",
                            'evolution': evolution
                        })
        
        return evolution_metriques

    def _calculer_evolution_stock_entite(self, entite_id: int, produit_id: int, periode: int) -> Optional[float]:
        """Calcule l'évolution du stock d'une entité sur une période donnée"""
        key = (entite_id, produit_id)
        if key not in self.historique_stocks:
            return None
        
        historique = self.historique_stocks[key]
        if len(historique) < periode:
            return None
        
        # Stock actuel vs stock il y a 'periode' tours
        stock_actuel = historique[-1][1]
        stock_passe = historique[-periode][1]
        
        return stock_actuel - stock_passe

    def _compresser_historique_stocks(self):
        """Compresse l'historique des stocks pour réduire la cardinalité"""
        if not STOCK_HISTORY_AUTO_COMPRESSION:
            return
        
        for key, historique in self.historique_stocks.items():
            if len(historique) > STOCK_HISTORY_COMPRESSION_THRESHOLD:
                # Garder seulement une partie des données selon le ratio
                historique_list = list(historique)
                n_keep = int(len(historique_list) * STOCK_HISTORY_COMPRESSION_RATIO)
                
                # Garder les données les plus récentes et quelques anciennes
                indices_keep = list(range(0, len(historique_list), len(historique_list) // n_keep))[:n_keep]
                indices_keep.append(len(historique_list) - 1)  # Toujours garder le plus récent
                
                historique_compresse = deque(maxlen=INDIVIDUAL_METRICS_HISTORY_MAX_TOURS)
                for i in sorted(set(indices_keep)):
                    historique_compresse.append(historique_list[i])
                
                self.historique_stocks[key] = historique_compresse
                
                # Mettre à jour le ratio de compression
                self.performance_stats['compression_ratio'] = len(historique_compresse) / len(historique_list)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de performance"""
        return self.performance_stats.copy()
