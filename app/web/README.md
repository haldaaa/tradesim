# 🌐 TradeSim - Interface Web Phase 1

## 📋 **Vue d'ensemble**

Interface Web moderne pour TradeSim développée avec React et Bootstrap. Cette Phase 1 fournit une interface utilisateur complète pour configurer et lancer des simulations avec communication temps réel via WebSocket.

## 🎯 **Fonctionnalités**

### **✅ Implémentées**
- **Interface React moderne** : Composants React avec Bootstrap 5
- **Configuration interactive** : Paramètres de simulation modifiables
- **Communication temps réel** : WebSocket pour les mises à jour live
- **Métriques en direct** : Affichage des métriques de simulation
- **Logs temps réel** : Suivi des événements de simulation
- **API REST complète** : Endpoints pour toutes les fonctionnalités

### **🔧 Endpoints API**
- `GET /health` - Health check
- `GET /config` - Récupération de la configuration
- `POST /config` - Mise à jour de la configuration
- `POST /simulation` - Lancement de simulation
- `GET /metrics` - Récupération des métriques
- `WS /ws` - WebSocket pour communication temps réel

## 🚀 **Utilisation**

### **Lancement rapide**
```bash
# Depuis la racine du projet
./run_phase1.sh
```

### **Lancement manuel**
```bash
# Terminal 1 - API FastAPI
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Interface Web
cd web
python3 server.py
```

### **Accès**
- **Interface Web** : http://localhost:3000
- **API FastAPI** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## 🏗️ **Architecture**

### **Frontend (React)**
```
web/
├── index.html          # Page principale
├── app.js             # Application React
├── server.py          # Serveur de développement
└── README.md          # Documentation
```

### **Backend (FastAPI)**
```
api/
└── main.py            # API étendue avec nouveaux endpoints
```

### **Communication**
- **HTTP REST** : Configuration et lancement de simulations
- **WebSocket** : Mises à jour temps réel et logs
- **CORS** : Configuration pour développement local

## 📊 **Interface utilisateur**

### **Configuration**
- **Nombre de tours** : Paramètre de simulation (1-1000)
- **Mode verbose** : Affichage détaillé des logs
- **Avec métriques** : Activation du monitoring

### **Métriques en direct**
- **Tours complétés** : Progression de la simulation
- **Entreprises actives** : Nombre d'entreprises
- **Produits actifs** : Nombre de produits
- **Fournisseurs actifs** : Nombre de fournisseurs

### **Logs temps réel**
- **Connexion WebSocket** : Statut de connexion
- **Événements simulation** : Progression et résultats
- **Erreurs** : Gestion des erreurs avec détails

## 🔧 **Développement**

### **Structure des composants React**
```javascript
// Composant principal
function TradeSimApp() {
    // États
    const [config, setConfig] = useState({});
    const [metrics, setMetrics] = useState({});
    const [isConnected, setIsConnected] = useState(false);
    const [logs, setLogs] = useState([]);
    
    // WebSocket
    const wsRef = useRef(null);
    
    // Fonctions
    const runSimulation = async () => { ... };
    const loadMetrics = async () => { ... };
    const updateConfig = async () => { ... };
}
```

### **Gestion WebSocket**
```javascript
// Connexion WebSocket
useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onopen = () => setIsConnected(true);
    ws.onmessage = (event) => handleMessage(JSON.parse(event.data));
    ws.onclose = () => setIsConnected(false);
}, []);
```

### **Communication API**
```javascript
// Lancement de simulation
const runSimulation = async () => {
    const response = await fetch('/simulation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(simulationConfig)
    });
    const data = await response.json();
};
```

## 🧪 **Tests**

### **Tests API**
```bash
# Tests des endpoints Phase 1
pytest tests/api/test_phase1_endpoints.py -v
```

### **Tests manuels**
1. **Interface Web** : Vérifier l'affichage et les interactions
2. **WebSocket** : Tester la connexion et les messages
3. **API** : Vérifier les endpoints avec curl ou Postman

## 📋 **Prochaines étapes**

### **Phase 2 - Base de données**
- **PostgreSQL** : Persistance des données
- **Repository Pattern** : Basculement CLI ↔ Web
- **Migrations** : Gestion des schémas

### **Phase 3 - Dashboard avancé**
- **Graphiques** : Visualisation des métriques
- **Intégration Grafana** : Liens directs
- **Templates** : Configuration avancée

### **Phase 4 - Containerisation**
- **Docker** : Images et orchestration
- **Kubernetes** : Déploiement cloud
- **CICD** : Pipeline automatisé

## 🐛 **Dépannage**

### **Problèmes courants**
1. **Port 8000 occupé** : Changer le port de l'API
2. **CORS errors** : Vérifier la configuration CORS
3. **WebSocket fermé** : Reconnexion automatique activée

### **Logs de débogage**
- **Console navigateur** : Erreurs JavaScript
- **Terminal API** : Logs FastAPI
- **Interface Web** : Logs temps réel

## 📝 **Notes techniques**

### **Sécurité**
- **CORS** : Configuration pour développement local
- **Validation** : Pydantic pour les requêtes
- **Gestion d'erreurs** : Try-catch et messages utilisateur

### **Performance**
- **WebSocket** : Connexion persistante
- **Reconnexion** : Automatique en cas de perte
- **Cache** : Métriques mises en cache

### **Compatibilité**
- **Navigateurs** : Chrome, Firefox, Safari, Edge
- **Responsive** : Bootstrap 5 pour mobile
- **Accessibilité** : Labels et ARIA

---

**Auteur** : Assistant IA  
**Date** : 04/09/2025  
**Version** : 1.0 - Phase 1 complète
