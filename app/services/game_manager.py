#!/usr/bin/env python3
"""
Game Manager TradeSim - Gestion du jeu et des templates
=======================================================

Ce module gère la génération des données de jeu, les templates
et l'orchestration de la simulation.

Refactorisation (02/08/2025) :
- Utilise les Repository au lieu d'accès directs aux données
- Code plus modulaire et testable
- Interface commune pour CLI et API

Auteur: Assistant IA
Date: 2024-08-02
"""

import json
import os
import random
from typing import Dict, List, Any
from datetime import datetime

# Imports des Repository (nouvelle architecture)
from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
from models import Produit, TypeProduit, Fournisseur, Entreprise
from .simulateur import simulation_tour
from config import (
    RECHARGE_BUDGET_MIN, RECHARGE_BUDGET_MAX,
    REASSORT_QUANTITE_MIN, REASSORT_QUANTITE_MAX,
    INFLATION_POURCENTAGE_MIN, INFLATION_POURCENTAGE_MAX,
    PROBABILITE_DESACTIVATION, PROBABILITE_REACTIVATION,
    TICK_INTERVAL_EVENT, PROBABILITE_EVENEMENT,
    PROBABILITE_SELECTION_ENTREPRISE, DUREE_PAUSE_ENTRE_TOURS
)

# Initialisation des Repository
produit_repo = ProduitRepository()
fournisseur_repo = FournisseurRepository()
entreprise_repo = EntrepriseRepository()

# Configuration par défaut
DEFAULT_CONFIG = {
    "entreprises": {
        "nombre": 3,
        "budget_min": 1000,
        "budget_max": 3000,
        "strategies": ["moins_cher", "par_type"],
        "types_preferes": ["matiere_premiere", "consommable", "produit_fini"]
    },
    "produits": {
        "nombre": 20,
        "prix_min": 5.0,
        "prix_max": 500.0,
        "actifs_min": 3,
        "actifs_max": 8,
        "types": ["matiere_premiere", "consommable", "produit_fini"]
    },
    "fournisseurs": {
        "nombre": 5,
        "produits_min": 3,
        "produits_max": 8,
        "stock_min": 10,
        "stock_max": 200
    },
    "simulation": {
        "probabilite_selection": 0.3,
        "pause_entre_tours": 0.1
    },
    "evenements": {
        "intervalle": 20,
        "probabilites": {
            "recharge_budget": 0.5,
            "reassort": 0.5,
            "inflation": 0.4,
            "variation_disponibilite": 0.3
        },
        "recharge_budget": {
            "min": 200,
            "max": 600
        },
        "reassort": {
            "min": 10,
            "max": 50
        },
        "inflation": {
            "min": 30,
            "max": 60
        },
        "variation_disponibilite": {
            "desactivation": 0.1,
            "reactivation": 0.2
        }
    }
}

# Noms des entreprises et fournisseurs par défaut
NOMS_ENTREPRISES = ["MagaToys", "BuildTech", "BioLogix"]
PAYS_ENTREPRISES = ["France", "Allemagne", "Canada"]

NOMS_FOURNISSEURS = [
    ("PlancheCompagnie", "France"),
    ("TechDistrib", "Allemagne"),
    ("AsieImport", "Chine"),
    ("NordicTools", "Suède"),
    ("ElectroPlus", "Corée du Sud")
]

NOMS_PRODUITS = [
    "Bois", "Acier", "Planches", "Ours en peluche", "Aspirateur",
    "Lampe", "Clavier", "Moniteur", "Chocolat", "Téléphone",
    "Vélo", "Chaise", "Table", "Sac à dos", "Batterie externe",
    "Câble USB", "Tapis de souris", "Tente", "Bureau", "Écouteurs"
]

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

def reset_game():
    """
    Remet le jeu aux valeurs par défaut.
    
    Refactorisation (02/08/2025) :
    - Utilise les Repository au lieu d'accès directs aux données
    """
    # Vider tous les Repository
    produit_repo.clear()
    fournisseur_repo.clear()
    entreprise_repo.clear()
    
    print("✅ Jeu remis à zéro avec succès")

