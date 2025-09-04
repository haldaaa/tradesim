#!/bin/bash
# Script de nettoyage complet du monitoring TradeSim
# Usage: ./scripts/clean_monitoring.sh

echo "🧹 Nettoyage complet du monitoring TradeSim..."

# 1. Arrêter les services
echo "📴 Arrêt des services..."
cd /Users/fares/Desktop/DevVoyage/tradesim/app/monitoring
docker-compose down

# 2. Supprimer les logs TradeSim
echo "🗑️ Suppression des logs TradeSim..."
cd /Users/fares/Desktop/DevVoyage/tradesim/app
rm -f logs/*.jsonl logs/*.log

# 3. Supprimer les données Prometheus
echo "🗑️ Suppression des données Prometheus..."
rm -rf monitoring/prometheus_data/*

# 4. Supprimer les données Grafana
echo "🗑️ Suppression des données Grafana..."
rm -rf monitoring/grafana_data/*

# 5. Redémarrer les services
echo "🚀 Redémarrage des services..."
cd monitoring
docker-compose up -d

# 6. Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 10

# 7. Vérifier le statut
echo "✅ Vérification du statut..."
docker-compose ps

echo "🎉 Nettoyage terminé ! Monitoring prêt pour une nouvelle simulation."
