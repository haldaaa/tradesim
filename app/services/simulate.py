#!/usr/bin/env python3
"""
Simulate TradeSim - Interface de simulation
==========================================

Ce module fournit l'interface de simulation pour TradeSim.
Il gère l'affichage du statut, le mode cheat et l'exécution
des simulations.

Refactorisation (02/08/2025) :
- Utilise les Repository au lieu d'accès directs aux données
- Code plus modulaire et testable
- Interface commune pour CLI et API

Monitoring (04/08/2025) :
- Intégration Prometheus/Grafana
- Option --with-metrics pour activer le monitoring
- Affichage du statut monitoring dans la configuration

Auteur: Assistant IA
Date: 2024-08-02
"""

import argparse
import sys
import time
import os
import threading

# Ajouter le chemin parent pour les imports si nécessaire
if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Imports des Repository (nouvelle architecture)
from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
from services.simulateur import simulation_tour
from config import DUREE_PAUSE_ENTRE_TOURS, METRICS_ENABLED, METRICS_EXPORTER_PORT
from services.game_manager import (
    reset_game, interactive_new_game, save_template, 
    load_template, list_templates
)
from services.game_state_service import game_state_service

# Import du monitoring
from monitoring.prometheus_exporter import PrometheusExporter, format_monitoring_status

# Initialisation des Repository
produit_repo = ProduitRepository()
fournisseur_repo = FournisseurRepository()
entreprise_repo = EntrepriseRepository()

# Variable globale pour l'exporter
exporter = None
exporter_thread = None

def afficher_configuration_actuelle():
    """
    Affiche la configuration actuelle incluant le statut du monitoring
    """
    print("\n" + "="*60)
    print("⚙️ CONFIGURATION ACTUELLE")
    print("="*60)
    print(f"Mode: CLI")
    print(f"Monitoring: {format_monitoring_status()}")
    if METRICS_ENABLED:
        print(f"Métriques: 5 actives")
        print(f"Stockage: logs/metrics.jsonl")
        print(f"Prometheus: http://localhost:9090")
        print(f"Grafana: http://localhost:3000")
    print("="*60)

def demarrer_monitoring():
    """
    Démarre l'exporter Prometheus dans un thread séparé
    """
    global exporter, exporter_thread
    
    if not METRICS_ENABLED:
        print("⚠️ Monitoring désactivé dans la configuration")
        return
    
    try:
        exporter = PrometheusExporter()
        exporter_thread = threading.Thread(target=exporter.start, daemon=True)
        exporter_thread.start()
        
        # Attendre un peu que l'exporter démarre
        time.sleep(2)
        print(f"✅ Monitoring démarré sur port {METRICS_EXPORTER_PORT}")
        
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du monitoring: {e}")

def arreter_monitoring():
    """
    Arrête l'exporter Prometheus
    """
    global exporter
    if exporter:
        print("🛑 Arrêt du monitoring...")
        # L'exporter s'arrêtera automatiquement quand le processus principal se termine

def afficher_status():
    """
    Affiche l'état des lieux : budgets des entreprises et prix/disponibilité des produits.
    
    Refactorisation (02/08/2025) :
    - Utilise les Repository au lieu d'accès directs aux données
    """
    print("\n" + "="*60)
    print("📊 ÉTAT DES LIEUX")
    print("="*60)
    
    # Budgets des entreprises
    print("\n💰 BUDGETS DES ENTREPRISES :")
    for entreprise in entreprise_repo.get_all():
        print(f"  • {entreprise.nom} ({entreprise.pays}) : {entreprise.budget:.2f}€")
    
    # Produits et leurs prix/disponibilité
    print("\n📦 PRODUITS ET PRIX :")
    for produit in produit_repo.get_all():
        if not produit.actif:
            continue
            
        print(f"\n  🏷️ {produit.nom} ({produit.type.value}) :")
        
        # Trouver les fournisseurs qui ont ce produit
        fournisseurs_avec_produit = [
            f for f in fournisseur_repo.get_all()
            if produit.id in f.stock_produit and f.stock_produit[produit.id] > 0
        ]
        
        if not fournisseurs_avec_produit:
            print(f"    ❌ Indisponible (aucun stock)")
            continue
            
        for fournisseur in fournisseurs_avec_produit:
            stock = fournisseur.stock_produit[produit.id]
            
            # Utiliser le service de gestion des prix
            import services.price_service
            prix = services.price_service.price_service.get_prix_produit_fournisseur(produit.id, fournisseur.id)
            
            # Debug: voir pourquoi prix est None
            if prix is None:
                print(f"    🔍 DEBUG: Prix None pour produit {produit.id}, fournisseur {fournisseur.id}")
                # Vérifier si le prix existe dans le stockage
                print(f"    🔍 DEBUG: Stockage contient {len(services.price_service.price_service._prix_stockage)} prix")
                print(f"    🔍 DEBUG: Clé ({produit.id}, {fournisseur.id}) dans stockage: {((produit.id, fournisseur.id)) in services.price_service.price_service._prix_stockage}")
            
            # Si le prix n'est pas défini, utiliser un prix par défaut (comme dans l'API)
            if prix is None:
                prix = 100.0  # Prix par défaut
                print(f"    ⚠️ {fournisseur.nom_entreprise} : {prix:.2f}€ (stock: {stock}) - Prix par défaut")
            else:
                print(f"    ✅ {fournisseur.nom_entreprise} : {prix:.2f}€ (stock: {stock})")
    
    print("\n" + "="*60)


