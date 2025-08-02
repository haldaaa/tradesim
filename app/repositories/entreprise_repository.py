#!/usr/bin/env python3
"""
Entreprise Repository - Gestion des entreprises avec pattern Repository
====================================================================

Ce fichier implémente le EntrepriseRepository avec deux implémentations :
- FakeEntrepriseRepository : Utilise les données en mémoire (pour les tests)
- SQLEntrepriseRepository : Utilise une base de données (pour la production)

L'interface commune permet d'utiliser le même code pour CLI et Web.

Auteur: Assistant IA
Date: 2024-08-02
"""

from typing import List, Optional
from models import Entreprise, TypeProduit
from repositories.base_repository import EntrepriseRepositoryInterface

# Import des données en mémoire (pour l'implémentation Fake)
from data import fake_entreprises_db


class FakeEntrepriseRepository(EntrepriseRepositoryInterface):
    """
    Implémentation Fake du EntrepriseRepository utilisant les données en mémoire.
    
    Cette implémentation est utilisée pour :
    - Les tests (rapides et isolés)
    - Le développement (pas besoin de base de données)
    - Le mode CLI (données en mémoire)
    
    Les données sont stockées dans fake_entreprises_db (liste globale).
    """
    
    def __init__(self):
        """
        Initialise le repository avec les données en mémoire.
        """
        self._data = fake_entreprises_db
    
    def get_all(self) -> List[Entreprise]:
        """
        Récupère toutes les entreprises.
        
        Returns:
            List[Entreprise]: Liste de toutes les entreprises
        """
        return self._data.copy()  # Retourne une copie pour éviter les modifications accidentelles
    
    def get_by_id(self, id: int) -> Optional[Entreprise]:
        """
        Récupère une entreprise par son ID.
        
        Args:
            id (int): ID de l'entreprise à récupérer
            
        Returns:
            Optional[Entreprise]: L'entreprise trouvée ou None
        """
        for entreprise in self._data:
            if entreprise.id == id:
                return entreprise
        return None
    
    def add(self, entreprise: Entreprise) -> None:
        """
        Ajoute une nouvelle entreprise.
        
        Args:
            entreprise (Entreprise): L'entreprise à ajouter
        """
        # Vérifier que l'ID n'existe pas déjà
        if self.get_by_id(entreprise.id) is not None:
            raise ValueError(f"Une entreprise avec l'ID {entreprise.id} existe déjà")
        
        self._data.append(entreprise)
    
    def update(self, entreprise: Entreprise) -> None:
        """
        Met à jour une entreprise existante.
        
        Args:
            entreprise (Entreprise): L'entreprise à mettre à jour
        """
        for i, existing_entreprise in enumerate(self._data):
            if existing_entreprise.id == entreprise.id:
                self._data[i] = entreprise
                return
        
        raise ValueError(f"Entreprise avec l'ID {entreprise.id} non trouvée")
    
    def delete(self, id: int) -> None:
        """
        Supprime une entreprise par son ID.
        
        Args:
            id (int): ID de l'entreprise à supprimer
        """
        for i, entreprise in enumerate(self._data):
            if entreprise.id == id:
                del self._data[i]
                return
        
        raise ValueError(f"Entreprise avec l'ID {id} non trouvée")
    
    def clear(self) -> None:
        """
        Vide toutes les entreprises (utile pour les tests).
        """
        self._data.clear()


class SQLEntrepriseRepository(EntrepriseRepositoryInterface):
    """
    Implémentation SQL du EntrepriseRepository utilisant une base de données.
    
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
    
    def get_all(self) -> List[Entreprise]:
        """
        Récupère toutes les entreprises depuis la base de données.
        
        Returns:
            List[Entreprise]: Liste de toutes les entreprises
        """
        # TODO: Implémenter avec SQLAlchemy
        # return self._db.query(Entreprise).all()
        raise NotImplementedError("SQLEntrepriseRepository pas encore implémenté")
    
    def get_by_id(self, id: int) -> Optional[Entreprise]:
        """
        Récupère une entreprise par son ID depuis la base de données.
        
        Args:
            id (int): ID de l'entreprise à récupérer
            
        Returns:
            Optional[Entreprise]: L'entreprise trouvée ou None
        """
        # TODO: Implémenter avec SQLAlchemy
        # return self._db.query(Entreprise).filter(Entreprise.id == id).first()
        raise NotImplementedError("SQLEntrepriseRepository pas encore implémenté")
    
    def add(self, entreprise: Entreprise) -> None:
        """
        Ajoute une nouvelle entreprise dans la base de données.
        
        Args:
            entreprise (Entreprise): L'entreprise à ajouter
        """
        # TODO: Implémenter avec SQLAlchemy
        # self._db.add(entreprise)
        # self._db.commit()
        raise NotImplementedError("SQLEntrepriseRepository pas encore implémenté")
    
    def update(self, entreprise: Entreprise) -> None:
        """
        Met à jour une entreprise existante dans la base de données.
        
        Args:
            entreprise (Entreprise): L'entreprise à mettre à jour
        """
        # TODO: Implémenter avec SQLAlchemy
        # self._db.merge(entreprise)
        # self._db.commit()
        raise NotImplementedError("SQLEntrepriseRepository pas encore implémenté")
    
    def delete(self, id: int) -> None:
        """
        Supprime une entreprise par son ID depuis la base de données.
        
        Args:
            id (int): ID de l'entreprise à supprimer
        """
        # TODO: Implémenter avec SQLAlchemy
        # entreprise = self.get_by_id(id)
        # if entreprise:
        #     self._db.delete(entreprise)
        #     self._db.commit()
        raise NotImplementedError("SQLEntrepriseRepository pas encore implémenté")
    
    def clear(self) -> None:
        """
        Vide toutes les entreprises de la base de données (utile pour les tests).
        """
        # TODO: Implémenter avec SQLAlchemy
        # self._db.query(Entreprise).delete()
        # self._db.commit()
        raise NotImplementedError("SQLEntrepriseRepository pas encore implémenté")


# Alias pour utiliser l'implémentation par défaut
EntrepriseRepository = FakeEntrepriseRepository 