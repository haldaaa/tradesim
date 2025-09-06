#!/bin/bash
# Script de lancement Phase 1 - TradeSim Web Interface
# ====================================================

echo "🚀 PHASE 1 - TRADESIM WEB INTERFACE"
echo "===================================="

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé"
    exit 1
fi

# Vérifier que l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé. Créez-le avec: python3 -m venv venv"
    exit 1
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances si nécessaire
echo "📦 Vérification des dépendances..."
pip install -q fastapi uvicorn websockets

# Fonction pour nettoyer les processus
cleanup() {
    echo "🛑 Arrêt des services..."
    kill $API_PID $WEB_PID 2>/dev/null
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT

# Lancer l'API FastAPI
echo "🚀 Lancement de l'API FastAPI sur le port 8000..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Attendre que l'API soit prête
echo "⏳ Attente du démarrage de l'API..."
sleep 3

# Lancer l'interface Web
echo "🌐 Lancement de l'interface Web sur le port 3001..."
cd web
python3 server.py &
WEB_PID=$!
cd ..

echo ""
echo "✅ PHASE 1 DÉMARRÉE AVEC SUCCÈS!"
echo "================================"
echo "🌐 Interface Web: http://localhost:3001"
echo "📡 API FastAPI: http://localhost:8000"
echo "📊 Documentation API: http://localhost:8000/docs"
echo "🔗 Grafana: http://localhost:3000 (si monitoring actif)"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter tous les services"

# Attendre que les processus se terminent
wait
