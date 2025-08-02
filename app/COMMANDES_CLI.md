# Commandes CLI TradeSim
## Guide de référence rapide

**Date :** 02/08/2025  
**Version :** 1.0.0

---

## 🚀 **Démarrage rapide**

### **1. Activation de l'environnement**
```bash
source ../venv/bin/activate
```

### **2. Nouvelle partie basique**
```bash
# Remettre à zéro
python3 services/simulate.py --reset

# Lancer 10 tours
python3 services/simulate.py --tours 10 --verbose
```

---

## 📋 **Toutes les commandes disponibles**

### **Commandes de base**
```bash
# Afficher l'aide
python3 services/simulate.py --help

# Afficher l'état actuel (budgets et prix)
python3 services/simulate.py --status

# Remettre le jeu à zéro
python3 services/simulate.py --reset
```

### **Commandes de simulation**
```bash
# Simulation de N tours
python3 services/simulate.py --tours 5
python3 services/simulate.py --tours 10
python3 services/simulate.py --tours 20

# Simulation avec mode verbose (détails)
python3 services/simulate.py --tours 10 --verbose

# Simulation infinie
python3 services/simulate.py --infinite

# Simulation infinie avec verbose
python3 services/simulate.py --infinite --verbose
```

### **Commandes de configuration**
```bash
# Configuration interactive d'une nouvelle partie
python3 services/simulate.py --new-game

# Sauvegarder la configuration actuelle
python3 services/simulate.py --save-template "nom_template"

# Charger un template
python3 services/simulate.py --load-template "nom_template"

# Lister tous les templates disponibles
python3 services/simulate.py --list-templates
```

### **Commandes de debug/cheat**
```bash
# Mode cheat (ajouter de l'argent à une entreprise)
python3 services/simulate.py --cheat
```

---

## 🎮 **Exemples de parties**

### **Partie rapide (5 minutes)**
```bash
source ../venv/bin/activate
python3 services/simulate.py --reset
python3 services/simulate.py --tours 10 --verbose
```

### **Partie moyenne (15 minutes)**
```bash
source ../venv/bin/activate
python3 services/simulate.py --reset
python3 services/simulate.py --tours 30 --verbose
```

### **Partie longue (observation)**
```bash
source ../venv/bin/activate
python3 services/simulate.py --reset
python3 services/simulate.py --infinite --verbose
# Arrêter avec Ctrl+C
```

### **Partie avec configuration personnalisée**
```bash
source ../venv/bin/activate
python3 services/simulate.py --new-game
python3 services/simulate.py --tours 20 --verbose
```

---

## 📊 **Monitoring et observation**

### **Vérifier l'état**
```bash
# État avant simulation
python3 services/simulate.py --status

# État après simulation
python3 services/simulate.py --status
```

### **Tests de validation**
```bash
# Test d'intégration complet
python3 test_integration_complete.py

# Test des services
python3 test_services_complets.py

# Test de l'architecture
python3 test_architecture.py
```

### **API REST**
```bash
# Lancer l'API
uvicorn api.main:app --reload

# Accéder à l'API
curl http://localhost:8000/
curl http://localhost:8000/produits
curl http://localhost:8000/entreprises
```

---

## 🔧 **Dépannage**

### **Si l'environnement n'est pas activé**
```bash
# Erreur : ModuleNotFoundError
source ../venv/bin/activate
```

### **Si les imports échouent**
```bash
# Vérifier que vous êtes dans le bon répertoire
pwd  # Doit afficher /Users/fares/Desktop/DevVoyage/tradesim/app

# Réactiver l'environnement
source ../venv/bin/activate
```

### **Si le CLI ne répond pas**
```bash
# Arrêter avec Ctrl+C
# Puis relancer
python3 services/simulate.py --status
```

---

## 🎯 **Workflow recommandé**

### **1. Démarrage de session**
```bash
# Activer l'environnement
source ../venv/bin/activate

# Vérifier que tout fonctionne
python3 services/simulate.py --status
```

### **2. Nouvelle partie**
```bash
# Remettre à zéro
python3 services/simulate.py --reset

# Vérifier l'état initial
python3 services/simulate.py --status

# Lancer la simulation
python3 services/simulate.py --tours 15 --verbose

# Vérifier l'état final
python3 services/simulate.py --status
```

### **3. Sauvegarde (optionnel)**
```bash
# Sauvegarder la configuration
python3 services/simulate.py --save-template "ma_partie_01"

# Plus tard, recharger
python3 services/simulate.py --load-template "ma_partie_01"
```

---

## 📈 **Conseils d'utilisation**

### **Pour observer l'évolution**
- Utilisez `--verbose` pour voir les détails
- Lancez `--status` avant et après pour comparer
- Utilisez `--infinite` pour une observation continue

### **Pour tester différentes configurations**
- Utilisez `--new-game` pour configurer interactivement
- Sauvegardez avec `--save-template`
- Comparez les résultats avec `--status`

### **Pour le développement**
- Lancez les tests après chaque modification
- Utilisez l'API pour intégration web
- Consultez les logs pour debug

---

## 🚨 **Commandes importantes**

### **Toujours commencer par**
```bash
source ../venv/bin/activate
```

### **Pour une nouvelle partie**
```bash
python3 services/simulate.py --reset
python3 services/simulate.py --tours 10 --verbose
```

### **Pour arrêter une simulation infinie**
```bash
Ctrl+C
```

---

**TradeSim CLI** - Guide de référence rapide  
**Dernière mise à jour :** 02/08/2025 