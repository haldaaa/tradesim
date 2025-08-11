# 🎮 TradeSim - Simulation Économique Modulaire
==============================================

## 📋 **Vue d'ensemble**

TradeSim est une application de simulation économique modulaire et évolutive, conçue pour simuler des transactions entre entreprises et fournisseurs avec des événements dynamiques (inflation, recharge de budget, etc.). L'architecture utilise le pattern Repository pour séparer la logique métier de l'accès aux données.

## 🎯 **Fonctionnalités principales**

- **Simulation économique** : Transactions entre entreprises et fournisseurs
- **Événements dynamiques** : Inflation, recharge de budget, réassortiment
- **Monitoring en temps réel** : Métriques Prometheus et dashboards Grafana
- **Logging structuré** : Logs humains et JSON pour analyse
- **Thread-safety** : Cache optimisé et accès concurrent sécurisé
- **Validation robuste** : Vérification des données et configurations

## 🏗️ **Structure du projet**

```
app/
├── models/           # Modèles Pydantic (entités)
├── repositories/     # Accès aux données (Repository pattern)
├── services/        # Logique métier (simulation, événements)
├── events/          # Événements de simulation
├── api/             # Endpoints FastAPI
├── config/          # Configuration
└── tests/           # Tests organisés par module
```

## 🔄 **Pattern Repository**

### **Principe :**
- **Interface commune** pour tous les accès aux données
- **Implémentations multiples** : In-memory (tests) + Base de données (prod)
- **Code identique** pour CLI et Web

### **Exemple :**
```python
# Interface commune
class ProduitRepository:
    def get_all(self) -> List[Produit]: pass
    def get_by_id(self, id: int) -> Produit: pass
    def add(self, produit: Produit) -> None: pass

# Implémentation In-memory (pour les tests)
class FakeProduitRepository(ProduitRepository):
    def get_all(self) -> List[Produit]:
        return fake_produits_db

# Implémentation SQL (pour la production)
class SQLProduitRepository(ProduitRepository):
    def get_all(self) -> List[Produit]:
        return db.query(Produit).all()
```

## 🚀 **Utilisation**

### **Lancement rapide :**
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Nouvelle partie
python services/simulate.py --new-game

# Simulation de 10 tours
python services/simulate.py --tours 10

# Simulation infinie avec monitoring
python services/simulate.py --infinite --with-metrics
```

### **Mode API :**
```bash
# Lancer l'API
uvicorn api.main:app --reload

# Accéder aux métriques
curl http://localhost:8000/metrics
```

### **Monitoring Prometheus/Grafana :**
```bash
# Lancer le monitoring
cd monitoring && docker-compose up -d

# Accéder à Grafana
# http://localhost:3000 (admin/admin)
```

### **Tests :**
```bash
# Tests unitaires
pytest tests/unit/ -v

# Tests d'intégration
pytest tests/integration/ -v

# Tests avec couverture
pytest tests/ --cov=services --cov-report=html
```

## 📚 **Documentation par module**

- `models/README.md` - Modèles Pydantic (entités)
- `repositories/README.md` - Accès aux données (Repository pattern)
- `services/README.md` - Logique métier (simulation, métriques)
- `events/README.md` - Événements de simulation (inflation, recharge, etc.)
- `api/README.md` - Endpoints FastAPI (API REST)
- `config/README.md` - Configuration centralisée
- `monitoring/README.md` - Monitoring Prometheus/Grafana
- `tests/README.md` - Tests unitaires et d'intégration

## 🔧 **Changement de mode CLI ↔ Web**

L'architecture Repository permet de basculer facilement entre CLI et Web :

### **Mode CLI (développement) :**
```python
# config/mode.py
CURRENT_MODE = ExecutionMode.CLI  # Données en mémoire
```

### **Mode Web (production) :**
```python
# config/mode.py  
CURRENT_MODE = ExecutionMode.WEB  # Base de données
```

### **Instructions de changement :**

1. **Ouvrir** `config/mode.py`
2. **Modifier** la variable `CURRENT_MODE`
3. **Redémarrer** l'application
4. **Tester** le bon fonctionnement

### **Avantages :**
- ✅ **Un seul fichier** à modifier
- ✅ **Code identique** pour CLI et Web
- ✅ **Migration transparente** sans refactorisation
- ✅ **Tests automatisés** pour vérifier le bon fonctionnement

## 🔄 **Dernières améliorations (11/08/2025)**

- **Thread-safety** : Cache optimisé avec verrous pour accès concurrent
- **Logging structuré** : Logs humains et JSON pour traçabilité complète
- **Validation robuste** : Vérification des configurations et données
- **Tests de performance** : Tests de charge et thread-safety
- **Monitoring avancé** : Métriques Prometheus et dashboards Grafana
- **Documentation complète** : README détaillés pour chaque module

## 📊 **Métriques disponibles**

- **Budget** : Revenus, dépenses, ratios
- **Entreprises** : Performance, stratégies
- **Produits** : Prix, stocks, disponibilité
- **Fournisseurs** : Stocks, prix, performance
- **Transactions** : Volume, succès, échecs
- **Événements** : Fréquence, impact
- **Performance** : Latences, débits

---
**Auteur** : Assistant IA  
**Dernière mise à jour** : 11/08/2025  
**Version** : 1.5.0 - Corrections finales appliquées

### **Migration vers base de données :**
1. Remplacer les implémentations Fake par SQL
2. Le reste du code reste identique
3. Tests et production utilisent la même interface

**Guide détaillé :** `GUIDE_MIGRATION_CLI_WEB_UNIFIED.md`

## 📝 **Auteur**
Assistant IA - 2024-08-02 