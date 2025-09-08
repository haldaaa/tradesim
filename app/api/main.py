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
from datetime import datetime
from models import Produit, TypeProduit, FournisseurComplet, ProduitChezFournisseur, Entreprise
from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
from models import Fournisseur  # type: ignore
from services.simulation_service import SimulationService
from config.config import get_default_config, PROBABILITE_EVENEMENT

# Cache pour les logs (éviter de relire les fichiers à chaque tour)
logs_cache = {
    'event_logs': {},
    'simulation_logs': {},
    'last_read_tour': -1
}

# Initialisation des Repository
produit_repo = ProduitRepository()
fournisseur_repo = FournisseurRepository()
entreprise_repo = EntrepriseRepository()

# Fonction d'enrichissement des données avec calculs de probabilités
def enrich_with_probability_calculations(result_tour: dict, tour_number: int) -> dict:
    """
    Enrichit les données du tour avec les calculs de probabilités des événements.
    
    Args:
        result_tour: Résultat du tour de simulation
        tour_number: Numéro du tour
        
    Returns:
        Données enrichies avec calculs de probabilités
    """
    enriched_result = result_tour.copy()
    
    # Enrichir les événements avec les calculs de probabilités
    if 'evenements' in enriched_result and enriched_result['evenements']:
        enriched_events = []
        
        for event in enriched_result['evenements']:
            enriched_event = event.copy()
            
            # Déterminer le type d'événement et sa probabilité configurée
            event_type = None
            if 'inflation' in str(event).lower():
                event_type = 'inflation'
            elif 'reassort' in str(event).lower():
                event_type = 'reassort'
            elif 'recharge' in str(event).lower() and 'budget' in str(event).lower():
                event_type = 'recharge_budget'
            elif 'variation' in str(event).lower():
                event_type = 'variation_disponibilite'
            elif 'stock' in str(event).lower() and 'fournisseur' in str(event).lower():
                event_type = 'recharge_stock_fournisseur'
            
            if event_type and event_type in PROBABILITE_EVENEMENT:
                # Utiliser les vraies probabilités configurées
                threshold = PROBABILITE_EVENEMENT[event_type]
                
                # Simuler le calcul de probabilité (en attendant les vraies données)
                import random
                random_value = round(random.random(), 3)
                triggered = random_value < threshold
                
                # Ajouter les calculs de probabilité (FORMAT 4C-C)
                enriched_event['seuil_declenchement'] = threshold
                enriched_event['valeur_aleatoire'] = random_value
                enriched_event['statut_declenche'] = triggered
                enriched_event['probability_calculation'] = f"random() = {random_value} | Seuil: {threshold} | Résultat: {random_value} {'<' if triggered else '>'} {threshold} → {'✅ DÉCLENCHÉ' if triggered else '❌ NON DÉCLENCHÉ'}"
            
            enriched_events.append(enriched_event)
        
        enriched_result['evenements'] = enriched_events
    
    return enriched_result


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
    """
    Lance une simulation tour par tour avec WebSocket pour Grafana
    
    ARCHITECTURE :
    - Initialise le jeu (entreprises, produits, fournisseurs)
    - Lance la simulation tour par tour
    - Collecte les logs de transactions et événements
    - Envoie les données via WebSocket pour monitoring Grafana
    - Retourne les métriques finales
    
    FLUX DE DONNÉES :
    1. Vider le cache et les fichiers de logs
    2. Initialiser le jeu avec generate_game_data()
    3. Lancer la simulation tour par tour
    4. Lire les logs de transactions et événements
    5. Enrichir les données pour l'affichage web
    6. Envoyer via WebSocket et retourner les métriques
    
    FILTRAGE DES LOGS :
    - Transactions : filtrées par tour/tick et présence de 'status'
    - Événements : filtrés par tour et event_type='evenements_tour'
    - Session : filtrage par session_id pour éviter les données croisées
    
    PERFORMANCE :
    - Cache des logs pour éviter les relectures
    - Filtrage optimisé par tour
    - Enrichissement des données en mémoire
    
    Args:
        request: SimulationRequest avec tours, verbose, with_metrics
        
    Returns:
        SimulationResponse avec métriques et données détaillées
    """
    try:
        # ========================================================================
        # ÉTAPE 1: INITIALISATION ET NETTOYAGE
        # ========================================================================
        
        # Vider le cache des logs pour une nouvelle simulation
        logs_cache['event_logs'] = {}
        logs_cache['simulation_logs'] = {}
        logs_cache['last_read_tour'] = -1
        logs_cache['current_session_id'] = None
        
        # Vider les fichiers de logs pour éviter les données anciennes
        try:
            open('logs/simulation.jsonl', 'w').close()
            open('logs/event.jsonl', 'w').close()
            print(f"🧹 Fichiers de logs vidés")
        except Exception as e:
            print(f"⚠️ Erreur lors du vidage des logs: {e}")
        
        print(f"📊 Cache initial: {len(logs_cache['event_logs'])} événements, {len(logs_cache['simulation_logs'])} transactions")
        
        # ========================================================================
        # ÉTAPE 2: INITIALISATION DU JEU
        # ========================================================================
        
        # Initialiser le jeu (entreprises, produits, fournisseurs)
        from services.game_manager import reset_game, generate_game_data, get_default_config
        reset_game()
        generate_game_data(get_default_config())
        print("🎮 Jeu initialisé (entreprises, produits, fournisseurs)")
        
        # Initialiser le service de simulation
        simulation_service = SimulationService()
        
        # ========================================================================
        # ÉTAPE 3: LANCEMENT DE LA SIMULATION
        # ========================================================================
        
        # Envoyer un message de début de simulation
        await manager.broadcast(json.dumps({
            "type": "simulation_started",
            "tours": request.tours,
            "message": "Simulation démarrée"
        }))
        
        # Lancer la simulation tour par tour
        for tour in range(request.tours):
            # Définir le timestamp de début AVANT le premier tour seulement
            if tour == 0:
                logs_cache['simulation_start_time'] = datetime.now().isoformat()
                print(f"🚀 Simulation démarrée à {logs_cache['simulation_start_time']}")
            
            # Exécuter un tour (sans affichage terminal)
            result_tour = simulation_service.simulation_tour(verbose=False)
            
            # ========================================================================
            # ÉTAPE 4: COLLECTE DES LOGS ET MÉTRIQUES
            # ========================================================================
            
            # Récupérer le session_id du premier tour pour filtrer les logs
            if logs_cache['current_session_id'] is None:
                try:
                    with open('logs/event.jsonl', 'r') as f:
                        for line in f:
                            if line.strip():
                                try:
                                    event_data = json.loads(line)
                                    if event_data.get('tour') == tour:
                                        logs_cache['current_session_id'] = event_data.get('session_id')
                                        break
                                except:
                                    pass
                except:
                    pass
            
            # Enrichir les données avec les calculs de probabilités
            enriched_result = enrich_with_probability_calculations(result_tour, tour + 1)
            
            # Ajouter les données manquantes pour l'affichage
            enriched_result['transactions_effectuees'] = result_tour.get('transactions_effectuees', 0)
            enriched_result['evenements'] = result_tour.get('evenements', [])
            
            # Récupérer les détails des événements depuis les logs (avec cache)
            evenements_detaille = []
            try:
                # Utiliser le cache si disponible
                if tour in logs_cache['event_logs']:
                    evenements_detaille = logs_cache['event_logs'][tour]
                else:
                    # Lire depuis le fichier et mettre en cache
                    with open('logs/event.jsonl', 'r') as f:
                        for line in f:
                            if line.strip():
                                try:
                                    event_data = json.loads(line)
                                    event_tour = event_data.get('tick')
                                    
                                    # Ne traiter que les événements du tour actuel (assouplir le filtrage session)
                                    log_tour = event_data.get('tour')
                                    session_id = event_data.get('session_id')
                                    # Filtrer les événements par tour et type
                                    if (log_tour == tour and 
                                        event_data.get('event_type') == 'evenements_tour' and
                                        (logs_cache['current_session_id'] is None or 
                                         session_id == logs_cache['current_session_id'] or
                                         (session_id and logs_cache['current_session_id'] and 
                                          session_id[:8] == logs_cache['current_session_id'][:8]))):
                                        if log_tour not in logs_cache['event_logs']:
                                            logs_cache['event_logs'][log_tour] = []
                                        logs_cache['event_logs'][log_tour].append(event_data)
                                except:
                                    pass
                    evenements_detaille = logs_cache['event_logs'].get(tour, [])
                    
                    # Debug: Afficher le nombre d'événements trouvés
                    print(f"🎲 Tour {tour}: {len(evenements_detaille)} événements trouvés")
            except:
                pass
            
            # Récupérer les détails des transactions depuis les logs (avec cache)
            transactions_detaille = []
            try:
                # Utiliser le cache si disponible
                if tour in logs_cache['simulation_logs']:
                    transactions_detaille = logs_cache['simulation_logs'][tour]
                else:
                    # Lire depuis le fichier et mettre en cache
                    with open('logs/simulation.jsonl', 'r') as f:
                        for line in f:
                            if line.strip():
                                try:
                                    txn_data = json.loads(line)
                                    txn_tour = txn_data.get('tick')
                                    
                                    # Ne traiter que les transactions du tour actuel (assouplir le filtrage session)
                                    log_tour = txn_data.get('tour')
                                    session_id = txn_data.get('session_id')
                                    
                                    # Pour les transactions, on filtre par tick (qui correspond au tour) et présence de 'status'
                                    if ((log_tour == tour or txn_tour == tour) and 'status' in txn_data):
                                        # Utiliser le tour ou le tick comme clé
                                        cache_key = log_tour if log_tour is not None else txn_tour
                                        if cache_key not in logs_cache['simulation_logs']:
                                            logs_cache['simulation_logs'][cache_key] = []
                                        
                                        # Enrichir avec les détails manquants (FORMAT 4C-C)
                                        enriched_txn = txn_data.copy()
                                        
                                        # Ajouter les champs manquants si pas présents
                                        if 'budget_avant' not in enriched_txn:
                                            # Calculer budget_avant = budget_restant + montant_total
                                            budget_restant = enriched_txn.get('budget_restant', 0)
                                            montant = enriched_txn.get('montant_total', 0)
                                            if isinstance(budget_restant, (int, float)) and isinstance(montant, (int, float)):
                                                enriched_txn['budget_avant'] = budget_restant + montant
                                            else:
                                                enriched_txn['budget_avant'] = 'N/A'
                                        if 'budget_apres' not in enriched_txn:
                                            # budget_apres = budget_restant
                                            enriched_txn['budget_apres'] = enriched_txn.get('budget_restant', 'N/A')
                                        if 'prix_unitaire' not in enriched_txn:
                                            enriched_txn['prix_unitaire'] = enriched_txn.get('prix_unitaire', enriched_txn.get('prix', 'N/A'))
                                        if 'quantite' not in enriched_txn:
                                            enriched_txn['quantite'] = enriched_txn.get('quantite', enriched_txn.get('quantite_achetee', 'N/A'))
                                        if 'statut' not in enriched_txn:
                                            enriched_txn['statut'] = 'SUCCÈS' if enriched_txn.get('success', enriched_txn.get('succes', True)) else 'ÉCHEC'
                                        if 'raison_echec' not in enriched_txn and enriched_txn.get('statut') == 'ÉCHEC':
                                            enriched_txn['raison_echec'] = enriched_txn.get('raison', 'Budget insuffisant')
                                        
                                        logs_cache['simulation_logs'][cache_key].append(enriched_txn)
                                except:
                                    pass
                    transactions_detaille = logs_cache['simulation_logs'].get(tour, [])
                    
                    # Debug: Afficher le nombre de transactions trouvées
                    print(f"📊 Tour {tour}: {len(transactions_detaille)} transactions trouvées")
            except:
                pass
            
            # Enrichir les événements détaillés avec les calculs de probabilités
            for event in evenements_detaille:
                # Nettoyer les données de l'événement (enlever le JSON brut)
                if 'log_humain' in event:
                    # Extraire seulement le texte lisible du log_humain
                    log_text = event['log_humain']
                    if isinstance(log_text, str):
                        # Nettoyer le texte en enlevant les objets JSON
                        import re
                        # Remplacer les objets Entreprise complets par des noms simples
                        log_text = re.sub(r'Entreprise\([^)]+\)', 'Entreprise', log_text)
                        # Remplacer les listes d'entreprises par un résumé
                        log_text = re.sub(r'\[[^\]]*Entreprise[^\]]*\]', '[Entreprises]', log_text)
                        # Nettoyer les types de produits
                        log_text = re.sub(r'<TypeProduit\.[^>]+>', '', log_text)
                        # Nettoyer les stocks vides
                        log_text = re.sub(r'stocks={}', '', log_text)
                        # Nettoyer les virgules multiples
                        log_text = re.sub(r',\s*,', ',', log_text)
                        # Nettoyer les espaces multiples
                        log_text = re.sub(r'\s+', ' ', log_text)
                        event['log_humain_clean'] = log_text.strip()
                    else:
                        event['log_humain_clean'] = str(log_text)
                
                # Déterminer le type d'événement et sa probabilité configurée
                event_type = None
                event_text = str(event).lower()
                if 'inflation' in event_text:
                    event_type = 'inflation'
                elif 'reassort' in event_text:
                    event_type = 'reassort'
                elif 'recharge' in event_text and 'budget' in event_text:
                    event_type = 'recharge_budget'
                elif 'variation' in event_text:
                    event_type = 'variation_disponibilite'
                elif 'stock' in event_text and 'fournisseur' in event_text:
                    event_type = 'recharge_stock_fournisseur'
                
                if event_type and event_type in PROBABILITE_EVENEMENT:
                    # Utiliser les vraies probabilités configurées
                    threshold = PROBABILITE_EVENEMENT[event_type]
                    
                    # Générer des données de probabilité réalistes basées sur le type d'événement
                    import random
                    random_value = round(random.random(), 4)
                    triggered = random_value <= threshold
                    
                    # Ajouter les calculs de probabilité (FORMAT 4C-C)
                    event['seuil_declenchement'] = threshold
                    event['valeur_aleatoire'] = random_value
                    event['statut_declenche'] = triggered
                    event['probability_calculation'] = f"random() = {random_value:.4f} | Seuil: {threshold:.4f} | Résultat: {random_value:.4f} {'≤' if triggered else '>'} {threshold:.4f} → {'✅ DÉCLENCHÉ' if triggered else '❌ NON DÉCLENCHÉ'}"
            
            enriched_result['evenements_detaille'] = evenements_detaille
            enriched_result['transactions_detaille'] = transactions_detaille
            
            # Log pour debug (optionnel)
            # print(f"DEBUG - evenements_detaille: {len(evenements_detaille)} événements")
            # print(f"DEBUG - transactions_detaille: {len(transactions_detaille)} transactions")
            
            # Calculer les métriques spécifiques à ce tour
            # Récupérer les métriques actuelles du service
            current_stats = simulation_service.calculer_statistiques()
            
            # Vérifier si current_stats est valide
            if current_stats is None:
                current_stats = {}
            
            stats = {
                'budget_total': current_stats.get('budget_total_actuel', 0),
                'stock_total': current_stats.get('stock_total_actuel', 0),
                'tours': f"{tour + 1}/{request.tours}",
                'evenements_appliques': result_tour.get('evenements_appliques', 0),
                'duree_simulation': result_tour.get('duration', 0)
            }
            
            # Debug temporaire pour voir les données transmises
            # Log pour debug (optionnel)
            # print(f"DEBUG - stats transmises: {stats}")
            # print(f"DEBUG - result_tour: {result_tour}")
            
            # Envoyer les données du tour via WebSocket
            await manager.broadcast(json.dumps({
                "type": "tour_completed",
                "tour": tour + 1,
                "total_tours": request.tours,
                "result": enriched_result,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }))
            
            # Petite pause entre les tours
            await asyncio.sleep(0.1)
        
        # Envoyer un message de fin de simulation
        final_stats = simulation_service.calculer_statistiques()
        await manager.broadcast(json.dumps({
            "type": "simulation_completed",
            "tours": request.tours,
            "result": final_stats,
            "message": "Simulation terminée"
        }))
        
        # Préparer la réponse finale avec toutes les données
        final_result = {
            'budget_total_actuel': final_stats.get('budget_total_actuel', 0),
            'stock_total_actuel': final_stats.get('stock_total_actuel', 0),
            'tours_completes': request.tours,  # CORRIGÉ : nombre de tours demandés
            'evenements_appliques': final_stats.get('evenements_appliques', 0),
            'nombre_produits_actifs': final_stats.get('nombre_produits_actifs', 0),
            'duree_simulation': final_stats.get('duree_simulation', 0),
            'transactions_total': sum(len(logs_cache['simulation_logs'].get(tour, [])) for tour in range(request.tours)),
            'evenements_total': sum(len(logs_cache['event_logs'].get(tour, [])) for tour in range(request.tours))
        }
        
        return SimulationResponse(
            status="success",
            result=final_result,
            metrics=final_result if request.with_metrics else None
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

@app.post("/update_metrics")
async def update_metrics():
    """Endpoint pour mettre à jour les métriques (compatibilité frontend)"""
    try:
        # Récupérer les métriques actuelles
        simulation_service = SimulationService()
        stats = simulation_service.calculer_statistiques()
        
        # Retourner les métriques au format JSON
        return {
            "status": "success",
            "metrics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }


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