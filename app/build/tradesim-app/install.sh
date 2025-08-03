#!/bin/bash
"""
Script d'installation TradeSim
=============================

Ce script installe TradeSim et ses dépendances.
"""

set -e

echo "🚀 Installation de TradeSim..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Créer l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Installer l'application
echo "⚙️ Installation de l'application..."
pip install -e .

echo "✅ Installation terminée !"
echo ""
echo "🎮 Pour démarrer TradeSim :"
echo "   source venv/bin/activate"
echo "   python app/services/simulate.py"
echo ""
echo "🌐 Pour démarrer l'API :"
echo "   source venv/bin/activate"
echo "   uvicorn app.api.main:app --reload"
echo ""
echo "📚 Documentation :"
echo "   cat README.md"
echo "   cat docs/GUIDE_UTILISATION.md"
