#!/usr/bin/env python3
"""
Name Manager TradeSim - Gestion des noms uniques pour TradeSim
=============================================================

Ce module gère la sélection aléatoire de noms pour les entités TradeSim
sans doublons dans une même partie.

Responsabilités :
- Sélection aléatoire d'entreprises, fournisseurs et produits
- Gestion des doublons par session de jeu
- Réinitialisation des noms utilisés pour nouvelle partie
- Interface simple pour la génération de données

Utilisation :
- Importé par data.py pour la génération de données
- Utilisé par GameManager pour les nouvelles parties
- Reset automatique à chaque nouvelle partie

Auteur: Assistant IA
Date: 2025-01-27
"""

import random
from typing import Dict, List, Optional
from data.names_data import ENTREPRISES_DATA, FOURNISSEURS_DATA, PRODUITS_DATA


class NameManager:
    """
    Gestionnaire de noms pour TradeSim.
    
    Responsabilités :
    - Sélection aléatoire de noms sans doublons
    - Gestion des noms utilisés par session
    - Réinitialisation pour nouvelles parties
    
    Attributs :
    - used_entreprises : Set des noms d'entreprises utilisés
    - used_fournisseurs : Set des noms de fournisseurs utilisés
    - used_produits : Set des noms de produits utilisés
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire de noms.
        
        Crée des sets vides pour tracker les noms utilisés
        dans la session actuelle.
        """
        self.used_entreprises = set()
        self.used_fournisseurs = set()
        self.used_produits = set()
    
    def reset(self):
        """
        Réinitialise tous les noms utilisés.
        
        Appelé au début d'une nouvelle partie pour permettre
        la réutilisation de tous les noms disponibles.
        """
        self.used_entreprises.clear()
        self.used_fournisseurs.clear()
        self.used_produits.clear()
    
    def get_unique_entreprise(self) -> Dict[str, str]:
        """
        Sélectionne une entreprise aléatoire non utilisée.
        
        Returns:
            Dict[str, str]: Dictionnaire avec nom, pays, continent
            
        Raises:
            ValueError: Si plus d'entreprises disponibles
        """
        available = [e for e in ENTREPRISES_DATA if e["nom"] not in self.used_entreprises]
        
        if not available:
            raise ValueError("Plus d'entreprises disponibles dans la base de données")
        
        selected = random.choice(available)
        self.used_entreprises.add(selected["nom"])
        return selected
    
    def get_unique_fournisseur(self) -> Dict[str, str]:
        """
        Sélectionne un fournisseur aléatoire non utilisé.
        
        Returns:
            Dict[str, str]: Dictionnaire avec nom, pays, continent
            
        Raises:
            ValueError: Si plus de fournisseurs disponibles
        """
        available = [f for f in FOURNISSEURS_DATA if f["nom"] not in self.used_fournisseurs]
        
        if not available:
            raise ValueError("Plus de fournisseurs disponibles dans la base de données")
        
        selected = random.choice(available)
        self.used_fournisseurs.add(selected["nom"])
        return selected
    
    def get_unique_produit(self, type_produit: Optional[str] = None) -> Dict[str, str]:
        """
        Sélectionne un produit aléatoire non utilisé.
        
        Args:
            type_produit (Optional[str]): Type de produit spécifique
                Si None, sélectionne parmi tous les types
                Valeurs possibles : "produit_fini", "consommable", "matiere_premiere"
        
        Returns:
            Dict[str, str]: Dictionnaire avec nom, type
            
        Raises:
            ValueError: Si plus de produits disponibles pour le type demandé
        """
        if type_produit:
            available = [p for p in PRODUITS_DATA 
                        if p["type"] == type_produit and p["nom"] not in self.used_produits]
        else:
            available = [p for p in PRODUITS_DATA if p["nom"] not in self.used_produits]
        
        if not available:
            if type_produit:
                raise ValueError(f"Plus de produits de type '{type_produit}' disponibles")
            else:
                raise ValueError("Plus de produits disponibles dans la base de données")
        
        selected = random.choice(available)
        self.used_produits.add(selected["nom"])
        return selected
    
    def get_multiple_entreprises(self, count: int) -> List[Dict[str, str]]:
        """
        Sélectionne plusieurs entreprises aléatoires non utilisées.
        
        Args:
            count (int): Nombre d'entreprises à sélectionner
            
        Returns:
            List[Dict[str, str]]: Liste d'entreprises sélectionnées
            
        Raises:
            ValueError: Si pas assez d'entreprises disponibles
        """
        if count > len(ENTREPRISES_DATA):
            raise ValueError(f"Demande de {count} entreprises mais seulement {len(ENTREPRISES_DATA)} disponibles")
        
        selected = []
        for _ in range(count):
            selected.append(self.get_unique_entreprise())
        
        return selected
    
    def get_multiple_fournisseurs(self, count: int) -> List[Dict[str, str]]:
        """
        Sélectionne plusieurs fournisseurs aléatoires non utilisés.
        
        Args:
            count (int): Nombre de fournisseurs à sélectionner
            
        Returns:
            List[Dict[str, str]]: Liste de fournisseurs sélectionnés
            
        Raises:
            ValueError: Si pas assez de fournisseurs disponibles
        """
        if count > len(FOURNISSEURS_DATA):
            raise ValueError(f"Demande de {count} fournisseurs mais seulement {len(FOURNISSEURS_DATA)} disponibles")
        
        selected = []
        for _ in range(count):
            selected.append(self.get_unique_fournisseur())
        
        return selected
    
    def get_multiple_produits(self, count: int, type_produit: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Sélectionne plusieurs produits aléatoires non utilisés.
        
        Args:
            count (int): Nombre de produits à sélectionner
            type_produit (Optional[str]): Type de produit spécifique
            
        Returns:
            List[Dict[str, str]]: Liste de produits sélectionnés
            
        Raises:
            ValueError: Si pas assez de produits disponibles
        """
        if type_produit:
            available_count = len([p for p in PRODUITS_DATA if p["type"] == type_produit])
            if count > available_count:
                raise ValueError(f"Demande de {count} produits de type '{type_produit}' mais seulement {available_count} disponibles")
        else:
            if count > len(PRODUITS_DATA):
                raise ValueError(f"Demande de {count} produits mais seulement {len(PRODUITS_DATA)} disponibles")
        
        selected = []
        for _ in range(count):
            selected.append(self.get_unique_produit(type_produit))
        
        return selected
    
    def get_stats(self) -> Dict[str, int]:
        """
        Retourne les statistiques d'utilisation des noms.
        
        Returns:
            Dict[str, int]: Statistiques d'utilisation
        """
        return {
            "entreprises_utilisees": len(self.used_entreprises),
            "entreprises_disponibles": len(ENTREPRISES_DATA),
            "fournisseurs_utilises": len(self.used_fournisseurs),
            "fournisseurs_disponibles": len(FOURNISSEURS_DATA),
            "produits_utilises": len(self.used_produits),
            "produits_disponibles": len(PRODUITS_DATA)
        }


# Instance globale pour utilisation dans l'application
name_manager = NameManager() 