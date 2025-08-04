# Guide d'utilisation TradeSim

## 🚀 **Comment lancer une partie**

### **1. Activer l'environnement**
```bash
source ../venv/bin/activate
```

### **2. Créer une nouvelle partie**
```bash
python3 services/simulate.py --new-game
```

### **3. Lancer la simulation**
```bash
# Simulation de 10 tours
python3 services/simulate.py --tours 10

# Simulation infinie
python3 services/simulate.py --infinite

# Avec détails
python3 services/simulate.py --tours 10 --verbose
```

### **4. Vérifier l'état**
```bash
python3 services/simulate.py --status
```

---

## 📋 **Commandes principales**

- `python3 services/simulate.py --new-game` - Créer une nouvelle partie
- `python3 services/simulate.py --reset` - Remettre à zéro
- `python3 services/simulate.py --tours 10` - Lancer 10 tours
- `python3 services/simulate.py --infinite` - Simulation infinie
- `python3 services/simulate.py --status` - Voir l'état
- `python3 services/simulate.py --verbose` - Mode détaillé

---

## 🎮 **Exemple complet d'une partie**

```bash
# 1. Activer l'environnement
source ../venv/bin/activate

# 2. Créer une nouvelle partie
python3 services/simulate.py --new-game

# 3. Lancer 10 tours avec détails
python3 services/simulate.py --tours 10 --verbose

# 4. Vérifier l'état final
python3 services/simulate.py --status
``` 