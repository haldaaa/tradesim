#!/usr/bin/env python3
"""
Serveur simple pour l'interface Web TradeSim
============================================

Ce serveur sert l'interface React et fait du proxy vers l'API FastAPI.

Auteur: Assistant IA
Date: 2024-09-04
"""

import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import os
from pathlib import Path

class TradeSimHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def do_GET(self):
        # Si c'est une requête vers l'API, faire du proxy
        if self.path.startswith('/api/'):
            self.proxy_to_api()
        else:
            # Sinon, servir les fichiers statiques
            super().do_GET()
    
    def do_POST(self):
        # Toutes les requêtes POST vont vers l'API
        if self.path.startswith('/api/'):
            self.proxy_to_api()
        else:
            self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        # Gestion CORS pour les requêtes preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def proxy_to_api(self):
        """Fait du proxy vers l'API FastAPI"""
        try:
            # Construire l'URL de l'API
            api_url = f"http://localhost:8000{self.path.replace('/api', '')}"
            
            # Préparer la requête
            if self.command == 'GET':
                req = urllib.request.Request(api_url)
            else:  # POST
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                req = urllib.request.Request(api_url, data=post_data)
                req.add_header('Content-Type', self.headers.get('Content-Type', 'application/json'))
            
            # Ajouter les headers
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'content-length']:
                    req.add_header(header, value)
            
            # Faire la requête
            with urllib.request.urlopen(req) as response:
                # Lire la réponse
                response_data = response.read()
                
                # Envoyer la réponse
                self.send_response(response.status)
                self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_data)
                
        except Exception as e:
            self.send_error(500, f"Erreur proxy: {str(e)}")

def run_server(port=3000):
    """Lance le serveur web"""
    with socketserver.TCPServer(("", port), TradeSimHandler) as httpd:
        print(f"🌐 Interface Web TradeSim disponible sur http://localhost:{port}")
        print(f"📡 Proxy API vers http://localhost:8000")
        print("Appuyez sur Ctrl+C pour arrêter")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Serveur arrêté")

if __name__ == "__main__":
    run_server()
