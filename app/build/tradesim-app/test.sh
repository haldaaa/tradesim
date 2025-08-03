#!/bin/bash
"""
Script de test TradeSim
=======================

Ce script lance les tests de TradeSim.
"""

# Activer l'environnement virtuel
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Environnement virtuel non trouvé. Exécutez d'abord ./install.sh"
    exit 1
fi

# Lancer les tests
echo "🧪 Lancement des tests TradeSim..."
pytest tests/ -v

echo "✅ Tests terminés !"
