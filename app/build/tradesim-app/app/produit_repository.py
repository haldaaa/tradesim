#!/usr/bin/env python3
"""
Produit Repository - Gestion des produits avec pattern Repository
===============================================================

Ce fichier implémente le ProduitRepository avec deux implémentations :

MODE CLI (développement) : FakeProduitRepository
- Utilise les données en mémoire (fake_produits_db)
- Rapide pour les tests et le développement
- Pas besoin de base de données

MODE WEB (production) : SQLProduitRepository  
- Utilise une base de données (PostgreSQL, MySQL, etc.)
- Persistant et scalable
- Nécessite une base de données configurée

L'interface commune permet d'utiliser le même code pour CLI et Web.
Pour changer de mode, modifier config/mode.py

Auteur: Assistant IA
Date: 2024-08-02
"""

from typing import List, Optional
from models import Produit, TypeProduit
from repositories.base_repository import ProduitRepositoryInterface

# Import des données en mémoire (pour l'implémentation Fake)
from data import fake_produits_db


class FakeProduitRepository(ProduitRepositoryInterface):
    """
    Implémentation Fake du ProduitRepository utilisant les données en mémoire.
    
    MODE CLI (développement) : Cette implémentation est utilisée pour :
    - Les tests (rapides et isolés)
    - Le développement (pas besoin de base de données)
    - Le mode CLI (données en mémoire)
    
    Les données sont stockées dans fake_produits_db (liste globale).
    """
    
    def __init__(self):
        """
        Initialise le repository avec les données en mémoire.
        """
        self._data = fake_produits_db
    
    def get_all(self) -> List[Produit]:
        """
        Récupère tous les produits.
        
        Returns:
            List[Produit]: Liste de tous les produits
        """
        return self._data.copy()  # Retourne une copie pour éviter les modifications accidentelles
    
    def get_by_id(self, id: int) -> Optional[Produit]:
        """
        Récupère un produit par son ID.
        
        Args:
            id (int): ID du produit à récupérer
            
        Returns:
            Optional[Produit]: Le produit trouvé ou None
        """
        for produit in self._data:
            if produit.id == id:
                return produit
        return None
    
    def add(self, produit: Produit) -> None:
        """
        Ajoute un nouveau produit.
        
        Args:
            produit (Produit): Le produit à ajouter
        """
        # Vérifier que l'ID n'existe pas déjà
        if self.get_by_id(produit.id) is not None:
            raise ValueError(f"Un produit avec l'ID {produit.id} existe déjà")
        
        self._data.append(produit)
    
    def update(self, produit: Produit) -> None:
        """
        Met à jour un produit existant.
        
        Args:
            produit (Produit): Le produit à mettre à jour
        """
        for i, existing_produit in enumerate(self._data):
            if existing_produit.id == produit.id:
                self._data[i] = produit
                return
        
        raise ValueError(f"Produit avec l'ID {produit.id} non trouvé")
    
    def delete(self, id: int) -> None:
        """
        Supprime un produit par son ID.
        
        Args:
            id (int): ID du produit à supprimer
        """
        for i, produit in enumerate(self._data):
            if produit.id == id:
                del self._data[i]
                return
        
        raise ValueError(f"Produit avec l'ID {id} non trouvé")
    
    def clear(self) -> None:
        """
        Vide tous les produits (utile pour les tests).
        """
        self._data.clear()


class SQLProduitRepository(ProduitRepositoryInterface):
    """
    Implémentation SQL du ProduitRepository utilisant une base de données.
    
    MODE WEB (production) : Cette implémentation sera utilisée pour :
    - La production (données persistantes)
    - Le mode Web (base de données PostgreSQL)
    - Les tests d'intégration avec la DB
    
    Note: Cette implémentation sera développée quand on migrera vers une DB.
    """
    
    def __init__(self, db_session=None):
        """
        Initialise le repository avec une session de base de données.
        
        Args:
            db_session: Session de base de données (SQLAlchemy, etc.)
        """
        self._db = db_session
        # TODO: Implémenter quand on aura une base de données
    
    def get_all(self) -> List[Produit]:
        """
        Récupère tous les produits depuis la base de données.
        
        Returns:
            List[Produit]: Liste de tous les produits
        """
        # TODO: Implémenter avec SQLAlchemy
        # return self._db.query(Produit).all()
        raise NotImplementedError("SQLProduitRepository pas encore implémenté")
    
    def get_by_id(self, id: int) -> Optional[Produit]:
        """
        Récupère un produit par son ID depuis la base de données.
        
        Args:
            id (int): ID du produit à récupérer
            
        Returns:
            Optional[Produit]: Le produit trouvé ou None
        """
        # TODO: Implémenter avec SQLAlchemy
        # return self._db.query(Produit).filter(Produit.id == id).first()
        raise NotImplementedError("SQLProduitRepository pas encore implémenté")
    
    def add(self, produit: Produit) -> None:
        """
        Ajoute un nouveau produit dans la base de données.
        
        Args:
            produit (Produit): Le produit à ajouter
        """
        # TODO: Implémenter avec SQLAlchemy
        # self._db.add(produit)
        # self._db.commit()
        raise NotImplementedError("SQLProduitRepository pas encore implémenté")
    
    def update(self, produit: Produit) -> None:
        """
        Met à jour un produit existant dans la base de données.
        
        Args:
            produit (Produit): Le produit à mettre à jour
        """
        # TODO: Implémenter avec SQLAlchemy
        # self._db.merge(produit)
        # self._db.commit()
        raise NotImplementedError("SQLProduitRepository pas encore implémenté")
    
    def delete(self, id: int) -> None:
        """
        Supprime un produit par son ID depuis la base de données.
        
        Args:
            id (int): ID du produit à supprimer
        """
        # TODO: Implémenter avec SQLAlchemy
        # produit = self.get_by_id(id)
        # if produit:
        #     self._db.delete(produit)
        #     self._db.commit()
        raise NotImplementedError("SQLProduitRepository pas encore implémenté")
    
    def clear(self) -> None:
        """
        Vide tous les produits de la base de données (utile pour les tests).
        """
        # TODO: Implémenter avec SQLAlchemy
        # self._db.query(Produit).delete()
        # self._db.commit()
        raise NotImplementedError("SQLProduitRepository pas encore implémenté")


# Alias pour utiliser l'implémentation par défaut
ProduitRepository = FakeProduitRepository 