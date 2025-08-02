import argparse
import sys
import time
import os

# Ajouter le chemin parent pour les imports si nécessaire
if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.simulateur import simulation_tour
from app.data import fake_entreprises_db, fake_produits_db, fake_fournisseurs_db, prix_par_fournisseur
from app.config import DUREE_PAUSE_ENTRE_TOURS
from app.game_manager import (
    reset_game, interactive_new_game, save_template, 
    load_template, list_templates
)

def afficher_status():
    """Affiche l'état des lieux : budgets des entreprises et prix/disponibilité des produits"""
    print("\n" + "="*60)
    print("📊 ÉTAT DES LIEUX")
    print("="*60)
    
    # Budgets des entreprises
    print("\n💰 BUDGETS DES ENTREPRISES :")
    for entreprise in fake_entreprises_db:
        print(f"  • {entreprise.nom} ({entreprise.pays}) : {entreprise.budget:.2f}€")
    
    # Produits et leurs prix/disponibilité
    print("\n📦 PRODUITS ET PRIX :")
    for produit in fake_produits_db:
        if not produit.actif:
            continue
            
        print(f"\n  🏷️ {produit.nom} ({produit.type.value}) :")
        
        # Trouver les fournisseurs qui ont ce produit
        fournisseurs_avec_produit = [
            f for f in fake_fournisseurs_db
            if produit.id in f.stock_produit and f.stock_produit[produit.id] > 0
        ]
        
        if not fournisseurs_avec_produit:
            print(f"    ❌ Indisponible (aucun stock)")
            continue
            
        for fournisseur in fournisseurs_avec_produit:
            stock = fournisseur.stock_produit[produit.id]
            prix_cle = (produit.id, fournisseur.id)
            
            if prix_cle in prix_par_fournisseur:
                prix = prix_par_fournisseur[prix_cle]
                print(f"    ✅ {fournisseur.nom_entreprise} : {prix:.2f}€ (stock: {stock})")
            else:
                print(f"    ⚠️ {fournisseur.nom_entreprise} : Prix non défini (stock: {stock})")
    
    print("\n" + "="*60)


def mode_cheat():
    """Mode cheat pour ajouter de l'argent à une entreprise"""
    print("\n" + "="*60)
    print("🎮 MODE CHEAT - AJOUT D'ARGENT")
    print("="*60)
    
    # Afficher les entreprises disponibles
    print("\nEntreprises disponibles :")
    for i, entreprise in enumerate(fake_entreprises_db, 1):
        print(f"  {i}. {entreprise.nom} ({entreprise.pays}) - Budget actuel : {entreprise.budget:.2f}€")
    
    # Demander à l'utilisateur de choisir
    while True:
        try:
            choix = input(f"\nChoisissez une entreprise (1-{len(fake_entreprises_db)}) ou 'q' pour quitter : ")
            if choix.lower() == 'q':
                print("Mode cheat annulé.")
                return
            
            choix_int = int(choix)
            if 1 <= choix_int <= len(fake_entreprises_db):
                entreprise = fake_entreprises_db[choix_int - 1]
                ancien_budget = entreprise.budget
                entreprise.budget += 5000
                print(f"\n✅ {entreprise.nom} : {ancien_budget:.2f}€ → {entreprise.budget:.2f}€ (+5000€)")
                break
            else:
                print("❌ Choix invalide. Veuillez choisir un numéro valide.")
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")


def run_simulation(n_tours: int = None, infinite: bool = False, verbose: bool = False):
    """
    Lance la simulation sur un nombre défini de tours,
    ou en boucle infinie si 'infinite' est True.
    """
    print("🚀 Lancement de la simulation...\n")
    
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
            
            if not infinite and tick >= n_tours:
                break

            time.sleep(DUREE_PAUSE_ENTRE_TOURS)

    except KeyboardInterrupt:
        print("\n⏹️ Simulation interrompue manuellement.")

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

    args = parser.parse_args()

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
        run_simulation(infinite=True, verbose=args.verbose)
    elif args.tours:
        run_simulation(n_tours=args.tours, verbose=args.verbose)
    else:
        print("❌ Veuillez spécifier --tours <n> ou --infinite")
        sys.exit(1)
