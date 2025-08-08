# Métriques disponibles dans TradeSim
====================================

## ✅ Totaux par catégorie (document actuel)

- Simulation: 8
- Budgets: 14
- Entreprises: 9
- Produits: 13
- Fournisseurs: 5
- Transactions: 8
- Événements: 18
- Jeu: 4
- Performance: 10
- Techniques: 11
- Calculées: 4
- Système: 8

Total global (document actuel): 112

## 📊 **Métriques de simulation** — Total: 8

### **Temps et tours** — Total: 4
- **tick_actuel** -- Numéro du tick actuel de simulation -- services/simulation_service.py:SimulationService.tick_actuel
- **tours_completes** -- Nombre de tours de simulation complétés -- services/simulation_service.py:SimulationService.tours_completes
- **evenements_appliques** -- Nombre d'événements appliqués -- services/simulation_service.py:SimulationService.evenements_appliques
- **duree_simulation** -- Durée totale de la simulation en secondes -- services/simulation_service.py:SimulationService.calculer_statistiques()

### **Configuration** — Total: 4
- **probabilite_selection_entreprise** -- Probabilité de sélection d'une entreprise par tour -- config/config.py:PROBABILITE_SELECTION_ENTREPRISE
- **duree_pause_entre_tours** -- Pause entre les tours en secondes -- config/config.py:DUREE_PAUSE_ENTRE_TOURS
- **tick_interval_event** -- Intervalle entre les événements -- config/config.py:TICK_INTERVAL_EVENT
- **probabilite_evenement** -- Probabilité d'occurrence des événements -- config/config.py:PROBABILITE_EVENEMENT

## 💰 **Métriques de budget** — Total: 14

### **Budgets des entreprises** — Total: 10
- **budget_total_initial** -- Budget total initial de toutes les entreprises -- services/budget_service.py:BudgetService.get_statistiques_budgets()
- **budget_total_actuel** -- Budget total actuel de toutes les entreprises -- services/budget_service.py:BudgetService.get_statistiques_budgets()
- **budget_moyen** -- Budget moyen par entreprise -- services/budget_service.py:BudgetService.get_statistiques_budgets()
- **budget_min** -- Budget minimum d'une entreprise -- services/budget_service.py:BudgetService.get_statistiques_budgets()
- **budget_max** -- Budget maximum d'une entreprise -- services/budget_service.py:BudgetService.get_statistiques_budgets()
- **budget_moyen_initial** -- Budget moyen initial par entreprise -- services/budget_service.py:BudgetService.get_statistiques_budgets()
- **evolution_budget** -- Évolution du budget total (actuel - initial) -- services/budget_service.py:BudgetService.get_statistiques_budgets()
- **entreprises_solvables** -- Nombre d'entreprises avec budget > 0 -- services/budget_service.py:BudgetService.get_statistiques_budgets()
- **entreprises_en_difficulte** -- Nombre d'entreprises avec budget < seuil -- services/budget_service.py:BudgetService.get_entreprises_en_difficulte()
- **entreprises_prosperes** -- Nombre d'entreprises avec budget > seuil -- services/budget_service.py:BudgetService.get_entreprises_prosperes()

### **Recharges de budget** — Total: 4
- **recharges_budget_effectuees** -- Nombre de recharges de budget effectuées -- events/recharge_budget.py:appliquer_recharge_budget()
- **montant_recharge_moyen** -- Montant moyen des recharges -- events/recharge_budget.py:appliquer_recharge_budget()
- **recharge_budget_min** -- Montant minimum de recharge -- config/config.py:RECHARGE_BUDGET_MIN
- **recharge_budget_max** -- Montant maximum de recharge -- config/config.py:RECHARGE_BUDGET_MAX

## 🏢 **Métriques d'entreprises** — Total: 9

### **Comptage et état** — Total: 3
- **nombre_entreprises** -- Nombre total d'entreprises -- services/simulation_service.py:SimulationService.calculer_statistiques()
- **entreprises_actives** -- Nombre d'entreprises avec budget > 0 -- services/transaction_service.py:TransactionService.get_statistiques_transactions()
- **entreprises_selectionnees** -- Nombre d'entreprises sélectionnées par tour -- services/simulateur.py:simulation_tour()

### **Stratégies** — Total: 2
- **entreprises_strategie_moins_cher** -- Nombre d'entreprises avec stratégie "moins_cher" -- services/game_manager.py:generate_entreprises()
- **entreprises_strategie_par_type** -- Nombre d'entreprises avec stratégie "par_type" -- services/game_manager.py:generate_entreprises()

