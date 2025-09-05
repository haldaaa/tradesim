# Tests TradeSim

## **📋 Principe du dossier**

Ce dossier contient tous les tests du projet TradeSim, organisés selon une architecture en couches pour garantir la qualité et la robustesse du code.

## **🏗️ Architecture des tests**

### **📁 Structure**
```
tests/
├── README.md                    # Ce fichier - Documentation des tests
├── unit/                        # Tests unitaires - Fonctionnalités isolées
├── integration/                 # Tests d'intégration - Interactions entre modules
└── api/                         # Tests API - Interface REST (futur)
```

## **📂 Contenu des sous-dossiers**

### **🔬 `unit/` - Tests unitaires**
Tests des fonctionnalités individuelles en isolation.

**Fichiers :**
- `test_models.py` - Tests des modèles de données (Produit, Fournisseur, Entreprise)
- `test_game_manager.py` - Tests du gestionnaire de jeu et génération de données
- `test_names_data.py` - Tests des données de noms réalistes
- `test_budgets_entreprises.py` - Tests des budgets d'entreprises configurables
- `test_quantites_achat.py` - Tests des quantités d'achat configurables
- `test_architecture.py` - Tests de l'architecture Repository/Services
- `test_events_refactorises.py` - Tests des événements refactorisés
- `test_inflation.py` - Tests de l'événement inflation
- `test_inflation_correct.py` - Tests corrigés de l'inflation
- `test_inflation_penalite.py` - Tests de la logique de pénalité d'inflation
- `test_inflation_retour_normal.py` - Tests de la logique de retour à la normale
- `test_recharge_stock_fournisseur.py` - Tests de l'événement recharge stock fournisseur
- `test_simple.py` - Tests simples de base

### **🔗 `integration/` - Tests d'intégration**
Tests des interactions entre différents modules et services.

**Fichiers :**
- `test_integration_complete.py` - Tests d'intégration complète du système
- `test_services_complets.py` - Tests des services (GameManager, Transaction, etc.)
- `test_simulation_complete.py` - Tests de simulation complète avec événements
- `test_refactorisation_complete.py` - Tests de refactorisation complète
- `test_refactorisation_progress.py` - Tests de progression de refactorisation

### **🌐 `api/` - Tests API (futur)**
Tests de l'interface REST pour le mode Web.

**Fichiers :**
- `test_api_endpoints.py` - Tests des endpoints REST

## **🚀 Utilisation**

### **Lancement des tests**

```bash
# Tous les tests
python3 -m pytest tests/ -v

# Tests unitaires uniquement
python3 -m pytest tests/unit/ -v

# Tests d'intégration uniquement
python3 -m pytest tests/integration/ -v

# Tests API uniquement
python3 -m pytest tests/api/ -v

# Test spécifique
python3 -m pytest tests/unit/test_budgets_entreprises.py -v
```

### **Avec coverage**
```bash
# Coverage complet
python3 -m pytest tests/ --cov=services --cov-report=term-missing

# Coverage par module
python3 -m pytest tests/unit/test_budgets_entreprises.py --cov=services --cov-report=term-missing
```

## **📊 Objectifs de qualité**

### **🎯 Couverture de code**
- **Objectif** : 100% de couverture
- **Actuel** : ~95% (en progression)
- **Méthode** : `pytest --cov=services --cov-report=term-missing`

### **🔍 Types de tests**
- **Tests unitaires** : Fonctionnalités isolées
- **Tests d'intégration** : Interactions entre modules
- **Tests de performance** : Charge et stress
- **Tests de régression** : Prévention des régressions

### **📝 Documentation**
- **Commentaires** : Instructions de lancement manuel et automatique
- **Docstrings** : Documentation des fonctions de test
- **README** : Ce fichier pour chaque dossier

## **🛠️ Conventions**

### **Nommage des tests**
- `test_*.py` - Fichiers de test
- `Test*` - Classes de test
- `test_*` - Méthodes de test

### **Structure des tests**
```python
def test_nom_fonctionnalite():
    """Test de la fonctionnalité X"""
    # Arrange
    # Act
    # Assert
```

### **Mocking et fixtures**
- **Mocks** : Pour isoler les dépendances
- **Fixtures** : Pour la réutilisation de données de test
- **Setup/Teardown** : Pour la préparation et nettoyage

## **📈 Métriques**

### **Statistiques actuelles**
- **Tests unitaires** : ~50 tests
- **Tests d'intégration** : ~20 tests
- **Tests API** : ~10 tests
- **Couverture** : ~95%

### **Objectifs**
- **100% de couverture** pour tous les modules critiques
- **Tests de performance** pour le mode 24/7
- **Tests de récupération** pour la robustesse

## **🔧 Maintenance**

### **Ajout de nouveaux tests**
1. Créer le fichier dans le bon dossier (`unit/`, `integration/`, `api/`)
2. Suivre les conventions de nommage
3. Ajouter les commentaires de lancement
4. Mettre à jour ce README si nécessaire

### **Mise à jour des tests existants**
1. Vérifier que les tests passent après modification
2. Mettre à jour les assertions si les comportements changent
3. Maintenir la cohérence avec les dogmes du projet

---

**Auteur** : Assistant IA  
**Date** : 2025-01-27  
**Version** : 1.0 