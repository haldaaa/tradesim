# Guide d'utilisation TradeSim
## Simulation économique modulaire

**Version :** 1.0.0  
**Date :** 02/08/2025  
**Architecture :** Repository Pattern + Services

---

## 📋 **Vue d'ensemble**

TradeSim est une application de simulation économique modulaire qui permet de :
- Simuler des transactions entre entreprises et fournisseurs
- Gérer des événements aléatoires (inflation, reassort, etc.)
- Suivre les budgets et performances des entreprises
- Exposer les données via une API REST
- Utiliser une architecture modulaire et extensible

## 🏗️ **Architecture**

### **Structure du projet**
```
app/
├── models/           # Modèles Pydantic
├── repositories/     # Pattern Repository
├── services/         # Logique métier
├── api/              # Endpoints FastAPI
├── config/           # Configuration centralisée
├── events/           # Événements de simulation
└── tests/            # Tests organisés
```

### **Composants principaux**

#### **1. Repository Pattern**
- **`ProduitRepository`** : Gestion des produits
- **`FournisseurRepository`** : Gestion des fournisseurs  
- **`EntrepriseRepository`** : Gestion des entreprises
- **Interface commune** pour tous les accès aux données

#### **2. Services**
- **`SimulationService`** : Orchestration de la simulation
- **`GameManagerService`** : Gestion des templates et configuration
- **`TransactionService`** : Gestion des transactions
- **`BudgetService`** : Gestion des budgets

#### **3. Événements**
- **`inflation`** : Modification des prix des produits
- **`reassort`** : Réapprovisionnement des stocks
- **`recharge_budget`** : Recharge des budgets d'entreprises
- **`variation_disponibilite`** : Activation/désactivation de produits

## 🚀 **Installation et démarrage**

### **Prérequis**
```bash
# Python 3.8+
# Environnement virtuel recommandé
```

### **Installation**
```bash
# Cloner le projet
git clone <repository>
cd tradesim/app

# Activer l'environnement virtuel
source ../venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### **Dépendances principales**
- `pydantic` : Validation des données
- `fastapi` : API REST
- `uvicorn` : Serveur ASGI
- `httpx` : Client HTTP pour les tests

## 🎮 **Utilisation**

### **📋 Guide de référence rapide**
Pour toutes les commandes CLI disponibles, consultez : **`COMMANDES_CLI.md`**

### **🌐 Transition vers l'interface web**
Pour migrer du CLI vers l'interface web, consultez : **`GUIDE_MIGRATION_CLI_WEB_UNIFIED.md`**

### **1. Initialisation du jeu**
```python
from services import game_manager_service

# Remettre le jeu à zéro
game_manager_service.reset_game()

# Vérifier l'état
summary = game_manager_service.get_game_summary()
print(f"Jeu initialisé: {summary['entreprises']['nombre']} entreprises")
```

### **2. Lancement d'une simulation**
```python
from services import simulation_service

# Réinitialiser la simulation
simulation_service.reset_simulation()

# Lancer une simulation de 10 tours
resultats = simulation_service.run_simulation_tours(10, verbose=True)

# Lancer une simulation infinie
simulation_service.run_simulation_infinite(verbose=True)
```

### **3. Gestion des transactions**
```python
from services import transaction_service, game_manager_service

# Initialiser le jeu
game_manager_service.reset_game()

# Effectuer un achat
from models import Entreprise
entreprise = Entreprise(id=1, nom="Test", pays="France", budget=1000, 
                       budget_initial=1000, types_preferes=[], strategie="moins_cher")

transaction = transaction_service.effectuer_achat(entreprise, produit_id=1, quantite=2)
if transaction:
    print(f"Achat effectué: {transaction.total}€")

# Voir les statistiques
stats = transaction_service.get_statistiques_transactions()
print(f"Nombre de transactions: {stats['nombre_transactions']}")
```

### **4. Gestion des budgets**
```python
from services import budget_service

# Ajouter du budget à une entreprise
budget_service.ajouter_budget(entreprise_id=1, montant=500)

# Recharge aléatoire
budget_service.recharge_budget_aleatoire(entreprise_id=1, min_montant=200, max_montant=600)

# Voir les statistiques
stats = budget_service.get_statistiques_budgets()
print(f"Budget total: {stats['budget_total']}€")

# Entreprises en difficulté
difficulte = budget_service.get_entreprises_en_difficulte(seuil=100)
print(f"Entreprises en difficulté: {len(difficulte)}")
```

## 🌐 **API REST**

### **Lancement du serveur**
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### **Endpoints disponibles**

#### **GET /** - Point d'entrée
```bash
curl http://localhost:8000/
```
```json
{
  "message": "Bienvenue sur TradeSim",
  "version": "1.0.0",
  "endpoints": {
    "produits": "/produits",
    "fournisseurs": "/fournisseurs",
    "entreprises": "/entreprises"
  }
}
```

#### **GET /produits** - Liste des produits actifs
```bash
curl http://localhost:8000/produits
```

#### **GET /entreprises** - Liste des entreprises
```bash
curl http://localhost:8000/entreprises
```

#### **GET /fournisseurs** - Liste des fournisseurs avec leurs produits
```bash
curl http://localhost:8000/fournisseurs
```

## 🧪 **Tests**

### **Tests de base**
```bash
# Test de l'architecture
python3 test_architecture.py

