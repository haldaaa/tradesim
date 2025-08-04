# Guide d'utilisation TradeSim

## 🚀 Comment lancer le jeu

### 1. **Mode CLI (simulation)**
```bash
# Lancer la simulation
python services/simulate.py
```

### 2. **Mode API (serveur web)**
```bash
# Démarrer le serveur API
uvicorn api.main:app --reload

# Puis ouvrir http://localhost:8000
```

### 3. **Mode interactif (configuration)**
```bash
# Configuration interactive du jeu
python services/game_manager.py
```

---

## 📋 Commandes principales

### **Simulation**
- `python services/simulate.py` - Lance la simulation
- `python services/simulate.py --tours 10` - Simulation sur 10 tours
- `python services/simulate.py --infinite` - Simulation infinie

### **API**
- `uvicorn api.main:app --reload` - Démarre le serveur API
- `curl http://localhost:8000/` - Test de l'API
- `curl http://localhost:8000/produits` - Liste des produits

### **Tests**
- `pytest tests/` - Lance tous les tests
- `pytest tests/unit/` - Tests unitaires
- `pytest tests/integration/` - Tests d'intégration

---

## 🎮 Fonctionnalités

### **Simulation économique**
- Entreprises qui achètent des produits
- Fournisseurs avec stocks limités
- Événements aléatoires (inflation, réassort, etc.)
- Logs détaillés des transactions

### **API REST**
- `GET /` - Accueil
- `GET /produits` - Liste des produits
- `GET /fournisseurs` - Liste des fournisseurs
- `GET /entreprises` - Liste des entreprises

### **Configuration**
- Nombre d'entreprises, produits, fournisseurs
- Budgets et stratégies d'achat
- Types de produits (matières premières, consommables, produits finis)

---

## 📁 Structure des fichiers

```
app/
├── services/          # Logique métier
│   ├── simulate.py    # Simulation principale
│   ├── game_manager.py # Configuration
│   └── simulation_service.py # Service de simulation
├── api/               # API web
│   └── main.py        # Endpoints FastAPI
├── models/            # Modèles de données
├── repositories/      # Accès aux données
├── events/            # Événements de simulation
├── config/            # Configuration
└── tests/             # Tests
```

---

## 🔧 Configuration

### **Variables d'environnement**
```bash
# Mode de simulation
SIMULATION_MODE=cli  # ou web

# Logs
LOG_LEVEL=INFO
```

### **Fichiers de configuration**
- `config/config.py` - Configuration principale
- `templates/` - Templates de jeu

---

## 📊 Logs et monitoring

### **Fichiers de logs**
- `logs/simulation.jsonl` - Logs JSON
- `logs/simulation_humain.log` - Logs lisibles
- `logs/event.jsonl` - Logs d'événements

### **Métriques disponibles**
- Nombre de transactions
- Budgets des entreprises
- Stocks des fournisseurs
- Événements appliqués

---

## 🐛 Dépannage

### **Problèmes courants**
1. **Import errors** : Vérifiez que vous êtes dans le bon dossier
2. **Port déjà utilisé** : Changez le port avec `--port 8001`
3. **Tests qui échouent** : Lancez `pytest tests/ -v` pour voir les détails

### **Commandes de debug**
```bash
# Vérifier l'installation
python -c "import services.simulate; print('✅ OK')"

# Tester l'API
curl http://localhost:8000/

# Voir les logs
tail -f logs/simulation_humain.log
```

---

## 📚 Pour aller plus loin

- **Documentation API** : http://localhost:8000/docs
- **Tests** : `pytest tests/ -v`
- **Monitoring** : Voir `METRIQUES_DISPONIBLES.md`
- **Packaging** : Voir `GUIDE_PACKAGING.md` 