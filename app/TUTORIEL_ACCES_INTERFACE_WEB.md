# 🌐 TUTORIEL D'ACCÈS À L'INTERFACE WEB TRADESIM

## 📋 **PRÉREQUIS**

### **1. Environnement Python**
- ✅ Python 3.8+ installé
- ✅ Environnement virtuel activé
- ✅ Dépendances installées

### **2. Vérifications préalables**
```bash
# Vérifier Python
python3 --version

# Vérifier l'environnement virtuel
ls -la venv/

# Vérifier les dépendances
pip list | grep -E "(fastapi|uvicorn|websockets)"
```

## 🚀 **LANCEMENT DE L'INTERFACE WEB**

### **Méthode 1 : Script automatisé (RECOMMANDÉ)**

```bash
# 1. Aller dans le dossier du projet
cd /Users/fares/Desktop/DevVoyage/tradesim/app

# 2. Lancer le script de démarrage
./run_phase1.sh
```

**Ce script fait automatiquement :**
- ✅ Vérification de Python et de l'environnement virtuel
- ✅ Installation des dépendances manquantes
- ✅ Lancement de l'API FastAPI sur le port 8000
- ✅ Lancement de l'interface web sur le port 3001
- ✅ Gestion des processus en arrière-plan

### **Méthode 2 : Lancement manuel**

```bash
# 1. Activer l'environnement virtuel
source venv/bin/activate

# 2. Installer les dépendances
pip install fastapi uvicorn websockets

# 3. Lancer l'API FastAPI (Terminal 1)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Lancer l'interface web (Terminal 2)
cd web
python3 server.py
```

## 🌐 **ACCÈS À L'INTERFACE**

### **URLs disponibles :**

| Service | URL | Description |
|---------|-----|-------------|
| **Interface Web** | http://localhost:3001 | Interface principale |
| **API FastAPI** | http://localhost:8000 | API REST |
| **Documentation API** | http://localhost:8000/docs | Swagger UI |
| **Health Check** | http://localhost:8000/health | Test de connexion |

### **Navigation dans l'interface :**

1. **Page d'accueil** (`/`)
   - Présentation de TradeSim
   - Bouton "Lancer une partie"

2. **Page de configuration** (`/config`)
   - 34 paramètres configurables
   - Sauvegarde/chargement de templates
   - Bouton "Lancer la partie"

3. **Page de jeu** (`/game`)
   - Simulation en temps réel
   - Log des événements
   - Métriques de la partie

## ⚙️ **CONFIGURATION DISPONIBLE**

### **Paramètres de base (5 champs)**
- Nombre de tours
- Nombre d'entreprises par tour
- Probabilité de sélection (%)
- Durée de pause entre tours (ms)
- Intervalle d'événements (tours)

### **Paramètres de transaction (7 champs)**
- Quantité d'achat min/max
- Quantité achat prix élevé min/max
- Seuil prix élevé (€)
- Budget initial (€)
- Stock initial des fournisseurs

### **Configuration avancée (9 champs)**
- Nombre d'entreprises
- Budget entreprise min/max (€)
- Prix produit min/max (€)
- Nombre de produits par défaut
- Produits actifs min/max
- Nombre de fournisseurs

### **Événements (4 champs)**
- Inflation (checkbox)
- Recharge de budget (checkbox)
- Réassort (checkbox)
- Variation de disponibilité (checkbox)

### **Paramètres d'événements (4 champs)**
- Recharge budget min/max (€)
- Réassort quantité min/max

### **Paramètres d'inflation (4 champs)**
- Inflation % min/max
- Pénalité inflation (%)
- Durée pénalité (tours)

### **Probabilités d'événements (4 champs)**
- Recharge budget (%)
- Réassort (%)
- Inflation (%)
- Variation disponibilité (%)

### **Monitoring avancé (4 champs)**
- Intervalle collecte métriques (s)
- Métriques système (checkbox)
- Labels métriques (checkbox)
- Niveau de log (select)

## 💾 **GESTION DES TEMPLATES**

