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
