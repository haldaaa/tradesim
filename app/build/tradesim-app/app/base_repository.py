#!/usr/bin/env python3
"""
Base Repository - Interface commune pour l'accès aux données
==========================================================

Ce fichier définit l'interface commune pour tous les Repository de TradeSim.
L'interface commune permet d'avoir un code identique pour CLI et Web,
avec des implémentations différentes (In-memory pour les tests, SQL pour la prod).

Auteur: Assistant IA
Date: 2024-08-02
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from models import Produit, Fournisseur, Entreprise, TypeProduit

# Type générique pour les entités
T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """
    Interface commune pour tous les Repository.
    
    Cette classe abstraite définit les méthodes CRUD de base que tous
    les Repository doivent implémenter. L'utilisation de génériques
    permet d'avoir un typage fort pour chaque entité.
    
    Exemple d'utilisation :
        class ProduitRepository(BaseRepository[Produit]):
            def get_all(self) -> List[Produit]: ...
    """
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """
        Récupère tous les éléments de l'entité.
        
        Returns:
            List[T]: Liste de tous les éléments
        """
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Récupère un élément par son ID.
        
        Args:
            id (int): ID de l'élément à récupérer
            
        Returns:
            Optional[T]: L'élément trouvé ou None
        """
        pass
    
    @abstractmethod
    def add(self, entity: T) -> None:
        """
        Ajoute un nouvel élément.
        
        Args:
            entity (T): L'élément à ajouter
        """
        pass
    
    @abstractmethod
    def update(self, entity: T) -> None:
        """
        Met à jour un élément existant.
        
        Args:
            entity (T): L'élément à mettre à jour
        """
        pass
    
    @abstractmethod
    def delete(self, id: int) -> None:
        """
        Supprime un élément par son ID.
        
        Args:
            id (int): ID de l'élément à supprimer
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        Vide tous les éléments (utile pour les tests).
        """
        pass


class ProduitRepositoryInterface(BaseRepository[Produit]):
    """
    Interface spécifique pour les produits avec des méthodes métier.
    
    Cette interface étend BaseRepository avec des méthodes spécifiques
    aux produits comme get_actifs(), get_by_type(), etc.
    """
    
    def get_actifs(self) -> List[Produit]:
        """
        Récupère tous les produits actifs.
        
        Returns:
            List[Produit]: Liste des produits actifs
        """
        return [p for p in self.get_all() if p.actif]
    
    def get_by_type(self, type_produit: TypeProduit) -> List[Produit]:
        """
        Récupère les produits d'un type spécifique.
        
        Args:
            type_produit (TypeProduit): Type de produit à filtrer
            
        Returns:
            List[Produit]: Liste des produits du type spécifié
        """
        return [p for p in self.get_all() if p.type == type_produit]
    
    def get_actifs_by_type(self, type_produit: TypeProduit) -> List[Produit]:
        """
        Récupère les produits actifs d'un type spécifique.
        
        Args:
            type_produit (TypeProduit): Type de produit à filtrer
            
        Returns:
            List[Produit]: Liste des produits actifs du type spécifié
        """
        return [p for p in self.get_actifs() if p.type == type_produit]


class FournisseurRepositoryInterface(BaseRepository[Fournisseur]):
    """
    Interface spécifique pour les fournisseurs avec des méthodes métier.
    """
    
    def get_by_pays(self, pays: str) -> List[Fournisseur]:
        """
        Récupère les fournisseurs d'un pays spécifique.
        
        Args:
            pays (str): Pays des fournisseurs à récupérer
            
        Returns:
            List[Fournisseur]: Liste des fournisseurs du pays
        """
        return [f for f in self.get_all() if f.pays == pays]
    
    def get_avec_stock(self) -> List[Fournisseur]:
        """
        Récupère les fournisseurs qui ont du stock.
        
        Returns:
            List[Fournisseur]: Liste des fournisseurs avec du stock
        """
        return [f for f in self.get_all() if any(stock > 0 for stock in f.stock_produit.values())]


class EntrepriseRepositoryInterface(BaseRepository[Entreprise]):
    """
    Interface spécifique pour les entreprises avec des méthodes métier.
    """
    
    def get_by_strategie(self, strategie: str) -> List[Entreprise]:
        """
        Récupère les entreprises avec une stratégie spécifique.
        
        Args:
            strategie (str): Stratégie des entreprises à récupérer
            
        Returns:
            List[Entreprise]: Liste des entreprises avec la stratégie
        """
        return [e for e in self.get_all() if e.strategie == strategie]
    
    def get_avec_budget(self, budget_min: float = 0.0) -> List[Entreprise]:
        """
        Récupère les entreprises avec un budget minimum.
        
        Args:
            budget_min (float): Budget minimum requis
            
        Returns:
            List[Entreprise]: Liste des entreprises avec le budget requis
        """
        return [e for e in self.get_all() if e.budget >= budget_min]
    
    def get_by_types_preferes(self, types: List[TypeProduit]) -> List[Entreprise]:
        """
        Récupère les entreprises qui préfèrent certains types de produits.
        
        Args:
            types (List[TypeProduit]): Types de produits préférés
            
        Returns:
            List[Entreprise]: Liste des entreprises avec ces préférences
        """
        return [e for e in self.get_all() if any(t in e.types_preferes for t in types)] 