def generate_game_data(config: Dict[str, Any]):
    """
    Génère les données du jeu selon la configuration.
    
    Refactorisation (02/08/2025) :
    - Utilise les Repository au lieu d'accès directs aux données
    """
    # Génération des produits
    generate_produits(config["produits"])
    
    # Génération des fournisseurs
    generate_fournisseurs(config["fournisseurs"])
    
    # Génération des entreprises
    generate_entreprises(config["entreprises"])

def generate_produits(config_produits: Dict[str, Any]):
    """
    Génère les produits selon la configuration.
    
    Refactorisation (02/08/2025) :
    - Utilise ProduitRepository au lieu de fake_produits_db
    """
    nombre_produits = config_produits["nombre"]
    prix_min = config_produits["prix_min"]
    prix_max = config_produits["prix_max"]
    actifs_min = config_produits["actifs_min"]
    actifs_max = config_produits["actifs_max"]
    
    # Nombre de produits actifs au début
    nb_produits_actifs = random.randint(actifs_min, actifs_max)
    
    # Vider le repository
    produit_repo.clear()
    
    for i in range(nombre_produits):
        nom = NOMS_PRODUITS[i] if i < len(NOMS_PRODUITS) else f"Produit_{i+1}"
        produit = Produit(
            id=i + 1,
            nom=nom,
            prix=round(random.uniform(prix_min, prix_max), 2),
            actif=(i < nb_produits_actifs),
            type=random.choice([TypeProduit.matiere_premiere, TypeProduit.consommable, TypeProduit.produit_fini])
        )
        produit_repo.add(produit)

def generate_fournisseurs(config_fournisseurs: Dict[str, Any]):
    """
    Génère les fournisseurs selon la configuration.
    
    Refactorisation (02/08/2025) :
    - Utilise FournisseurRepository au lieu de fake_fournisseurs_db
    - Gestion des prix à migrer vers un service plus tard
    """
    nombre_fournisseurs = config_fournisseurs["nombre"]
    produits_min = config_fournisseurs["produits_min"]
    produits_max = config_fournisseurs["produits_max"]
    stock_min = config_fournisseurs["stock_min"]
    stock_max = config_fournisseurs["stock_max"]
    
    # Vider le repository
    fournisseur_repo.clear()
    
    # Récupérer tous les produits disponibles
    produits_disponibles = produit_repo.get_all()
    
    for fid in range(1, nombre_fournisseurs + 1):
        nom, pays = NOMS_FOURNISSEURS[fid-1] if fid-1 < len(NOMS_FOURNISSEURS) else (f"Fournisseur_{fid}", "France")
        
        stock_produit = {}
        nb_produits = random.randint(produits_min, produits_max)
        
        produits_attribués = random.sample(produits_disponibles, min(nb_produits, len(produits_disponibles)))
        
        for produit in produits_attribués:
            stock = random.randint(stock_min, stock_max)
            stock_produit[produit.id] = stock
            
            # Calcul d'un prix fournisseur spécifique
            prix_base = produit.prix
            facteur = random.uniform(0.9, 1.2) * (100 / (stock + 1))
            prix_fournisseur = round(prix_base * facteur, 2)
            
            # TODO: Migrer vers un service de gestion des prix
            # Pour l'instant, on utilise une variable globale
            from simulateur import set_prix_produit_fournisseur
            set_prix_produit_fournisseur(produit.id, fid, prix_fournisseur)
        
        fournisseur = Fournisseur(
            id=fid,
            nom_entreprise=nom,
            pays=pays,
            stock_produit=stock_produit
        )
        fournisseur_repo.add(fournisseur)

