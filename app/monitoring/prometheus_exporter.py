#!/usr/bin/env python3
"""
Exporter Prometheus pour TradeSim CLI
=====================================

Ce module expose les métriques de TradeSim au format Prometheus.
Il collecte les métriques depuis les services et les expose sur un endpoint HTTP.

Architecture:
- Processus séparé de la simulation principale
- Endpoint /metrics sur port 8000 par défaut
- Métriques système (CPU/mémoire) incluses
- Stockage JSONL pour persistance

Métriques exposées:
- budget_total (Gauge)
- transactions_total (Counter)
- produits_actifs (Gauge)
- tours_completes (Counter)
- temps_simulation_tour_seconds (Histogram)
- Métriques système (CPU, mémoire, etc.)
"""

import time
import json
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from prometheus_client import (
    start_http_server, 
    Gauge, 
    Counter, 
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)
from flask import Flask, Response
import psutil

# Configuration
from config import (
    METRICS_ENABLED,
    METRICS_EXPORTER_PORT,
    METRICS_EXPORTER_HOST,
    METRICS_COLLECTION_INTERVAL,
    METRICS_SYSTEM_ENABLED,
    METRICS_SYSTEM_INTERVAL
)

# ============================================================================
# MÉTRIQUES PROMETHEUS
# ============================================================================

