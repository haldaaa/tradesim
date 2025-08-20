# Système Automatique de Gestion des Métriques - TradeSim

## 🎯 Objectif

Le système automatique de gestion des métriques permet d'ajouter de nouvelles métriques à TradeSim sans modifier manuellement le code de l'exporter Prometheus. Toutes les nouvelles métriques sont automatiquement détectées, créées et exposées.

## 🏗️ Architecture

### DynamicMetricsManager

Le `DynamicMetricsManager` est le cœur du système automatique. Il gère :

- **Création dynamique** des métriques Prometheus
- **Cache des métriques** pour éviter les doublons
- **Traitement automatique** des données reçues
- **Gestion des labels** et types de métriques

### Types de Métriques Supportés

1. **Gauge** : Valeurs numériques qui peuvent monter et descendre
2. **Counter** : Compteurs qui ne peuvent qu'augmenter
3. **Histogram** : Distribution de valeurs avec buckets

## 📝 Comment Ajouter de Nouvelles Métriques

### Méthode 1 : Métriques Simples

```python
# Dans votre service de métriques
metrics_data = {
    'nouvelle_metrique': 42.5,  # Sera automatiquement préfixé avec 'tradesim_'
    'tradesim_autre_metrique': 100  # Déjà préfixé
}
```

### Méthode 2 : Métriques avec Labels

```python
# Métrique avec labels
metrics_data = {
    'prix_produit': {
        'value': 150.0,
        'labels': {
            'produit': 'Marteau',
            'fournisseur': 'AsiaImport'
        },
        'type': 'gauge',
        'description': 'Prix du produit par fournisseur'
    }
}
```

### Méthode 3 : Métriques Agrégées

```python
# Dictionnaire simple - sera agrégé automatiquement
metrics_data = {
    'ventes_par_pays': {
        'France': 150,
        'Allemagne': 200,
        'Espagne': 100
    }
    # Sera automatiquement converti en: tradesim_ventes_par_pays = 450
}
```

## 🔧 Configuration

### Préfixe Automatique

Toutes les métriques sont automatiquement préfixées avec `tradesim_` :

```python
# Si vous envoyez:
metrics_data = {'budget_total': 100000}

# L'exporter créera automatiquement:
# tradesim_budget_total = 100000
```

### Gestion des Types

Le système détecte automatiquement le type de métrique :

- **int/float** → Gauge
- **dict avec 'value' et 'labels'** → Gauge avec labels
- **dict simple** → Gauge (valeur agrégée)

## 📊 Exemples d'Utilisation

### Exemple 1 : Métrique de Performance

```python
# Dans services/performance_metrics_service.py
def collect_performance_metrics():
    return {
        'temps_reponse_api': 0.15,
        'utilisation_memoire': 75.2,
        'requetes_par_seconde': 120
    }
```

### Exemple 2 : Métrique avec Labels

```python
# Dans services/transaction_metrics_service.py
def collect_transaction_metrics():
    return {
        'transaction_duree': {
            'value': 0.25,
            'labels': {
                'type': 'achat',
                'statut': 'reussi'
            },
            'description': 'Durée des transactions par type et statut'
        }
    }
```

### Exemple 3 : Métriques Complexes

```python
# Dans services/analytics_service.py
def collect_analytics_metrics():
    return {
        'tendances_prix': {
            'produit_1': 150.0,
            'produit_2': 200.0,
            'produit_3': 175.0
        },
        'satisfaction_client': {
            'value': 4.5,
            'labels': {
                'region': 'Europe',
                'periode': 'Q1'
            }
        }
    }
```

## 🚀 Avantages

### ✅ Automatique
- Aucune modification du code de l'exporter
- Détection automatique des nouvelles métriques
- Création dynamique des objets Prometheus

### ✅ Flexible
- Support de tous les types de métriques Prometheus
- Gestion automatique des labels
- Agrégation automatique des dictionnaires

### ✅ Robuste
- Gestion d'erreurs intégrée
- Cache pour éviter les doublons
- Compatibilité avec l'existant

### ✅ Maintenable
- Code centralisé dans `DynamicMetricsManager`
- Documentation complète
- Tests automatisés

## 🔍 Monitoring

### Vérification des Métriques

```bash
# Vérifier les métriques dans l'exporter
curl http://localhost:8000/metrics | grep tradesim_

# Vérifier dans Prometheus
curl "http://localhost:9090/api/v1/query?query=tradesim_nouvelle_metrique"
```

### Logs de Debug

Le système affiche des logs informatifs :

```
📊 Métriques mises à jour: budget=31863.09, tours=1, events=2
✅ Nouvelle métrique créée: tradesim_nouvelle_metrique
⚠️ Type de valeur non supporté pour tradesim_metrique_invalide: <class 'str'>
```

## 🧪 Tests

### Test d'Intégration

```python
def test_automatic_metrics():
    """Test l'ajout automatique de nouvelles métriques"""
    metrics_data = {
        'test_metrique': 42,
        'test_metrique_labels': {
            'value': 100,
            'labels': {'test': 'value'},
            'description': 'Test metric'
        }
    }
    
    exporter = PrometheusExporter()
    exporter.update_tradesim_metrics(metrics_data)
    
    # Vérifier que les métriques sont créées
    assert 'tradesim_test_metrique' in metrics_manager.metrics_registry
```

## 📚 Migration

### Compatibilité avec l'Existant

Le système est 100% compatible avec les métriques existantes :

- Les métriques prédéfinies continuent de fonctionner
- Le traitement manuel est conservé pour les cas complexes
- Aucune modification des services existants nécessaire

### Migration Progressive

1. **Phase 1** : Le système automatique fonctionne en parallèle
2. **Phase 2** : Les nouvelles métriques utilisent le système automatique
3. **Phase 3** : Migration des métriques existantes (optionnel)

## 🎯 Bonnes Pratiques

### Naming Convention

```python
# ✅ Bon
metrics_data = {
    'budget_total': 100000,
    'transactions_reussies': 50
}

# ❌ Éviter
metrics_data = {
    'BudgetTotal': 100000,  # Pas de camelCase
    'transactions-reussies': 50  # Pas de tirets
}
```

### Types de Données

```python
# ✅ Types supportés
int, float, dict

# ❌ Types non supportés
str, bool, list, tuple
```

### Labels

```python
# ✅ Labels valides
labels = {
    'produit': 'Marteau',
    'fournisseur': 'AsiaImport',
    'region': 'Asie'
}

# ❌ Labels invalides
labels = {
    'produit': '',  # Valeur vide
    'fournisseur': None,  # Valeur None
    'region': 'A' * 100  # Trop long
}
```

## 🔧 Dépannage

### Problèmes Courants

1. **Métrique non visible** : Vérifier le préfixe `tradesim_`
2. **Erreur de type** : S'assurer que la valeur est numérique
3. **Labels manquants** : Vérifier la structure du dictionnaire

### Debug

```python
# Activer le debug
import logging
logging.basicConfig(level=logging.DEBUG)

# Vérifier le registre des métriques
print(metrics_manager.metrics_registry.keys())
```

---

**Auteur** : Assistant IA  
**Date** : 2025-08-20  
**Version** : 1.0
