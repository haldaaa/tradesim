#!/usr/bin/env python3
"""
Configuration des modes d'exécution - TradeSim
==============================================

Ce fichier centralise la configuration des modes d'exécution de TradeSim.
Il permet de basculer facilement entre le mode CLI (données en mémoire)
et le mode Web (base de données) sans modifier le reste du code.

Auteur: Assistant IA
Date: 2024-08-02
"""

from enum import Enum
from typing import Literal

class ExecutionMode(Enum):
    """
    Modes d'exécution disponibles pour TradeSim.
    
    CLI: Utilise les données en mémoire (FakeRepository)
    WEB: Utilise une base de données (SQLRepository)
    """
    CLI = "cli"
    WEB = "web"

# Configuration actuelle du mode d'exécution
# Pour changer de mode, modifiez cette variable :
CURRENT_MODE: ExecutionMode = ExecutionMode.CLI

# Alias pour faciliter l'utilisation
MODE_CLI = ExecutionMode.CLI
MODE_WEB = ExecutionMode.WEB

def get_current_mode() -> ExecutionMode:
    """
    Récupère le mode d'exécution actuel.
    
    Returns:
        ExecutionMode: Le mode d'exécution actuel (CLI ou WEB)
    """
    return CURRENT_MODE

def is_cli_mode() -> bool:
    """
    Vérifie si l'application est en mode CLI.
    
    Returns:
        bool: True si en mode CLI, False sinon
    """
    return CURRENT_MODE == ExecutionMode.CLI

def is_web_mode() -> bool:
    """
    Vérifie si l'application est en mode Web.
    
    Returns:
        bool: True si en mode Web, False sinon
    """
    return CURRENT_MODE == ExecutionMode.WEB

def set_mode(mode: ExecutionMode) -> None:
    """
    Change le mode d'exécution de l'application.
    
    Args:
        mode (ExecutionMode): Le nouveau mode d'exécution
        
    Example:
        # Passer en mode Web
        set_mode(ExecutionMode.WEB)
        
        # Passer en mode CLI
        set_mode(ExecutionMode.CLI)
    """
    global CURRENT_MODE
    CURRENT_MODE = mode
    print(f"🔄 Mode d'exécution changé vers: {mode.value.upper()}")

def get_mode_description() -> str:
    """
    Récupère une description du mode actuel.
    
    Returns:
        str: Description du mode actuel
    """
    if is_cli_mode():
        return "Mode CLI - Données en mémoire (pour développement et tests)"
    else:
        return "Mode Web - Base de données (pour production)"

# Configuration des Repository selon le mode
def get_repository_config() -> dict:
    """
    Récupère la configuration des Repository selon le mode actuel.
    
    Returns:
        dict: Configuration des Repository
    """
    if is_cli_mode():
        return {
            "produit_repository": "FakeProduitRepository",
            "fournisseur_repository": "FakeFournisseurRepository", 
            "entreprise_repository": "FakeEntrepriseRepository",
            "description": "Données en mémoire pour développement"
        }
    else:
        return {
            "produit_repository": "SQLProduitRepository",
            "fournisseur_repository": "SQLFournisseurRepository",
            "entreprise_repository": "SQLEntrepriseRepository", 
            "description": "Base de données pour production"
        }

# Instructions pour changer de mode
MODE_CHANGE_INSTRUCTIONS = """
📋 Instructions pour changer de mode :

1. MODE CLI (développement) :
   - Ouvrir config/mode.py
   - Changer CURRENT_MODE = ExecutionMode.CLI
   - Les Repository utilisent les données en mémoire

2. MODE WEB (production) :
   - Ouvrir config/mode.py  
   - Changer CURRENT_MODE = ExecutionMode.WEB
   - Les Repository utilisent la base de données
   - Nécessite une base de données configurée

3. Vérification :
   - Lancer les tests pour vérifier le bon fonctionnement
   - Tester l'API si en mode Web
""" 