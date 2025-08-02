#!/usr/bin/env python3
"""
API - Module des endpoints FastAPI
==================================

Ce module exporte l'application FastAPI de TradeSim.
L'API expose les fonctionnalités de l'application via des endpoints REST.

Auteur: Assistant IA
Date: 2024-08-02
"""

# Import de l'application FastAPI principale
from .main import app

# Exports publics
__all__ = ['app'] 