#!/usr/bin/env python3
"""
Services TradeSim - Logique métier de l'application
==================================================

Ce module contient tous les services de l'application TradeSim.
Les services encapsulent la logique métier et utilisent les Repository
pour l'accès aux données.

Services disponibles :
- SimulationService : Orchestration de la simulation
- GameManagerService : Gestion des templates et configuration
- TransactionService : Gestion des transactions
- BudgetService : Gestion des budgets

Auteur: Assistant IA
Date: 2024-08-02
"""

# Services principaux
from .simulation_service import SimulationService, simulation_service
from .game_manager_service import GameManagerService, game_manager_service
from .transaction_service import TransactionService, transaction_service
from .budget_service import BudgetService, budget_service

# Services existants (à refactoriser progressivement)
from .simulateur import simulation_tour
from .game_manager import reset_game, generate_game_data, save_template, load_template, list_templates
from .simulate import afficher_status, mode_cheat, run_simulation

__all__ = [
    # Nouveaux services
    "SimulationService",
    "simulation_service",
    "GameManagerService", 
    "game_manager_service",
    "TransactionService",
    "transaction_service",
    "BudgetService",
    "budget_service",
    
    # Services existants
    "simulation_tour",
    "reset_game",
    "generate_game_data", 
    "save_template",
    "load_template",
    "list_templates",
    "afficher_status",
    "mode_cheat",
    "run_simulation"
] 