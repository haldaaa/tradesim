# TradeSim - Interface Web

## 🎯 **VUE D'ENSEMBLE**

Interface web complète pour TradeSim avec navigation, configuration et simulation en temps réel.

## 🏗️ **ARCHITECTURE**

### **Pages disponibles :**
1. **Page d'accueil** - Présentation et navigation
2. **Page de configuration** - Paramétrage complet de la simulation
3. **Page de jeu** - Simulation en cours avec événements temps réel

### **Fonctionnalités :**
- ✅ **Navigation fluide** entre les pages
- ✅ **Configuration complète** (34 paramètres CLI)
- ✅ **Sauvegarde/chargement** de templates
- ✅ **Simulation temps réel** via API
- ✅ **WebSocket** pour événements en direct
- ✅ **Interface moderne** avec Bootstrap 5

## 🚀 **UTILISATION**

### **1. Accès à l'interface**
```bash
# Lancer les services
./run_phase1.sh

# Accéder à l'interface
http://localhost:3001
```

### **2. Workflow utilisateur**
1. **Page d'accueil** → Cliquer "Lancer une partie"
2. **Configuration** → Paramétrer la simulation
3. **Sauvegarder template** (optionnel)
4. **Lancer la partie** → Aller à la page de jeu
5. **Suivre les événements** en temps réel

## ⚙️ **CONFIGURATION DISPONIBLE**

### **Paramètres de base :**
- Nombre de tours
- Nombre d'entreprises par tour
- Probabilité de sélection d'entreprise
- Durée de pause entre tours

### **Paramètres de transaction :**
- Quantité d'achat min/max
- Budget initial des entreprises
- Stock initial des fournisseurs

### **Événements :**
- Inflation
- Recharge de budget
- Réassort
- Variation de disponibilité

### **Monitoring :**
- Métriques activées/désactivées
- Mode verbose
- Niveau de log

## 💾 **GESTION DES TEMPLATES**

### **Sauvegarde :**
- Templates stockés en localStorage
- Nom et description personnalisables
- Date de création automatique

### **Chargement :**
- Liste des templates disponibles
- Sélection par numéro
- Application automatique des paramètres

## 🔌 **COMMUNICATION API**

### **Endpoints utilisés :**
- `GET /api/health` - Test de connexion
- `POST /api/simulation` - Lancement de simulation
- `WebSocket /api/ws` - Événements temps réel

### **Format des requêtes :**
```javascript
// Simulation
{
  "tours": 10,
  "verbose": true,
  "with_metrics": true
}

// WebSocket
{
  "type": "subscribe"
}
```

## 📊 **AFFICHAGE TEMPS RÉEL**

### **Informations de partie :**
- Tours complétés / Total
- Budget total des entreprises
- Stock total des fournisseurs
- Nombre d'événements appliqués

### **Log des événements :**
- Timestamp de chaque événement
- Type d'événement (info, success, warning, error)
- Auto-scroll activé/désactivé
- Limite de 100 événements affichés

## 🎨 **INTERFACE UTILISATEUR**

### **Design :**
- **Bootstrap 5** pour le style
- **Font Awesome** pour les icônes
- **Responsive** design
- **Navigation** intuitive

### **Couleurs :**
- **Primaire** : #667eea (bleu)
- **Secondaire** : #764ba2 (violet)
- **Succès** : Vert Bootstrap
- **Erreur** : Rouge Bootstrap

## 🔧 **DÉVELOPPEMENT**

### **Structure des fichiers :**
```
web/
├── index.html          # Interface principale
├── app.js             # Logique JavaScript
├── server.py          # Serveur de développement
└── README.md          # Documentation
```

### **Fonctions principales :**
- `showPage()` - Navigation entre pages
- `saveTemplate()` - Sauvegarde de configuration
- `loadTemplate()` - Chargement de configuration
- `startGame()` - Lancement de simulation
- `connectWebSocket()` - Connexion temps réel

## 🐛 **DÉPANNAGE**

### **Problèmes courants :**

1. **API non connectée**
   - Vérifier que l'API FastAPI tourne sur le port 8000
   - Tester : `curl http://localhost:8000/health`

2. **WebSocket ne fonctionne pas**
   - Vérifier la configuration CORS
   - Tester la connexion WebSocket

3. **Templates non sauvegardés**
   - Vérifier que localStorage est activé
   - Tester en mode navigation privée

## 📈 **MÉTRIQUES ET MONITORING**

### **Métriques affichées :**
- Budget total des entreprises
- Stock total des fournisseurs
- Nombre de tours complétés
- Événements appliqués
- Durée de simulation

### **Intégration future :**
- **Grafana** pour visualisation avancée
- **Prometheus** pour collecte de métriques
- **PostgreSQL** pour persistance des templates

## 🚀 **PROCHAINES ÉTAPES**

1. **Base de données** - Migration vers PostgreSQL
2. **Authentification** - Gestion des utilisateurs
3. **Graphiques** - Visualisation des métriques
4. **Tests** - Tests automatisés de l'interface
5. **Déploiement** - Docker et Kubernetes

---

**Interface web TradeSim - Version 1.0**  
*Développée avec ❤️ pour la simulation économique interactive*