# Test des événements refactorisés
python3 test_events_refactorises.py

# Test de la refactorisation complète
python3 test_refactorisation_complete.py

# Test des services complets
python3 test_services_complets.py

# Test d'intégration complet
python3 test_integration_complete.py
```

### **Tests avec pytest**
```bash
# Lancer tous les tests
pytest tests/ -v

# Tests unitaires
pytest tests/unit/ -v

# Tests d'intégration
pytest tests/integration/ -v

# Tests API
pytest tests/api/ -v
```

## 📊 **Configuration**

### **Fichier de configuration**
```python
# config/config.py
NOMBRE_TOURS = 10
N_ENTREPRISES_PAR_TOUR = 3
DUREE_PAUSE_ENTRE_TOURS = 0.1
PROBABILITE_SELECTION_ENTREPRISE = 0.3

# Événements
TICK_INTERVAL_EVENT = 20
PROBABILITE_EVENEMENT = 0.3

# Budgets
RECHARGE_BUDGET_MIN = 200
RECHARGE_BUDGET_MAX = 600

# Stocks
REASSORT_QUANTITE_MIN = 10
REASSORT_QUANTITE_MAX = 50

# Inflation
INFLATION_POURCENTAGE_MIN = 30
INFLATION_POURCENTAGE_MAX = 60
```

## 🔧 **Développement**

### **Ajouter un nouveau service**
```python
# services/nouveau_service.py
from repositories import ProduitRepository, EntrepriseRepository

class NouveauService:
    def __init__(self):
        self.produit_repo = ProduitRepository()
        self.entreprise_repo = EntrepriseRepository()
    
    def nouvelle_fonctionnalite(self):
        # Logique métier
        pass
```

### **Ajouter un nouvel événement**
```python
# events/nouvel_evenement.py
from repositories import ProduitRepository
from events.event_logger import log_evenement_json, log_evenement_humain

def appliquer_nouvel_evenement(tick: int):
    # Logique de l'événement
    pass
```

### **Ajouter un nouvel endpoint API**
```python
# api/main.py
@app.get("/nouvel-endpoint")
def nouveau_endpoint():
    return {"message": "Nouvel endpoint"}
```

## 📈 **Monitoring et logs**

### **Logs JSONL**
```bash
# Logs pour machine (Prometheus, Grafana)
tail -f logs/tradesim.jsonl
```

### **Logs humains**
```bash
# Logs pour debugging
tail -f logs/tradesim.log
```

### **Métriques**
- Nombre de tours de simulation
- Nombre de transactions effectuées
- Budgets des entreprises
- Événements appliqués
- Performance des services

## 🔄 **Migration vers base de données**

### **Étapes de migration**
1. **Implémenter les Repository SQL**
   ```python
   # repositories/sql_produit_repository.py
   class SQLProduitRepository(ProduitRepositoryInterface):
       def __init__(self, connection_string):
           self.db = create_engine(connection_string)
   ```

2. **Configurer la base de données**
   ```python
   # config/database.py
   DATABASE_URL = "postgresql://user:password@localhost/tradesim"
   ```

3. **Migrer les données**
   ```python
   # scripts/migration.py
   def migrer_donnees():
       # Logique de migration
       pass
   ```

## 🚀 **Déploiement**

### **Docker**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Kubernetes**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tradesim
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tradesim
  template:
    metadata:
      labels:
        app: tradesim
    spec:
      containers:
      - name: tradesim
        image: tradesim:latest
        ports:
        - containerPort: 8000
```

## 📚 **Documentation technique**

### **Pattern Repository**
- **Abstraction** : Interface commune pour l'accès aux données
- **Flexibilité** : Facile de changer de source de données
- **Testabilité** : Mock des Repository pour les tests
- **Évolutivité** : Ajout facile de nouveaux Repository

### **Services**
- **Séparation des responsabilités** : Chaque service a un rôle précis
- **Réutilisabilité** : Services utilisables par CLI et API
- **Maintenabilité** : Code modulaire et organisé
- **Extensibilité** : Ajout facile de nouveaux services

### **Événements**
- **Découplage** : Événements indépendants les uns des autres
- **Configurabilité** : Probabilités et paramètres ajustables
- **Observabilité** : Logs détaillés de chaque événement
- **Extensibilité** : Ajout facile de nouveaux événements

## 🤝 **Contribution**

### **Standards de code**
- **PEP 8** : Style de code Python
- **Type hints** : Annotations de types
- **Docstrings** : Documentation des fonctions
- **Tests** : Couverture de tests élevée

### **Workflow de développement**
1. **Fork** du repository
2. **Branch** pour la fonctionnalité
3. **Développement** avec tests
4. **Pull Request** avec description
5. **Review** et merge

## 📞 **Support**

### **Issues**
- **Bug reports** : Description détaillée du problème
- **Feature requests** : Justification et cas d'usage
- **Documentation** : Améliorations de la documentation

### **Contact**
- **Email** : support@tradesim.com
- **Discord** : #tradesim-support
- **Documentation** : https://docs.tradesim.com

---

**TradeSim** - Simulation économique modulaire et extensible  
**Version 1.0.0** - Architecture Repository Pattern + Services  
**Dernière mise à jour :** 02/08/2025 