#!/usr/bin/env python3
"""
Repositories - Module d'accès aux données
========================================

Ce module exporte tous les Repository de TradeSim.
L'utilisation du pattern Repository permet de séparer la logique métier
de l'accès aux données, facilitant les tests et la migration vers une DB.

MODE CLI (développement) : Utilise FakeRepository (données en mémoire)
MODE WEB (production) : Utilise SQLRepository (base de données)

Pour changer de mode, modifier config/mode.py

Auteur: Assistant IA
Date: 2024-08-02
"""

# Imports des interfaces communes
from .base_repository import (
    BaseRepository,
    ProduitRepositoryInterface,
    FournisseurRepositoryInterface,
    EntrepriseRepositoryInterface
)

# Imports des implémentations Fake (par défaut)
from .produit_repository import (
    FakeProduitRepository,
    SQLProduitRepository,
    ProduitRepository  # Alias vers FakeProduitRepository
)

from .fournisseur_repository import (
    FakeFournisseurRepository,
    SQLFournisseurRepository,
    FournisseurRepository  # Alias vers FakeFournisseurRepository
)

from .entreprise_repository import (
    FakeEntrepriseRepository,
    SQLEntrepriseRepository,
    EntrepriseRepository  # Alias vers FakeEntrepriseRepository
)

# Exports publics
__all__ = [
    # Interfaces
    'BaseRepository',
    'ProduitRepositoryInterface',
    'FournisseurRepositoryInterface',
    'EntrepriseRepositoryInterface',
    
    # Implémentations Fake
    'FakeProduitRepository',
    'FakeFournisseurRepository',
    'FakeEntrepriseRepository',
    
    # Implémentations SQL
    'SQLProduitRepository',
    'SQLFournisseurRepository',
    'SQLEntrepriseRepository',
    
    # Aliases par défaut
    'ProduitRepository',
    'FournisseurRepository',
    'EntrepriseRepository'
] 