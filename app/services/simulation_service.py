#!/usr/bin/env python3
"""
SimulationService TradeSim - Orchestration de la simulation
==========================================================

Ce service orchestre la simulation économique TradeSim.
Il gère les tours de simulation, les événements et l'état global.

Refactorisation (02/08/2025) :
- Utilise les Repository pour l'accès aux données
- Code modulaire et testable
- Interface commune pour CLI et API

Monitoring (04/08/2025) :
- Intégration Prometheus/Grafana
- Collecte des métriques pendant la simulation
- Mise à jour de l'exporter en temps réel

Auteur: Assistant IA
Date: 2024-08-02
"""

import random
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
from models import Produit, Fournisseur, Entreprise, TypeProduit
from events.inflation import appliquer_inflation_et_retour
from events.reassort import evenement_reassort
from events.recharge_budget import appliquer_recharge_budget
from events.variation_disponibilite import appliquer_variation_disponibilite
from config import (
    PROBABILITE_SELECTION_ENTREPRISE, DUREE_PAUSE_ENTRE_TOURS,
    TICK_INTERVAL_EVENT, PROBABILITE_EVENEMENT, METRICS_ENABLED
)

# Import du monitoring
try:
    from monitoring.prometheus_exporter import PrometheusExporter
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    PrometheusExporter = None


