#!/usr/bin/env python3
"""
Fournisseur Repository - Gestion des fournisseurs avec pattern Repository
=======================================================================

Ce fichier implémente le FournisseurRepository avec deux implémentations :
- FakeFournisseurRepository : Utilise les données en mémoire (pour les tests)
- SQLFournisseurRepository : Utilise une base de données (pour la production)

L'interface commune permet d'utiliser le même code pour CLI et Web.

Auteur: Assistant IA
Date: 2024-08-02
"""

from typing import List, Optional
from models import Fournisseur
from repositories.base_repository import FournisseurRepositoryInterface

# Import des données en mémoire (pour l'implémentation Fake)
from data import fake_fournisseurs_db


class FakeFournisseurRepository(FournisseurRepositoryInterface):
    """
    Implémentation Fake du FournisseurRepository utilisant les données en mémoire.
    
    Cette implémentation est utilisée pour :
    - Les tests (rapides et isolés)
    - Le développement (pas besoin de base de données)
    - Le mode CLI (données en mémoire)
    
    Les données sont stockées dans fake_fournisseurs_db (liste globale).
    """
    
    def __init__(self):
        """
        Initialise le repository avec les données en mémoire.
        """
        self._data = fake_fournisseurs_db
    
    def get_all(self) -> List[Fournisseur]:
        """
        Récupère tous les fournisseurs.
        
        Returns:
            List[Fournisseur]: Liste de tous les fournisseurs
        """
        return self._data.copy()  # Retourne une copie pour éviter les modifications accidentelles
    
    def get_by_id(self, id: int) -> Optional[Fournisseur]:
        """
        Récupère un fournisseur par son ID.
        
        Args:
            id (int): ID du fournisseur à récupérer
            
        Returns:
            Optional[Fournisseur]: Le fournisseur trouvé ou None
        """
        for fournisseur in self._data:
            if fournisseur.id == id:
                return fournisseur
        return None
    
    def add(self, fournisseur: Fournisseur) -> None:
        """
        Ajoute un nouveau fournisseur.
        
        Args:
            fournisseur (Fournisseur): Le fournisseur à ajouter
        """
        # Vérifier que l'ID n'existe pas déjà
        if self.get_by_id(fournisseur.id) is not None:
            raise ValueError(f"Un fournisseur avec l'ID {fournisseur.id} existe déjà")
        
        self._data.append(fournisseur)
    
    def update(self, fournisseur: Fournisseur) -> None:
        """
        Met à jour un fournisseur existant.
        
        Args:
            fournisseur (Fournisseur): Le fournisseur à mettre à jour
        """
        for i, existing_fournisseur in enumerate(self._data):
            if existing_fournisseur.id == fournisseur.id:
                self._data[i] = fournisseur
                return
        
        raise ValueError(f"Fournisseur avec l'ID {fournisseur.id} non trouvé")
    
    def delete(self, id: int) -> None:
        """
        Supprime un fournisseur par son ID.
        
        Args:
            id (int): ID du fournisseur à supprimer
        """
        for i, fournisseur in enumerate(self._data):
            if fournisseur.id == id:
                del self._data[i]
                return
        
        raise ValueError(f"Fournisseur avec l'ID {id} non trouvé")
    
    def clear(self) -> None:
        """
        Vide tous les fournisseurs (utile pour les tests).
        """
        self._data.clear()


class SQLFournisseurRepository(FournisseurRepositoryInterface):
    """
    Implémentation SQL du FournisseurRepository utilisant une base de données.
    
    Cette implémentation sera utilisée pour :
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
    
    def get_all(self) -> List[Fournisseur]:
        """
        Récupère tous les fournisseurs depuis la base de données.
        
        Returns:
            List[Fournisseur]: Liste de tous les fournisseurs
        """
        # TODO: Implémenter avec SQLAlchemy
        # return self._db.query(Fournisseur).all()
        raise NotImplementedError("SQLFournisseurRepository pas encore implémenté")
    
    def get_by_id(self, id: int) -> Optional[Fournisseur]:
        """
        Récupère un fournisseur par son ID depuis la base de données.
        
        Args:
            id (int): ID du fournisseur à récupérer
            
        Returns:
            Optional[Fournisseur]: Le fournisseur trouvé ou None
        """
        # TODO: Implémenter avec SQLAlchemy
        # return self._db.query(Fournisseur).filter(Fournisseur.id == id).first()
        raise NotImplementedError("SQLFournisseurRepository pas encore implémenté")
    
    def add(self, fournisseur: Fournisseur) -> None:
        """
        Ajoute un nouveau fournisseur dans la base de données.
        
        Args:
            fournisseur (Fournisseur): Le fournisseur à ajouter
        """
        # TODO: Implémenter avec SQLAlchemy
        # self._db.add(fournisseur)
        # self._db.commit()
        raise NotImplementedError("SQLFournisseurRepository pas encore implémenté")
    
    def update(self, fournisseur: Fournisseur) -> None:
        """
        Met à jour un fournisseur existant dans la base de données.
        
        Args:
            fournisseur (Fournisseur): Le fournisseur à mettre à jour
        """
        # TODO: Implémenter avec SQLAlchemy
        # self._db.merge(fournisseur)
        # self._db.commit()
        raise NotImplementedError("SQLFournisseurRepository pas encore implémenté")
    
    def delete(self, id: int) -> None:
        """
        Supprime un fournisseur par son ID depuis la base de données.
        
        Args:
            id (int): ID du fournisseur à supprimer
        """
        # TODO: Implémenter avec SQLAlchemy
        # fournisseur = self.get_by_id(id)
        # if fournisseur:
        #     self._db.delete(fournisseur)
        #     self._db.commit()
        raise NotImplementedError("SQLFournisseurRepository pas encore implémenté")
    
    def clear(self) -> None:
        """
        Vide tous les fournisseurs de la base de données (utile pour les tests).
        """
        # TODO: Implémenter avec SQLAlchemy
        # self._db.query(Fournisseur).delete()
        # self._db.commit()
        raise NotImplementedError("SQLFournisseurRepository pas encore implémenté")


# Alias pour utiliser l'implémentation par défaut
FournisseurRepository = FakeFournisseurRepository 