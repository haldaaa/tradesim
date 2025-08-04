#!/usr/bin/env python3
"""
Game State Service TradeSim - Gestion de la persistance de l'état du jeu
=======================================================================

Ce service gère la sauvegarde et le chargement de l'état complet du jeu
dans des fichiers JSON pour assurer la persistance entre les commandes CLI
et faciliter la transition vers le mode Web.

Responsabilités :
- Sauvegarder l'état complet (produits, fournisseurs, entreprises, prix)
- Charger l'état depuis un fichier JSON
- Gérer les erreurs de corruption de fichiers
- Assurer la cohérence des données

Auteur: Assistant IA
Date: 2025-08-04
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

# Imports des modèles et repositories
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models import Produit, Fournisseur, Entreprise, TypeProduit
from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
from services.price_service import price_service


class GameStateService:
    """
    Service pour la gestion de la persistance de l'état du jeu.
    
    Sauvegarde et charge l'état complet du jeu dans des fichiers JSON
    pour assurer la persistance entre les commandes CLI.
    """
    
    def __init__(self):
        """Initialise le service avec les repositories nécessaires."""
        self.produit_repo = ProduitRepository()
        self.fournisseur_repo = FournisseurRepository()
        self.entreprise_repo = EntrepriseRepository()
        self.data_dir = Path("data")
        
        # Créer le dossier data s'il n'existe pas
        self.data_dir.mkdir(exist_ok=True)
    
    def save_game_state(self, filename: Optional[str] = None) -> str:
        """
        Sauvegarde l'état complet du jeu dans un fichier JSON.
        
        Args:
            filename: Nom du fichier (optionnel, généré automatiquement si None)
            
        Returns:
            Le nom du fichier créé
            
        Raises:
            Exception: Si erreur lors de la sauvegarde
        """
        try:
            # Supprimer tous les anciens fichiers de partie
            self._cleanup_old_game_files()
            
            # Générer le nom de fichier si non fourni
            if filename is None:
                filename = "partie_active.json"
            
            filepath = self.data_dir / filename
            
            # Récupérer toutes les données
            produits = self.produit_repo.get_all()
            fournisseurs = self.fournisseur_repo.get_all()
            entreprises = self.entreprise_repo.get_all()
            
            # Récupérer les prix depuis le PriceService
            prix_data = {}
            for produit in produits:
                for fournisseur in fournisseurs:
                    if produit.id in fournisseur.stock_produit:
                        prix = price_service.get_prix_produit_fournisseur(produit.id, fournisseur.id)
                        if prix is not None:
                            prix_data[f"{produit.id}_{fournisseur.id}"] = prix
            
            # Construire l'état complet
            game_state = {
                "metadata": {
                    "date_creation": datetime.now(timezone.utc).isoformat(),
                    "version": "0.1"
                },
                "produits": [produit.model_dump() for produit in produits],
                "fournisseurs": [fournisseur.model_dump() for fournisseur in fournisseurs],
                "entreprises": [entreprise.model_dump() for entreprise in entreprises],
                "prix": prix_data
            }
            
            # Sauvegarder dans le fichier JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=2, ensure_ascii=False)
            
            print(f"✅ État du jeu sauvegardé dans {filepath}")
            return str(filepath)
            
        except Exception as e:
            error_msg = f"[SYSTEME] Erreur lors de la sauvegarde de l'état du jeu: {e}"
            print(error_msg)
            raise Exception(error_msg)
    
    def load_game_state(self, filename: str) -> bool:
        """
        Charge l'état du jeu depuis un fichier JSON.
        
        Args:
            filename: Nom du fichier à charger
            
        Returns:
            True si chargement réussi, False sinon
            
        Raises:
            Exception: Si erreur lors du chargement
        """
        try:
            filepath = self.data_dir / filename
            
            if not filepath.exists():
                raise FileNotFoundError(f"Fichier {filepath} introuvable")
            
            # Charger le JSON
            with open(filepath, 'r', encoding='utf-8') as f:
                game_state = json.load(f)
            
            # Valider la structure
            required_keys = ["metadata", "produits", "fournisseurs", "entreprises", "prix"]
            for key in required_keys:
                if key not in game_state:
                    raise ValueError(f"Clé manquante dans le JSON: {key}")
            
            # Vider les repositories existants
            self.produit_repo.clear()
            self.fournisseur_repo.clear()
            self.entreprise_repo.clear()
            price_service.reset()
            
            # Charger les produits
            for produit_data in game_state["produits"]:
                produit = Produit(**produit_data)
                self.produit_repo.add(produit)
            
            # Charger les fournisseurs
            for fournisseur_data in game_state["fournisseurs"]:
                fournisseur = Fournisseur(**fournisseur_data)
                self.fournisseur_repo.add(fournisseur)
            
            # Charger les entreprises
            for entreprise_data in game_state["entreprises"]:
                entreprise = Entreprise(**entreprise_data)
                self.entreprise_repo.add(entreprise)
            
            # Charger les prix
            for prix_key, prix_value in game_state["prix"].items():
                produit_id, fournisseur_id = map(int, prix_key.split("_"))
                price_service.set_prix_produit_fournisseur_force(produit_id, fournisseur_id, prix_value)
            
            print(f"✅ État du jeu chargé depuis {filepath}")
            return True
            
        except Exception as e:
            error_msg = f"[SYSTEME] Erreur lors du chargement de l'état du jeu: {e}"
            print(error_msg)
            raise Exception(error_msg)
    
    def get_latest_game_file(self) -> Optional[str]:
        """
        Trouve le fichier de partie active.
        
        Returns:
            Le nom du fichier de partie active, ou None si aucun trouvé
        """
        try:
            active_file = self.data_dir / "partie_active.json"
            if active_file.exists():
                return "partie_active.json"
            return None
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la recherche du fichier de partie active: {e}")
            return None
    
    def _cleanup_old_game_files(self) -> None:
        """
        Supprime tous les anciens fichiers de partie pour ne garder qu'une seule partie active.
        """
        try:
            for file_path in self.data_dir.glob("partie_*.json"):
                if file_path.name != "partie_active.json":
                    file_path.unlink()
                    print(f"🗑️ Fichier ancien supprimé: {file_path.name}")
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage des anciens fichiers: {e}")
    
    def delete_game_file(self, filename: str) -> bool:
        """
        Supprime un fichier de partie.
        
        Args:
            filename: Nom du fichier à supprimer
            
        Returns:
            True si suppression réussie, False sinon
        """
        try:
            filepath = self.data_dir / filename
            if filepath.exists():
                filepath.unlink()
                print(f"✅ Fichier {filename} supprimé")
                return True
            else:
                print(f"⚠️ Fichier {filename} introuvable")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de {filename}: {e}")
            return False


# Instance globale du service
game_state_service = GameStateService() 