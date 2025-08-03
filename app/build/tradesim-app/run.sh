#!/bin/bash
"""
Script de lancement TradeSim
============================

Ce script lance TradeSim avec l'environnement virtuel.
"""

# Activer l'environnement virtuel
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Environnement virtuel non trouvé. Exécutez d'abord ./install.sh"
    exit 1
fi

# Lancer l'application
echo "🚀 Lancement de TradeSim..."
python app/services/simulate.py "$@"
