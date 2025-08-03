# Instructions pour les Tests TradeSim
=====================================

Ce fichier explique comment exécuter tous les tests de l'application TradeSim.

## 📋 Prérequis

### Installation des dépendances
```bash
# Installer pytest et les dépendances de test
pip install pytest pytest-asyncio pytest-cov fastapi httpx

# Ou avec les requirements (si disponible)
pip install -r requirements.txt
```

### Structure des tests
```
tests/
├── unit/                    # Tests unitaires
│   ├── test_models.py      # Tests des modèles Pydantic
│   ├── test_game_manager.py # Tests du gestionnaire de jeu
│   └── test_events/        # Tests des événements
│       ├── test_inflation.py
│       ├── test_reassort.py
│       ├── test_recharge_budget.py
│       └── test_variation_disponibilite.py
├── integration/            # Tests d'intégration
│   └── test_simulation_complete.py
└── api/                   # Tests API
    └── test_api_endpoints.py
```

## 🚀 Exécution des Tests

### 1. Tests Unitaires

#### Tests des Modèles Pydantic
```bash
# Test des modèles de données
python tests/unit/test_models.py

# Ou avec pytest
pytest tests/unit/test_models.py -v
```

**Ce que testent ces tests :**
- ✅ Validation des modèles Produit, Fournisseur, Entreprise
- ✅ Contraintes de données (prix > 0, stock >= 0, etc.)
- ✅ Types de données (enum TypeProduit, etc.)
- ✅ Relations entre entités

#### Tests du Game Manager
```bash
# Test des fonctions de génération et gestion
python tests/unit/test_game_manager.py

# Ou avec pytest
pytest tests/unit/test_game_manager.py -v
```

**Ce que testent ces tests :**
- ✅ Génération d'entités (produits, fournisseurs, entreprises)
- ✅ Gestion des templates de configuration
- ✅ Sauvegarde/chargement de configurations
- ✅ Performance avec beaucoup d'entités

#### Tests des Événements
```bash
# Test des événements de simulation
python tests/unit/test_events/test_inflation.py
python tests/unit/test_events/test_reassort.py
python tests/unit/test_events/test_recharge_budget.py
python tests/unit/test_events/test_variation_disponibilite.py

# Ou tous ensemble
pytest tests/unit/test_events/ -v
```

**Ce que testent ces tests :**
- ✅ Application de l'inflation sur les produits
- ✅ Réassort de stock chez les fournisseurs
- ✅ Recharge de budget des entreprises
- ✅ Variation de disponibilité des produits

### 2. Tests d'Intégration

#### Test de Simulation Complète
```bash
# Test de l'intégration complète
python tests/integration/test_simulation_complete.py

# Ou avec pytest
pytest tests/integration/test_simulation_complete.py -v
```

**Ce que testent ces tests :**
- ✅ Génération complète des données de jeu
- ✅ Simulation de tours avec achats
- ✅ Déclenchement des événements
- ✅ Cohérence des données entre modules
- ✅ Logs et monitoring
- ✅ Performance avec beaucoup d'entités

### 3. Tests API

#### Tests des Endpoints FastAPI
```bash
# Test des endpoints API
python tests/api/test_api_endpoints.py

# Ou avec pytest
pytest tests/api/test_api_endpoints.py -v
```

**Ce que testent ces tests :**
- ✅ Endpoints GET /, /produits, /fournisseurs, /entreprises
- ✅ Validation des réponses JSON
- ✅ Cohérence des données API vs base
- ✅ Gestion d'erreurs (404, 405)
- ✅ Performance de l'API

## 🎯 Exécution de Tous les Tests

### Avec pytest (recommandé)
```bash
# Tous les tests
pytest tests/ -v

# Avec couverture de code
pytest tests/ -v --cov=app --cov-report=html

# Tests spécifiques
pytest tests/unit/ -v                    # Tests unitaires seulement
pytest tests/integration/ -v             # Tests d'intégration seulement
pytest tests/api/ -v                     # Tests API seulement
```

