# API - Endpoints FastAPI
============================

## 📋 **Vue d'ensemble**

Le module `api` contient tous les endpoints FastAPI de TradeSim.
Cette couche expose les fonctionnalités de l'application via une API REST
qui peut être utilisée par une interface web ou d'autres clients.

## 🏗️ **Architecture**

### **Endpoints disponibles :**
- `GET /` - Informations générales sur l'API
- `GET /produits` - Liste des produits disponibles
- `GET /fournisseurs` - Liste des fournisseurs avec leurs stocks
- `GET /entreprises` - Liste des entreprises
- `POST /simulation/start` - Démarrer une simulation
- `GET /simulation/status` - État actuel de la simulation

### **Avantages FastAPI :**
- ✅ **Documentation automatique** (Swagger/OpenAPI)
- ✅ **Validation automatique** des données (Pydantic)
- ✅ **Performance élevée** (basé sur Starlette)
- ✅ **Type hints** complets
- ✅ **Async/await** support

## 📁 **Structure**

```
api/
├── __init__.py              # Exports de l'API
├── main.py                  # Application FastAPI principale
├── endpoints/               # Endpoints organisés par module
│   ├── __init__.py
│   ├── produits.py         # Endpoints pour les produits
│   ├── fournisseurs.py     # Endpoints pour les fournisseurs
│   ├── entreprises.py      # Endpoints pour les entreprises
│   └── simulation.py       # Endpoints pour la simulation
├── middleware/              # Middleware personnalisé
│   └── logging.py          # Middleware de logging
└── README.md               # Cette documentation
```

## 🔧 **Utilisation**

### **Démarrer l'API :**
```bash
# Mode développement
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Mode production
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### **Accéder à la documentation :**
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **OpenAPI JSON** : http://localhost:8000/openapi.json

### **Exemple de requête :**
```bash
# Récupérer tous les produits
curl http://localhost:8000/produits

# Récupérer les fournisseurs
curl http://localhost:8000/fournisseurs

# Démarrer une simulation
curl -X POST http://localhost:8000/simulation/start \
  -H "Content-Type: application/json" \
  -d '{"tours": 10, "verbose": true}'
```

## 📝 **Endpoints détaillés**

### **GET /**
```python
@app.get("/")
def read_root():
    """
    Endpoint racine - Informations générales sur l'API.
    
    Returns:
        Dict: Informations sur l'API TradeSim
    """
    return {
        "message": "TradeSim API",
        "version": "1.0.0",
        "description": "API de simulation économique",
        "endpoints": {
            "produits": "/produits",
            "fournisseurs": "/fournisseurs", 
            "entreprises": "/entreprises",
            "simulation": "/simulation"
        }
    }
```

### **GET /produits**
```python
@app.get("/produits", response_model=List[Produit])
def get_produits():
    """
    Récupère tous les produits disponibles.
    
    Returns:
        List[Produit]: Liste des produits avec validation Pydantic
    """
    produit_repo = ProduitRepository()
    return produit_repo.get_all()
```

### **GET /fournisseurs**
```python
@app.get("/fournisseurs", response_model=List[FournisseurComplet])
def get_fournisseurs_enrichis():
    """
    Récupère tous les fournisseurs avec leurs stocks enrichis.
    
    Returns:
        List[FournisseurComplet]: Liste des fournisseurs avec stocks détaillés
    """
    fournisseur_repo = FournisseurRepository()
    return fournisseur_repo.get_all_enriched()
```

### **GET /entreprises**
```python
@app.get("/entreprises", response_model=List[Entreprise])
def get_entreprises():
    """
    Récupère toutes les entreprises.
    
    Returns:
        List[Entreprise]: Liste des entreprises
    """
    entreprise_repo = EntrepriseRepository()
    return entreprise_repo.get_all()
```

### **POST /simulation/start**
```python
@app.post("/simulation/start")
def start_simulation(config: SimulationConfig):
    """
    Démarre une nouvelle simulation.
    
    Args:
        config (SimulationConfig): Configuration de la simulation
        
    Returns:
        Dict: Résultats de la simulation
    """
    simulation_service = SimulationService()
    return simulation_service.run_simulation(
        tours=config.tours,
        verbose=config.verbose
    )
```

### **GET /simulation/status**
```python
@app.get("/simulation/status")
def get_simulation_status():
    """
    Récupère l'état actuel de la simulation.
    
    Returns:
        Dict: État de la simulation (tick, statistiques, etc.)
    """
    simulation_service = SimulationService()
    return simulation_service.get_current_state()
```

## 🧪 **Tests**

### **Tests unitaires :**
```bash
pytest tests/unit/test_api.py -v
```

### **Tests d'intégration :**
```bash
pytest tests/integration/test_api_integration.py -v
```

### **Tests avec httpx :**
```python
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_get_produits():
    response = client.get("/produits")
    assert response.status_code == 200
    assert len(response.json()) > 0
```

## 🔄 **Migration vers base de données**

### **Avec Repository :**
```python
# L'API utilise les Repository, donc la migration est transparente
@app.get("/produits")
def get_produits():
    # Utilise le Repository (Fake ou SQL)
    produit_repo = ProduitRepository()
    return produit_repo.get_all()
```

### **Avantages :**
- ✅ **Code identique** pour CLI et API
- ✅ **Migration transparente** vers SQL
- ✅ **Tests simplifiés** avec Repository Fake

## 📚 **Exemples d'utilisation**

### **Interface web (futur) :**
```javascript
// Récupérer les produits
fetch('/api/produits')
  .then(response => response.json())
  .then(produits => {
    console.log('Produits:', produits);
  });

// Démarrer une simulation
fetch('/api/simulation/start', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({tours: 100, verbose: true})
})
.then(response => response.json())
.then(resultat => {
  console.log('Simulation terminée:', resultat);
});
```

### **Client Python :**
```python
import requests

# Récupérer les produits
response = requests.get('http://localhost:8000/produits')
produits = response.json()

# Démarrer une simulation
response = requests.post('http://localhost:8000/simulation/start', 
                       json={'tours': 10, 'verbose': True})
resultat = response.json()
```

## 🔧 **Configuration**

### **Mode de développement :**
```python
# Dans main.py
app = FastAPI(
    title="TradeSim API",
    description="API de simulation économique",
    version="1.0.0",
    debug=True
)
```

### **Mode de production :**
```python
# Dans main.py
app = FastAPI(
    title="TradeSim API",
    description="API de simulation économique",
    version="1.0.0",
    debug=False
)
```

### **CORS (pour l'interface web) :**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📝 **Auteur**
Assistant IA - 2024-08-02 