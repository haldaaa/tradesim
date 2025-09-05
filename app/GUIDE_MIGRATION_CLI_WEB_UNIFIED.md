# Guide de Migration CLI ↔ Web - TradeSim
==========================================

## 📋 **Vue d'ensemble**

Ce guide explique comment basculer TradeSim entre le mode CLI (développement) et le mode Web (production). Grâce à l'architecture Repository, cette migration est **très simple** et ne nécessite qu'un changement de configuration.

## 🎯 **Objectifs**

### **Mode CLI (Développement)**
- ✅ **Données en mémoire** - Rapide pour les tests
- ✅ **Pas de base de données** - Installation simple
- ✅ **Développement local** - IDE et debugging
- ✅ **Tests automatisés** - Validation continue

### **Mode Web (Production)**
- ✅ **Base de données PostgreSQL** - Données persistantes
- ✅ **API REST** - Interface web
- ✅ **Scalabilité** - Multi-utilisateurs
- ✅ **Monitoring** - Métriques et alertes
- ✅ **Graphiques historiques** - Métriques avec label 'tick'
- ✅ **Scripts de nettoyage** - Maintenance automatique

## 🔧 **Migration simple (Recommandée)**

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
- **Mode Web** : `SQLProduitRepository`, `SQLFournisseurRepository`, `SQLEntrepriseRepository` (PostgreSQL)

### **Étape 3 : Tester la migration**

```bash
# Tests de validation
pytest tests/ -v

# Test de l'API
uvicorn api.main:app --reload
curl http://localhost:8000/
```

## 🏗️ **Migration avancée (Structure complète)**

### **Phase 1 : Préparation de l'API**

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
sqlalchemy==2.0.0
psycopg2-binary==2.9.0
prometheus-client==0.19.0
flask==3.0.0
```

### **Phase 2 : Interface Web**

#### **2.1 Créer l'interface React**
```bash
npx create-react-app frontend
cd frontend
npm install axios react-router-dom bootstrap react-bootstrap
```

#### **2.2 Composants principaux**
```jsx
// src/components/Dashboard.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Dashboard() {
  const [metrics, setMetrics] = useState({});
  
  useEffect(() => {
    axios.get('/api/metrics').then(response => {
      setMetrics(response.data);
    });
  }, []);
  
  return (
    <div>
      <h1>TradeSim Dashboard</h1>
      <div>Budget total: {metrics.budget_total}€</div>
      <div>Transactions: {metrics.transactions_count}</div>
    </div>
  );
}
```

### **Phase 3 : Infrastructure**

#### **3.1 Docker**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **3.2 Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/tradesim
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
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
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

### **Migration simple :**

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

### **Migration complète :**

```bash
# 1. Préparer l'infrastructure
docker-compose up -d

# 2. Migrer les données
python scripts/migrate_data.py

# 3. Tester l'application complète
pytest tests/ -v
curl http://localhost:8000/
curl http://localhost:3000/
```

## 🚨 **Points d'attention**

### **Avant la migration :**
- ✅ **Sauvegarder** les données importantes
- ✅ **Tester** en environnement de développement
- ✅ **Vérifier** les dépendances
- ✅ **Documenter** les changements

### **Pendant la migration :**
- ✅ **Migration progressive** - Pas de big bang
- ✅ **Tests continus** - Validation à chaque étape
- ✅ **Rollback planifié** - Retour en arrière possible
- ✅ **Monitoring** - Surveiller les performances

### **Après la migration :**
- ✅ **Validation complète** - Tests de bout en bout
- ✅ **Performance** - Vérifier les temps de réponse
- ✅ **Sécurité** - Audit des accès
- ✅ **Documentation** - Mettre à jour les guides

## 📊 **Métriques de migration**

### **Temps estimé :**
- **Migration simple** : 30 minutes
- **Migration complète** : 2-3 jours
- **Tests et validation** : 1 jour
- **Documentation** : 0.5 jour

### **Risques :**
- **Faible** - Architecture Repository robuste
- **Contrôlé** - Tests automatisés
- **Réversible** - Rollback facile

## 🎯 **Conclusion**

La migration CLI ↔ Web de TradeSim est **simple et fiable** grâce à l'architecture Repository. Le code reste identique, seule la configuration change.

**Prochaine étape :** Développer l'interface Web React avec Bootstrap et intégration Grafana.

---

**Auteur :** Assistant IA  
**Date :** 2024-09-04  
**Version :** 2.1 - Guide unifié CLI ↔ Web avec nouvelles fonctionnalités 