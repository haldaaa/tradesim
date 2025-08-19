#!/usr/bin/env python3
"""
Script d'import automatique des dashboards Grafana via l'API REST
Utilise l'API Grafana pour importer les dashboards JSON depuis le dossier provisioning
"""

import os
import json
import requests
import glob
from pathlib import Path

# Configuration
GRAFANA_URL = "http://localhost:3000"
GRAFANA_USER = "admin"
GRAFANA_PASSWORD = "admin"
DASHBOARDS_DIR = "monitoring/grafana/dashboards"

def import_dashboard(dashboard_file):
    """Import un dashboard via l'API Grafana"""
    try:
        # Lire le fichier JSON
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            dashboard_data = json.load(f)
        
        # Préparer la requête
        url = f"{GRAFANA_URL}/api/dashboards/db"
        headers = {"Content-Type": "application/json"}
        auth = (GRAFANA_USER, GRAFANA_PASSWORD)
        
        # Envoyer la requête
        response = requests.post(url, json=dashboard_data, headers=headers, auth=auth)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Dashboard importé: {dashboard_data['dashboard']['title']} (UID: {result['uid']})")
            return True
        else:
            print(f"❌ Erreur import {dashboard_file}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lecture {dashboard_file}: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Import automatique des dashboards Grafana")
    print("=" * 50)
    
    # Vérifier que Grafana est accessible
    try:
        response = requests.get(f"{GRAFANA_URL}/api/health", auth=(GRAFANA_USER, GRAFANA_PASSWORD))
        if response.status_code != 200:
            print("❌ Grafana n'est pas accessible")
            return
    except Exception as e:
        print(f"❌ Erreur connexion Grafana: {e}")
        return
    
    # Trouver tous les fichiers JSON de dashboards
    dashboard_files = glob.glob(f"{DASHBOARDS_DIR}/*.json")
    
    if not dashboard_files:
        print("❌ Aucun fichier dashboard trouvé")
        return
    
    print(f"📁 {len(dashboard_files)} fichiers dashboard trouvés")
    
    # Importer chaque dashboard
    success_count = 0
    for dashboard_file in dashboard_files:
        if os.path.basename(dashboard_file) in ['dashboard.yml', 'simple.json', 'test.json']:
            continue  # Ignorer les fichiers de config et de test
        
        print(f"\n📊 Import: {os.path.basename(dashboard_file)}")
        if import_dashboard(dashboard_file):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Import terminé: {success_count}/{len(dashboard_files)} dashboards importés")
    print(f"🌐 Accès Grafana: {GRAFANA_URL}")
    print(f"👤 Login: {GRAFANA_USER}/{GRAFANA_PASSWORD}")

if __name__ == "__main__":
    main()
