# Transition CLI → Web TradeSim
## Guide de migration vers l'interface web

**Date :** 02/08/2025  
**Version :** 1.0.0  
**Architecture actuelle :** Repository Pattern + Services

---

## 🎯 **Vue d'ensemble de la transition**

### **État actuel (CLI)**
- ✅ Architecture Repository Pattern implémentée
- ✅ Services modulaires (SimulationService, GameManagerService, etc.)
- ✅ API FastAPI fonctionnelle
- ✅ Tests complets
- ✅ Documentation complète

### **Objectif (Web)**
- 🌐 Interface web React + FastAPI
- 🗄️ Base de données PostgreSQL
- 🐳 Docker + Kubernetes
- 📊 Monitoring Grafana/Prometheus
- ☁️ Déploiement AWS

---

## 🏗️ **Architecture de transition**

### **Structure actuelle (CLI)**
```
app/
├── models/           # Modèles Pydantic ✅
├── repositories/     # Pattern Repository ✅
├── services/         # Logique métier ✅
├── api/              # Endpoints FastAPI ✅
├── config/           # Configuration ✅
├── events/           # Événements ✅
└── tests/            # Tests ✅
```

### **Structure cible (Web)**
```
tradesim/
├── backend/          # API FastAPI
│   ├── app/
│   │   ├── models/       # Modèles Pydantic
│   │   ├── repositories/ # Repository SQL
│   │   ├── services/     # Services métier
│   │   ├── api/          # Endpoints REST
│   │   ├── config/       # Configuration
│   │   └── events/       # Événements
│   ├── tests/            # Tests backend
│   ├── requirements.txt  # Dépendances Python
│   └── Dockerfile       # Container backend
├── frontend/         # Interface React
│   ├── src/
│   │   ├── components/   # Composants React
│   │   ├── pages/        # Pages de l'application
│   │   ├── services/     # Services API
│   │   └── utils/        # Utilitaires
│   ├── public/           # Assets statiques
│   ├── package.json      # Dépendances Node.js
│   └── Dockerfile       # Container frontend
├── docker-compose.yml   # Orchestration locale
├── kubernetes/          # Config K8s
├── terraform/           # Infrastructure AWS
└── monitoring/          # Grafana/Prometheus
```

---

## 🔄 **Étapes de migration**

### **Phase 1 : Préparation de l'API (1-2 jours)**

#### **1.1 Réorganiser la structure**
```bash
# Créer la nouvelle structure
mkdir -p backend/app
mv models repositories services api config events backend/app/
mv tests backend/
```

#### **1.2 Adapter les imports**
```python
# Avant (CLI)
from models import Produit
from services import simulation_service

# Après (Web)
from app.models import Produit
from app.services import simulation_service
```

#### **1.3 Créer requirements.txt**
```txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.0
pytest==7.4.3
httpx==0.25.2
```

#### **1.4 Créer Dockerfile backend**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Phase 2 : Migration base de données (2-3 jours)**

#### **2.1 Créer les Repository SQL**
```python
# backend/app/repositories/sql_produit_repository.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.repositories.base_repository import ProduitRepositoryInterface

class SQLProduitRepository(ProduitRepositoryInterface):
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_all(self):
        session = self.Session()
        # Logique SQL
        session.close()
```

#### **2.2 Configuration base de données**
```python
# backend/app/config/database.py
DATABASE_URL = "postgresql://user:password@localhost/tradesim"
```

#### **2.3 Migration des données**
```python
# backend/scripts/migrate_data.py
def migrate_from_fake_to_sql():
    """Migre les données des Fake Repository vers SQL"""
    # Logique de migration
    pass
```

### **Phase 3 : Interface web React (3-5 jours)**

#### **3.1 Créer l'application React**
```bash
npx create-react-app frontend
cd frontend
npm install axios react-router-dom @mui/material
```

#### **3.2 Structure frontend**
```
frontend/src/
├── components/
│   ├── Simulation.jsx      # Interface de simulation
│   ├── GameStatus.jsx      # État du jeu
│   ├── Transactions.jsx    # Historique des transactions
│   └── Budgets.jsx        # Gestion des budgets
├── pages/
│   ├── Dashboard.jsx       # Page principale
│   ├── Simulation.jsx      # Page de simulation
│   └── Settings.jsx        # Configuration
├── services/
│   └── api.js             # Appels API
└── utils/
    └── helpers.js         # Utilitaires
```

#### **3.3 Services API frontend**
```javascript
// frontend/src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // Simulation
  startSimulation: (tours) => 
    axios.post(`${API_BASE_URL}/simulation/start`, { tours }),
  
  getStatus: () => 
    axios.get(`${API_BASE_URL}/status`),
  
  // Jeu
  resetGame: () => 
    axios.post(`${API_BASE_URL}/game/reset`),
  
  // Transactions
  getTransactions: () => 
    axios.get(`${API_BASE_URL}/transactions`),
  
  // Budgets
  getBudgets: () => 
    axios.get(`${API_BASE_URL}/budgets`),
};
```

### **Phase 4 : Déploiement (2-3 jours)**

