# Scripts TradeSim
**Dossier : scripts/**

Ce dossier contient tous les scripts utilitaires pour TradeSim, facilitant la maintenance, le nettoyage et la gestion du projet.

## 📁 Contenu du dossier

### **Scripts de nettoyage du monitoring**

#### `clean_monitoring.sh`
**Script de nettoyage standard du monitoring**
- Arrête les services Docker (Prometheus, Grafana)
- Supprime les logs TradeSim
- Supprime les données Prometheus et Grafana
- Redémarre les services
- Vérifie le statut

**Usage :**
```bash
./scripts/clean_monitoring.sh
```

#### `clean_monitoring_complete.sh` ⭐ **RECOMMANDÉ**
**Script de nettoyage COMPLET du monitoring**
- Arrête l'exporter Python (processus en arrière-plan)
- Supprime les logs TradeSim
- Arrête et supprime le container Prometheus
- Nettoie les volumes Docker orphelins
- Redémarre tous les services
- Vérifie que Prometheus est vraiment vide

**Usage :**
```bash
./scripts/clean_monitoring_complete.sh
```

**Avantages :**
- ✅ Supprime complètement les anciennes données
- ✅ Évite les interférences entre simulations
- ✅ Vérification automatique du succès
- ✅ Nettoyage des processus en arrière-plan

## 🎯 Cas d'usage

### **Avant chaque nouvelle simulation**
```bash
# Pour un nettoyage complet (recommandé)
./scripts/clean_monitoring_complete.sh

# Puis lancer la simulation
python services/simulate.py --tours 60 --with-metrics
```

### **En cas de problème de données persistantes**
```bash
# Si Grafana affiche encore d'anciennes données
./scripts/clean_monitoring_complete.sh
```

### **Nettoyage rapide (moins fiable)**
```bash
# Pour un nettoyage rapide (peut laisser des données)
./scripts/clean_monitoring.sh
```

## 🔧 Dépannage

### **Problème : Grafana affiche encore d'anciennes données**
**Cause :** L'exporter Python est encore en cours d'exécution
**Solution :** Utiliser `clean_monitoring_complete.sh` qui arrête l'exporter

### **Problème : Prometheus contient encore des métriques**
**Cause :** Le container Prometheus n'a pas été supprimé
**Solution :** Le script complet supprime le container et recrée un nouveau

### **Problème : Erreur de permissions**
**Solution :**
```bash
chmod +x scripts/clean_monitoring_complete.sh
```

## 📊 Vérification du succès

Après exécution du script, vous devriez voir :
```
✅ Prometheus est vide - Succès !
📊 Statut des services:
[Services Docker en cours d'exécution]
🎉 Nettoyage terminé ! Monitoring prêt pour une nouvelle simulation.
```

## 🚀 Prochaines étapes

Après le nettoyage :
1. **Lancer une nouvelle simulation** : `python services/simulate.py --tours X --with-metrics`
2. **Vérifier Grafana** : http://localhost:3000 (admin/admin)
3. **Vérifier Prometheus** : http://localhost:9090

## 📝 Notes importantes

- **Scripts exécutables** : Tous les scripts sont pré-configurés avec les bonnes permissions
- **Sécurité** : Les scripts ne suppriment que les données de monitoring, pas le code source
- **Performance** : Le nettoyage complet prend environ 30 secondes
- **Compatibilité** : Fonctionne sur macOS, Linux et Windows (avec Docker)

---

**Dernière mise à jour :** 4 septembre 2025  
**Auteur :** Assistant IA  
**Version :** 1.0
