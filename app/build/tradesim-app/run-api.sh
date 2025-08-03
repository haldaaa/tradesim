#!/bin/bash
"""
Script de lancement API TradeSim
===============================

Ce script lance l'API TradeSim avec l'environnement virtuel.
"""

# Activer l'environnement virtuel
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Environnement virtuel non trouvé. Exécutez d'abord ./install.sh"
    exit 1
fi

# Lancer l'API
echo "🌐 Lancement de l'API TradeSim..."
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
