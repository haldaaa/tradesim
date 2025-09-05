#!/bin/bash
"""
Script de création de package TradeSim
=====================================

Ce script crée un package complet de l'application TradeSim
avec toutes les dépendances et la documentation.

Auteur: Assistant IA
Date: 2024-08-02
"""

set -e  # Arrêter en cas d'erreur

# Configuration
PACKAGE_NAME="tradesim-app"
VERSION="0.2.0"
BUILD_DIR="build"
PACKAGE_DIR="$BUILD_DIR/$PACKAGE_NAME"

echo "🚀 Création du package TradeSim v$VERSION..."

# Nettoyer et créer le répertoire de build
rm -rf "$BUILD_DIR"
mkdir -p "$PACKAGE_DIR"

echo "📁 Création de la structure du package..."

# Créer la structure du package
mkdir -p "$PACKAGE_DIR/app"
mkdir -p "$PACKAGE_DIR/docs"
mkdir -p "$PACKAGE_DIR/scripts"

# Copier les fichiers principaux
echo "📋 Copie des fichiers source..."

# Code source
cp -r services/ "$PACKAGE_DIR/app/"
cp -r models/ "$PACKAGE_DIR/app/"
cp -r repositories/ "$PACKAGE_DIR/app/"
cp -r events/ "$PACKAGE_DIR/app/"
cp -r config/ "$PACKAGE_DIR/app/"
cp -r api/ "$PACKAGE_DIR/app/"
cp -r tests/ "$PACKAGE_DIR/app/"
cp -r templates/ "$PACKAGE_DIR/app/"

# Fichiers racine
cp data.py "$PACKAGE_DIR/app/"
cp __init__.py "$PACKAGE_DIR/app/"
cp pytest.ini "$PACKAGE_DIR/"

# Documentation
cp README.md "$PACKAGE_DIR/"
cp GUIDE_UTILISATION.md "$PACKAGE_DIR/docs/"
cp GUIDE_MIGRATION_CLI_WEB_UNIFIED.md "$PACKAGE_DIR/docs/"
cp GUIDE_MONITORING_CLI.md "$PACKAGE_DIR/docs/"
cp METRIQUES_DISPONIBLES.md "$PACKAGE_DIR/docs/"
cp COMMANDES_CLI.md "$PACKAGE_DIR/docs/"
cp DOCUMENTATION_STATUS.md "$PACKAGE_DIR/docs/"

# Créer requirements.txt
echo "📦 Création du fichier requirements.txt..."
cat > "$PACKAGE_DIR/requirements.txt" << 'EOF'
# TradeSim - Dépendances principales
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0

# Tests
pytest>=7.4.0
pytest-asyncio>=0.21.0

# Monitoring (optionnel)
prometheus-client>=0.19.0
rich>=13.7.0

# Utilitaires
python-dotenv>=1.0.0
typing-extensions>=4.8.0
EOF

