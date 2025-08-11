# Tests Unitaires - TradeSim

## 📋 Description

Ce dossier contient tous les tests unitaires de l'application TradeSim. Les tests unitaires vérifient le bon fonctionnement de chaque composant individuellement.

## 🗂️ Organisation des Tests

### Tests par Service
- **`test_simulation_service.py`** - Tests du service de simulation principal (CORRECTION BUG 10/08/2025)
- **`test_game_manager.py`** - Tests du gestionnaire de jeu
- **`test_game_state_service.py`** - Tests du service d'état du jeu
- **`test_models.py`** - Tests des modèles de données
- **`test_names_data.py`** - Tests des données de noms

### Tests par Fonctionnalité
- **`test_inflation.py`** - Tests des événements d'inflation
- **`test_inflation_correct.py`** - Tests de correction d'inflation
- **`test_inflation_penalite.py`** - Tests des pénalités d'inflation
- **`test_inflation_retour_normal.py`** - Tests du retour à la normale
- **`test_events_refactorises.py`** - Tests des événements refactorisés
- **`test_budgets_entreprises.py`** - Tests des budgets d'entreprises
- **`test_quantites_achat.py`** - Tests des quantités d'achat
- **`test_optimisations.py`** - Tests des optimisations de performance
- **`test_architecture.py`** - Tests de l'architecture générale
- **`test_simple.py`** - Tests simples de base

## 🚀 Instructions de Lancement

### Lancement de Tous les Tests Unitaires
```bash
# Depuis le dossier app/
pytest tests/unit/ -v

# Avec couverture
pytest tests/unit/ --cov=services --cov-report=html
```

### Lancement d'un Test Spécifique
```bash
# Test du service de simulation
pytest tests/unit/test_simulation_service.py -v

# Test avec couverture spécifique
pytest tests/unit/test_simulation_service.py --cov=services.simulation_service --cov-report=html

# Test d'un fichier spécifique
pytest tests/unit/test_inflation.py -v
```

### Lancement d'une Classe de Test Spécifique
```bash
# Test d'une classe spécifique
pytest tests/unit/test_simulation_service.py::TestSimulationService -v

# Test d'une méthode spécifique
pytest tests/unit/test_simulation_service.py::TestSimulationService::test_initialisation_service -v
```

## 📊 Couverture de Code

### Génération du Rapport de Couverture
```bash
# Couverture complète
pytest tests/unit/ --cov=services --cov=models --cov=events --cov=config --cov-report=html

# Couverture avec rapport détaillé
pytest tests/unit/ --cov=services --cov-report=term-missing
```

### Visualisation
- Les rapports HTML sont générés dans `htmlcov/`
- Ouvrir `htmlcov/index.html` dans un navigateur

## 🔧 Configuration

### Fichier pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### Variables d'Environnement
```bash
# Pour les tests avec monitoring
export METRICS_ENABLED=true

# Pour les tests de performance
export PERFORMANCE_TESTING=true
```

## 📝 Conventions de Nommage

### Fichiers de Test
- Format : `test_<module_name>.py`
- Exemple : `test_simulation_service.py`

### Classes de Test
- Format : `Test<ClassName>`
- Exemple : `TestSimulationService`

### Méthodes de Test
- Format : `test_<method_name>_<scenario>`
- Exemple : `test_acheter_produit_stock_insuffisant`

## 🐛 Debugging des Tests

### Mode Verbose
```bash
pytest tests/unit/ -v -s
```

### Arrêt au Premier Échec
```bash
pytest tests/unit/ -x
```

### Affichage des Variables Locales
```bash
pytest tests/unit/ --tb=long
```

## 📈 Métriques de Qualité

### Indicateurs Clés
- **Couverture de code** : Objectif > 90%
- **Temps d'exécution** : Objectif < 30 secondes pour tous les tests
- **Tests passants** : Objectif 100%

### Commandes de Vérification
```bash
# Vérification rapide
pytest tests/unit/ --tb=no -q

# Rapport de couverture
pytest tests/unit/ --cov=services --cov-report=term-missing --cov-fail-under=90
```

## 🔄 Maintenance

### Ajout de Nouveaux Tests
1. Créer le fichier `test_<module>.py`
2. Ajouter la classe `Test<ClassName>`
3. Implémenter les méthodes de test
4. Ajouter les instructions de lancement dans le docstring
5. Mettre à jour ce README si nécessaire

### Mise à Jour des Tests Existants
1. Identifier les tests à modifier
2. Mettre à jour les assertions si nécessaire
3. Vérifier que tous les tests passent
4. Mettre à jour la documentation

## 📚 Ressources

### Documentation
- [Documentation pytest](https://docs.pytest.org/)
- [Documentation coverage.py](https://coverage.readthedocs.io/)
- [Guide des tests unitaires](https://realpython.com/python-testing/)

### Exemples
- Voir `test_simulation_service.py` pour un exemple complet
- Voir `test_simple.py` pour des exemples basiques

---

**Dernière mise à jour : 10/08/2025**
**Responsable : Assistant IA**
**Version : 1.0**
