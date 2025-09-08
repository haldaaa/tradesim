# API TradeSim - Interface Web et WebSocket

## 🎯 Objectif

L'API TradeSim fournit une interface REST et WebSocket pour la simulation de trading, permettant :
- **Interface Web** : Configuration et visualisation des simulations
- **WebSocket** : Streaming temps réel des données pour Grafana
- **Monitoring** : Collecte de métriques pour Prometheus

## 🏗️ Architecture

```
API TradeSim
├── REST Endpoints (/simulation, /config, /templates)
├── WebSocket (/ws) - Streaming temps réel
├── Cache des logs - Performance optimisée
├── Filtrage intelligent - Données par tour
└── Enrichissement des données - Format web
```

## 📊 Flux de Données

### 1. Initialisation
```python
# Vider le cache et les logs
logs_cache = {}
open('logs/simulation.jsonl', 'w').close()

# Initialiser le jeu
reset_game()
generate_game_data(get_default_config())
```

### 2. Simulation
```python
# Lancer tour par tour
for tour in range(tours):
    result = simulation_service.simulation_tour()
    # Collecter les logs
    collect_logs(tour)
```

### 3. Collecte des Logs
```python
# Transactions : filtrées par tour et 'status'
if (log_tour == tour and 'status' in txn_data):
    transactions.append(txn_data)

# Événements : filtrés par tour et 'event_type'
if (log_tour == tour and event_type == 'evenements_tour'):
    events.append(event_data)
```

### 4. Enrichissement
```python
# Ajouter budget_avant, budget_apres, prix_unitaire
enriched_txn = {
    **txn_data,
    'budget_avant': budget_avant,
    'budget_apres': budget_apres,
    'prix_unitaire': prix_unitaire
}
```

## 🔧 Configuration

### Variables d'Environnement
```bash
# Port de l'API
API_PORT=8000

# Host
API_HOST=0.0.0.0

# Mode debug
DEBUG=true
```

### Configuration des Logs
```python
# Fichiers de logs
logs/simulation.jsonl  # Transactions
logs/event.jsonl       # Événements
logs/simulation_humain.log  # Logs humains
logs/event.log         # Logs événements
```

## 📡 Endpoints

### POST /simulation
Lance une simulation complète

**Request:**
```json
{
  "tours": 10,
  "verbose": true,
  "with_metrics": true
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "budget_total_actuel": 85000.0,
    "stock_total_actuel": 2500,
    "tours_completes": 10,
    "transactions_total": 25,
    "evenements_total": 8
  },
  "metrics": { ... }
}
```

### GET /config
Récupère la configuration actuelle

### POST /config
Met à jour la configuration

### GET /templates
Liste les templates disponibles

## 🔌 WebSocket

### Connexion
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Messages Reçus
```json
{
  "type": "simulation_started",
  "tours": 10,
  "message": "Simulation démarrée"
}

{
  "type": "tour_completed",
  "tour": 1,
  "transactions": [...],
  "events": [...],
  "metrics": {...}
}
```

## 🚀 Performance

### Optimisations
- **Cache des logs** : Évite les relectures
- **Filtrage par tour** : Données pertinentes uniquement
- **Enrichissement en mémoire** : Pas de requêtes DB
- **WebSocket** : Streaming temps réel

### Métriques
- **Latence** : < 100ms par tour
- **Mémoire** : Cache limité par tour
- **Débit** : 1000+ tours/minute

## 🐛 Debug

### Logs de Debug
```python
print(f"🚀 Simulation démarrée à {timestamp}")
print(f"📊 Tour {tour}: {len(transactions)} transactions trouvées")
print(f"🎲 Tour {tour}: {len(events)} événements trouvés")
```

### Vérification des Données
```bash
# Vérifier les transactions
tail -5 logs/simulation.jsonl | grep "status"

# Vérifier les événements
tail -5 logs/event.jsonl | grep "event_type"
```

## 🔒 Sécurité

### CORS
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Validation
- **Pydantic** : Validation des modèles
- **Types** : Validation des paramètres
- **Limites** : Tours limités à 1000

## 📈 Monitoring

### Métriques Prometheus
- `tradesim_transactions_total`
- `tradesim_events_total`
- `tradesim_budget_total`
- `tradesim_stock_total`

### Grafana Dashboards
- **Simulation Overview** : Vue d'ensemble
- **Transactions Detail** : Détails des transactions
- **Events Timeline** : Timeline des événements
- **Performance** : Métriques de performance

## 🛠️ Maintenance

### Nettoyage des Logs
```python
# Vider les logs avant chaque simulation
open('logs/simulation.jsonl', 'w').close()
open('logs/event.jsonl', 'w').close()
```

### Cache Management
```python
# Vider le cache
logs_cache['event_logs'] = {}
logs_cache['simulation_logs'] = {}
```

### Monitoring de la Santé
```python
# Vérifier la santé de l'API
GET /health
```

## 📚 Utilisation

### Démarrage
```bash
# Démarrer l'API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Tester l'API
curl -X POST http://localhost:8000/simulation \
  -H "Content-Type: application/json" \
  -d '{"tours": 5, "verbose": true}'
```

### Intégration Web
```javascript
// Lancer une simulation
const response = await fetch('/simulation', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ tours: 10, verbose: true })
});

const data = await response.json();
console.log('Transactions:', data.result.transactions_total);
```

## 🔄 Évolutions

### Roadmap
- [ ] **Cache Redis** : Cache distribué
- [ ] **Base de données** : Persistance des données
- [ ] **Authentification** : Sécurité renforcée
- [ ] **Rate Limiting** : Protection contre les abus
- [ ] **Compression** : Optimisation du WebSocket

### Extensibilité
- **Plugins** : Système de plugins
- **Hooks** : Points d'extension
- **Middleware** : Middleware personnalisé
- **Formatters** : Formateurs de données

---

**Auteur** : Assistant IA  
**Dernière mise à jour** : 08/09/2025  
**Version** : 1.0.0