# Créer setup.py
echo "⚙️ Création du fichier setup.py..."
cat > "$PACKAGE_DIR/setup.py" << 'EOF'
#!/usr/bin/env python3
"""
Setup TradeSim
=============

Script d'installation pour TradeSim.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tradesim",
    version="1.0.0",
    author="Assistant IA",
    author_email="assistant@tradesim.com",
    description="Simulation économique TradeSim",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tradesim/tradesim",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "monitoring": [
            "prometheus-client>=0.19.0",
            "rich>=13.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tradesim=app.services.simulate:main",
            "tradesim-api=app.api.main:app",
        ],
    },
)
EOF

# Créer le script d'installation
echo "🔧 Création du script d'installation..."
cat > "$PACKAGE_DIR/install.sh" << 'EOF'
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
EOF

chmod +x "$PACKAGE_DIR/install.sh"

# Créer le script de lancement
echo "▶️ Création du script de lancement..."
cat > "$PACKAGE_DIR/run.sh" << 'EOF'
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
EOF

chmod +x "$PACKAGE_DIR/run.sh"

# Créer le script de lancement API
echo "🌐 Création du script de lancement API..."
cat > "$PACKAGE_DIR/run-api.sh" << 'EOF'
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
EOF

chmod +x "$PACKAGE_DIR/run-api.sh"

# Créer le fichier .env.example
echo "⚙️ Création du fichier .env.example..."
cat > "$PACKAGE_DIR/.env.example" << 'EOF'
# Configuration TradeSim
# Copiez ce fichier vers .env et modifiez les valeurs

# Mode d'exécution (cli/web)
TRADESIM_MODE=cli

# Configuration de l'API
API_HOST=0.0.0.0
API_PORT=8000

# Configuration des logs
LOG_LEVEL=INFO
LOG_FILE=logs/tradesim.log

# Configuration de la simulation
SIMULATION_TICKS=100
SIMULATION_PAUSE=0.1

# Configuration du monitoring (optionnel)
PROMETHEUS_PORT=8000
GRAFANA_PORT=3000
EOF

# Créer le README du package
echo "📝 Création du README du package..."
cat > "$PACKAGE_DIR/README_PACKAGE.md" << 'EOF'
# TradeSim - Package d'installation
==================================

Ce package contient TradeSim prêt à l'installation.

## 🚀 Installation rapide

### 1. Installer les dépendances
```bash
./install.sh
```

### 2. Lancer l'application
```bash
# Mode CLI
./run.sh

# Mode API
./run-api.sh
```

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip3
- Terminal compatible bash

## 🎮 Utilisation

### Mode CLI
```bash
./run.sh
```

### Mode API
```bash
./run-api.sh
# Puis ouvrir http://localhost:8000
```

### Tests
```bash
source venv/bin/activate
pytest tests/
```

## 📚 Documentation

- `README.md` - Documentation principale
- `docs/GUIDE_UTILISATION.md` - Guide d'utilisation
- `docs/GUIDE_MIGRATION_CLI_WEB.md` - Migration CLI ↔ Web
- `docs/METRIQUES_DISPONIBLES.md` - Métriques disponibles

## 🔧 Configuration

1. Copier `.env.example` vers `.env`
2. Modifier les valeurs selon vos besoins
3. Redémarrer l'application

## 🐛 Dépannage

### Problème d'installation
```bash
# Réinstaller les dépendances
rm -rf venv
./install.sh
```

### Problème de permissions
```bash
# Rendre les scripts exécutables
chmod +x *.sh
```

### Problème de Python
```bash
# Vérifier la version
python3 --version
# Doit être >= 3.8
```

## 📦 Contenu du package

- `app/` - Code source de l'application
- `docs/` - Documentation
- `tests/` - Tests unitaires et d'intégration
- `templates/` - Templates de configuration
- `requirements.txt` - Dépendances Python
- `setup.py` - Configuration d'installation
- `install.sh` - Script d'installation
- `run.sh` - Script de lancement CLI
- `run-api.sh` - Script de lancement API

## 🔄 Mise à jour

Pour mettre à jour TradeSim :
1. Sauvegarder vos données personnalisées
2. Supprimer l'ancienne version
3. Installer la nouvelle version
4. Restaurer vos données

## 📞 Support

En cas de problème :
1. Consulter la documentation
2. Vérifier les logs dans `logs/`
3. Exécuter les tests : `pytest tests/`
EOF

# Créer un script de test
echo "🧪 Création du script de test..."
cat > "$PACKAGE_DIR/test.sh" << 'EOF'
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
EOF

chmod +x "$PACKAGE_DIR/test.sh"

# Créer un script de nettoyage
echo "🧹 Création du script de nettoyage..."
cat > "$PACKAGE_DIR/clean.sh" << 'EOF'
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
EOF

chmod +x "$PACKAGE_DIR/clean.sh"

# Créer l'archive
echo "📦 Création de l'archive..."
cd "$BUILD_DIR"
tar -czf "${PACKAGE_NAME}-v${VERSION}.tar.gz" "$PACKAGE_NAME"

echo "✅ Package créé avec succès !"
echo ""
echo "📦 Fichier créé : $BUILD_DIR/${PACKAGE_NAME}-v${VERSION}.tar.gz"
echo "📁 Contenu : $BUILD_DIR/$PACKAGE_NAME/"
echo ""
echo "🚀 Pour installer sur une autre machine :"
echo "   tar -xzf ${PACKAGE_NAME}-v${VERSION}.tar.gz"
echo "   cd $PACKAGE_NAME"
echo "   ./install.sh"
echo "   ./run.sh" 