#### **4.1 Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db/tradesim
    depends_on:
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=tradesim
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### **4.2 Kubernetes**
```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tradesim-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tradesim-backend
  template:
    metadata:
      labels:
        app: tradesim-backend
    spec:
      containers:
      - name: backend
        image: tradesim-backend:latest
        ports:
        - containerPort: 8000
```

---

## 🔧 **Commandes de transition**

### **Démarrage rapide (développement)**
```bash
# 1. Lancer l'API
cd backend
uvicorn app.api.main:app --reload

# 2. Lancer le frontend
cd frontend
npm start

# 3. Accéder à l'application
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### **Déploiement Docker**
```bash
# 1. Construire les images
docker-compose build

# 2. Lancer l'application
docker-compose up -d

# 3. Vérifier les services
docker-compose ps
```

### **Déploiement Kubernetes**
```bash
# 1. Appliquer les configurations
kubectl apply -f kubernetes/

# 2. Vérifier les pods
kubectl get pods

# 3. Accéder à l'application
kubectl port-forward service/tradesim-frontend 3000:3000
```

---

## 📊 **Migration des fonctionnalités**

### **CLI → Web mapping**

| Fonctionnalité CLI | Équivalent Web |
|-------------------|----------------|
| `--status` | Dashboard avec état en temps réel |
| `--tours 10` | Bouton "Lancer simulation" + slider |
| `--verbose` | Logs en temps réel dans l'interface |
| `--reset` | Bouton "Nouvelle partie" |
| `--cheat` | Interface admin avec ajout de budget |
| `--save-template` | Sauvegarde dans la base de données |
| `--load-template` | Sélecteur de templates |

### **Endpoints API nécessaires**
```python
# Simulation
POST /api/simulation/start
GET /api/simulation/status
POST /api/simulation/stop

# Jeu
GET /api/game/status
POST /api/game/reset
POST /api/game/new

# Transactions
GET /api/transactions
GET /api/transactions/recent
POST /api/transactions/simulate

# Budgets
GET /api/budgets
POST /api/budgets/add
GET /api/budgets/statistics

# Templates
GET /api/templates
POST /api/templates/save
POST /api/templates/load
```

---

## 🧪 **Tests de transition**

### **Tests backend**
```bash
# Tests unitaires
pytest backend/tests/unit/

# Tests d'intégration
pytest backend/tests/integration/

# Tests API
pytest backend/tests/api/
```

### **Tests frontend**
```bash
# Tests unitaires
npm test

# Tests E2E
npm run test:e2e
```

### **Tests de déploiement**
```bash
# Test Docker
docker-compose up --build

# Test Kubernetes
kubectl apply -f kubernetes/
kubectl get pods
```

---

## 📈 **Monitoring et observabilité**

### **Logs**
```python
# backend/app/config/logging.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### **Métriques Prometheus**
```python
# backend/app/monitoring/metrics.py
from prometheus_client import Counter, Histogram

simulation_counter = Counter('tradesim_simulations_total', 'Total simulations')
transaction_counter = Counter('tradesim_transactions_total', 'Total transactions')
```

### **Grafana Dashboard**
```json
{
  "dashboard": {
    "title": "TradeSim Metrics",
    "panels": [
      {
        "title": "Simulations per hour",
        "type": "graph"
      },
      {
        "title": "Active transactions",
        "type": "stat"
      }
    ]
  }
}
```

---

## 🚨 **Points d'attention**

### **Sécurité**
- Authentification JWT pour l'API
- CORS configuré pour le frontend
- Validation des données côté serveur
- Rate limiting sur les endpoints

### **Performance**
- Cache Redis pour les données fréquentes
- Pagination pour les grandes listes
- Optimisation des requêtes SQL
- CDN pour les assets statiques

### **Scalabilité**
- Load balancing avec Kubernetes
- Auto-scaling basé sur les métriques
- Base de données en cluster
- Cache distribué

---

## 📚 **Documentation de transition**

### **Pour les développeurs**
- Guide de développement local
- Documentation de l'API
- Standards de code
- Workflow Git

### **Pour les opérations**
- Guide de déploiement
- Configuration monitoring
- Procédures de backup
- Plan de reprise d'activité

### **Pour les utilisateurs**
- Guide d'utilisation web
- Tutoriels vidéo
- FAQ
- Support utilisateur

---

## 🎯 **Timeline de transition**

### **Semaine 1**
- [ ] Réorganisation structure backend
- [ ] Migration base de données
- [ ] Tests backend

### **Semaine 2**
- [ ] Développement frontend React
- [ ] Intégration API
- [ ] Tests frontend

### **Semaine 3**
- [ ] Dockerisation
- [ ] Déploiement Kubernetes
- [ ] Monitoring

### **Semaine 4**
- [ ] Tests de charge
- [ ] Optimisations
- [ ] Documentation finale

---

**TradeSim** - Transition CLI → Web  
**Architecture :** Repository Pattern + Services  
**Objectif :** Interface web moderne et scalable  
**Dernière mise à jour :** 02/08/2025 