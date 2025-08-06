#!/usr/bin/env python3
"""
Data Package TradeSim - Package pour les données TradeSim
========================================================

Ce package contient les modules de données pour TradeSim :
- names_data.py : Données de noms réalistes
- __init__.py : Ce fichier

Auteur: Assistant IA
Date: 2025-01-27
"""

# Import des données depuis data.py pour compatibilité avec les anciens tests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("data_module", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.py"))
data_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_module)

# Exporter les variables pour compatibilité
fake_produits_db = data_module.fake_produits_db
fake_fournisseurs_db = data_module.fake_fournisseurs_db
fake_entreprises_db = data_module.fake_entreprises_db
prix_par_fournisseur = data_module.prix_par_fournisseur
produits_ayant_subi_inflation = data_module.produits_ayant_subi_inflation 