### **Géographie** — Total: 4
- **entreprises_par_continent** -- Répartition des entreprises par continent -- models/models.py:Entreprise.continent
- **fournisseurs_par_continent** -- Répartition des fournisseurs par continent -- models/models.py:Fournisseur.continent
- **transactions_intercontinentales** -- Nombre de transactions entre continents -- services/transaction_service.py:TransactionService.effectuer_achat()
- **prix_moyen_par_continent** -- Prix moyen des produits par continent -- services/price_service.py:PriceService.get_prix_moyen_continent()

## 📦 **Métriques de produits** — Total: 13

### **Comptage et état** — Total: 3
- **nombre_produits_total** -- Nombre total de produits -- services/simulation_service.py:SimulationService.calculer_statistiques()
- **nombre_produits_actifs** -- Nombre de produits actifs -- services/simulation_service.py:SimulationService.calculer_statistiques()
- **nombre_produits_inactifs** -- Nombre de produits inactifs -- services/simulation_service.py:SimulationService.calculer_statistiques()

### **Types de produits** — Total: 3
- **produits_matiere_premiere** -- Nombre de produits de type matière première -- services/game_manager.py:generate_produits()
- **produits_consommable** -- Nombre de produits de type consommable -- services/game_manager.py:generate_produits()
- **produits_produit_fini** -- Nombre de produits de type produit fini -- services/game_manager.py:generate_produits()

### **Prix** — Total: 3
- **prix_moyen_produits** -- Prix moyen des produits -- services/game_manager.py:generate_produits()
- **prix_min_produits** -- Prix minimum des produits -- services/game_manager.py:generate_produits()
- **prix_max_produits** -- Prix maximum des produits -- services/game_manager.py:generate_produits()

### **Évolution des prix** — Total: 4
- **evolution_prix_produits** -- Évolution des prix par produit -- events/inflation.py:appliquer_inflation()
- **volatilite_prix** -- Volatilité des prix (écart-type) -- services/price_service.py:PriceService.calculer_volatilite()
- **tendance_prix_par_produit** -- Tendance des prix par produit -- events/inflation.py:produits_inflation_timers
- **correlation_budget_transactions** -- Corrélation entre budget et transactions -- services/transaction_service.py:TransactionService.calculer_correlation()

## 🏪 **Métriques de fournisseurs** — Total: 5

### **Comptage** — Total: 2
- **nombre_fournisseurs** -- Nombre total de fournisseurs -- services/simulation_service.py:SimulationService.calculer_statistiques()
- **fournisseurs_actifs** -- Nombre de fournisseurs avec stock > 0 -- services/transaction_service.py:TransactionService.get_statistiques_transactions()

### **Stocks** — Total: 3
- **stock_total_produits** -- Stock total de tous les produits -- services/game_manager.py:generate_fournisseurs()
- **stock_moyen_par_produit** -- Stock moyen par produit -- services/game_manager.py:generate_fournisseurs()
- **produits_en_rupture** -- Nombre de produits en rupture de stock -- services/transaction_service.py:TransactionService.trouver_fournisseurs_produit()

## 💸 **Métriques de transactions** — Total: 8

### **Comptage et montants** — Total: 5
- **nombre_transactions** -- Nombre total de transactions -- services/transaction_service.py:TransactionService.get_statistiques_transactions()
- **montant_total_transactions** -- Montant total des transactions -- services/transaction_service.py:TransactionService.get_statistiques_transactions()
- **moyenne_prix_transactions** -- Prix moyen des transactions -- services/transaction_service.py:TransactionService.get_statistiques_transactions()
- **transactions_reussies** -- Nombre de transactions réussies -- services/transaction_service.py:TransactionService.effectuer_achat()
- **transactions_echouees** -- Nombre de transactions échouées -- services/transaction_service.py:TransactionService.effectuer_achat()

### **Détails des transactions** — Total: 3
- **dernieres_transactions** -- Liste des 10 dernières transactions -- services/transaction_service.py:TransactionService.get_statistiques_transactions()
- **transactions_par_entreprise** -- Nombre de transactions par entreprise -- services/transaction_service.py:TransactionService.get_statistiques_transactions()
- **transactions_par_fournisseur** -- Nombre de transactions par fournisseur -- services/transaction_service.py:TransactionService.get_statistiques_transactions()

## 📈 **Métriques d'événements** — Total: 18

