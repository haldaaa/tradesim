#!/bin/bash
"""
Script de démarrage du monitoring TradeSim
Lance Prometheus, Grafana et importe automatiquement les dashboards
"""

echo "🚀 Démarrage du monitoring TradeSim"
echo "=================================="

# Démarrer les services
echo "📦 Démarrage de Prometheus et Grafana..."
cd monitoring
docker-compose up -d

# Attendre que Grafana soit prêt
echo "⏳ Attente du démarrage de Grafana..."
sleep 10

# Vérifier que Grafana est accessible
echo "🔍 Vérification de l'accessibilité de Grafana..."
for i in {1..30}; do
    if curl -s http://localhost:3000/api/health > /dev/null; then
        echo "✅ Grafana est prêt !"
        break
    fi
    echo "⏳ Tentative $i/30..."
    sleep 2
done

# Importer les dashboards
echo "📊 Import automatique des dashboards..."
cd ..
source venv/bin/activate
python monitoring/import_dashboards.py

echo ""
echo "🎉 Monitoring TradeSim démarré avec succès !"
echo "=========================================="
echo "🌐 Grafana: http://localhost:3000 (admin/admin)"
echo "📊 Prometheus: http://localhost:9090"
echo "📈 Exporteur: http://localhost:8000/metrics"
echo ""
echo "📋 Dashboards disponibles:"
echo "  - TradeSim - Simulation Overview"
echo "  - TradeSim - Finances & Budgets"
echo "  - TradeSim - Entreprises & Stratégies"
echo "  - TradeSim - Produits & Fournisseurs"
echo "  - TradeSim - Événements & Métriques Avancées"
echo "  - TradeSim - Produit: \$produit (template)"
echo "  - TradeSim - Entreprise: \$entreprise (template)"
echo "  - TradeSim - Fournisseur: \$fournisseur (template)"
echo ""
echo "🔄 Pour relancer l'import des dashboards:"
echo "   python monitoring/import_dashboards.py"