### Exécution directe
```bash
# Tests unitaires
python tests/unit/test_models.py
python tests/unit/test_game_manager.py

# Tests d'intégration
python tests/integration/test_simulation_complete.py

# Tests API
python tests/api/test_api_endpoints.py
```

## 📊 Résultats Attendus

### Tests Unitaires
```
✅ Test TypeProduit - Tous les types sont valides
✅ Test Produit - Création valide réussie
✅ Test Produit - Prix négatif rejeté
✅ Test Fournisseur - Création valide réussie
✅ Test Entreprise - Création valide réussie
✅ Test generate_produits - Génération réussie
✅ Test generate_fournisseurs - Génération réussie
✅ Test generate_entreprises - Génération réussie
```

### Tests d'Intégration
```
✅ Test état initial - Données cohérentes
✅ Test tour unique - Simulation exécutée
✅ Test tours multiples - Simulation étendue
✅ Test événements - Déclenchement vérifié
✅ Test cohérence - Données cohérentes
✅ Test format logs - Logs valides
✅ Test performance - 10 tours en 0.XXs
```

### Tests API
```
✅ Test endpoint racine - Réponse valide
✅ Test endpoint produits - Données valides
✅ Test endpoint fournisseurs - Données valides
✅ Test endpoint entreprises - Données valides
✅ Test filtrage produits - Seuls les actifs retournés
✅ Test cohérence fournisseurs - Données cohérentes
```

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

### Variables d'environnement (optionnel)
```bash
# Pour les tests de performance
export TRADESIM_TEST_PERFORMANCE=true

# Pour les tests avec beaucoup de données
export TRADESIM_LARGE_DATASET=true
```

## 🐛 Dépannage

### Erreurs courantes

#### ModuleNotFoundError
```bash
# Solution : Ajouter le répertoire app au PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/chemin/vers/tradesim/app"
```

#### ImportError pour les modèles
```bash
# Vérifier que les imports sont corrects dans les tests
from app.models import Produit, TypeProduit, Fournisseur, Entreprise
```

#### Tests qui échouent à cause de la nature probabiliste
```bash
# Certains tests sont probabilistes (événements)
# Relancer les tests plusieurs fois si nécessaire
pytest tests/unit/test_events/ -v -x  # Arrêter au premier échec
```

### Debug des tests
```bash
# Mode verbose pour voir les détails
pytest tests/ -v -s

# Debug d'un test spécifique
pytest tests/unit/test_models.py::TestProduit::test_produit_creation_valide -v -s
```

## 📈 Métriques de Test

### Couverture de code
```bash
# Générer un rapport de couverture
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Ouvrir le rapport HTML
open htmlcov/index.html
```

### Performance des tests
```bash
# Mesurer le temps d'exécution
time pytest tests/ -v

# Tests de performance spécifiques
pytest tests/unit/test_game_manager.py::TestGameManagerPerformance -v
pytest tests/integration/test_simulation_complete.py::TestSimulationStress -v
```

## 🎯 Bonnes Pratiques

### Pour ajouter de nouveaux tests
1. **Nommage** : `test_*.py` pour les fichiers, `test_*` pour les fonctions
2. **Documentation** : Ajouter des docstrings explicites
3. **Isolation** : Chaque test doit être indépendant
4. **Setup/Teardown** : Utiliser `setup_method()` et `teardown_method()`
5. **Assertions claires** : Messages d'erreur explicites

### Structure recommandée pour un nouveau test
```python
class TestNouveauModule:
    """Tests pour le nouveau module"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        pass
    
    def teardown_method(self):
        """Cleanup après chaque test"""
        pass
    
    def test_fonctionnalite(self):
        """Test de la fonctionnalité"""
        # Arrange
        # Act
        # Assert
        print("✅ Test fonctionnalité - Succès")
```

## 🚀 Intégration Continue

### GitHub Actions (exemple)
```yaml
name: Tests TradeSim
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install pytest pytest-cov fastapi httpx
      - name: Run tests
        run: pytest tests/ -v --cov=app
```

---

**Note** : Ces tests couvrent l'ensemble de l'application TradeSim, de la validation des modèles jusqu'à l'API complète. Ils garantissent la qualité et la robustesse du code. 