### **Inflation** — Total: 5
- **inflation_appliquee** -- Nombre d'inflations appliquées -- events/inflation.py:appliquer_inflation()
- **produits_inflates** -- Nombre de produits ayant subi une inflation -- events/inflation.py:appliquer_inflation()
- **pourcentage_inflation_moyen** -- Pourcentage moyen d'inflation -- events/inflation.py:appliquer_inflation()
- **inflation_pourcentage_min** -- Pourcentage minimum d'inflation -- config/config.py:INFLATION_POURCENTAGE_MIN
- **inflation_pourcentage_max** -- Pourcentage maximum d'inflation -- config/config.py:INFLATION_POURCENTAGE_MAX

### **Inflation avancée (nouvelles features)** — Total: 5
- **inflation_penalite_appliquee** -- Nombre de pénalités d'inflation appliquées -- events/inflation.py:appliquer_inflation()
- **inflation_retour_normal_appliquee** -- Nombre de retours à la normale appliqués -- events/inflation.py:appliquer_retour_normal()
- **produits_en_phase_retour** -- Nombre de produits en phase de retour progressif -- events/inflation.py:produits_inflation_timers
- **duree_penalite_moyenne** -- Durée moyenne des pénalités d'inflation -- events/inflation.py:DUREE_PENALITE_INFLATION
- **pourcentage_penalite_moyen** -- Pourcentage moyen de pénalité appliquée -- events/inflation.py:PENALITE_INFLATION_PRODUIT_EXISTANT

### **Réassort** — Total: 5
- **reassort_applique** -- Nombre de réassorts appliqués -- events/reassort.py:evenement_reassort()
- **fournisseurs_reassortis** -- Nombre de fournisseurs réassortis -- events/reassort.py:evenement_reassort()
- **quantite_reassort_moyenne** -- Quantité moyenne de réassort -- events/reassort.py:evenement_reassort()
- **reassort_quantite_min** -- Quantité minimum de réassort -- config/config.py:REASSORT_QUANTITE_MIN
- **reassort_quantite_max** -- Quantité maximum de réassort -- config/config.py:REASSORT_QUANTITE_MAX

### **Variation de disponibilité** — Total: 3
- **variation_disponibilite_appliquee** -- Nombre de variations appliquées -- events/variation_disponibilite.py:appliquer_variation_disponibilite()
- **produits_actives** -- Nombre de produits activés -- events/variation_disponibilite.py:appliquer_variation_disponibilite()
- **produits_desactives** -- Nombre de produits désactivés -- events/variation_disponibilite.py:appliquer_variation_disponibilite()

## 🎮 **Métriques de jeu** — Total: 4

### **Templates** — Total: 2
- **nombre_templates** -- Nombre de templates sauvegardés -- services/game_manager.py:list_templates()
- **templates_disponibles** -- Liste des templates disponibles -- services/game_manager.py:list_templates()

### **Configuration** — Total: 2
- **config_actuelle** -- Configuration actuelle du jeu -- services/game_manager.py:get_current_config()
- **mode_execution** -- Mode d'exécution (CLI/WEB) -- config/mode.py:get_current_mode()

## 📊 **Métriques de performance** — Total: 10

### **Temps d'exécution** — Total: 3
- **temps_simulation_tour** -- Temps d'exécution d'un tour -- services/simulation_service.py:SimulationService.simulation_tour()
- **temps_evenement** -- Temps d'exécution des événements -- services/simulation_service.py:SimulationService.appliquer_evenements()
- **temps_transaction** -- Temps d'exécution des transactions -- services/transaction_service.py:TransactionService.effectuer_achat()

### **Mémoire** — Total: 3
- **nombre_entreprises_memoire** -- Nombre d'entreprises en mémoire -- repositories/entreprise_repository.py:FakeEntrepriseRepository.get_all()
- **nombre_produits_memoire** -- Nombre de produits en mémoire -- repositories/produit_repository.py:FakeProduitRepository.get_all()
- **nombre_fournisseurs_memoire** -- Nombre de fournisseurs en mémoire -- repositories/fournisseur_repository.py:FakeFournisseurRepository.get_all()

### **Performance système** — Total: 4
- **temps_calcul_prix** -- Temps de calcul des prix -- services/price_service.py:PriceService.calculer_prix()
- **temps_generation_entites** -- Temps de génération des entités -- services/game_manager.py:generate_entreprises()
- **memoire_utilisee_par_entite** -- Mémoire utilisée par entité -- repositories/base_repository.py:BaseRepository.get_memory_usage()
- **frequence_garbage_collection** -- Fréquence du garbage collection -- gc.get_stats()

