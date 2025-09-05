#!/usr/bin/env python3
"""
API TradeSim - Interface REST pour TradeSim
==========================================

Ce module fournit l'API REST pour TradeSim.
Il expose les endpoints pour accéder aux données
de manière structurée.

Refactorisation (02/08/2025) :
- Utilise les Repository au lieu d'accès directs aux données
- Code plus modulaire et testable
- Interface commune pour CLI et API

Auteur: Assistant IA
Date: 2024-08-02
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import asyncio
from models import Produit, TypeProduit, FournisseurComplet, ProduitChezFournisseur, Entreprise
from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
from models import Fournisseur  # type: ignore
from services.simulation_service import SimulationService
from config.config import get_default_config

# Initialisation des Repository
produit_repo = ProduitRepository()
fournisseur_repo = FournisseurRepository()
entreprise_repo = EntrepriseRepository()

# Création de l'application FastAPI
app = FastAPI(
    title="TradeSim API",
    description="API REST pour la simulation économique TradeSim",
    version="2.0.0"
)

# Configuration CORS pour l'interface React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic pour les requêtes
class SimulationRequest(BaseModel):
    tours: int = 10
    verbose: bool = False
    with_metrics: bool = True

class SimulationResponse(BaseModel):
    status: str
    result: Dict
    metrics: Optional[Dict] = None

class ConfigUpdateRequest(BaseModel):
    key: str
    value: str

# Gestionnaire WebSocket pour les connexions
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Supprimer les connexions fermées
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Route GET /
@app.get("/")
def read_root():
    """Point d'entrée de l'API"""
    return {
        "message": "Bienvenue sur TradeSim",
        "version": "1.0.0",
        "endpoints": {
            "produits": "/produits",
            "fournisseurs": "/fournisseurs", 
            "entreprises": "/entreprises"
        }
    }

@app.get("/produits", response_model=list[Produit])
def get_produits():
    """
    Récupère tous les produits actifs.
    
    Refactorisation (02/08/2025) :
    - Utilise ProduitRepository au lieu d'accès direct aux données
    """
    return [p for p in produit_repo.get_all() if p.actif]

@app.get("/fournisseurs", response_model=list[FournisseurComplet])
def get_fournisseurs_enrichis():
    """
    Récupère tous les fournisseurs avec leurs produits enrichis.
    
    Refactorisation (02/08/2025) :
    - Utilise FournisseurRepository et ProduitRepository
    - Gestion des prix à migrer vers un service plus tard
    """
    fournisseurs = fournisseur_repo.get_all()
    
    # Validation des données avant sérialisation
    if not isinstance(fournisseurs, list):
        raise HTTPException(status_code=500, detail="Données invalides")
    
    result = []
    for fournisseur in fournisseurs:
        produits = []

        for produit_id, stock in fournisseur.stock_produit.items():
            # Récupérer le produit depuis le repository
            produit = produit_repo.get_by_id(produit_id)
            nom_produit = produit.nom if produit else "???"
            
            # Utilise le service centralisé de gestion des prix
            from services.price_service import price_service
            prix = price_service.get_prix_produit_fournisseur(produit_id, fournisseur.id)
            
            # Si le prix n'est pas défini, utiliser un prix par défaut
            if prix is None:
                prix = 100.0  # Prix par défaut

            produits.append(ProduitChezFournisseur(
                produit_id=produit_id,
                nom=nom_produit,
                stock=stock,
                prix_unitaire=prix
            ))

        result.append(FournisseurComplet(
            id=fournisseur.id,
            nom_entreprise=fournisseur.nom_entreprise,
            pays=fournisseur.pays,
            continent=fournisseur.continent,
            produits=produits
        ))

    return result

@app.get("/entreprises", response_model=list[Entreprise])
def get_entreprises():
    """
    Récupère toutes les entreprises.
    
    Refactorisation (02/08/2025) :
    - Utilise EntrepriseRepository au lieu d'accès direct aux données
    """
    return entreprise_repo.get_all()

# ===== NOUVEAUX ENDPOINTS PHASE 1 =====

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": "2025-09-04T14:00:00Z"
    }

@app.get("/config")
def get_config():
    """Récupère la configuration actuelle"""
    try:
        config = get_default_config()
        return {
            "status": "success",
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la configuration: {str(e)}")

@app.post("/config")
def update_config(request: ConfigUpdateRequest):
    """Met à jour une valeur de configuration"""
    try:
        # Note: Dans une vraie implémentation, on sauvegarderait en base
        # Pour l'instant, on retourne juste un succès
        return {
            "status": "success",
            "message": f"Configuration {request.key} mise à jour avec la valeur {request.value}",
            "updated": {
                "key": request.key,
                "value": request.value
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

@app.post("/simulation", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest):
    """Lance une simulation avec les paramètres spécifiés"""
    try:
        # Initialiser le service de simulation
        simulation_service = SimulationService()
        
        # Lancer la simulation
        result = simulation_service.run_simulation_tours(
            nombre_tours=request.tours,
            verbose=request.verbose
        )
        
        # Envoyer un message WebSocket
        await manager.broadcast(json.dumps({
            "type": "simulation_completed",
            "tours": request.tours,
            "result": result
        }))
        
        return SimulationResponse(
            status="success",
            result=result,
            metrics=result.get("metrics") if request.with_metrics else None
        )
        
    except Exception as e:
        # Envoyer un message d'erreur WebSocket
        await manager.broadcast(json.dumps({
            "type": "simulation_error",
            "error": str(e)
        }))
        
        raise HTTPException(status_code=500, detail=f"Erreur lors de la simulation: {str(e)}")

@app.get("/metrics")
def get_metrics():
    """Récupère les métriques Prometheus"""
    try:
        # Dans une vraie implémentation, on récupérerait les métriques depuis Prometheus
        # Pour l'instant, on retourne des métriques factices
        return {
            "status": "success",
            "metrics": {
                "tours_completes": 0,
                "entreprises_actives": len(entreprise_repo.get_all()),
                "produits_actifs": len([p for p in produit_repo.get_all() if p.actif]),
                "fournisseurs_actifs": len(fournisseur_repo.get_all())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des métriques: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket pour la communication temps réel"""
    await manager.connect(websocket)
    try:
        while True:
            # Attendre des messages du client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Traiter le message selon son type
            if message.get("type") == "ping":
                await manager.send_personal_message(json.dumps({
                    "type": "pong",
                    "timestamp": "2025-09-04T14:00:00Z"
                }), websocket)
            elif message.get("type") == "subscribe":
                await manager.send_personal_message(json.dumps({
                    "type": "subscribed",
                    "message": "Abonnement aux mises à jour temps réel activé"
                }), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Erreur WebSocket: {e}")
        manager.disconnect(websocket)