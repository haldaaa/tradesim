# API - Endpoints FastAPI TradeSim
==================================

## 📋 **Vue d'ensemble**

Le dossier `api/` contient l'interface REST de TradeSim, construite avec FastAPI. L'API expose les fonctionnalités de TradeSim via des endpoints HTTP, permettant l'intégration avec des applications web.

**MODE CLI (développement) :** API utilisée pour les tests et le développement
**MODE WEB (production) :** API principale pour l'interface utilisateur

## 🏗️ **Architecture**

### **FastAPI Framework :**
- **Performance** : Basé sur Starlette et Pydantic
- **Documentation automatique** : Swagger UI et ReDoc
- **Validation** : Validation automatique des données
- **Type hints** : Support complet des types Python

### **Structure :**
```
api/
├── __init__.py      # Exports de l'API
├── main.py          # Endpoints FastAPI
└── README.md        # Cette documentation
```

## 📁 **Endpoints disponibles**

### **GET /** - Point d'entrée
```bash
curl http://localhost:8000/
```
**Réponse :**
```json
{
  "message": "Bienvenue sur TradeSim",
  "version": "1.0.0",
  "mode": "CLI",
  "endpoints": {
    "produits": "/produits",
    "fournisseurs": "/fournisseurs", 
    "entreprises": "/entreprises"
  }
}
```

### **GET /produits** - Liste des produits actifs
```bash
curl http://localhost:8000/produits
```
**Réponse :**
```json
[
  {
    "id": 1,
    "nom": "Bois",
    "prix": 25.50,
    "actif": true,
    "type": "matiere_premiere"
  }
]
```

### **GET /entreprises** - Liste des entreprises
```bash
curl http://localhost:8000/entreprises
```
**Réponse :**
```json
[
  {
    "id": 1,
    "nom": "MagaToys",
    "pays": "France",
    "budget": 1500.0,
    "strategie": "moins_cher",
    "types_preferes": ["matiere_premiere"]
  }
]
```

### **GET /fournisseurs** - Liste des fournisseurs
```bash
curl http://localhost:8000/fournisseurs
```
**Réponse :**
```json
[
  {
    "id": 1,
    "nom_entreprise": "PlancheCompagnie",
    "pays": "France",
    "stock_produit": {
      "1": 50,
      "2": 30
    }
  }
]
```

## 🔧 **Utilisation**

### **Lancement du serveur :**
```bash
# Mode développement
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Mode production
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Documentation automatique :**
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### **Tests de l'API :**
```bash
# Tests unitaires
pytest tests/api/ -v

# Tests d'intégration
pytest tests/integration/test_api_integration.py -v
```

## 🎯 **Avantages de cette architecture**

### **Performance :**
- ✅ **Asynchrone** : Gestion efficace des requêtes concurrentes
- ✅ **Validation automatique** : Pydantic pour la validation des données
- ✅ **Documentation automatique** : Swagger UI généré automatiquement

### **Développement :**
- ✅ **Hot reload** : Redémarrage automatique lors des modifications
- ✅ **Type hints** : Support complet des types Python
- ✅ **Tests automatisés** : Tests unitaires et d'intégration

### **Production :**
- ✅ **Scalabilité** : Support de multiples workers
- ✅ **Sécurité** : Validation et sanitisation des données
- ✅ **Monitoring** : Logs détaillés et métriques

## 📝 **Exemples d'utilisation**

### **Client Python :**
```python
import httpx

async with httpx.AsyncClient() as client:
    # Récupérer les produits
    response = await client.get("http://localhost:8000/produits")
    produits = response.json()
    
    # Récupérer les entreprises
    response = await client.get("http://localhost:8000/entreprises")
    entreprises = response.json()
```

### **Client JavaScript :**
```javascript
// Récupérer les produits
const response = await fetch('http://localhost:8000/produits');
const produits = await response.json();

// Récupérer les entreprises
const response = await fetch('http://localhost:8000/entreprises');
const entreprises = await response.json();
```

### **Client cURL :**
```bash
# Récupérer tous les produits
curl -X GET "http://localhost:8000/produits" \
  -H "accept: application/json"

# Récupérer toutes les entreprises
curl -X GET "http://localhost:8000/entreprises" \
  -H "accept: application/json"
```

## 🔄 **Migration CLI → Web**

### **Étape 1 : Vérifier le mode**
```python
# Dans api/main.py
from config.mode import get_current_mode

@app.get("/")
def root():
    mode = get_current_mode()
    return {
        "message": "Bienvenue sur TradeSim",
        "mode": mode.value,
        "endpoints": {...}
    }
```

### **Étape 2 : Adapter les endpoints**
```python
# Les endpoints utilisent déjà les Repository
# Pas de modification nécessaire !
```

### **Étape 3 : Tester l'API**
```bash
# Lancer le serveur
uvicorn api.main:app --reload

# Tester les endpoints
curl http://localhost:8000/
curl http://localhost:8000/produits
curl http://localhost:8000/entreprises
```

## 📚 **Documentation technique**

### **FastAPI Features :**
- **Automatic docs** : Documentation générée automatiquement
- **Request validation** : Validation automatique des requêtes
- **Response serialization** : Sérialisation automatique des réponses
- **OpenAPI** : Spécification OpenAPI 3.0

### **Repository Integration :**
- **Abstraction** : API utilise les Repository pour l'accès aux données
- **Mode agnostic** : Même code pour CLI et Web
- **Tests** : Tests unitaires et d'intégration
- **Performance** : Optimisé pour les requêtes concurrentes

### **Error Handling :**
```python
from fastapi import HTTPException

@app.get("/produits/{produit_id}")
def get_produit(produit_id: int):
    produit = produit_repo.get_by_id(produit_id)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return produit
```

## 🧪 **Tests**

### **Tests unitaires :**
```bash
pytest tests/api/test_api_endpoints.py -v
```

### **Tests d'intégration :**
```bash
pytest tests/integration/test_api_integration.py -v
```

### **Tests de performance :**
```bash
# Avec locust
locust -f tests/performance/locustfile.py
```

## 📝 **Auteur**
Assistant IA - 2024-08-02 