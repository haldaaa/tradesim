#!/usr/bin/env python3
"""
Models TradeSim - Définitions des modèles de données
===================================================

Ce module définit tous les modèles de données Pydantic utilisés dans TradeSim.
Ces modèles assurent la validation des données et la cohérence du système.

Modèles définis :
- TypeProduit : Enumération des types de produits
- Produit : Modèle d'un produit avec ses caractéristiques
- Fournisseur : Modèle d'un fournisseur avec ses stocks
- Entreprise : Modèle d'une entreprise avec son budget et stratégie
- Transaction : Modèle d'une transaction commerciale
- ProduitChezFournisseur : Vue produit dans le contexte d'un fournisseur
- FournisseurComplet : Vue complète d'un fournisseur avec ses produits

Responsabilités :
- Validation automatique des données
- Sérialisation/désérialisation JSON
- Interface commune pour CLI et Web

Auteur: Assistant IA
Date: 2024-08-02
"""

from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Dict, List


class TypeProduit(str, Enum):
    """
    Enumération des types de produits dans TradeSim.
    
    Types disponibles :
    - produit_fini : Produit final prêt à la vente
    - consommable : Produit consommé dans la production
    - matiere_premiere : Matière première de base
    """
    produit_fini = "produit_fini"
    consommable = "consommable"
    matiere_premiere = "matiere_premiere"


class Produit(BaseModel):
    """
    Modèle d'un produit dans TradeSim.
    
    Attributs :
    - id : Identifiant unique du produit
    - nom : Nom du produit
    - prix : Prix de base du produit
    - actif : Statut actif/inactif du produit
    - type : Type de produit (enum TypeProduit)
    """
    id: int
    nom: str
    prix: float
    actif: bool
    type: TypeProduit


class Fournisseur(BaseModel):
    """
    Modèle d'un fournisseur dans TradeSim.
    
    Attributs :
    - id : Identifiant unique du fournisseur
    - nom_entreprise : Nom de l'entreprise fournisseur
    - pays : Pays d'origine du fournisseur
    - continent : Continent d'origine du fournisseur
    - stock_produit : Dictionnaire {produit_id → quantité en stock}
    """
    id: int
    nom_entreprise: str
    pays: str
    continent: str
    stock_produit: Dict[int, int]  # produit_id → stock possédé


class ProduitChezFournisseur(BaseModel):
    """
    Vue d'un produit dans le contexte d'un fournisseur.
    
    Utilisé pour l'API et les affichages détaillés.
    
    Attributs :
    - produit_id : ID du produit
    - nom : Nom du produit
    - stock : Quantité disponible chez ce fournisseur
    - prix_unitaire : Prix unitaire chez ce fournisseur
    """
    produit_id: int
    nom: str
    stock: int
    prix_unitaire: float


class FournisseurComplet(BaseModel):
    """
    Vue complète d'un fournisseur avec tous ses produits.
    
    Utilisé pour l'API et les affichages détaillés.
    
    Attributs :
    - id : Identifiant unique du fournisseur
    - nom_entreprise : Nom de l'entreprise fournisseur
    - pays : Pays d'origine du fournisseur
    - continent : Continent d'origine du fournisseur
    - produits : Liste des produits disponibles chez ce fournisseur
    """
    id: int
    nom_entreprise: str
    pays: str
    continent: str
    produits: List[ProduitChezFournisseur]


class Entreprise(BaseModel):
    """
    Modèle d'une entreprise dans TradeSim.
    
    Attributs :
    - id : Identifiant unique de l'entreprise
    - nom : Nom de l'entreprise
    - pays : Pays d'origine de l'entreprise
    - continent : Continent d'origine de l'entreprise
    - budget : Budget actuel de l'entreprise
    - budget_initial : Budget initial de l'entreprise
    - types_preferes : Types de produits préférés par l'entreprise
    - strategie : Stratégie d'achat ("moins_cher" ou "par_type")
    - stocks : Dictionnaire {produit_id → quantité en stock}
    """
    id: int
    nom: str
    pays: str
    continent: str
    budget: float
    budget_initial: float
    types_preferes: List[TypeProduit]
    strategie: str  # "moins_cher" ou "par_type"
    stocks: Dict[int, int] = {}  # produit_id → stock possédé


class Transaction(BaseModel):
    """
    Modèle d'une transaction commerciale dans TradeSim.
    
    Attributs :
    - timestamp : Horodatage de la transaction
    - entreprise_id : ID de l'entreprise acheteuse
    - fournisseur_id : ID du fournisseur vendeur
    - produit_id : ID du produit acheté
    - produit_nom : Nom du produit acheté
    - quantite : Quantité achetée
    - prix_unitaire : Prix unitaire du produit
    - total : Montant total de la transaction
    - succes : Indique si la transaction a réussi
    - raison_echec : Raison de l'échec si la transaction a échoué
    """
    timestamp: datetime
    entreprise_id: int
    fournisseur_id: int
    produit_id: int
    produit_nom: str
    quantite: int
    prix_unitaire: float
    total: float
    succes: bool
    raison_echec: str | None = None
