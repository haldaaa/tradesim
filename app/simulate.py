import argparse
import time
import sys

# Ajouter le chemin parent pour les imports si nécessaire
if __name__ == "__main__" and __package__ is None:
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.simulateur import simulation_tour
from app.config import DUREE_PAUSE_ENTRE_TOURS


def run_simulation(n_tours: int = None, infinite: bool = False):
    """
    Lance la simulation sur un nombre défini de tours,
    ou en boucle infinie si 'infinite' est True.
    """
    print("🚀 Lancement de la simulation...\n")

    tick = 0
    try:
        while True:
            simulation_tour()
            tick += 1

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

    args = parser.parse_args()

    if args.tours and args.infinite:
        print("❌ Erreur : Ne pas utiliser --tours avec --infinite en même temps.")
        sys.exit(1)

    if args.infinite:
        run_simulation(infinite=True)
    elif args.tours:
        run_simulation(n_tours=args.tours)
    else:
        print("❌ Veuillez spécifier --tours <n> ou --infinite")
        sys.exit(1)