## 🔧 **Métriques techniques** — Total: 11

### **API** — Total: 4
- **requetes_api_total** -- Nombre total de requêtes API -- api/main.py:app
- **requetes_api_produits** -- Nombre de requêtes GET /produits -- api/main.py:get_produits()
- **requetes_api_entreprises** -- Nombre de requêtes GET /entreprises -- api/main.py:get_entreprises()
- **requetes_api_fournisseurs** -- Nombre de requêtes GET /fournisseurs -- api/main.py:get_fournisseurs()

### **Logs** — Total: 3
- **logs_evenements_total** -- Nombre total de logs d'événements -- events/event_logger.py:log_evenement_json()
- **logs_transactions_total** -- Nombre total de logs de transactions -- services/transaction_service.py:TransactionService.effectuer_achat()
- **logs_erreurs_total** -- Nombre total de logs d'erreurs -- events/event_logger.py:log_evenement_humain()

### **Debug et monitoring** — Total: 4
- **erreurs_import** -- Nombre d'erreurs d'import de modules -- sys.modules
- **erreurs_validation_pydantic** -- Nombre d'erreurs de validation Pydantic -- models/models.py
- **erreurs_repository** -- Nombre d'erreurs de repository -- repositories/base_repository.py
- **warnings_system** -- Nombre d'avertissements système -- warnings.warn()

## 📈 **Métriques calculées** — Total: 4

### **Ratios et pourcentages** — Total: 4
- **ratio_transactions_reussies** -- Pourcentage de transactions réussies -- services/transaction_service.py:TransactionService.get_statistiques_transactions()
- **ratio_entreprises_solvables** -- Pourcentage d'entreprises solvables -- services/budget_service.py:BudgetService.get_statistiques_budgets()
- **ratio_produits_actifs** -- Pourcentage de produits actifs -- services/simulation_service.py:SimulationService.calculer_statistiques()
- **evolution_budget_pourcentage** -- Évolution du budget en pourcentage -- services/budget_service.py:BudgetService.get_statistiques_budgets()

## 🖥️ **Métriques système** — Total: 8

### **Ressources système** — Total: 4
- **cpu_usage** -- Utilisation CPU de l'application -- psutil.cpu_percent()
- **memory_usage** -- Utilisation mémoire de l'application -- psutil.virtual_memory()
- **disk_usage** -- Utilisation disque -- psutil.disk_usage()
- **network_usage** -- Utilisation réseau -- psutil.net_io_counters()

### **Tendances** — Total: 4
- **tendance_budget** -- Tendance du budget (croissant/décroissant) -- services/budget_service.py:BudgetService.get_statistiques_budgets()
- **tendance_transactions** -- Tendance des transactions -- services/transaction_service.py:TransactionService.get_statistiques_transactions()
- **tendance_prix** -- Tendance des prix -- events/inflation.py:appliquer_inflation()
- **tendance_achats_par_type** -- Évolution des achats par type de produit -- services/transaction_service.py:TransactionService.get_statistiques_transactions()

---

## 📝 **Notes d'implémentation**

### **Format des métriques pour Prometheus :**
```python
# Exemple de métrique Prometheus
tradesim_budget_total = Gauge('tradesim_budget_total', 'Budget total des entreprises')
tradesim_transactions_total = Counter('tradesim_transactions_total', 'Nombre total de transactions')
tradesim_simulation_duration = Histogram('tradesim_simulation_duration', 'Durée de simulation')
```

### **Métriques critiques pour le monitoring :**
1. **Budget total** - Indicateur de santé économique
2. **Nombre de transactions** - Activité du marché
3. **Produits actifs** - Disponibilité des biens
4. **Entreprises solvables** - Stabilité du système
5. **Temps de simulation** - Performance du système
6. **CPU/Mémoire** - Ressources système
7. **Pénalités d'inflation** - Santé économique avancée
8. **Transactions intercontinentales** - Activité géographique

### **Alertes recommandées :**
- Budget total < 1000€
- Aucune transaction pendant 5 tours
- Aucun produit actif
- Aucune entreprise solvable
- Temps de simulation > 10 secondes
- CPU usage > 80%
- Mémoire usage > 90%
- Aucune transaction intercontinentale
- Trop de pénalités d'inflation (> 50% des produits)

---

**Auteur :** Assistant IA  
**Date :** 2024-08-02  
**Version :** 2.0 (ajout de 25 nouvelles métriques) 

---

