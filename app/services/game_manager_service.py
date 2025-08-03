#!/usr/bin/env python3
"""
GameManagerService TradeSim - Gestion des templates et configuration
==================================================================

Ce service gère les templates de jeu, la configuration
et l'initialisation des données de simulation.

Refactorisation (02/08/2025) :
- Utilise les Repository pour l'accès aux données
- Code modulaire et testable
- Interface commune pour CLI et API

Auteur: Assistant IA
Date: 2024-08-02
"""

import json
import os
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
from models import Produit, TypeProduit, Fournisseur, Entreprise
from config import (
    RECHARGE_BUDGET_MIN, RECHARGE_BUDGET_MAX,
    REASSORT_QUANTITE_MIN, REASSORT_QUANTITE_MAX,
    INFLATION_POURCENTAGE_MIN, INFLATION_POURCENTAGE_MAX,
    PROBABILITE_DESACTIVATION, PROBABILITE_REACTIVATION,
    TICK_INTERVAL_EVENT, PROBABILITE_EVENEMENT,
    PROBABILITE_SELECTION_ENTREPRISE, DUREE_PAUSE_ENTRE_TOURS
)


class GameManagerService:
    """
    Service de gestion des templates et de la configuration TradeSim.
    
    Responsabilités :
    - Gérer les templates de jeu
    - Initialiser les données de simulation
    - Gérer la configuration
    - Fournir des statistiques de jeu
    """
    
    def __init__(self):
        """Initialise le service de gestion de jeu"""
        self.produit_repo = ProduitRepository()
        self.fournisseur_repo = FournisseurRepository()
        self.entreprise_repo = EntrepriseRepository()
        
        # Configuration par défaut
        self.default_config = {
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
        
        # Noms par défaut
        self.noms_entreprises = ["MagaToys", "BuildTech", "BioLogix"]
        self.pays_entreprises = ["France", "Allemagne", "Canada"]
        
        self.noms_fournisseurs = [
            ("PlancheCompagnie", "France"),
            ("TechDistrib", "Allemagne"),
            ("AsieImport", "Chine"),
            ("NordicTools", "Suède"),
            ("ElectroPlus", "Corée du Sud")
        ]
        
        self.noms_produits = [
            "Bois", "Acier", "Planches", "Ours en peluche", "Aspirateur",
            "Lampe", "Clavier", "Moniteur", "Chocolat", "Téléphone",
            "Vélo", "Chaise", "Table", "Sac à dos", "Batterie externe",
            "Câble USB", "Tapis de souris", "Tente", "Bureau", "Écouteurs"
        ]
        
        # Dossier des templates
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def reset_game(self):
        """
        Remet le jeu aux valeurs par défaut.
        
        Returns:
            True si le reset a réussi
        """
        try:
            # Vider tous les Repository
            self.produit_repo.clear()
            self.fournisseur_repo.clear()
            self.entreprise_repo.clear()
            
            # Générer les données par défaut
            self.generate_game_data(self.default_config)
            
            print("✅ Jeu remis à zéro avec succès")
            return True
        except Exception as e:
            print(f"❌ Erreur lors du reset du jeu: {e}")
            return False
    
    def generate_game_data(self, config: Dict[str, Any]):
        """
        Génère les données du jeu selon la configuration.
        
        Args:
            config: Configuration du jeu
        """
        # Génération des produits
        self.generate_produits(config["produits"])
        
        # Génération des fournisseurs
        self.generate_fournisseurs(config["fournisseurs"])
        
        # Génération des entreprises
        self.generate_entreprises(config["entreprises"])
    
    def generate_produits(self, config_produits: Dict[str, Any]):
        """
        Génère les produits selon la configuration.
        
        Args:
            config_produits: Configuration des produits
        """
        nombre_produits = config_produits["nombre"]
        prix_min = config_produits["prix_min"]
        prix_max = config_produits["prix_max"]
        actifs_min = config_produits["actifs_min"]
        actifs_max = config_produits["actifs_max"]
        
        # Nombre de produits actifs au début
        nb_produits_actifs = random.randint(actifs_min, actifs_max)
        
        # Vider le repository
        self.produit_repo.clear()
        
        for i in range(nombre_produits):
            nom = self.noms_produits[i] if i < len(self.noms_produits) else f"Produit_{i+1}"
            produit = Produit(
                id=i + 1,
                nom=nom,
                prix=round(random.uniform(prix_min, prix_max), 2),
                actif=(i < nb_produits_actifs),
                type=random.choice([TypeProduit.matiere_premiere, TypeProduit.consommable, TypeProduit.produit_fini])
            )
            self.produit_repo.add(produit)
    
    def generate_fournisseurs(self, config_fournisseurs: Dict[str, Any]):
        """
        Génère les fournisseurs selon la configuration.
        
        Args:
            config_fournisseurs: Configuration des fournisseurs
        """
        nombre_fournisseurs = config_fournisseurs["nombre"]
        produits_min = config_fournisseurs["produits_min"]
        produits_max = config_fournisseurs["produits_max"]
        stock_min = config_fournisseurs["stock_min"]
        stock_max = config_fournisseurs["stock_max"]
        
        # Vider le repository
        self.fournisseur_repo.clear()
        
        # Récupérer tous les produits disponibles
        produits_disponibles = self.produit_repo.get_all()
        
        for fid in range(1, nombre_fournisseurs + 1):
            nom, pays = self.noms_fournisseurs[fid-1] if fid-1 < len(self.noms_fournisseurs) else (f"Fournisseur_{fid}", "France")
            
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
                
                # Utilise le service centralisé de gestion des prix
                from .price_service import price_service
                price_service.set_prix_produit_fournisseur(produit.id, fid, prix_fournisseur)
            
            fournisseur = Fournisseur(
                id=fid,
                nom_entreprise=nom,
                pays=pays,
                stock_produit=stock_produit
            )
            self.fournisseur_repo.add(fournisseur)
    
    def generate_entreprises(self, config_entreprises: Dict[str, Any]):
        """
        Génère les entreprises selon la configuration.
        
        Args:
            config_entreprises: Configuration des entreprises
        """
        nombre_entreprises = config_entreprises["nombre"]
        budget_min = config_entreprises["budget_min"]
        budget_max = config_entreprises["budget_max"]
        strategies = config_entreprises["strategies"]
        types_preferes = config_entreprises["types_preferes"]
        
        # Vider le repository
        self.entreprise_repo.clear()
        
        for i in range(nombre_entreprises):
            nom = self.noms_entreprises[i] if i < len(self.noms_entreprises) else f"Entreprise_{i+1}"
            pays = self.pays_entreprises[i] if i < len(self.pays_entreprises) else "France"
            
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
            self.entreprise_repo.add(entreprise)
    
    def save_template(self, nom: str) -> bool:
        """
        Sauvegarde la configuration actuelle comme template.
        
        Args:
            nom: Nom du template
            
        Returns:
            True si la sauvegarde a réussi
        """
        try:
            config = self.get_current_config()
            
            template_path = os.path.join(self.templates_dir, f"{nom}.json")
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Template '{nom}' sauvegardé avec succès")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde du template '{nom}': {e}")
            return False
    
    def load_template(self, nom: str) -> bool:
        """
        Charge un template et l'applique.
        
        Args:
            nom: Nom du template
            
        Returns:
            True si le chargement a réussi
        """
        try:
            template_path = os.path.join(self.templates_dir, f"{nom}.json")
            
            if not os.path.exists(template_path):
                print(f"❌ Template '{nom}' non trouvé")
                return False
            
            with open(template_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Appliquer la configuration
            self.generate_game_data(config)
            
            print(f"✅ Template '{nom}' chargé et appliqué avec succès")
            return True
        except Exception as e:
            print(f"❌ Erreur lors du chargement du template '{nom}': {e}")
            return False
    
    def list_templates(self) -> List[str]:
        """
        Liste tous les templates disponibles.
        
        Returns:
            Liste des noms de templates
        """
        templates = []
        
        if os.path.exists(self.templates_dir):
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.json'):
                    templates.append(filename[:-5])  # Enlever l'extension .json
        
        return sorted(templates)
    
    def get_current_config(self) -> Dict[str, Any]:
        """
        Récupère la configuration actuelle du jeu.
        
        Returns:
            Configuration actuelle
        """
        entreprises = self.entreprise_repo.get_all()
        produits = self.produit_repo.get_all()
        fournisseurs = self.fournisseur_repo.get_all()
        
        return {
            "entreprises": {
                "nombre": len(entreprises),
                "budget_min": min([e.budget_initial for e in entreprises]) if entreprises else 1000,
                "budget_max": max([e.budget_initial for e in entreprises]) if entreprises else 3000,
                "strategies": list(set([e.strategie for e in entreprises])),
                "types_preferes": list(set([t.value for e in entreprises for t in e.types_preferes]))
            },
            "produits": {
                "nombre": len(produits),
                "prix_min": min([p.prix for p in produits]) if produits else 5.0,
                "prix_max": max([p.prix for p in produits]) if produits else 500.0,
                "actifs_min": 3,  # Valeur par défaut
                "actifs_max": 8,   # Valeur par défaut
                "types": list(set([p.type.value for p in produits]))
            },
            "fournisseurs": {
                "nombre": len(fournisseurs),
                "produits_min": min([len(f.stock_produit) for f in fournisseurs]) if fournisseurs else 3,
                "produits_max": max([len(f.stock_produit) for f in fournisseurs]) if fournisseurs else 8,
                "stock_min": min([min(f.stock_produit.values()) for f in fournisseurs if f.stock_produit]) if fournisseurs else 10,
                "stock_max": max([max(f.stock_produit.values()) for f in fournisseurs if f.stock_produit]) if fournisseurs else 200
            },
            "simulation": {
                "probabilite_selection": PROBABILITE_SELECTION_ENTREPRISE,
                "pause_entre_tours": DUREE_PAUSE_ENTRE_TOURS
            },
            "evenements": {
                "intervalle": TICK_INTERVAL_EVENT,
                "probabilites": {
                    "recharge_budget": 0.5,
                    "reassort": 0.5,
                    "inflation": 0.4,
                    "variation_disponibilite": 0.3
                },
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
    
    def get_game_summary(self) -> Dict[str, Any]:
        """
        Récupère un résumé complet du jeu actuel.
        
        Returns:
            Résumé du jeu
        """
        entreprises = self.entreprise_repo.get_all()
        produits = self.produit_repo.get_all()
        fournisseurs = self.fournisseur_repo.get_all()
        
        return {
            "entreprises": {
                "nombre": len(entreprises),
                "budgets": [e.budget for e in entreprises],
                "strategies": [e.strategie for e in entreprises],
                "pays": [e.pays for e in entreprises]
            },
            "produits": {
                "total": len(produits),
                "actifs": len([p for p in produits if p.actif]),
                "types": {t.value: len([p for p in produits if p.type == t]) for t in TypeProduit},
                "prix_moyen": sum(p.prix for p in produits) / len(produits) if produits else 0
            },
            "fournisseurs": {
                "nombre": len(fournisseurs),
                "pays": list(set(f.pays for f in fournisseurs)),
                "produits_moyen": sum(len(f.stock_produit) for f in fournisseurs) / len(fournisseurs) if fournisseurs else 0
            },
            "configuration": self.get_current_config()
        }


# Instance globale du service
game_manager_service = GameManagerService() 