# Métriques TradeSim
budget_total = Gauge('tradesim_budget_total', 'Budget total des entreprises')
transactions_total = Counter('tradesim_transactions_total', 'Nombre total de transactions')
produits_actifs = Gauge('tradesim_produits_actifs', 'Nombre de produits actifs')
tours_completes = Counter('tradesim_tours_completes', 'Nombre de tours effectués')
temps_simulation_tour_seconds = Histogram(
    'tradesim_temps_simulation_tour_seconds',
    'Durée d\'un tour de simulation',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Métriques système
cpu_usage_percent = Gauge('tradesim_cpu_usage_percent', 'Utilisation CPU (%)')
memory_usage_bytes = Gauge('tradesim_memory_usage_bytes', 'Utilisation mémoire (bytes)')
memory_usage_percent = Gauge('tradesim_memory_usage_percent', 'Utilisation mémoire (%)')
disk_usage_percent = Gauge('tradesim_disk_usage_percent', 'Utilisation disque (%)')
process_uptime_seconds = Gauge('tradesim_process_uptime_seconds', 'Temps de fonctionnement du processus')

# ============================================================================
# CLASSE EXPORTER
# ============================================================================

class PrometheusExporter:
    """
    Exporteur Prometheus pour TradeSim
    
    Responsabilités:
    - Démarrer/arrêter le serveur HTTP
    - Collecter les métriques système
    - Stocker les métriques en JSONL
    - Fournir les métriques au format Prometheus
    """
    
    def __init__(self, port: int = None, host: str = None):
        """
        Initialise l'exporteur Prometheus
        
        Args:
            port: Port de l'exporter (défaut: METRICS_EXPORTER_PORT)
            host: Host de l'exporter (défaut: METRICS_EXPORTER_HOST)
        """
        self.port = port or METRICS_EXPORTER_PORT
        self.host = host or METRICS_EXPORTER_HOST
        self.app = Flask(__name__)
        self.collection_thread = None
        self.running = False
        self.start_time = time.time()
        
        # Configuration des routes Flask
        self._setup_routes()
        
        # Fichier de stockage JSONL
        self.metrics_file = "logs/metrics.jsonl"
        
    def _setup_routes(self):
        """Configure les routes Flask pour l'exporter"""
        
        @self.app.route('/metrics')
        def metrics():
            """Endpoint principal pour les métriques Prometheus"""
            return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
        
        @self.app.route('/health')
        def health():
            """Endpoint de santé de l'exporter"""
            return {
                'status': 'healthy',
                'uptime': time.time() - self.start_time,
                'metrics_enabled': METRICS_ENABLED
            }
        
        @self.app.route('/')
        def index():
            """Page d'accueil avec informations sur l'exporter"""
            return {
                'service': 'TradeSim Prometheus Exporter',
                'version': '1.0.0',
                'endpoints': {
                    '/metrics': 'Métriques Prometheus',
                    '/health': 'Santé du service',
                    '/': 'Cette page'
                },
                'configuration': {
                    'port': self.port,
                    'host': self.host,
                    'metrics_enabled': METRICS_ENABLED,
                    'collection_interval': METRICS_COLLECTION_INTERVAL
                }
            }
    
    def start(self):
        """Démarre l'exporteur Prometheus"""
        if not METRICS_ENABLED:
            print("⚠️  Monitoring désactivé dans la configuration")
            return
            
        try:
            # Démarrage du serveur Flask
            self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False
            )
            print(f"✅ Exporter Prometheus démarré sur {self.host}:{self.port}")
            
        except Exception as e:
            print(f"❌ Erreur lors du démarrage de l'exporter: {e}")
    
    def collect_system_metrics(self):
        """Collecte les métriques système"""
        if not METRICS_SYSTEM_ENABLED:
            return
            
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_usage_percent.set(cpu_percent)
            
            # Mémoire
            memory = psutil.virtual_memory()
            memory_usage_bytes.set(memory.used)
            memory_usage_percent.set(memory.percent)
            
            # Disque
            disk = psutil.disk_usage('/')
            disk_usage_percent.set(disk.percent)
            
            # Uptime du processus
            process_uptime_seconds.set(time.time() - self.start_time)
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la collecte des métriques système: {e}")
    
    def update_tradesim_metrics(self, metrics_data: Dict[str, Any]):
        """
        Met à jour les métriques TradeSim
        
        Args:
            metrics_data: Dictionnaire contenant les métriques à mettre à jour
        """
        try:
            # Mise à jour des métriques selon les données reçues
            if 'budget_total' in metrics_data:
                budget_total.set(metrics_data['budget_total'])
            
            if 'transactions_total' in metrics_data:
                transactions_total.inc(metrics_data['transactions_total'])
            
            if 'produits_actifs' in metrics_data:
                produits_actifs.set(metrics_data['produits_actifs'])
            
            if 'tours_completes' in metrics_data:
                tours_completes.inc(metrics_data['tours_completes'])
            
            if 'temps_simulation_tour_seconds' in metrics_data:
                temps_simulation_tour_seconds.observe(metrics_data['temps_simulation_tour_seconds'])
            
            # Stockage en JSONL
            self._store_metrics_jsonl(metrics_data)
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la mise à jour des métriques: {e}")
    
    def _store_metrics_jsonl(self, metrics_data: Dict[str, Any]):
        """
        Stocke les métriques en format JSONL
        
        Args:
            metrics_data: Données des métriques à stocker
        """
        try:
            # Ajout du timestamp
            metrics_entry = {
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics_data
            }
            
            # Écriture en JSONL
            with open(self.metrics_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metrics_entry) + '\n')
                
        except Exception as e:
            print(f"⚠️  Erreur lors du stockage JSONL: {e}")

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_exporter_status() -> Dict[str, Any]:
    """
    Retourne le statut de l'exporteur
    
    Returns:
        Dictionnaire contenant le statut de l'exporteur
    """
    return {
        'enabled': METRICS_ENABLED,
        'port': METRICS_EXPORTER_PORT,
        'host': METRICS_EXPORTER_HOST,
        'endpoint': f"http://{METRICS_EXPORTER_HOST}:{METRICS_EXPORTER_PORT}/metrics",
        'health': f"http://{METRICS_EXPORTER_HOST}:{METRICS_EXPORTER_PORT}/health"
    }

def format_monitoring_status() -> str:
    """
    Formate le statut du monitoring pour l'affichage CLI
    
    Returns:
        Chaîne formatée du statut monitoring
    """
    if not METRICS_ENABLED:
        return "❌ DÉSACTIVÉ"
    
    return f"✅ ACTIVÉ (port {METRICS_EXPORTER_PORT})"

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    """Point d'entrée pour tester l'exporteur en standalone"""
    print("🚀 Démarrage de l'exporteur Prometheus TradeSim...")
    
    exporter = PrometheusExporter()
    exporter.start() 