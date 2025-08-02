# TradeSim - Architecture Modulaire
=====================================

## 📋 **Vue d'ensemble**

TradeSim est une application de simulation économique modulaire, conçue pour être évolutive et maintenable. L'architecture utilise le pattern Repository pour séparer la logique métier de l'accès aux données.

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

### **Mode CLI (actuel) :**
```bash
python services/simulateur.py
```

### **Mode API (futur) :**
```bash
uvicorn api.main:app --reload
```

### **Tests :**
```bash
pytest tests/ -v
```

## 📚 **Documentation par module**

- `models/README.md` - Modèles Pydantic
- `repositories/README.md` - Accès aux données
- `services/README.md` - Logique métier
- `events/README.md` - Événements de simulation
- `api/README.md` - Endpoints FastAPI
- `config/README.md` - Configuration

## 🔧 **Migration vers base de données**

L'architecture Repository permet une migration transparente :
1. Remplacer les implémentations Fake par SQL
2. Le reste du code reste identique
3. Tests et production utilisent la même interface

## 📝 **Auteur**
Assistant IA - 2024-08-02 