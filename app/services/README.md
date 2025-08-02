# Services - Logique métier
============================

## 📋 **Vue d'ensemble**

Le module `services` contient toute la logique métier de TradeSim.
Cette couche sépare la logique de simulation de l'accès aux données (Repository)
et des événements (Events).

## 🏗️ **Architecture**

### **Services disponibles :**
- `SimulationService` - Orchestration de la simulation
- `GameManagerService` - Gestion du jeu et des templates
- `TransactionService` - Gestion des transactions
- `BudgetService` - Gestion des budgets des entreprises

### **Avantages de cette architecture :**
- ✅ **Séparation des responsabilités** : Logique métier isolée
- ✅ **Testabilité** : Services facilement mockables
- ✅ **Réutilisabilité** : Services utilisables par CLI et API
- ✅ **Maintenabilité** : Code organisé et modulaire

## 📁 **Structure**

```
services/
├── __init__.py              # Exports des services
├── simulation_service.py    # Orchestration de la simulation
├── game_manager_service.py  # Gestion du jeu
├── transaction_service.py   # Gestion des transactions
├── budget_service.py        # Gestion des budgets
└── README.md               # Cette documentation
```

## 🔧 **Utilisation**

### **Import des services :**
```python
from services import SimulationService, GameManagerService
```

### **Utilisation du SimulationService :**
```python
# Créer le service
simulation_service = SimulationService()

# Lancer une simulation
resultat = simulation_service.run_simulation(tours=10, verbose=True)

# Obtenir l'état actuel
etat = simulation_service.get_current_state()
```

### **Utilisation du GameManagerService :**
```python
# Créer le service
game_service = GameManagerService()

# Générer de nouvelles données de jeu
game_service.generate_new_game()

# Sauvegarder un template
game_service.save_template("mon_template")

# Charger un template
game_service.load_template("mon_template")
```

## 📝 **Services détaillés**

### **SimulationService**
```python
class SimulationService:
    """
    Service principal pour orchestrer la simulation.
    
    Ce service coordonne :
    - La sélection des entreprises
    - Les achats de produits
    - Le déclenchement des événements
    - La génération des logs
    """
    
    def __init__(self):
        self.produit_repo = ProduitRepository()
        self.fournisseur_repo = FournisseurRepository()
        self.entreprise_repo = EntrepriseRepository()
        self.tick = 0
    
    def run_simulation(self, tours: int, verbose: bool = False):
        """Lance une simulation complète."""
        pass
    
    def run_single_tick(self, verbose: bool = False):
        """Exécute un seul tick de simulation."""
        pass
    
    def get_current_state(self):
        """Retourne l'état actuel de la simulation."""
        pass
```

### **GameManagerService**
```python
class GameManagerService:
    """
    Service pour gérer les configurations de jeu.
    
    Ce service gère :
    - La génération de nouvelles parties
    - La sauvegarde/chargement de templates
    - La configuration des paramètres
    """
    
    def generate_new_game(self, config: Dict[str, Any]):
        """Génère une nouvelle partie avec la configuration donnée."""
        pass
    
    def save_template(self, nom: str):
        """Sauvegarde la configuration actuelle comme template."""
        pass
    
    def load_template(self, nom: str):
        """Charge un template de configuration."""
        pass
```

### **TransactionService**
```python
class TransactionService:
    """
    Service pour gérer les transactions entre entreprises et fournisseurs.
    
    Ce service gère :
    - La validation des achats
    - Le calcul des prix
    - La mise à jour des stocks
    - La génération des logs de transaction
    """
    
    def process_purchase(self, entreprise: Entreprise, 
                        produit: Produit, fournisseur: Fournisseur):
        """Traite un achat entre une entreprise et un fournisseur."""
        pass
    
    def validate_purchase(self, entreprise: Entreprise, 
                         produit: Produit, fournisseur: Fournisseur):
        """Valide si un achat est possible."""
        pass
```

### **BudgetService**
```python
class BudgetService:
    """
    Service pour gérer les budgets des entreprises.
    
    Ce service gère :
    - La recharge de budget
    - La validation des achats
    - Le suivi des dépenses
    """
    
    def recharge_budget(self, entreprise: Entreprise, montant: float):
        """Recharge le budget d'une entreprise."""
        pass
    
    def can_afford(self, entreprise: Entreprise, montant: float):
        """Vérifie si une entreprise peut se permettre un achat."""
        pass
```

## 🧪 **Tests**

### **Tests unitaires :**
```bash
pytest tests/unit/test_services.py -v
```

### **Tests d'intégration :**
```bash
pytest tests/integration/test_services_integration.py -v
```

### **Exemple de test :**
```python
def test_simulation_service():
    # Arrange
    service = SimulationService()
    
    # Act
    resultat = service.run_single_tick()
    
    # Assert
    assert resultat is not None
    assert service.tick == 1
```

## 🔄 **Migration vers base de données**

### **Avec Repository :**
```python
class SimulationService:
    def __init__(self):
        # Utilise les Repository au lieu d'accès directs
        self.produit_repo = ProduitRepository()
        self.fournisseur_repo = FournisseurRepository()
        self.entreprise_repo = EntrepriseRepository()
    
    def get_produits_disponibles(self):
        # Utilise le Repository
        return self.produit_repo.get_actifs()
```

### **Avantages :**
- ✅ **Code identique** pour CLI et Web
- ✅ **Facilité de test** avec des Repository Fake
- ✅ **Migration transparente** vers SQL

## 📚 **Exemples d'utilisation**

### **Dans le CLI :**
```python
from services import SimulationService

def main():
    service = SimulationService()
    service.run_simulation(tours=100, verbose=True)
```

### **Dans l'API :**
```python
from fastapi import FastAPI
from services import SimulationService

app = FastAPI()
simulation_service = SimulationService()

@app.post("/simulation/start")
def start_simulation(tours: int):
    return simulation_service.run_simulation(tours=tours)
```

### **Dans les événements :**
```python
from services import BudgetService

def appliquer_recharge_budget():
    budget_service = BudgetService()
    entreprises = entreprise_repo.get_all()
    
    for entreprise in entreprises:
        budget_service.recharge_budget(entreprise, 200.0)
```

## 🔧 **Configuration**

### **Mode de développement :**
```python
# Utilise les Repository Fake
SIMULATION_MODE = "development"
```

### **Mode de production :**
```python
# Utilise les Repository SQL
SIMULATION_MODE = "production"
```

## 📝 **Auteur**
Assistant IA - 2024-08-02 