# Log de Packaging TradeSim
============================

## Historique des versions

### Version 0.1 - 04/08/2025
- **Package** : `tradesim-app-v0.1.0.tar.gz`
- **Date** : 04/08/2025 13:40
- **Description** : Version initiale avec corrections des tests
- **Tests** : 88/88 tests passent (100% de succès)
- **Fonctionnalités** :
  - Application CLI fonctionnelle
  - Simulation avec vraie logique d'achat
  - Événements (inflation, réassort, etc.)
  - Sauvegarde/chargement de templates
  - Architecture Repository Pattern + Services
  - PriceService centralisé
  - Correction des 5 tests qui échouaient
- **Package créé** : ✅ `build/tradesim-app-v0.1.0.tar.gz`
- **Corrections de cette session** :
  - ✅ Correction import `app.simulateur` → `services.simulateur`
  - ✅ Correction ordre des opérations dans `test_reset_game`
  - ✅ Ajout génération de produits avant fournisseurs
  - ✅ Tests plus tolérants pour budgets modifiés par événements
  - ✅ Gestion améliorée de l'inflation probabiliste
  - ✅ Suppression dossier tests obsolète `../tests/`
  - ✅ Mise en place système de packaging avec log
  - ✅ Workflow d'activation environnement virtuel clarifié
  - ✅ **Découverte et documentation des commandes CLI manquantes** :
    - `--new-game` : Configuration interactive d'une nouvelle partie
    - `--reset` : Remettre le jeu à zéro
    - `--save-template` : Sauvegarder la configuration
    - `--load-template` : Charger un template
    - `--list-templates` : Lister les templates
    - `--cheat` : Mode cheat pour ajouter de l'argent
  - ✅ **Création du script de lancement** : `run_cli.sh` pour simplifier l'utilisation
  - ✅ **Mise à jour du guide d'utilisation** : Toutes les commandes documentées

### Version 0.2 - 04/09/2025
- **Package** : `tradesim-app-v0.2.0.tar.gz`
- **Date** : 04/09/2025 14:00
- **Description** : Version avec monitoring avancé et graphiques historiques
- **Tests** : 88/88 tests passent (100% de succès)
- **Fonctionnalités** :
  - Application CLI fonctionnelle
  - Simulation avec vraie logique d'achat
  - Événements (inflation, réassort, recharge_budget, recharge_stock_fournisseur, variation_disponibilite)
  - Sauvegarde/chargement de templates
  - Architecture Repository Pattern + Services
  - PriceService centralisé
  - **NOUVEAU** : Monitoring Prometheus/Grafana avec métriques temporelles
  - **NOUVEAU** : Label 'tick' sur toutes les métriques pour graphiques historiques
  - **NOUVEAU** : Dashboards Grafana avec visualisation par tour
  - **NOUVEAU** : Scripts de nettoyage automatique du monitoring
  - **NOUVEAU** : Correction des erreurs de labels Prometheus
  - **NOUVEAU** : Documentation complète et cohérente
- **Package créé** : ✅ `build/tradesim-app-v0.2.0.tar.gz`
- **Corrections de cette session** :
  - ✅ **Monitoring avancé** : Métriques avec historique par tour
  - ✅ **Graphiques historiques** : Suivi de l'évolution des budgets par tour
  - ✅ **Scripts de nettoyage** : `clean_monitoring_complete.sh` et `clean_monitoring.sh`
  - ✅ **Correction bugs** : Résolution des erreurs "Incorrect label names"
  - ✅ **Documentation** : Tous les README mis à jour avec nouvelles fonctionnalités
  - ✅ **Cahier des charges** : Statuts corrigés (Dashboards Grafana marqués comme implémentés)
  - ✅ **Guide migration** : Mise à jour avec PostgreSQL et nouvelles fonctionnalités
  - ✅ **Workflow** : Session 42 documentée avec transition CLI → Web

### Prochaines versions
- **0.3** : Interface Web React avec Bootstrap
- **0.4** : API FastAPI complète
- **0.5** : Intégration WebSocket temps réel
- **...**
- **1.0** : Version stable finale

## Règles de versioning
- **0.x** : Versions de développement
- **1.x** : Version stable
- **Incrément automatique** : 0.1 → 0.2 → 0.3 → ... → 1.0
- **Log obligatoire** : Chaque package doit être enregistré ici 