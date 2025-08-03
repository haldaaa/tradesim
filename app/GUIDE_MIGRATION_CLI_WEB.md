# Guide de Migration CLI → Web - TradeSim
==========================================

## 📋 **Vue d'ensemble**

Ce guide explique comment basculer TradeSim du mode CLI (développement) vers le mode Web (production). Grâce à l'architecture Repository, cette migration est **très simple** et ne nécessite qu'un changement de configuration.

## 🎯 **Objectif**

**Avant :** Mode CLI avec données en mémoire
**Après :** Mode Web avec base de données

## 🔧 **Étapes de migration**

### **Étape 1 : Changer le mode d'exécution**

Ouvrir le fichier `config/mode.py` et modifier :

```python
# MODE CLI (développement) - Données en mémoire
CURRENT_MODE = ExecutionMode.CLI

# MODE WEB (production) - Base de données  
CURRENT_MODE = ExecutionMode.WEB
```

### **Étape 2 : Vérifier la configuration**

Le système utilise automatiquement :
- **Mode CLI** : `FakeProduitRepository`, `FakeFournisseurRepository`, `FakeEntrepriseRepository`
- **Mode Web** : `SQLProduitRepository`, `SQLFournisseurRepository`, `SQLEntrepriseRepository`

### **Étape 3 : Tester la migration**

```bash
# Tests de validation
pytest tests/ -v

# Test de l'API
uvicorn api.main:app --reload
curl http://localhost:8000/
```

## ✅ **Avantages de cette approche**

### **Simplicité :**
- ✅ **Un seul fichier** à modifier (`config/mode.py`)
- ✅ **Code identique** pour CLI et Web
- ✅ **Pas de refactorisation** nécessaire
- ✅ **Migration transparente**

### **Fiabilité :**
- ✅ **Tests automatisés** pour vérifier le bon fonctionnement
- ✅ **Validation automatique** des données
- ✅ **Logs détaillés** pour le debugging
- ✅ **Rollback facile** en cas de problème

### **Performance :**
- ✅ **Mode CLI** : Rapide pour les tests et le développement
- ✅ **Mode Web** : Persistant et scalable pour la production
- ✅ **Même interface** : Pas de changement dans le code métier

## 📁 **Fichiers concernés**

### **Configuration :**
- `config/mode.py` - **Fichier principal à modifier**

### **Repository (automatique) :**
- `repositories/produit_repository.py` - Utilise le bon Repository selon le mode
- `repositories/fournisseur_repository.py` - Utilise le bon Repository selon le mode
- `repositories/entreprise_repository.py` - Utilise le bon Repository selon le mode

### **Services (inchangés) :**
- `services/game_manager.py` - Utilise les Repository (mode agnostique)
- `services/simulateur.py` - Utilise les Repository (mode agnostique)
- `services/transaction_service.py` - Utilise les Repository (mode agnostique)

### **Événements (inchangés) :**
- `events/inflation.py` - Utilise les Repository (mode agnostique)
- `events/reassort.py` - Utilise les Repository (mode agnostique)
- `events/recharge_budget.py` - Utilise les Repository (mode agnostique)

### **API (inchangée) :**
- `api/main.py` - Utilise les Repository (mode agnostique)

## 🔄 **Exemples de migration**

### **Migration complète :**

```bash
# 1. Changer le mode
echo "CURRENT_MODE = ExecutionMode.WEB" > config/mode.py

# 2. Tester la migration
pytest tests/ -v

# 3. Lancer l'API
uvicorn api.main:app --reload

# 4. Vérifier le bon fonctionnement
curl http://localhost:8000/
```

### **Rollback en cas de problème :**

```bash
# Revenir au mode CLI
echo "CURRENT_MODE = ExecutionMode.CLI" > config/mode.py

# Tester le rollback
pytest tests/ -v
```

## 🧪 **Tests de validation**

### **Tests automatiques :**
```bash
# Tests unitaires
pytest tests/unit/ -v

# Tests d'intégration
pytest tests/integration/ -v

# Tests API
pytest tests/api/ -v
```

### **Tests manuels :**
```bash
# Test de l'API
curl http://localhost:8000/produits
curl http://localhost:8000/entreprises
curl http://localhost:8000/fournisseurs

# Test de la simulation
python services/simulateur.py
```

## 📊 **Vérification de la migration**

### **Indicateurs de succès :**
- ✅ **Tests passent** : Tous les tests unitaires et d'intégration passent
- ✅ **API fonctionne** : Les endpoints retournent les bonnes données
- ✅ **Simulation fonctionne** : La simulation s'exécute sans erreur
- ✅ **Logs cohérents** : Les logs indiquent le bon mode d'exécution

### **Indicateurs de problème :**
- ❌ **Tests échouent** : Vérifier la configuration de la base de données
- ❌ **API erreur 500** : Vérifier les Repository SQL
- ❌ **Simulation plante** : Vérifier les données de test
- ❌ **Logs d'erreur** : Vérifier la configuration

## 🔧 **Configuration avancée**

### **Variables d'environnement :**
```bash
# Mode d'exécution
export TRADESIM_MODE=WEB

# Configuration de la base de données
export DATABASE_URL=postgresql://user:password@localhost/tradesim
```

### **Configuration par fichier :**
```python
# config/database.py
DATABASE_URL = "postgresql://user:password@localhost/tradesim"
DATABASE_POOL_SIZE = 10
DATABASE_MAX_OVERFLOW = 20
```

## 📚 **Documentation technique**

### **Architecture Repository :**
- **Interface commune** : Tous les Repository ont la même interface
- **Implémentations multiples** : Fake (CLI) et SQL (Web)
- **Injection de dépendances** : Les services utilisent les Repository
- **Tests automatisés** : Validation du bon fonctionnement

### **Pattern de configuration :**
- **Centralisation** : Toute la config dans `config/mode.py`
- **Validation** : Vérification automatique du mode
- **Documentation** : Commentaires détaillés pour chaque mode
- **Tests** : Tests automatisés pour chaque mode

## 🚀 **Déploiement en production**

### **Étape 1 : Préparer l'environnement**
```bash
# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données
python scripts/setup_database.py
```

### **Étape 2 : Changer le mode**
```python
# config/mode.py
CURRENT_MODE = ExecutionMode.WEB
```

### **Étape 3 : Déployer**
```bash
# Lancer l'API en production
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Ou avec Docker
docker build -t tradesim .
docker run -p 8000:8000 tradesim
```

## 📝 **Auteur**
Assistant IA - 2024-08-02 