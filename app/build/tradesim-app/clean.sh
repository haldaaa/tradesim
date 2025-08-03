#!/bin/bash
"""
Script de nettoyage TradeSim
============================

Ce script nettoie les fichiers temporaires.
"""

echo "🧹 Nettoyage de TradeSim..."

# Supprimer les fichiers Python compilés
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Supprimer les logs
rm -rf logs/*.log
rm -rf logs/*.jsonl

# Supprimer les fichiers de test
rm -rf .pytest_cache
rm -rf .coverage

echo "✅ Nettoyage terminé !"
