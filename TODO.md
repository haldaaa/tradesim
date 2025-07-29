## Création du fichier le 28 juillet 2025 16H16 heure local Phnom Phen Cambodia
## Ici sera inscrit le reste a faire pour les prochaines sessions (chatgpt generated)




28/08/2025 16h16

Ajout de la logique d’achat

Chaque entreprise doit pouvoir acheter des produits

Deux stratégies à implémenter :

moins_cher ➝ elle achète le produit le moins cher disponible

par_type ➝ elle achète selon ses types préférés

Créer une route /tick ou /simulate

Pour simuler un cycle d’achat (genre une journée)

Réduction du budget des entreprises

Réduction du stock des fournisseurs

Afficher l’historique des achats (plus tard) :

Tu pourras logguer ou exposer dans /achats par exemple

À terme : servir ces logs à Prometheus ou les stocker dans un fichier / base

Ajout de fonctions utilitaires (progressivement) :

Créer une entreprise aléatoire (futur bouton ou crontab)

Augmenter automatiquement le budget des entreprises tous les X temps

Dashboard et visualisation (étapes futures) :

Exporter les données en JSON ou exposer des métriques

Brancher un Grafana via Prometheus ou autre



29/07/2025

🔧 À faire absolument :
 Ajouter une option --infinite à simulate.py pour un mode sans fin

 Refactoriser le tick pour qu’il soit persistant ou réinitialisé proprement si besoin

 Ajouter un champ nb_achats au log JSON pour faciliter l’exploitation dans Grafana

🧪 Tests unitaires (démarrage dès que le simulateur est stable) :
 Tester les comportements des stratégies d’achat

 Vérifier que le budget diminue correctement et que le stock se met à jour

 Tester les cas d’erreur (ex. : pas de stock, budget insuffisant)

🚀 Prochaine roadmap :
 Mettre tous les paramètres (budget, nb entreprises, etc.) dans un fichier .env ou config.json

 Préparer le Dockerfile + conteneurisation

 Intégration future avec Prometheus et Grafana pour visualiser les logs


