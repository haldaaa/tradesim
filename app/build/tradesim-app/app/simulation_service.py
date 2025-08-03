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

Auteur: Assistant IA
Date: 2024-08-02
"""

import random
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
from models import Produit, Fournisseur, Entreprise, TypeProduit
from events.inflation import appliquer_inflation
from events.reassort import evenement_reassort
from events.recharge_budget import appliquer_recharge_budget
from events.variation_disponibilite import appliquer_variation_disponibilite
from config import (
    PROBABILITE_SELECTION_ENTREPRISE, DUREE_PAUSE_ENTRE_TOURS,
    TICK_INTERVAL_EVENT, PROBABILITE_EVENEMENT
)


class SimulationService:
    """
    Service d'orchestration de la simulation TradeSim.
    
    Responsabilités :
    - Gérer les tours de simulation
    - Orchestrer les événements
    - Maintenir l'état global
    - Fournir des statistiques
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
    
    def appliquer_evenements(self, tick: int) -> List[Dict[str, Any]]:
        """
        Applique les événements aléatoires selon la configuration.
        
        Args:
            tick: Le tick actuel de la simulation
            
        Returns:
            Liste des événements appliqués
        """
        evenements_appliques = []
        
        # Vérifier si un événement doit être appliqué
        if tick % TICK_INTERVAL_EVENT == 0 and random.random() < PROBABILITE_EVENEMENT:
            # Choisir un événement aléatoire
            evenements_disponibles = [
                ("inflation", appliquer_inflation),
                ("reassort", evenement_reassort),
                ("recharge_budget", appliquer_recharge_budget),
                ("variation_disponibilite", appliquer_variation_disponibilite)
            ]
            
            nom_evenement, fonction_evenement = random.choice(evenements_disponibles)
            
            try:
                resultat = fonction_evenement(tick)
                if resultat:
                    evenements_appliques.extend(resultat)
                    self.evenements_appliques.extend(resultat)
                    print(f"🎲 Événement '{nom_evenement}' appliqué au tick {tick}")
            except Exception as e:
                print(f"❌ Erreur lors de l'application de l'événement '{nom_evenement}': {e}")
        
        return evenements_appliques
    
    def simulation_tour(self, verbose: bool = False) -> Dict[str, Any]:
        """
        Exécute un tour de simulation complet.
        
        Args:
            verbose: Afficher les détails du tour
            
        Returns:
            Résumé du tour effectué
        """
        if verbose:
            print(f"\n🔄 TOUR {self.tours_completes + 1} - Tick {self.tick_actuel}")
            print("=" * 50)
        
        # Appliquer les événements
        evenements = self.appliquer_evenements(self.tick_actuel)
        
        # Sélectionner les entreprises pour ce tour
        entreprises = self.entreprise_repo.get_all()
        entreprises_selectionnees = []
        
        for entreprise in entreprises:
            if random.random() < PROBABILITE_SELECTION_ENTREPRISE:
                entreprises_selectionnees.append(entreprise)
        
        # Simuler les achats des entreprises sélectionnées
        transactions_effectuees = 0
        for entreprise in entreprises_selectionnees:
            if verbose:
                print(f"💰 {entreprise.nom} (Budget: {entreprise.budget:.2f}€)")
            
            # TODO: Implémenter la logique d'achat
            # Pour l'instant, on simule juste une transaction
            transactions_effectuees += 1
            
            if verbose:
                print(f"  ✅ Transaction simulée")
        
        # Mettre à jour les statistiques
        self.tours_completes += 1
        self.tick_actuel += 1
        self.statistiques["transactions_effectuees"] += transactions_effectuees
        
        # Calculer les nouvelles statistiques
        stats = self.calculer_statistiques()
        
        resultat_tour = {
            "tour": self.tours_completes,
            "tick": self.tick_actuel,
            "entreprises_selectionnees": len(entreprises_selectionnees),
            "transactions_effectuees": transactions_effectuees,
            "evenements_appliques": len(evenements),
            "statistiques": stats
        }
        
        if verbose:
            print(f"📊 Résumé du tour: {transactions_effectuees} transactions, {len(evenements)} événements")
            print("=" * 50)
        
        return resultat_tour
    
    def run_simulation_tours(self, n_tours: int, verbose: bool = False) -> List[Dict[str, Any]]:
        """
        Exécute une simulation sur un nombre défini de tours.
        
        Args:
            n_tours: Nombre de tours à exécuter
            verbose: Afficher les détails
            
        Returns:
            Liste des résultats de chaque tour
        """
        print(f"🚀 Lancement de la simulation sur {n_tours} tours...")
        
        resultats = []
        
        for tour in range(n_tours):
            resultat = self.simulation_tour(verbose)
            resultats.append(resultat)
            
            # Pause entre les tours
            if tour < n_tours - 1:  # Pas de pause après le dernier tour
                time.sleep(DUREE_PAUSE_ENTRE_TOURS)
        
        print(f"✅ Simulation terminée après {n_tours} tours")
        return resultats
    
    def run_simulation_infinite(self, verbose: bool = False):
        """
        Exécute une simulation en boucle infinie.
        
        Args:
            verbose: Afficher les détails
        """
        print("♾️ Lancement de la simulation en mode infini...")
        print("Appuyez sur Ctrl+C pour arrêter")
        
        try:
            while True:
                self.simulation_tour(verbose)
                time.sleep(DUREE_PAUSE_ENTRE_TOURS)
        except KeyboardInterrupt:
            print("\n⏹️ Simulation arrêtée par l'utilisateur")
            print(f"📊 Statistiques finales: {self.statistiques}")
    
    def get_etat_actuel(self) -> Dict[str, Any]:
        """
        Récupère l'état actuel de la simulation.
        
        Returns:
            État complet de la simulation
        """
        stats = self.calculer_statistiques()
        
        return {
            "tick_actuel": self.tick_actuel,
            "tours_completes": self.tours_completes,
            "statistiques": stats,
            "derniers_evenements": self.evenements_appliques[-10:] if self.evenements_appliques else []
        }
    
    def afficher_etat(self):
        """Affiche l'état actuel de la simulation"""
        etat = self.get_etat_actuel()
        
        print("\n" + "=" * 60)
        print("📊 ÉTAT DE LA SIMULATION")
        print("=" * 60)
        
        print(f"🔄 Tours complétés: {etat['tours_completes']}")
        print(f"⏰ Tick actuel: {etat['tick_actuel']}")
        print(f"🎲 Événements appliqués: {etat['statistiques']['evenements_appliques']}")
        print(f"💰 Budget total: {etat['statistiques']['budget_total_actuel']:.2f}€")
        print(f"🏢 Entreprises: {etat['statistiques']['nombre_entreprises']}")
        print(f"📦 Produits actifs: {etat['statistiques']['nombre_produits_actifs']}")
        print(f"🏪 Fournisseurs: {etat['statistiques']['nombre_fournisseurs']}")
        
        print("\n" + "=" * 60)


# Instance globale du service
simulation_service = SimulationService() 