def mode_cheat():
    """
    Mode cheat pour ajouter de l'argent à une entreprise.
    
    Refactorisation (02/08/2025) :
    - Utilise EntrepriseRepository au lieu d'accès direct aux données
    """
    print("\n" + "="*60)
    print("🎮 MODE CHEAT - AJOUT D'ARGENT")
    print("="*60)
    
    # Afficher les entreprises disponibles
    entreprises = entreprise_repo.get_all()
    print("\nEntreprises disponibles :")
    for i, entreprise in enumerate(entreprises, 1):
        print(f"  {i}. {entreprise.nom} ({entreprise.pays}) - Budget actuel : {entreprise.budget:.2f}€")
    
    # Demander à l'utilisateur de choisir
    while True:
        try:
            choix = input(f"\nChoisissez une entreprise (1-{len(entreprises)}) ou 'q' pour quitter : ")
            if choix.lower() == 'q':
                print("Mode cheat annulé.")
                return
            
            choix_int = int(choix)
            if 1 <= choix_int <= len(entreprises):
                entreprise = entreprises[choix_int - 1]
                ancien_budget = entreprise.budget
                entreprise.budget += 5000
                
                # Mettre à jour dans le repository
                entreprise_repo.update(entreprise)
                
                print(f"\n✅ {entreprise.nom} : {ancien_budget:.2f}€ → {entreprise.budget:.2f}€ (+5000€)")
                break
            else:
                print("❌ Choix invalide. Veuillez choisir un numéro valide.")
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")


def run_simulation(n_tours: int = None, infinite: bool = False, verbose: bool = False, with_metrics: bool = False):
    """
    Lance la simulation sur un nombre défini de tours,
    ou en boucle infinie si 'infinite' est True.
    
    Refactorisation (02/08/2025) :
    - Utilise SimulationService pour une logique cohérente
    
    Monitoring (04/08/2025) :
    - Intégration avec l'exporter Prometheus
    - Mise à jour des métriques pendant la simulation
    """
    print("🚀 Lancement de la simulation...\n")
    
    if verbose:
        print("📢 Mode parlant activé - Affichage en temps réel des événements\n")

    # Démarrer le monitoring si demandé
    if with_metrics:
        demarrer_monitoring()
        afficher_configuration_actuelle()

    # Utiliser SimulationService au lieu de simulation_tour
    from services.simulation_service import SimulationService
    simulation_service = SimulationService()
    
    try:
        if infinite:
            simulation_service.run_simulation_infinite(verbose=verbose)
        else:
            simulation_service.run_simulation_tours(n_tours, verbose=verbose)

    except KeyboardInterrupt:
        print("\n⏹️ Simulation interrompue manuellement.")

    finally:
        # Arrêter le monitoring si il était actif
        if with_metrics:
            arreter_monitoring()

    print("✅ Simulation terminée.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lancer la simulation TradeSim")
    parser.add_argument("--tours", type=int, help="Nombre de tours à simuler")
    parser.add_argument("--infinite", action="store_true", help="Lancer la simulation indéfiniment")
    parser.add_argument("--verbose", action="store_true", help="Mode parlant - Affiche les événements en temps réel")
    parser.add_argument("--status", action="store_true", help="Afficher l'état des lieux (budgets et prix)")
    parser.add_argument("--cheat", action="store_true", help="Mode cheat - Ajouter 5000€ à une entreprise")
    parser.add_argument("--reset", action="store_true", help="Remettre le jeu aux valeurs par défaut")
    parser.add_argument("--new-game", action="store_true", help="Configuration interactive d'une nouvelle partie")
    parser.add_argument("--save-template", type=str, help="Sauvegarder la configuration actuelle comme template")
    parser.add_argument("--load-template", type=str, help="Charger un template existant")
    parser.add_argument("--list-templates", action="store_true", help="Lister tous les templates disponibles")
    parser.add_argument("--with-metrics", action="store_true", help="Activer le monitoring Prometheus/Grafana")

    args = parser.parse_args()
    
    # Essayer de charger l'état du jeu au démarrage
    try:
        latest_file = game_state_service.get_latest_game_file()
        if latest_file:
            game_state_service.load_game_state(latest_file)
    except Exception as e:
        print(f"⚠️ Impossible de charger l'état du jeu: {e}")

    # Gestion des modes spéciaux
    if args.status:
        afficher_status()
        sys.exit(0)
    
    if args.cheat:
        mode_cheat()
        sys.exit(0)
    
    if args.reset:
        reset_game()
        sys.exit(0)
    
    if args.new_game:
        interactive_new_game()
        sys.exit(0)
    
    if args.save_template:
        save_template(args.save_template)
        sys.exit(0)
    
    if args.load_template:
        if load_template(args.load_template):
            sys.exit(0)
        else:
            sys.exit(1)
    
    if args.list_templates:
        list_templates()
        sys.exit(0)

    # Vérification des arguments de simulation
    if args.tours and args.infinite:
        print("❌ Erreur : Ne pas utiliser --tours avec --infinite en même temps.")
        sys.exit(1)

    if args.infinite:
        run_simulation(infinite=True, verbose=args.verbose, with_metrics=args.with_metrics)
    elif args.tours:
        run_simulation(n_tours=args.tours, verbose=args.verbose, with_metrics=args.with_metrics)
    else:
        print("❌ Veuillez spécifier --tours <n> ou --infinite")
        sys.exit(1)
