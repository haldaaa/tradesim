# Logs TradeSim - Format et Cas d'Usage

## 📁 **Structure des fichiers de logs**

```
logs/
├── simulation_humain.log    # Logs humains des transactions (achats/ventes)
├── simulation.jsonl         # Données JSON des transactions
├── event.log               # Logs humains des événements (inflation, recharge, etc.)
├── event.jsonl             # Données JSON des événements
├── metrics.jsonl           # Données JSON des métriques Prometheus
└── monitoring.log          # Logs des erreurs Docker/monitoring
```

## 🆔 **Système d'IDs uniques**

### **Format des IDs**
```
DATE_HHMMSS_TYPE_COUNTER
```

**Exemples :**
- `20250810_143022_TXN_001` : Transaction #1 de la session 2025-08-10 14:30:22
- `20250810_143022_EVT_001` : Événement #1 de la session 2025-08-10 14:30:22
- `20250810_143022_METRIC_001` : Métrique #1 de la session 2025-08-10 14:30:22

### **Types d'actions**
- **TXN** : Transactions (achats/ventes)
- **EVT** : Événements (inflation, recharge, reassort, variation)
- **METRIC** : Collectes de métriques Prometheus
- **TICK** : Tours de simulation
- **ALERT** : Alertes système
- **TEMPLATE** : Templates de configuration

### **Session ID**
- **CLI** : Une session = Un lancement (`20250810_143022`)
- **Web** : Une session = Un jour complet (`20250810_000000`)

## 📊 **Format des logs JSON**

### **Transaction réussie**
```json
{
  "action_id": "20250810_143022_TXN_001",
  "session_id": "20250810_143022",
  "tick": 15,
  "timestamp": "2025-08-10T14:30:22.123456+00:00",
  "timestamp_humain": "10/08/2025 14:30:22",
  "strategie": "moins_cher",
  "entreprise_id": 3,
  "entreprise_nom": "ThaiTech",
  "produit_id": 5,
  "produit_nom": "Colle",
  "produit_type": "consommable",
  "fournisseur_id": 2,
  "fournisseur_nom": "SwedishTools",
  "quantite": 99,
  "prix_unitaire": 96.80,
  "montant_total": 9583.20,
  "budget_restant": 8183.54,
  "status": "success"
}
```

### **Transaction échouée**
```json
{
  "action_id": "20250810_143022_TXN_002",
  "session_id": "20250810_143022",
  "tick": 16,
  "timestamp": "2025-08-10T14:30:23.123456+00:00",
  "timestamp_humain": "10/08/2025 14:30:23",
  "strategie": "par_type",
  "entreprise_id": 1,
  "entreprise_nom": "NigerianTech",
  "produit_id": 6,
  "produit_nom": "Béton",
  "produit_type": "materiau",
  "fournisseur_id": 3,
  "fournisseur_nom": "FinnishDistrib",
  "prix_unitaire": 379.42,
  "quantite_voulue": 1,
  "prix_total_voulu": 379.42,
  "budget_disponible": 123.22,
  "status": "failed",
  "erreur": "budget_insuffisant"
}
```

### **Événement**
```json
{
  "action_id": "20250810_143022_EVT_001",
  "session_id": "20250810_143022",
  "tick": 20,
  "timestamp": "2025-08-10T14:30:25.123456+00:00",
  "timestamp_humain": "10/08/2025 14:30:25",
  "event_type": "inflation",
  "type": "inflation",
  "produits_affectes": [5, 8, 12],
  "pourcentages": [35.4, 42.1, 38.7],
  "statistiques": {
    "min": 35.4,
    "max": 42.1,
    "moyenne": 38.7
  },
  "log_humain": "[INFLATION] Catégorie ciblée : consommable - 2 prix modifiés | Min: +30.3% | Max: +40.5% | Moy: +35.4%"
}
```

### **Métrique**
```json
{
  "action_id": "20250810_143022_METRIC_001",
  "session_id": "20250810_143022",
  "tick": 15,
  "timestamp": "2025-08-10T14:30:22.123456+00:00",
  "timestamp_humain": "10/08/2025 14:30:22",
  "type": "metrics",
  "budget_total_actuel": 43238.75,
  "nombre_entreprises": 7,
  "nombre_produits_actifs": 15,
  "nombre_fournisseurs": 5,
  "tours_completes": 15,
  "evenements_appliques": 3,
  "temps_simulation_tour_seconds": 0.1234
}
```

## 🎯 **Cas d'usage concrets**

### **1. Analyse de l'impact des événements**
```bash
# Trouver toutes les transactions après un événement d'inflation
grep "20250810_143022_EVT_001" logs/simulation.jsonl

# Analyser l'évolution des prix
jq 'select(.action_id | startswith("20250810_143022_TXN")) | {tick, prix_unitaire, produit_nom}' logs/simulation.jsonl
```

### **2. Performance d'une session**
```bash
# Statistiques d'une session complète
jq 'select(.session_id == "20250810_143022") | {action_id, type, status}' logs/simulation.jsonl

# Taux de réussite des transactions
jq 'select(.session_id == "20250810_143022" and .type == "transaction") | .status' logs/simulation.jsonl | sort | uniq -c
```

### **3. Debugging d'une transaction spécifique**
```bash
# Replay d'une transaction
grep "20250810_143022_TXN_045" logs/*.jsonl

# Contexte avant/après
jq 'select(.tick >= 15 and .tick <= 17)' logs/simulation.jsonl
```

### **4. Dashboards Grafana**
```sql
-- Impact des événements sur les achats
SELECT 
  e.action_id as event_id,
  e.event_type,
  COUNT(t.action_id) as transactions_after_event,
  AVG(t.prix_unitaire) as avg_price_after_event
FROM event e
JOIN transaction t ON t.tick > e.tick
WHERE e.session_id = '20250810_143022'
GROUP BY e.action_id, e.event_type
```

### **5. Monitoring long terme (version Web)**
```sql
-- Performance par jour
SELECT 
  DATE(timestamp) as jour,
  COUNT(*) as total_transactions,
  AVG(montant_total) as avg_transaction_amount,
  COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_transactions
FROM transaction
WHERE session_id LIKE '20250810_%'
GROUP BY DATE(timestamp)
```

## 🔧 **Outils d'analyse**

### **Script d'analyse rapide**
```bash
#!/bin/bash
# Analyse d'une session
SESSION_ID="20250810_143022"

echo "=== Analyse session $SESSION_ID ==="
echo "Transactions: $(grep $SESSION_ID logs/simulation.jsonl | wc -l)"
echo "Événements: $(grep $SESSION_ID logs/event.jsonl | wc -l)"
echo "Métriques: $(grep $SESSION_ID logs/metrics.jsonl | wc -l)"
```

### **Filtrage par type**
```bash
# Transactions réussies
jq 'select(.status == "success")' logs/simulation.jsonl

# Événements d'inflation
jq 'select(.event_type == "inflation")' logs/event.jsonl

# Métriques avec budget élevé
jq 'select(.budget_total_actuel > 50000)' logs/metrics.jsonl
```

## 📈 **Évolution future**

### **Version Web (sessions longues)**
- Session par jour : `20250810_000000`
- Corrélation cross-sessions
- Analyse temporelle avancée

### **Corrélation avancée**
- Impact d'événements multiples sur une transaction
- Chaînes d'événements (inflation → recharge → achats)
- Patterns de comportement

### **Monitoring temps réel**
- Alertes sur patterns anormaux
- Dashboards dynamiques
- Analyse prédictive

---

**Note :** Ce système d'IDs permet une traçabilité complète pour l'analyse, le debugging et le monitoring de TradeSim.