def generate_entreprises(config_entreprises: Dict[str, Any]):
    """
    Génère les entreprises selon la configuration.
    
    Refactorisation (02/08/2025) :
    - Utilise EntrepriseRepository au lieu de fake_entreprises_db
    """
    nombre_entreprises = config_entreprises["nombre"]
    budget_min = config_entreprises["budget_min"]
    budget_max = config_entreprises["budget_max"]
    strategies = config_entreprises["strategies"]
    types_preferes = config_entreprises["types_preferes"]
    
    # Vider le repository
    entreprise_repo.clear()
    
    for i in range(nombre_entreprises):
        nom = NOMS_ENTREPRISES[i] if i < len(NOMS_ENTREPRISES) else f"Entreprise_{i+1}"
        pays = PAYS_ENTREPRISES[i] if i < len(PAYS_ENTREPRISES) else "France"
        
        entreprise = Entreprise(
            id=i + 1,
            nom=nom,
            pays=pays,
            budget=random.randint(budget_min, budget_max),
            budget_initial=random.randint(budget_min, budget_max),
            types_preferes=random.sample([TypeProduit(t) for t in types_preferes], 
                                       min(2, len(types_preferes))),
            strategie=random.choice(strategies)
        )
        entreprise_repo.add(entreprise)

def save_template(nom: str):
    """Sauvegarde la configuration actuelle comme template"""
    config_actuelle = get_current_config()
    
    template = {
        "nom": nom,
        "date_creation": datetime.now().isoformat(),
        "config": config_actuelle
    }
    
    template_file = os.path.join(TEMPLATES_DIR, f"{nom}.json")
    with open(template_file, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Template '{nom}' sauvegardé !")

def load_template(nom: str):
    """Charge un template existant"""
    template_file = os.path.join(TEMPLATES_DIR, f"{nom}.json")
    
    if not os.path.exists(template_file):
        print(f"❌ Template '{nom}' non trouvé !")
        return False
    
    with open(template_file, "r", encoding="utf-8") as f:
        template = json.load(f)
    
    generate_game_data(template["config"])
    print(f"✅ Template '{nom}' chargé !")
    return True

def list_templates():
    """Liste tous les templates disponibles"""
    templates = []
    for file in os.listdir(TEMPLATES_DIR):
        if file.endswith(".json"):
            nom = file[:-5]  # Enlever .json
            template_file = os.path.join(TEMPLATES_DIR, file)
            with open(template_file, "r", encoding="utf-8") as f:
                template = json.load(f)
            templates.append((nom, template.get("date_creation", "Inconnue")))
    
    if not templates:
        print("📁 Aucun template disponible")
        return
    
    print("📁 Templates disponibles :")
    for nom, date in templates:
        print(f"  • {nom} (créé le {date[:10]})")

def get_current_config() -> Dict[str, Any]:
    """Récupère la configuration actuelle du jeu"""
    return {
        "entreprises": {
            "nombre": len(entreprise_repo.get_all()),
            "budget_min": min([e.budget_initial for e in entreprise_repo.get_all()]),
            "budget_max": max([e.budget_initial for e in entreprise_repo.get_all()]),
            "strategies": list(set([e.strategie for e in entreprise_repo.get_all()])),
            "types_preferes": list(set([t.value for e in entreprise_repo.get_all() for t in e.types_preferes]))
        },
        "produits": {
            "nombre": len(produit_repo.get_all()),
            "prix_min": min([p.prix for p in produit_repo.get_all()]),
            "prix_max": max([p.prix for p in produit_repo.get_all()]),
            "actifs_min": 3,  # Valeur par défaut
            "actifs_max": 8,   # Valeur par défaut
            "types": list(set([p.type.value for p in produit_repo.get_all()]))
        },
        "fournisseurs": {
            "nombre": len(fournisseur_repo.get_all()),
            "produits_min": min([len(f.stock_produit) for f in fournisseur_repo.get_all()]),
            "produits_max": max([len(f.stock_produit) for f in fournisseur_repo.get_all()]),
            "stock_min": min([min(f.stock_produit.values()) for f in fournisseur_repo.get_all() if f.stock_produit]),
            "stock_max": max([max(f.stock_produit.values()) for f in fournisseur_repo.get_all() if f.stock_produit])
        },
        "simulation": {
            "probabilite_selection": PROBABILITE_SELECTION_ENTREPRISE,
            "pause_entre_tours": DUREE_PAUSE_ENTRE_TOURS
        },
        "evenements": {
            "intervalle": TICK_INTERVAL_EVENT,
            "probabilites": PROBABILITE_EVENEMENT,
            "recharge_budget": {
                "min": RECHARGE_BUDGET_MIN,
                "max": RECHARGE_BUDGET_MAX
            },
            "reassort": {
                "min": REASSORT_QUANTITE_MIN,
                "max": REASSORT_QUANTITE_MAX
            },
            "inflation": {
                "min": INFLATION_POURCENTAGE_MIN,
                "max": INFLATION_POURCENTAGE_MAX
            },
            "variation_disponibilite": {
                "desactivation": PROBABILITE_DESACTIVATION,
                "reactivation": PROBABILITE_REACTIVATION
            }
        }
    } 

def interactive_new_game():
    """Menu pour nouvelle partie avec options"""
    print("\n🎮 NOUVELLE PARTIE")
    print("=" * 60)
    print("Choisissez une option :")
    print("  [1] Jouer avec la config par défaut")
    print("  [2] Créer une nouvelle config interactive")
    print("  [3] Charger une config existante")
    print("  [Q] Quitter")
    
    while True:
        choix = input("\nVotre choix [1/2/3/Q]: ").strip().lower()
        
        if choix in ['q', 'quitter', 'quit', 'exit']:
            print("❌ Annulé.")
            exit(0)
        elif choix == '1':
            # Jouer avec la config par défaut
            generate_game_data(DEFAULT_CONFIG)
            print("✅ Configuration par défaut chargée !")
            if ask_launch_game():
                launch_simulation()
            return
        elif choix == '2':
            # Créer une nouvelle config interactive
            create_interactive_config()
            return
        elif choix == '3':
            # Charger une config existante
            load_existing_config()
            return
        else:
            print("❌ Veuillez choisir 1, 2, 3 ou Q")

def create_interactive_config():
    """Configuration interactive d'une nouvelle partie"""
    print("\n🎮 CRÉATION D'UNE NOUVELLE CONFIG")
    print("=" * 60)
    
    config = DEFAULT_CONFIG.copy()
    
    # Configuration des entreprises
    print("\n🏢 ENTREPRISES")
    config["entreprises"]["nombre"] = ask_number("Nombre d'entreprises", 3, 1, 10)
    config["entreprises"]["budget_min"] = ask_number("Range budget entreprises (minimum en €)", 1000, 100, 10000)
    config["entreprises"]["budget_max"] = ask_number("Range budget entreprises (maximum en €)", 3000, config["entreprises"]["budget_min"], 20000)
    
    # Configuration des produits
    print("\n📦 PRODUITS")
    config["produits"]["nombre"] = ask_number("Nombre de produits", 20, 5, 50)
    config["produits"]["prix_min"] = ask_number("Range prix produits (minimum en €)", 5.0, 0.1, 1000.0, is_float=True)
    config["produits"]["prix_max"] = ask_number("Range prix produits (maximum en €)", 500.0, config["produits"]["prix_min"], 10000.0, is_float=True)
    config["produits"]["actifs_min"] = ask_number("Nombre minimum de produits actifs", 3, 1, config["produits"]["nombre"])
    config["produits"]["actifs_max"] = ask_number("Nombre maximum de produits actifs", 8, config["produits"]["actifs_min"], config["produits"]["nombre"])
    
    # Configuration des fournisseurs
    print("\n🏪 FOURNISSEURS")
    config["fournisseurs"]["nombre"] = ask_number("Nombre de fournisseurs", 5, 2, 15)
    config["fournisseurs"]["produits_min"] = ask_number("Produits minimum par fournisseur", 3, 1, config["produits"]["nombre"])
    config["fournisseurs"]["produits_max"] = ask_number("Produits maximum par fournisseur", 8, config["fournisseurs"]["produits_min"], config["produits"]["nombre"])
    config["fournisseurs"]["stock_min"] = ask_number("Stock minimum par produit", 10, 1, 1000)
    config["fournisseurs"]["stock_max"] = ask_number("Stock maximum par produit", 200, config["fournisseurs"]["stock_min"], 10000)
    
    # Configuration de la simulation
    print("\n⚙️ SIMULATION")
    config["simulation"]["probabilite_selection"] = ask_number("Probabilité de sélection des entreprises", 0.3, 0.1, 1.0, is_float=True)
    config["simulation"]["pause_entre_tours"] = ask_number("Pause entre tours (secondes)", 0.1, 0.0, 5.0, is_float=True)
    
    # Configuration des événements
    print("\n🎲 ÉVÉNEMENTS")
    config["evenements"]["intervalle"] = ask_number("Intervalle des événements (ticks)", 20, 5, 100)
    config["evenements"]["probabilites"]["recharge_budget"] = ask_number("Probabilité recharge budget", 0.5, 0.0, 1.0, is_float=True)
    config["evenements"]["probabilites"]["reassort"] = ask_number("Probabilité reassort", 0.5, 0.0, 1.0, is_float=True)
    config["evenements"]["probabilites"]["inflation"] = ask_number("Probabilité inflation", 0.4, 0.0, 1.0, is_float=True)
    config["evenements"]["probabilites"]["variation_disponibilite"] = ask_number("Probabilité variation disponibilité", 0.3, 0.0, 1.0, is_float=True)
    
    # Paramètres des événements
    print("\n📊 PARAMÈTRES DES ÉVÉNEMENTS")
    config["evenements"]["recharge_budget"]["min"] = ask_number("Recharge budget minimum (€)", 200, 10, 10000)
    config["evenements"]["recharge_budget"]["max"] = ask_number("Recharge budget maximum (€)", 600, config["evenements"]["recharge_budget"]["min"], 50000)
    config["evenements"]["reassort"]["min"] = ask_number("Reassort minimum (unités)", 10, 1, 1000)
    config["evenements"]["reassort"]["max"] = ask_number("Reassort maximum (unités)", 50, config["evenements"]["reassort"]["min"], 10000)
    config["evenements"]["inflation"]["min"] = ask_number("Inflation minimum (%)", 30, 1, 200)
    config["evenements"]["inflation"]["max"] = ask_number("Inflation maximum (%)", 60, config["evenements"]["inflation"]["min"], 500)
    config["evenements"]["variation_disponibilite"]["desactivation"] = ask_number("Probabilité désactivation produit", 0.1, 0.0, 1.0, is_float=True)
    config["evenements"]["variation_disponibilite"]["reactivation"] = ask_number("Probabilité réactivation produit", 0.2, 0.0, 1.0, is_float=True)
    
    # Générer la nouvelle partie
    generate_game_data(config)
    
    print("\n✅ Nouvelle partie configurée et générée !")
    
    # Demander si sauvegarder
    save = input("\n💾 Voulez-vous sauvegarder cette configuration ? [O]ui [N]on: ").lower()
    if save in ['o', 'oui', 'y', 'yes']:
        nom = input("Nom du template: ")
        if nom.strip():
            save_template(nom.strip())
    
    # Demander si lancer la partie
    if ask_launch_game():
        launch_simulation()

def load_existing_config():
    """Charge une config existante"""
    print("\n📁 CHARGEMENT D'UNE CONFIG EXISTANTE")
    print("=" * 60)
    
    # Lister les templates disponibles
    templates = []
    for file in os.listdir(TEMPLATES_DIR):
        if file.endswith(".json"):
            nom = file[:-5]  # Enlever .json
            templates.append(nom)
    
    if not templates:
        print("❌ Aucun template disponible.")
        print("💡 Créez d'abord une config avec l'option 2, puis sauvegardez-la.")
        return
    
    print("Templates disponibles :")
    for i, nom in enumerate(templates, 1):
        print(f"  [{i}] {nom}")
    
    while True:
        try:
            choix = input(f"\nChoisissez un template (1-{len(templates)}) ou [Q]uitter: ").strip().lower()
            
            if choix in ['q', 'quitter', 'quit', 'exit']:
                print("❌ Annulé.")
                return
            
            choix_int = int(choix)
            if 1 <= choix_int <= len(templates):
                nom_template = templates[choix_int - 1]
                if load_template(nom_template):
                    print("✅ Configuration chargée !")
                    if ask_launch_game():
                        launch_simulation()
                    return
                else:
                    print("❌ Erreur lors du chargement.")
                    return
            else:
                print(f"❌ Veuillez choisir un nombre entre 1 et {len(templates)}")
        except ValueError:
            print("❌ Veuillez entrer un nombre valide")

def ask_number(question: str, default: float, min_val: float, max_val: float, is_float: bool = False) -> float:
    """Demande interactivement un nombre avec options par défaut/random/choix/quitter"""
    while True:
        if is_float:
            print(f"{question} [D]éfaut({default}) [R]andom({min_val}-{max_val}) [C]hoix [Q]uitter: ", end="")
        else:
            print(f"{question} [D]éfaut({int(default)}) [R]andom({int(min_val)}-{int(max_val)}) [C]hoix [Q]uitter: ", end="")
        
        choix = input().strip().lower()
        
        if choix in ['q', 'quitter', 'quit', 'exit']:
            print("❌ Configuration annulée.")
            exit(0)
        elif choix in ['d', 'défaut', 'default']:
            return default
        elif choix in ['r', 'random']:
            if is_float:
                return round(random.uniform(min_val, max_val), 2)
            else:
                return random.randint(int(min_val), int(max_val))
        elif choix in ['c', 'choix']:
            try:
                valeur = float(input(f"Entrez une valeur ({min_val}-{max_val}): "))
                if min_val <= valeur <= max_val:
                    return valeur if is_float else int(valeur)
                else:
                    print(f"❌ La valeur doit être entre {min_val} et {max_val}")
            except ValueError:
                print("❌ Veuillez entrer un nombre valide")
        else:
            print("❌ Veuillez choisir [D], [R], [C] ou [Q]") 

def ask_launch_game() -> bool:
    """Demande si l'utilisateur veut lancer la simulation"""
    print("\n🚀 Voulez-vous lancer la simulation maintenant ?")
    print("  [1] Lancer la simulation")
    print("  [2] Retourner au menu principal")
    
    while True:
        choix = input("Votre choix [1/2]: ").strip()
        
        if choix == '1':
            return True
        elif choix == '2':
            print("✅ Configuration sauvegardée. Vous pouvez lancer la simulation plus tard avec --tours ou --infinite")
            return False
        else:
            print("❌ Veuillez choisir 1 ou 2")

def launch_simulation():
    """Lance la simulation interactive"""
    print("\n🎮 LANCEMENT DE LA SIMULATION")
    print("=" * 60)
    print("Choisissez le mode de simulation :")
    print("  [1] Nombre de tours spécifique (mode verbose)")
    print("  [2] Simulation infinie (mode verbose)")
    print("  [3] Mode silencieux (sans affichage détaillé)")
    print("  [Q] Retour au menu principal")
    
    while True:
        choix = input("\nVotre choix [1/2/3/Q]: ").strip().lower()
        
        if choix in ['q', 'quitter', 'quit', 'exit']:
            print("✅ Retour au menu principal.")
            return
        elif choix == '1':
            try:
                tours = int(input("Nombre de tours: "))
                if tours > 0:
                    show_game_summary(n_tours=tours)
                    print(f"\n🚀 Lancement de la simulation verbose pour {tours} tours...")
                    run_simulation_tours(tours, verbose=True)
                    return
                else:
                    print("❌ Le nombre de tours doit être positif")
            except ValueError:
                print("❌ Veuillez entrer un nombre valide")
        elif choix == '2':
            show_game_summary()
            print("\n🚀 Lancement de la simulation infinie (mode verbose)...")
            print("💡 Appuyez sur Ctrl+C pour arrêter")
            run_simulation_infinite(verbose=True)
            return
        elif choix == '3':
            print("\n🔇 Mode silencieux activé !")
            try:
                tours = int(input("Nombre de tours (ou 0 pour infini): "))
                if tours >= 0:
                    if tours == 0:
                        show_game_summary()
                        print(f"\n🚀 Lancement de la simulation silencieuse infinie...")
                        run_simulation_infinite(verbose=False)
                    else:
                        show_game_summary(n_tours=tours)
                        print(f"\n🚀 Lancement de la simulation silencieuse pour {tours} tours...")
                        run_simulation_tours(tours, verbose=False)
                    return
                else:
                    print("❌ Le nombre de tours doit être positif ou 0")
            except ValueError:
                print("❌ Veuillez entrer un nombre valide")
        else:
            print("❌ Veuillez choisir 1, 2, 3 ou Q") 

def run_simulation_tours(n_tours: int, verbose: bool = False):
    """Lance la simulation pour un nombre défini de tours"""
    import time
    
    print("🚀 Lancement de la simulation...\n")
    
    if verbose:
        print("📢 Mode parlant activé - Affichage en temps réel des événements\n")

    tick = 0
    try:
        while tick < n_tours:
            tick += 1
            
            if verbose:
                print(f"🔄 Tick {tick} - ", end="", flush=True)
            
            simulation_tour(verbose=verbose)
            
            if verbose:
                print("✅ Tour terminé")
            
            if tick < n_tours:  # Ne pas faire de pause après le dernier tour
                time.sleep(DUREE_PAUSE_ENTRE_TOURS)

    except KeyboardInterrupt:
        print("\n⏹️ Simulation interrompue manuellement.")

    print("✅ Simulation terminée.")

def run_simulation_infinite(verbose: bool = False):
    """Lance la simulation en boucle infinie"""
    import time
    
    print("🚀 Lancement de la simulation infinie...\n")
    
    if verbose:
        print("📢 Mode parlant activé - Affichage en temps réel des événements\n")

    tick = 0
    try:
        while True:
            tick += 1
            
            if verbose:
                print(f"🔄 Tick {tick} - ", end="", flush=True)
            
            simulation_tour(verbose=verbose)
            
            if verbose:
                print("✅ Tour terminé")
            
            time.sleep(DUREE_PAUSE_ENTRE_TOURS)

    except KeyboardInterrupt:
        print("\n⏹️ Simulation interrompue manuellement.")

    print("✅ Simulation terminée.") 

def show_game_summary(n_tours: int = None):
    """Affiche un résumé complet de la configuration du jeu"""
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DE LA CONFIGURATION DU JEU")
    print("=" * 80)
    
    # 1. Entreprises
    print("\n🏢 ENTREPRISES")
    print("┌" + "─" * 50 + "┐")
    print("│ {:<15} {:<10} {:<12} {:<12} │".format("Nom", "Pays", "Budget", "Stratégie"))
    print("├" + "─" * 50 + "┤")
    for entreprise in entreprise_repo.get_all():
        types_str = ", ".join([t.value for t in entreprise.types_preferes])
        print("│ {:<15} {:<10} {:<12} {:<12} │".format(
            entreprise.nom, 
            entreprise.pays, 
            f"{entreprise.budget:.2f}€",
            entreprise.strategie
        ))
    print("└" + "─" * 50 + "┘")
    
    # 2. Produits actifs
    produits_actifs = [p for p in produit_repo.get_all() if p.actif]
    print(f"\n📦 PRODUITS ACTIFS ({len(produits_actifs)})")
    print("┌" + "─" * 50 + "┐")
    print("│ {:<20} {:<12} {:<15} │".format("Nom", "Prix", "Type"))
    print("├" + "─" * 50 + "┤")
    for produit in produits_actifs:
        type_court = produit.type.value.replace("_", "")
        print("│ {:<20} {:<12} {:<15} │".format(
            produit.nom, 
            f"{produit.prix:.2f}€",
            type_court
        ))
    print("└" + "─" * 50 + "┘")
    
    # 3. Fournisseurs
    print(f"\n🏪 FOURNISSEURS ({len(fournisseur_repo.get_all())})")
    print("┌" + "─" * 80 + "┐")
    print("│ {:<20} {:<12} {:<45} │".format("Nom", "Pays", "Produits"))
    print("├" + "─" * 80 + "┤")
    for fournisseur in fournisseur_repo.get_all():
        produits_info = []
        for produit_id, stock in fournisseur.stock_produit.items():
            if stock > 0:  # Seulement les produits en stock
                produit = next(p for p in produit_repo.get_all() if p.id == produit_id)
                # Utiliser le service de gestion des prix
                from simulateur import get_prix_produit_fournisseur
                prix_fournisseur = get_prix_produit_fournisseur(produit_id, fournisseur.id)
                if prix_fournisseur:
                    produits_info.append(
                        f"{produit.nom} ({produit.prix:.2f}€ prix de base, {prix_fournisseur:.2f}€ prix fournisseur, {stock} en stock)"
                    )
                else:
                    produits_info.append(
                        f"{produit.nom} ({produit.prix:.2f}€ prix de base, prix non défini, {stock} en stock)"
                    )
        
        produits_str = ", ".join(produits_info) if produits_info else "Aucun produit en stock"
        
        # Gérer les longues lignes
        if len(produits_str) > 45:
            produits_str = produits_str[:42] + "..."
        
        print("│ {:<20} {:<12} {:<45} │".format(
            fournisseur.nom_entreprise,
            fournisseur.pays,
            produits_str
        ))
    print("└" + "─" * 80 + "┘")
    
    # 4. Configuration
    print(f"\n⚙️ CONFIGURATION")
    print("┌" + "─" * 80 + "┐")
    print("│ {:<35} {:<42} │".format("Paramètre", "Valeur"))
    print("├" + "─" * 80 + "┤")
    
    if n_tours:
        print("│ {:<35} {:<42} │".format("Nombre de tours choisi", f"{n_tours} tours"))
    
    print("│ {:<35} {:<42} │".format("Probabilité sélection", f"{PROBABILITE_SELECTION_ENTREPRISE*100:.0f}% ({PROBABILITE_SELECTION_ENTREPRISE})"))
    print("│ {:<35} {:<42} │".format("Pause entre tours", f"{DUREE_PAUSE_ENTRE_TOURS} secondes"))
    print("│ {:<35} {:<42} │".format("Intervalle événements", f"{TICK_INTERVAL_EVENT} ticks"))
    print("│ {:<35} {:<42} │".format("Recharge budget range", f"{RECHARGE_BUDGET_MIN}€ - {RECHARGE_BUDGET_MAX}€"))
    print("│ {:<35} {:<42} │".format("Reassort range", f"{REASSORT_QUANTITE_MIN} - {REASSORT_QUANTITE_MAX} unités"))
    print("│ {:<35} {:<42} │".format("Inflation range", f"{INFLATION_POURCENTAGE_MIN}% - {INFLATION_POURCENTAGE_MAX}%"))
    
    probas_str = f"Recharge:{PROBABILITE_EVENEMENT['recharge_budget']*100:.0f}%, Reassort:{PROBABILITE_EVENEMENT['reassort']*100:.0f}%, Inf:{PROBABILITE_EVENEMENT['inflation']*100:.0f}%, Var:{PROBABILITE_EVENEMENT['variation_disponibilite']*100:.0f}%"
    print("│ {:<35} {:<42} │".format("Probabilités événements", probas_str))
    
    print("└" + "─" + "─" * 78 + "┘")
    
    # 5. Résumé général
    print(f"\n📊 RÉSUMÉ GÉNÉRAL")
    print(f"• {len(entreprise_repo.get_all())} entreprises avec budgets {min([e.budget for e in entreprise_repo.get_all()]):.0f}€-{max([e.budget for e in entreprise_repo.get_all()]):.0f}€")
    print(f"• {len(fournisseur_repo.get_all())} fournisseurs proposant 3-8 produits chacun")
    print(f"• {len(produits_actifs)} produits actifs sur {len(produit_repo.get_all())} produits totaux")
    print(f"• {PROBABILITE_SELECTION_ENTREPRISE*100:.0f}% de chance de sélection par entreprise")
    print(f"• Événements tous les {TICK_INTERVAL_EVENT} ticks")
    
    if n_tours:
        print(f"• Simulation pour {n_tours} tours")
    
    print("=" * 80) 