### **Sauvegarde :**
1. Configurer tous les paramètres
2. Cliquer "Sauvegarder Template"
3. Entrer un nom pour le template
4. Le template est stocké en localStorage

### **Chargement :**
1. Cliquer "Charger Template"
2. Sélectionner le template par numéro
3. Les paramètres sont automatiquement appliqués

## 🎮 **UTILISATION DE LA SIMULATION**

### **Workflow complet :**

1. **Accueil** → Cliquer "Lancer une partie"
2. **Configuration** → Modifier les paramètres si nécessaire
3. **Sauvegarder** → Template (optionnel)
4. **Lancer** → Cliquer "Lancer la Partie"
5. **Jeu** → Suivre les événements en temps réel

### **Fonctionnalités temps réel :**
- ✅ **WebSocket** : Connexion automatique
- ✅ **Événements** : Log coloré avec timestamps
- ✅ **Métriques** : Budget total, stock total, tours
- ✅ **Auto-scroll** : Suivi automatique des nouveaux événements

## 🔧 **DÉPANNAGE**

### **Problème 1 : Port déjà utilisé**
```bash
# Vérifier les ports utilisés
lsof -i :8000
lsof -i :3001

# Tuer les processus si nécessaire
kill -9 <PID>
```

### **Problème 2 : API non connectée**
```bash
# Tester la connexion API
curl http://localhost:8000/health

# Vérifier les logs
tail -f logs/api.log
```

### **Problème 3 : WebSocket ne fonctionne pas**
- Vérifier la console du navigateur (F12)
- Tester la connexion WebSocket
- Vérifier les erreurs CORS

### **Problème 4 : Templates non sauvegardés**
- Vérifier que localStorage est activé
- Tester en mode navigation privée
- Vérifier les permissions du navigateur

## 📊 **MONITORING ET MÉTRIQUES**

### **Métriques affichées :**
- Tours complétés / Total
- Budget total des entreprises
- Stock total des fournisseurs
- Nombre d'événements appliqués

### **Intégration future :**
- **Grafana** : http://localhost:3000 (si monitoring actif)
- **Prometheus** : Métriques collectées automatiquement
- **PostgreSQL** : Persistance des templates (Phase 2)

## 🛑 **ARRÊT DES SERVICES**

### **Avec le script automatisé :**
```bash
# Appuyer sur Ctrl+C dans le terminal
# Tous les services s'arrêtent automatiquement
```

### **Manuellement :**
```bash
# Tuer les processus
pkill -f "uvicorn api.main:app"
pkill -f "python3 server.py"

# Ou utiliser les PIDs
kill $API_PID $WEB_PID
```

## 📝 **LOGS ET DEBUGGING**

### **Logs disponibles :**
- **API** : Logs FastAPI dans le terminal
- **Interface** : Console du navigateur (F12)
- **WebSocket** : Messages dans la console
- **Simulation** : Logs dans `logs/`

### **Debugging :**
```bash
# Mode verbose pour l'API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

# Logs de simulation
tail -f logs/simulation.log
```

## 🚀 **PROCHAINES ÉTAPES**

### **Phase 2 (Prochaine session) :**
- **PostgreSQL** : Persistance des données
- **Repository Pattern** : Basculement CLI ↔ Web
- **Migrations** : Gestion des schémas
- **Tests d'intégration** : Validation complète

### **Phases suivantes :**
- **Phase 3** : Dashboard avancé + Intégration Grafana
- **Phase 4** : Docker + Kubernetes
- **Phase 5** : AWS + Terraform + CICD
- **Phase 6** : Optimisation + Monitoring avancé

---

## ✅ **RÉSUMÉ RAPIDE**

```bash
# 1. Aller dans le projet
cd /Users/fares/Desktop/DevVoyage/tradesim/app

# 2. Lancer l'interface
./run_phase1.sh

# 3. Ouvrir le navigateur
open http://localhost:3001

# 4. Configurer et lancer une partie
# 5. Suivre les événements en temps réel
```

**🎯 Interface web TradeSim - Prête à l'emploi !**

---

*Tutoriel créé le 06/09/2025 - Interface web Phase 1 complète*
