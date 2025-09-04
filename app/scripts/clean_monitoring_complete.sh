#!/bin/bash
# Script de nettoyage COMPLET du monitoring TradeSim
# Usage: ./scripts/clean_monitoring_complete.sh

echo "🧹 Nettoyage COMPLET du monitoring TradeSim..."

# 1. Arrêter l'exporter Python
echo "📴 Arrêt de l'exporter Python..."
pkill -f prometheus_exporter.py 2>/dev/null || true

# 2. Supprimer les logs TradeSim
echo "🗑️ Suppression des logs TradeSim..."
rm -f logs/*.jsonl logs/*.log

# 3. Arrêter les services Docker
echo "📴 Arrêt des services Docker..."
cd monitoring
docker-compose down

# 4. Supprimer le container Prometheus (données stockées dedans)
echo "🗑️ Suppression du container Prometheus..."
docker rm -f tradesim-prometheus 2>/dev/null || true

# 5. Supprimer les volumes Docker orphelins
echo "🗑️ Nettoyage des volumes Docker..."
docker volume prune -f

# 6. Redémarrer les services
echo "🚀 Redémarrage des services..."
docker-compose up -d

# 7. Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 15

# 8. Vérifier que Prometheus est vide
echo "✅ Vérification que Prometheus est vide..."
RESULT=$(curl -s "http://localhost:9090/api/v1/query?query=tradesim_entreprise_budget" | grep -o '"result":\[\]' || echo "HAS_DATA")
if [ "$RESULT" = '"result":[]' ]; then
    echo "✅ Prometheus est vide - Succès !"
else
    echo "❌ Prometheus contient encore des données"
fi

# 9. Vérifier le statut des services
echo "📊 Statut des services:"
docker-compose ps

echo "🎉 Nettoyage terminé ! Monitoring prêt pour une nouvelle simulation."
echo "💡 Pour lancer une nouvelle simulation: python services/simulate.py --tours X --with-metrics"
