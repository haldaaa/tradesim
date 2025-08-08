# Guide d'utilisation TradeSim

## 🚀 **Comment lancer une partie**

### **1. Activer l'environnement**
```bash
source venv/bin/activate
```

### **2. Choisir le mode de lancement**

#### **🎮 Mode interactif (recommandé pour nouvelle partie)**
```bash
python services/simulate.py --new-game
```
**Pourquoi utiliser ce mode ?**
- **Configuration complète** : Menu interactif pour configurer entreprises, produits, fournisseurs, événements
- **Nouvelle partie** : Créer une partie personnalisée selon vos préférences
- **Apprentissage** : Comprendre tous les paramètres du jeu
- **Flexibilité** : Choisir entre config par défaut, personnalisée, ou charger existante

**Cas d'usage :**
- Première utilisation
- Créer une nouvelle partie avec paramètres spécifiques
- Tester différentes configurations
- Apprendre le jeu

#### **⚡ Mode direct (pour tests rapides)**
```bash
python services/simulate.py --tours 10
```
**Pourquoi utiliser ce mode ?**
- **Simulation rapide** : Utilise la configuration existante (data/partie_active.json)
- **Tests rapides** : Pas besoin de reconfigurer à chaque fois
- **Performance** : Démarrage immédiat sans menus
- **Automatisation** : Idéal pour scripts et tests

**Cas d'usage :**
- Tests rapides de fonctionnalités
- Développement et debug
- Simulations répétitives
- Scripts automatisés

### **3. Lancer la simulation**

#### **Mode interactif**
```bash
# 1. Créer une nouvelle partie
python services/simulate.py --new-game

# 2. Suivre le menu interactif
# - Choisir config par défaut, personnalisée, ou charger existante
# - Configurer les paramètres souhaités
# - Lancer la simulation depuis le menu
```

#### **Mode direct**
```bash
# Simulation de 10 tours
python services/simulate.py --tours 10

# Simulation infinie
python services/simulate.py --infinite

# Avec détails
python services/simulate.py --tours 10 --verbose

# Avec monitoring Prometheus/Grafana
python services/simulate.py --tours 10 --with-metrics
```

### **4. Vérifier l'état**
```bash
python services/simulate.py --status
```

---

## 📋 **Commandes principales**

### **Mode interactif**
- `python services/simulate.py --new-game` - Créer une nouvelle partie (mode interactif)

### **Mode direct**
- `python services/simulate.py --tours 10` - Lancer 10 tours
- `python services/simulate.py --infinite` - Simulation infinie
- `python services/simulate.py --verbose` - Mode détaillé
- `python services/simulate.py --with-metrics` - Avec monitoring

### **Gestion**
- `python services/simulate.py --reset` - Remettre à zéro
- `python services/simulate.py --status` - Voir l'état
- `python services/simulate.py --cheat` - Mode cheat (+5000€)

---

## 🎮 **Exemples complets**

### **Exemple 1 : Première partie (mode interactif)**
```bash
# 1. Activer l'environnement
source venv/bin/activate

# 2. Créer une nouvelle partie
python services/simulate.py --new-game

# 3. Dans le menu interactif :
# - Choisir [1] pour config par défaut
# - Choisir [1] pour lancer la simulation
```

### **Exemple 2 : Tests rapides (mode direct)**
```bash
# 1. Activer l'environnement
source venv/bin/activate

# 2. Test rapide sans monitoring
python services/simulate.py --tours 5

# 3. Test avec monitoring
python services/simulate.py --tours 5 --with-metrics

# 4. Vérifier l'état
python services/simulate.py --status
```

### **Exemple 3 : Développement**
```bash
# 1. Activer l'environnement
source venv/bin/activate

# 2. Tests rapides répétés
python services/simulate.py --tours 3 --verbose
python services/simulate.py --tours 3 --with-metrics
python services/simulate.py --status
```

---

## 🔧 **Différences techniques**

| Aspect | Mode interactif | Mode direct |
|--------|----------------|-------------|
| **Configuration** | Menu interactif complet | Utilise config existante |
| **Vitesse** | Plus lent (menus) | Rapide (direct) |
| **Flexibilité** | Configuration complète | Paramètres fixes |
| **Cas d'usage** | Nouvelle partie, apprentissage | Tests rapides, développement |
| **Monitoring** | Disponible dans le menu | Option `--with-metrics` | 