class SimulationService:
    """
    Service d'orchestration de la simulation TradeSim.
    
    Responsabilités :
    - Gérer les tours de simulation
    - Orchestrer les événements
    - Maintenir l'état global
    - Fournir des statistiques
    - Collecter les métriques (monitoring)
    """
    
    def __init__(self):
        """Initialise le service de simulation"""
        self.produit_repo = ProduitRepository()
        self.fournisseur_repo = FournisseurRepository()
        self.entreprise_repo = EntrepriseRepository()
        
        # État de la simulation
        self.tick_actuel = 0
        self.tours_completes = 0
        self.evenements_appliques = []
        self.statistiques = {
            "tours_completes": 0,
            "evenements_appliques": 0,
            "transactions_effectuees": 0,
            "budget_total_initial": 0,
            "budget_total_actuel": 0
        }
        
        # Monitoring
        self.exporter = None
        if METRICS_ENABLED and MONITORING_AVAILABLE:
            try:
                self.exporter = PrometheusExporter()
            except Exception as e:
                print(f"⚠️ Erreur lors de l'initialisation du monitoring: {e}")
    
    def reset_simulation(self):
        """Remet la simulation à zéro"""
        self.tick_actuel = 0
        self.tours_completes = 0
        self.evenements_appliques = []
        self.statistiques = {
            "tours_completes": 0,
            "evenements_appliques": 0,
            "transactions_effectuees": 0,
            "budget_total_initial": 0,
            "budget_total_actuel": 0
        }
        print("✅ Simulation remise à zéro")
    
    def calculer_statistiques(self):
        """Calcule les statistiques actuelles de la simulation"""
        entreprises = self.entreprise_repo.get_all()
        produits = self.produit_repo.get_all()
        fournisseurs = self.fournisseur_repo.get_all()
        
        self.statistiques.update({
            "tours_completes": self.tours_completes,
            "evenements_appliques": len(self.evenements_appliques),
            "budget_total_initial": sum(e.budget_initial for e in entreprises),
            "budget_total_actuel": sum(e.budget for e in entreprises),
            "nombre_entreprises": len(entreprises),
            "nombre_produits_actifs": len([p for p in produits if p.actif]),
            "nombre_fournisseurs": len(fournisseurs)
        })
        
        return self.statistiques
    
    def collecter_metriques(self):
        """
        Collecte et envoie les métriques à l'exporter Prometheus
        """
        if not self.exporter:
            return
            
        try:
            # Calculer les statistiques
            stats = self.calculer_statistiques()
            
            # Préparer les métriques avec arrondi à 2 décimales
            metrics_data = {
                'budget_total': round(stats['budget_total_actuel'], 2),
                'produits_actifs': stats['nombre_produits_actifs'],
                'tours_completes': 1,  # Incrémenter de 1 à chaque tour
                'temps_simulation_tour_seconds': round(time.time() - getattr(self, '_tour_start_time', time.time()), 4)
            }
            
            # Mettre à jour l'exporter
            self.exporter.update_tradesim_metrics(metrics_data)
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la collecte des métriques: {e}")
    
    def appliquer_evenements(self, tick: int) -> List[Dict[str, Any]]:
        """
        Applique les événements aléatoires selon la configuration.
        
        Args:
            tick: Numéro du tick actuel
            
        Returns:
            Liste des événements appliqués
        """
        evenements_appliques = []
        
        # Événement d'inflation
        if random.random() < PROBABILITE_EVENEMENT["inflation"]:
            evenement = appliquer_inflation_et_retour(tick)
            if evenement:
                evenements_appliques.append(evenement)
        
        # Événement de reassort
        if random.random() < PROBABILITE_EVENEMENT["reassort"]:
            evenement = evenement_reassort(tick)
            if evenement:
                evenements_appliques.append(evenement)
        
        # Événement de recharge budget
        if random.random() < PROBABILITE_EVENEMENT["recharge_budget"]:
            evenement = appliquer_recharge_budget(tick)
            if evenement:
                evenements_appliques.append(evenement)
        
        # Événement de variation disponibilité
        if random.random() < PROBABILITE_EVENEMENT["variation_disponibilite"]:
            evenement = appliquer_variation_disponibilite(tick)
            if evenement:
                evenements_appliques.append(evenement)
        
        return evenements_appliques

    def simulation_tour(self, verbose: bool = False) -> Dict[str, Any]:
        """
        Exécute un tour de simulation complet.
        
        Args:
            verbose: Afficher les détails du tour
            
        Returns:
            Dictionnaire contenant les résultats du tour
        """
        # Marquer le début du tour pour les métriques
        self._tour_start_time = time.time()
        
        if verbose:
            print(f"\n🔄 Tour {self.tours_completes + 1} - Tick {self.tick_actuel}")
        
        # Appliquer les événements
        evenements = self.appliquer_evenements(self.tick_actuel)
        self.evenements_appliques.extend(evenements)
        
        if verbose and evenements:
            print(f"📊 {len(evenements)} événement(s) appliqué(s)")
            for event in evenements:
                if isinstance(event, dict):
                    print(f"  • {event.get('type', 'Inconnu')}: {event.get('description', '')}")
                else:
                    print(f"  • Événement: {event}")
        
        # Simuler les transactions
        transactions_effectuees = self.simuler_transactions()
        
        if verbose:
            print(f"💰 {transactions_effectuees} transaction(s) effectuée(s)")
        
        # Mettre à jour les statistiques
        self.tours_completes += 1
        self.tick_actuel += 1
        
        # Collecter les métriques
        self.collecter_metriques()
        
        # Pause entre les tours
        time.sleep(DUREE_PAUSE_ENTRE_TOURS)
        
        return {
            "tour": self.tours_completes,
            "tick": self.tick_actuel,
            "evenements": evenements,
            "transactions": transactions_effectuees,
            "statistiques": self.calculer_statistiques()
        }
    
    def simuler_transactions(self) -> int:
        """
        Simule les transactions entre entreprises et fournisseurs.
        
        Returns:
            Nombre de transactions effectuées
        """
        transactions_effectuees = 0
        entreprises = self.entreprise_repo.get_all()
        
        for entreprise in entreprises:
            if random.random() < PROBABILITE_SELECTION_ENTREPRISE:
                # Trouver des produits disponibles pour cette entreprise
                produits_disponibles = self.get_produits_disponibles_pour_entreprise(entreprise)
                
                if produits_disponibles:
                    # Simuler une transaction
                    produit = random.choice(produits_disponibles)
                    fournisseurs_avec_stock = [
                        f for f in self.fournisseur_repo.get_all()
                        if produit.id in f.stock_produit and f.stock_produit[produit.id] > 0
                    ]
                    
                    if fournisseurs_avec_stock:
                        fournisseur = random.choice(fournisseurs_avec_stock)
                        # Simuler l'achat (simplifié)
                        transactions_effectuees += 1
        
        return transactions_effectuees

    def run_simulation_tours(self, n_tours: int, verbose: bool = False) -> List[Dict[str, Any]]:
        """
        Lance la simulation sur un nombre défini de tours.
        
        Args:
            n_tours: Nombre de tours à simuler
            verbose: Afficher les détails
            
        Returns:
            Liste des résultats de chaque tour
        """
        print(f"🚀 Lancement de la simulation sur {n_tours} tours...")
        
        resultats = []
        for i in range(n_tours):
            resultat_tour = self.simulation_tour(verbose=verbose)
            resultats.append(resultat_tour)
            
            if verbose:
                stats = resultat_tour['statistiques']
                print(f"📊 Tour {i+1}/{n_tours} - Budget total: {stats['budget_total_actuel']:.2f}€")
        
        print(f"✅ Simulation terminée après {n_tours} tours")
        return resultats

    def run_simulation_infinite(self, verbose: bool = False):
        """
        Lance la simulation en boucle infinie.
        
        Args:
            verbose: Afficher les détails
        """
        print("🚀 Lancement de la simulation en mode infini...")
        
        try:
            while True:
                self.simulation_tour(verbose=verbose)
                
                # Afficher un résumé périodique
                if self.tours_completes % 10 == 0:
                    stats = self.calculer_statistiques()
                    print(f"📊 Tour {self.tours_completes} - Budget total: {stats['budget_total_actuel']:.2f}€")
                    
        except KeyboardInterrupt:
            print("\n⏹️ Simulation interrompue manuellement.")
            stats = self.calculer_statistiques()
            print(f"📊 Résumé final - Tours: {stats['tours_completes']}, Budget: {stats['budget_total_actuel']:.2f}€")

    def get_etat_actuel(self) -> Dict[str, Any]:
        """
        Retourne l'état actuel de la simulation.
        
        Returns:
            Dictionnaire contenant l'état actuel
        """
        return {
            "tick_actuel": self.tick_actuel,
            "tours_completes": self.tours_completes,
            "evenements_appliques": len(self.evenements_appliques),
            "statistiques": self.calculer_statistiques()
        }

    def get_produits_disponibles_pour_entreprise(self, entreprise: Entreprise) -> List[Produit]:
        """
        Retourne la liste des produits disponibles pour une entreprise.
        
        Args:
            entreprise: L'entreprise pour laquelle chercher les produits
            
        Returns:
            Liste des produits disponibles
        """
        produits_disponibles = []
        
        for produit in self.produit_repo.get_all():
            if not produit.actif:
                continue
                
            # Vérifier si au moins un fournisseur a ce produit en stock
            fournisseurs_avec_stock = [
                f for f in self.fournisseur_repo.get_all()
                if produit.id in f.stock_produit and f.stock_produit[produit.id] > 0
            ]
            
            if fournisseurs_avec_stock:
                produits_disponibles.append(produit)
        
        return produits_disponibles

    def afficher_etat(self):
        """Affiche l'état actuel de la simulation"""
        stats = self.calculer_statistiques()
        
        print("\n" + "="*50)
        print("📊 ÉTAT DE LA SIMULATION")
        print("="*50)
        print(f"Tours complétés: {stats['tours_completes']}")
        print(f"Événements appliqués: {stats['evenements_appliques']}")
        print(f"Budget total actuel: {stats['budget_total_actuel']:.2f}€")
        print(f"Nombre d'entreprises: {stats['nombre_entreprises']}")
        print(f"Produits actifs: {stats['nombre_produits_actifs']}")
        print(f"Fournisseurs: {stats['nombre_fournisseurs']}")
        print("="*50)


# Instance globale du service
simulation_service = SimulationService() 