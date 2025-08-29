#!/usr/bin/env python3
"""
Service de simulation principal pour TradeSim
============================================

ARCHITECTURE :
- Service central orchestrant la simulation complète
- Gestion des transactions entre entreprises et fournisseurs
- Application d'événements (inflation, recharge budget, etc.)
- Collecte de métriques et monitoring Prometheus
- Cache thread-safe pour les repositories mock
- Système d'IDs uniques avec traçabilité complète

FONCTIONNEMENT :
1. Initialisation avec données (entreprises, fournisseurs, produits)
2. Chargement automatique depuis repositories si données non fournies
3. Simulation par tours avec transactions et événements
4. Collecte de métriques en temps réel
5. Logging structuré pour traçabilité
6. Cache optimisé avec invalidation thread-safe

UTILISATION :
- Création : SimulationService(entreprises, fournisseurs, produits, verbose=False)
- Tour : service.simulation_tour(verbose=True)
- Statistiques : service.calculer_statistiques()
- Reset : service.reset_simulation()
- Simulation complète : service.run_simulation_tours(n_tours, verbose=True)

CORRECTIONS RÉCENTES (11/08/2025) :
- Cache thread-safe avec verrous
- Logging structuré complet
- Validation des configurations
- Tests de performance complets

AUTEUR : Assistant IA
DERNIÈRE MISE À JOUR : 11/08/2025
"""

import json
import time
import random
import logging
import threading
import requests
from datetime import datetime, timezone
from collections import defaultdict
from functools import lru_cache
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

from config.config import (
    # Configuration existante
    FICHIER_LOG, FICHIER_LOG_HUMAIN, EVENT_LOG_JSON, EVENT_LOG_HUMAIN,
    TICK_INTERVAL_EVENT, PROBABILITE_EVENEMENT,
    
    # Configuration des IDs uniques
    ID_FORMAT, ID_SESSION_FORMAT, MAX_COUNTER, VALID_ACTION_TYPES,
    
    # Configuration des optimisations
    BATCH_LOG_SIZE, CACHE_MAX_SIZE, COMPRESSION_DAYS, INDEX_ENABLED,
    VALIDATION_ENABLED, REALTIME_MONITORING, PERFORMANCE_THRESHOLD,
    
    # Seuils d'alerte temps réel
    ALERT_BUDGET_CRITIQUE, ALERT_STOCK_CRITIQUE, ALERT_ERROR_RATE,
    
    # Configuration des métriques
    METRICS_COLLECTION_INTERVAL, METRICS_RETENTION_DAYS, METRICS_ENABLED,
    
    # Configuration de simulation pour métriques
    PROBABILITE_SELECTION_ENTREPRISE, DUREE_PAUSE_ENTRE_TOURS,
    
    # Configuration des quantités
    QUANTITE_ACHAT_MIN, QUANTITE_ACHAT_MAX,
    
    # Configuration des métriques historiques de stock
    STOCK_HISTORY_PERFORMANCE_MONITORING
)

from models.models import Entreprise, Fournisseur, Produit, TypeProduit
from events.inflation import appliquer_inflation
from events.recharge_budget import appliquer_recharge_budget
from events.reassort import evenement_reassort
from events.variation_disponibilite import appliquer_variation_disponibilite
from events.recharge_stock_fournisseur import appliquer_recharge_stock_fournisseur

# Import du service de prix (CORRECTION BUG)
try:
    from services.price_service import price_service
    PRICE_SERVICE_AVAILABLE = True
except ImportError:
    PRICE_SERVICE_AVAILABLE = False
    print("⚠️ Service de prix non disponible")

# Import du service de latence
try:
    from services.latency_service import LatencyService
    LATENCY_SERVICE_AVAILABLE = True
except ImportError:
    LATENCY_SERVICE_AVAILABLE = False
    print("⚠️ Service de latence non disponible")

# Import conditionnel du monitoring
try:
    from monitoring.prometheus_exporter import PrometheusExporter
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("⚠️ Monitoring Prometheus non disponible")

# Import du service de métriques de budget
try:
    from services.budget_metrics_service import BudgetMetricsService
    BUDGET_METRICS_AVAILABLE = True
except ImportError:
    BUDGET_METRICS_AVAILABLE = False
    print("⚠️ Service de métriques de budget non disponible")

# Import du service de métriques d'entreprises
try:
    from services.enterprise_metrics_service import EnterpriseMetricsService
    ENTERPRISE_METRICS_AVAILABLE = True
except ImportError:
    ENTERPRISE_METRICS_AVAILABLE = False
    print("⚠️ Service de métriques d'entreprises non disponible")

# Import du service de métriques de produits
try:
    from services.product_metrics_service import ProductMetricsService
    PRODUCT_METRICS_AVAILABLE = True
except ImportError:
    PRODUCT_METRICS_AVAILABLE = False
    print("⚠️ Service de métriques de produits non disponible")

# Import du service de métriques de fournisseurs
try:
    from services.supplier_metrics_service import SupplierMetricsService
    SUPPLIER_METRICS_AVAILABLE = True
except ImportError:
    SUPPLIER_METRICS_AVAILABLE = False
    print("⚠️ Service de métriques de fournisseurs non disponible")

# Import du service de métriques de transactions
try:
    from services.transaction_metrics_service import TransactionMetricsService
    TRANSACTION_METRICS_AVAILABLE = True
except ImportError:
    TRANSACTION_METRICS_AVAILABLE = False
    print("⚠️ Service de métriques de transactions non disponible")

# Import du service de métriques d'événements
try:
    from services.event_metrics_service import EventMetricsService
    EVENT_METRICS_AVAILABLE = True
except ImportError:
    EVENT_METRICS_AVAILABLE = False
    print("⚠️ Service de métriques d'événements non disponible")

# Import du service de métriques de performance
try:
    from services.performance_metrics_service import PerformanceMetricsService
    PERFORMANCE_METRICS_AVAILABLE = True
except ImportError:
    PERFORMANCE_METRICS_AVAILABLE = False
    print("⚠️ Service de métriques de performance non disponible")

# Import du service de métriques individuelles
try:
    from services.individual_metrics_service import IndividualMetricsService
    INDIVIDUAL_METRICS_AVAILABLE = True
except ImportError:
    INDIVIDUAL_METRICS_AVAILABLE = False
    print("⚠️ Service de métriques individuelles non disponible")

class IDGenerator:
    """Générateur d'IDs uniques avec validation et configuration centralisée"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime(ID_SESSION_FORMAT)
        self.counters = defaultdict(int)
        self.log_buffer = []  # Buffer pour écriture en batch
        self.index = {} if INDEX_ENABLED else None  # Index pour recherche rapide

    def get_id(self, action_type: str) -> str:
        """Génère un ID unique avec validation"""
        if VALIDATION_ENABLED:
            if not action_type or action_type not in VALID_ACTION_TYPES:
                raise ValueError(f"Type d'action invalide: '{action_type}'. Types valides: {VALID_ACTION_TYPES}")
            
            if self.counters[action_type] > MAX_COUNTER:
                raise ValueError(f"Compteur dépassé pour {action_type}: {self.counters[action_type]}")
        
        self.counters[action_type] += 1
        action_id = f"{self.session_id}_{action_type}_{self.counters[action_type]:03d}"
        
        # Index pour recherche rapide
        if INDEX_ENABLED and self.index is not None:
            if self.session_id not in self.index:
                self.index[self.session_id] = []
            self.index[self.session_id].append(action_id)
        
        return action_id

    def get_session_id(self) -> str:
        return self.session_id

    def add_to_buffer(self, log_entry: Dict[str, Any]) -> None:
        """Ajoute un log au buffer pour écriture en batch"""
        self.log_buffer.append(log_entry)
        if len(self.log_buffer) >= BATCH_LOG_SIZE:
            self.flush_buffer()

    def flush_buffer(self) -> None:
        """Écrit le buffer en batch"""
        if not self.log_buffer:
            return
        
        # Écriture en batch pour performance
        with open(FICHIER_LOG, "a", encoding="utf-8") as f:
            for log in self.log_buffer:
                f.write(json.dumps(log) + "\n")
        
        self.log_buffer.clear()

    def search_by_session(self, session_id: str) -> List[str]:
        """Recherche rapide par session_id"""
        if not INDEX_ENABLED or self.index is None:
            return []
        return self.index.get(session_id, [])

class SimulationService:
    """Service de simulation principal avec optimisations et monitoring"""
    
    def __init__(self, entreprises: List[Entreprise] = None, fournisseurs: List[Fournisseur] = None, 
                 produits: List[Produit] = None, verbose: bool = False):
        # Charger les données depuis les repositories si non fournies
        if entreprises is None:
            try:
                from repositories import EntrepriseRepository
                repo = EntrepriseRepository()
                self.entreprises = repo.get_all()
                logger.info(f"Chargement réussi: {len(self.entreprises)} entreprises")
            except Exception as e:
                self.entreprises = []
                logger.error(f"Impossible de charger les entreprises: {e}")
                if verbose:
                    print(f"⚠️ Impossible de charger les entreprises: {e}")
        else:
            self.entreprises = entreprises
            logger.info(f"Entreprises fournies: {len(self.entreprises)}")
            
        if fournisseurs is None:
            try:
                from repositories import FournisseurRepository
                repo = FournisseurRepository()
                self.fournisseurs = repo.get_all()
                logger.info(f"Chargement réussi: {len(self.fournisseurs)} fournisseurs")
            except Exception as e:
                self.fournisseurs = []
                logger.error(f"Impossible de charger les fournisseurs: {e}")
                if verbose:
                    print(f"⚠️ Impossible de charger les fournisseurs: {e}")
        else:
            self.fournisseurs = fournisseurs
            logger.info(f"Fournisseurs fournis: {len(self.fournisseurs)}")
            
        if produits is None:
            try:
                from repositories import ProduitRepository
                repo = ProduitRepository()
                self.produits = repo.get_all()
                logger.info(f"Chargement réussi: {len(self.produits)} produits")
            except Exception as e:
                self.produits = []
                logger.error(f"Impossible de charger les produits: {e}")
                if verbose:
                    print(f"⚠️ Impossible de charger les produits: {e}")
        else:
            self.produits = produits
            logger.info(f"Produits fournis: {len(self.produits)}")
        self.verbose = verbose
        
        # Initialiser les repositories mock thread-safe pour compatibilité tests
        self._entreprise_repo = self._create_mock_repo(self.entreprises)
        self._produit_repo = self._create_mock_repo(self.produits)
        self._fournisseur_repo = self._create_mock_repo(self.fournisseurs)
        
        # État de simulation
        self.tick_actuel = 0
        self.tours_completes = 0
        self.evenements_appliques = 0
        self.debut_simulation = time.time()
        
        # Système d'IDs
        self.id_generator = IDGenerator()
        
        # Cache pour optimiser les calculs coûteux
        self._cache_stats = {}
        
        # Monitoring temps réel
        self.error_count = 0
        self.total_actions = 0
        
        # Service de latence
        self.latency_service = None
        if LATENCY_SERVICE_AVAILABLE:
            try:
                self.latency_service = LatencyService()
                print("⚡ Service de latence activé")
            except Exception as e:
                self._log_error("latency_service_init", str(e))
        
        # Prometheus exporter
        self.prometheus_exporter = None
        self.exporter = None  # Alias pour compatibilité tests
        if MONITORING_AVAILABLE:
            try:
                # Utiliser l'exporter permanent via HTTP
                import requests
                self.prometheus_exporter = {
                    'update_tradesim_metrics': lambda data: requests.post('http://localhost:8000/update_metrics', json=data, timeout=1)
                }
                self.exporter = self.prometheus_exporter  # Alias
                print("📊 Monitoring Prometheus connecté à l'exporter permanent")
            except Exception as e:
                self._log_error("prometheus_init", str(e))
        
        # Service de métriques de budget
        self.budget_metrics_service = None
        if BUDGET_METRICS_AVAILABLE:
            try:
                self.budget_metrics_service = BudgetMetricsService()
                print("💰 Service de métriques de budget activé")
            except Exception as e:
                self._log_error("budget_metrics_init", str(e))
        
        # Service de métriques d'entreprises
        self.enterprise_metrics_service = None
        if ENTERPRISE_METRICS_AVAILABLE:
            try:
                self.enterprise_metrics_service = EnterpriseMetricsService()
                print("🏢 Service de métriques d'entreprises activé")
            except Exception as e:
                self._log_error("enterprise_metrics_init", str(e))

        # Service de métriques de fournisseurs
        self.supplier_metrics_service = None
        if SUPPLIER_METRICS_AVAILABLE:
            try:
                self.supplier_metrics_service = SupplierMetricsService()
                print("🏭 Service de métriques de fournisseurs activé")
            except Exception as e:
                self._log_error("supplier_metrics_init", str(e))

        # Service de métriques de transactions
        self.transaction_metrics_service = None
        if TRANSACTION_METRICS_AVAILABLE:
            try:
                self.transaction_metrics_service = TransactionMetricsService()
                print("💳 Service de métriques de transactions activé")
            except Exception as e:
                self._log_error("transaction_metrics_init", str(e))

        # Service de métriques d'événements
        self.event_metrics_service = None
        if EVENT_METRICS_AVAILABLE:
            try:
                self.event_metrics_service = EventMetricsService()
                print("🎯 Service de métriques d'événements activé")
            except Exception as e:
                self._log_error("event_metrics_init", str(e))

        # Service de métriques de performance
        self.performance_metrics_service = None
        if PERFORMANCE_METRICS_AVAILABLE:
            try:
                self.performance_metrics_service = PerformanceMetricsService()
                print("⚡ Service de métriques de performance activé")
            except Exception as e:
                self._log_error("performance_metrics_init", str(e))
        
        # Service de métriques de produits
        self.product_metrics_service = None
        if PRODUCT_METRICS_AVAILABLE:
            try:
                self.product_metrics_service = ProductMetricsService()
                print("📦 Service de métriques de produits activé")
            except Exception as e:
                self._log_error("product_metrics_init", str(e))

        # Service de métriques individuelles
        self.individual_metrics_service = None
        if INDIVIDUAL_METRICS_AVAILABLE:
            try:
                self.individual_metrics_service = IndividualMetricsService()
                print("🏷️ Service de métriques individuelles avec labels activé")
            except Exception as e:
                self._log_error("individual_metrics_init", str(e))

    def _validate_data(self, data: Dict[str, Any], context: str) -> bool:
        """Validation des données métier"""
        if not VALIDATION_ENABLED:
            return True
            
        try:
            # Validation des prix
            if 'prix' in data and data['prix'] < 0:
                raise ValueError(f"Prix négatif dans {context}: {data['prix']}")
            
            # Validation des quantités
            if 'quantite' in data and data['quantite'] <= 0:
                raise ValueError(f"Quantité invalide dans {context}: {data['quantite']}")
            
            # Validation des budgets
            if 'budget' in data and data['budget'] < 0:
                raise ValueError(f"Budget négatif dans {context}: {data['budget']}")
            
            return True
        except Exception as e:
            self._log_error("validation", str(e))
            return False

    def _log_error(self, error_type: str, message: str) -> None:
        """Log d'erreur avec monitoring temps réel"""
        self.error_count += 1
        error_log = {
            "action_id": self.id_generator.get_id("ALERT"),
            "session_id": self.id_generator.get_session_id(),
            "tick": self.tick_actuel,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "timestamp_humain": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "type": "error",
            "error_type": error_type,
            "error_message": message,
            "context": "simulation_service"
        }
        
        # Log dans monitoring.log
        with open("logs/monitoring.log", "a", encoding="utf-8") as f:
            f.write(f"[ERROR] {error_type}: {message}\n")
        
        # Log dans metrics.jsonl
        with open("logs/metrics.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(error_log) + "\n")
        
        # Alerte temps réel si taux d'erreur critique
        if REALTIME_MONITORING and self.total_actions > 0:
            error_rate = self.error_count / self.total_actions
            if error_rate > ALERT_ERROR_RATE:
                self._send_alert("error_rate_critical", f"Taux d'erreur critique: {error_rate:.2%}")

    def _send_alert(self, alert_type: str, message: str) -> None:
        """Envoi d'alerte temps réel"""
        if not REALTIME_MONITORING:
            return
            
        alert_log = {
            "action_id": self.id_generator.get_id("ALERT"),
            "session_id": self.id_generator.get_session_id(),
            "tick": self.tick_actuel,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "timestamp_humain": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "type": "alert",
            "alert_type": alert_type,
            "message": message,
            "severity": "critical" if "critique" in message else "warning"
        }
        
        # Log de l'alerte
        with open("logs/monitoring.log", "a", encoding="utf-8") as f:
            f.write(f"[ALERT] {alert_type}: {message}\n")
        
        with open("logs/metrics.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(alert_log) + "\n")

    @lru_cache(maxsize=CACHE_MAX_SIZE)
    def calculer_statistiques(self) -> Dict[str, Any]:
        """Calcul des statistiques avec cache pour performance"""
        start_time = time.time()
        
        budget_total_actuel = sum(entreprise.budget for entreprise in self.entreprises)
        # Stock total : fournisseurs + entreprises
        stock_fournisseurs = sum(
            sum(fournisseur.stock_produit.values())
            for fournisseur in self.fournisseurs
        )
        
        stock_entreprises = sum(
            sum(getattr(entreprise, 'stocks', {}).values())
            for entreprise in self.entreprises
        )
        
        stock_total_actuel = stock_fournisseurs + stock_entreprises
        
        # Calcul détaillé du stock par produit
        stock_par_produit = {}
        for produit in self.produits:
            # Stock chez les fournisseurs
            stock_fournisseurs_produit = sum(
                fournisseur.stock_produit.get(produit.id, 0)
                for fournisseur in self.fournisseurs
            )
            
            # Stock chez les entreprises
            stock_entreprises_produit = sum(
                getattr(entreprise, 'stocks', {}).get(produit.nom, 0)
                for entreprise in self.entreprises
            )
            
            stock_par_produit[produit.nom] = {
                'fournisseurs': stock_fournisseurs_produit,
                'entreprises': stock_entreprises_produit,
                'total': stock_fournisseurs_produit + stock_entreprises_produit
            }
        
        # Validation des données calculées
        stats_data = {
            'budget_total': budget_total_actuel,
            'stock_total': stock_total_actuel,
            'stock_par_produit': stock_par_produit,
            'tours_completes': self.tours_completes,
            'evenements_appliques': self.evenements_appliques
        }
        
        if not self._validate_data(stats_data, "calculer_statistiques"):
            return {}
        
        # Alerte temps réel pour budget critique
        if REALTIME_MONITORING and budget_total_actuel < ALERT_BUDGET_CRITIQUE:
            self._send_alert("budget_critical", f"Budget total critique: {budget_total_actuel:.2f}€")
        
        # Alerte temps réel pour stock critique
        if REALTIME_MONITORING and stock_total_actuel < ALERT_STOCK_CRITIQUE:
            self._send_alert("stock_critical", f"Stock total critique: {stock_total_actuel}")
        
        # Test de performance
        duration = time.time() - start_time
        if duration > PERFORMANCE_THRESHOLD:
            self._send_alert("performance_slow", f"Calcul statistiques lent: {duration:.3f}s")
        
        # Fin du timer et enregistrement des métriques
        if self.latency_service:
            self.latency_service.end_timer("calcul_statistiques")
            self.latency_service.record_throughput("metriques")
        
        return {
            "budget_total_actuel": round(budget_total_actuel, 2),
            "stock_total_actuel": stock_total_actuel,
            "tours_completes": self.tours_completes,
            "evenements_appliques": self.evenements_appliques,
            "nombre_produits_actifs": len([p for p in self.produits if p.actif]),
            "duree_simulation": round(time.time() - self.debut_simulation, 4)
        }

    def acheter_produit_detaille(self, entreprise: Entreprise, produit: Produit, 
                                fournisseur: Fournisseur, strategie: str) -> bool:
        """Achat détaillé avec validation et monitoring"""
        self.total_actions += 1
        transaction_id = self.id_generator.get_id("TXN")
        
        # Démarrage du timer de latence
        if self.latency_service:
            self.latency_service.start_timer("achat_produit")
        
        try:
            # Validation des données d'entrée (CORRECTION BUG)
            prix = price_service.get_prix_produit_fournisseur(produit.id, fournisseur.id) if PRICE_SERVICE_AVAILABLE else 0
            stock_disponible = fournisseur.stock_produit.get(produit.id, 0)
            
            input_data = {
                'budget': entreprise.budget,
                'prix': prix or 0,
                'stock_disponible': stock_disponible
            }
            
            if not self._validate_data(input_data, "acheter_produit"):
                return False
            
            # Logique d'achat existante (CORRECTION BUG)
            stock_actuel = entreprise.stocks.get(produit.id, 0)
            prix = price_service.get_prix_produit_fournisseur(produit.id, fournisseur.id) if PRICE_SERVICE_AVAILABLE else 0
            stock_disponible = fournisseur.stock_produit.get(produit.id, 0)
            
            if stock_disponible <= 0 or prix <= 0:
                # Enregistrer la transaction échouée
                if self.transaction_metrics_service:
                    transaction_data = {
                        'entreprise': entreprise.nom,
                        'produit': produit.nom,
                        'fournisseur': fournisseur.nom_entreprise,
                        'quantite': 0,
                        'prix_unitaire': prix,
                        'montant_total': 0,
                        'strategie': strategie,
                        'raison_echec': 'stock_insuffisant' if stock_disponible <= 0 else 'prix_invalide'
                    }
                    self.transaction_metrics_service.enregistrer_transaction(transaction_data, reussie=False)
                
                if self.verbose:
                    print(f"❌ {entreprise.nom} ne peut pas acheter {produit.nom} chez {fournisseur.nom_entreprise}")
                    print(f"\t- Stock disponible: {stock_disponible} | Prix: {prix}€")
                return False
            
            # Calcul de la quantité d'achat (aléatoire entre min et max)
            quantite_max_budget = int(entreprise.budget / prix)
            quantite_max_stock = stock_disponible
            quantite_souhaitee = random.randint(QUANTITE_ACHAT_MIN, QUANTITE_ACHAT_MAX)
            quantite_achat = min(quantite_max_budget, quantite_max_stock, quantite_souhaitee)
            
            if quantite_achat <= 0:
                # Enregistrer la transaction échouée
                if self.transaction_metrics_service:
                    transaction_data = {
                        'entreprise': entreprise.nom,
                        'produit': produit.nom,
                        'fournisseur': fournisseur.nom_entreprise,
                        'quantite': 0,
                        'prix_unitaire': prix,
                        'montant_total': 0,
                        'strategie': strategie,
                        'raison_echec': 'budget_insuffisant'
                    }
                    self.transaction_metrics_service.enregistrer_transaction(transaction_data, reussie=False)
                
                if self.verbose:
                    print(f"❌ {entreprise.nom} ne peut pas acheter {produit.nom} chez {fournisseur.nom_entreprise}")
                    print(f"\t- Budget insuffisant ou stock épuisé")
                return False
            
            # Mise à jour des données (CORRECTION BUG)
            montant_total = quantite_achat * prix
            entreprise.budget -= montant_total
            
            # Enregistrer la transaction dans le service de budget
            if self.budget_metrics_service:
                self.budget_metrics_service.enregistrer_transaction(montant_total, "achat")
            
            # Enregistrer la transaction dans le service d'entreprises
            if self.enterprise_metrics_service:
                transaction_data = {
                    'produit': produit.nom,
                    'fournisseur': fournisseur.nom_entreprise,
                    'quantite': quantite_achat,
                    'prix_unitaire': prix,
                    'montant_total': montant_total,
                    'strategie': strategie
                }
                self.enterprise_metrics_service.enregistrer_transaction(entreprise.id, transaction_data)
            
            # Enregistrer la vente dans le service de fournisseurs
            if self.supplier_metrics_service:
                vente_data = {
                    'entreprise': entreprise.nom,
                    'produit': produit.nom,
                    'quantite': quantite_achat,
                    'prix_unitaire': prix,
                    'montant_total': montant_total,
                    'strategie': strategie
                }
                self.supplier_metrics_service.enregistrer_vente(fournisseur.id, vente_data)
            
            # Enregistrer l'achat dans le service de produits
            if self.product_metrics_service:
                achat_data = {
                    'entreprise': entreprise.nom,
                    'fournisseur': fournisseur.nom_entreprise,
                    'quantite': quantite_achat,
                    'prix_unitaire': prix,
                    'montant_total': montant_total,
                    'strategie': strategie
                }
                self.product_metrics_service.enregistrer_achat(produit.id, achat_data)
            
            # Enregistrer la transaction
            if self.transaction_metrics_service:
                transaction_data = {
                    'entreprise': entreprise.nom,
                    'produit': produit.nom,
                    'fournisseur': fournisseur.nom_entreprise,
                    'quantite': quantite_achat,
                    'prix_unitaire': prix,
                    'montant_total': montant_total,
                    'strategie': strategie
                }
                self.transaction_metrics_service.enregistrer_transaction(transaction_data, reussie=True)
            
            # Mise à jour des stocks (CORRECTION : utilisation de l'ID du produit)
            entreprise.stocks[produit.id] = entreprise.stocks.get(produit.id, 0) + quantite_achat
            fournisseur.stock_produit[produit.id] = stock_disponible - quantite_achat
            
            # Validation des données après modification (CORRECTION BUG)
            output_data = {
                'budget': entreprise.budget,
                'stock_entreprise': entreprise.stocks.get(produit.nom, 0) if hasattr(entreprise, 'stocks') else 0,
                'stock_fournisseur': fournisseur.stock_produit.get(produit.id, 0)
            }
            
            if not self._validate_data(output_data, "apres_achat"):
                return False
            
            # Affichage détaillé
            if self.verbose:
                print(f"🎯 {entreprise.nom} achète {quantite_achat} {produit.nom} chez {fournisseur.nom_entreprise} (stratégie: {strategie}) :")
                print(f"        - 💰 Prix unitaire: {prix:.2f}€ | Total: {montant_total:.2f}€ | Budget restant: {entreprise.budget:.2f}€")
                print("✅ Achat réussi !")
            
            # Log JSON avec ID
            log_json = {
                "action_id": transaction_id,
                "session_id": self.id_generator.get_session_id(),
                "tick": self.tick_actuel,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "timestamp_humain": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "type": "transaction",
                "entreprise": entreprise.nom,
                "produit": produit.nom,
                "fournisseur": fournisseur.nom_entreprise,
                "strategie": strategie,
                "quantite": quantite_achat,
                "prix_unitaire": prix,
                "montant_total": montant_total,
                "budget_restant": entreprise.budget,
                "success": True
            }
            
            # Ajout au buffer pour écriture en batch
            self.id_generator.add_to_buffer(log_json)
            
            # Log humain
            with open(FICHIER_LOG_HUMAIN, "a", encoding="utf-8") as f:
                f.write(f"[TXN] {transaction_id} - {entreprise.nom} achète {quantite_achat} {produit.nom} chez {fournisseur.nom_entreprise} pour {montant_total:.2f}€\n")
            
            # Fin du timer et enregistrement des métriques
            if self.latency_service:
                self.latency_service.end_timer("achat_produit")
                self.latency_service.record_throughput("transactions")
            
            return True
            
        except Exception as e:
            self._log_error("transaction", str(e))
            
            # Fin du timer même en cas d'erreur
            if self.latency_service:
                self.latency_service.end_timer("achat_produit")
            
            return False

    def simuler_transactions(self) -> int:
        """Simulation des transactions avec monitoring (CORRECTION BUG)"""
        transactions_effectuees = 0
        
        for entreprise in self.entreprises:
            for produit in [p for p in self.produits if p.actif]:
                # Trouver le fournisseur le moins cher (CORRECTION BUG)
                fournisseur_moins_cher = None
                prix_min = float('inf')
                
                for fournisseur in self.fournisseurs:
                    if produit.id in fournisseur.stock_produit and fournisseur.stock_produit[produit.id] > 0:
                        prix = price_service.get_prix_produit_fournisseur(produit.id, fournisseur.id) if PRICE_SERVICE_AVAILABLE else float('inf')
                        if prix and prix < prix_min:
                            prix_min = prix
                            fournisseur_moins_cher = fournisseur
                
                if fournisseur_moins_cher and self.acheter_produit_detaille(entreprise, produit, fournisseur_moins_cher, "moins_cher"):
                    transactions_effectuees += 1
        
        # Écriture du buffer en fin de simulation
        self.id_generator.flush_buffer()
        
        return transactions_effectuees

    def appliquer_evenements(self, tick: int) -> List[Dict[str, Any]]:
        """Application des événements avec validation"""
        evenements_appliques = []
        
        # Démarrage du timer de latence
        if self.latency_service:
            self.latency_service.start_timer("application_evenement")
        
        if tick % TICK_INTERVAL_EVENT == 0:
            # Inflation
            if self._valider_probabilite(PROBABILITE_EVENEMENT.get('inflation', 0)):
                logs = appliquer_inflation(tick)
                if logs:
                    evenements_appliques.extend(logs)
                    self.evenements_appliques += 1
            
            # Recharge budget
            if self._valider_probabilite(PROBABILITE_EVENEMENT.get('recharge_budget', 0)):
                logs = appliquer_recharge_budget(self.entreprises)
                if logs:
                    evenements_appliques.extend(logs)
                    self.evenements_appliques += 1
            
            # Reassort
            if self._valider_probabilite(PROBABILITE_EVENEMENT.get('reassort', 0)):
                logs = evenement_reassort(self.tick_actuel)
                if logs:
                    evenements_appliques.extend(logs)
                    self.evenements_appliques += 1
            
            # Variation disponibilité (CORRECTION BUG)
            if self._valider_probabilite(PROBABILITE_EVENEMENT.get('variation_disponibilite', 0)):
                logs = appliquer_variation_disponibilite(self.tick_actuel)
                if logs:
                    evenements_appliques.extend(logs)
                    self.evenements_appliques += 1
            
            # Recharge stock fournisseur
            if self._valider_probabilite(PROBABILITE_EVENEMENT.get('recharge_stock_fournisseur', 0)):
                logs = appliquer_recharge_stock_fournisseur(self.tick_actuel)
                if logs:
                    evenements_appliques.extend(logs)
                    self.evenements_appliques += 1
        
        # Enregistrement des événements dans le service de métriques
        if self.event_metrics_service and evenements_appliques:
            for evenement in evenements_appliques:
                self.event_metrics_service.enregistrer_evenement(evenement)
        
        # Fin du timer et enregistrement des métriques
        if self.latency_service:
            self.latency_service.end_timer("application_evenement")
            if evenements_appliques:
                self.latency_service.record_throughput("evenements", len(evenements_appliques))
        
        return evenements_appliques

    def _valider_probabilite(self, probabilite: float) -> bool:
        """Validation de probabilité avec gestion d'erreur"""
        try:
            import random
            return random.random() < probabilite
        except Exception as e:
            self._log_error("probabilite", str(e))
            return False

    def log_event(self, logs: List[Dict[str, Any]], event_type: str) -> None:
        """Log des événements avec IDs et validation"""
        if not logs:
            return
            
        event_id = self.id_generator.get_id("EVT")
        
        for log in logs:
            # Validation des données d'événement
            if not self._validate_data(log, f"event_{event_type}"):
                continue
                
            log_general = dict(log)
            log_general["action_id"] = event_id
            log_general["event_type"] = event_type
            log_general["session_id"] = self.id_generator.get_session_id()
            log_general["tick"] = self.tick_actuel
            log_general["timestamp"] = datetime.now(timezone.utc).isoformat()
            log_general["timestamp_humain"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            # Log JSON
            with open(FICHIER_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_general) + "\n")
            
            # Log humain
            with open(FICHIER_LOG_HUMAIN, "a", encoding="utf-8") as f:
                f.write(f"[EVT] {event_id} - {event_type}: {log.get('log_humain', str(log))}\n")
            
            # Log événement spécifique
            with open(EVENT_LOG_JSON, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_general) + "\n")
            
            with open(EVENT_LOG_HUMAIN, "a", encoding="utf-8") as f:
                f.write(f"[{event_type.upper()}] {log.get('log_humain', str(log))}\n")

    def collecter_metriques(self) -> None:
        """Collecte des métriques avec validation et monitoring"""
        metric_id = self.id_generator.get_id("METRIC")
        
        # Démarrage du timer de latence
        if self.latency_service:
            self.latency_service.start_timer("collecte_metriques")
        
        try:
            stats = self.calculer_statistiques()
            
            # Calcul des métriques de simulation
            simulation_metrics = self._calculer_metriques_simulation(stats)
            
            metrics_data = {
                "action_id": metric_id,
                "session_id": self.id_generator.get_session_id(),
                "tick": self.tick_actuel,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "timestamp_humain": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "type": "metrics",
                "budget_total": stats.get("budget_total_actuel", 0),
                "stock_total": stats.get("stock_total_actuel", 0),
                "stock_par_produit": stats.get("stock_par_produit", {}),
                "tours_completes": self.tours_completes,  # Utiliser directement l'attribut
                "evenements_appliques": stats.get("evenements_appliques", 0),
                "duree_simulation": stats.get("duree_simulation", 0),
                "error_count": self.error_count,
                "total_actions": self.total_actions,
                "error_rate": self.error_count / max(self.total_actions, 1),
                
                # ============================================================================
                # MÉTRIQUES DE SIMULATION (8 métriques)
                # ============================================================================
                "tick_actuel": self.tick_actuel,
                "probabilite_selection_entreprise": PROBABILITE_SELECTION_ENTREPRISE,
                "duree_pause_entre_tours": DUREE_PAUSE_ENTRE_TOURS,
                "tick_interval_event": TICK_INTERVAL_EVENT,
                "probabilite_evenement": PROBABILITE_EVENEMENT.get("inflation", 0.4),  # Probabilité moyenne
                "frequence_evenements": simulation_metrics["frequence_evenements"],
                "taux_succes_transactions": simulation_metrics["taux_succes_transactions"],
                "vitesse_simulation": simulation_metrics["vitesse_simulation"],
                "stabilite_prix": simulation_metrics["stabilite_prix"]
            }
            
            # Ajout des métriques de latence et throughput
            if self.latency_service:
                latency_metrics = self.latency_service.get_all_latency_metrics()
                throughput_metrics = self.latency_service.get_all_throughput_metrics()
                
                metrics_data["latency"] = latency_metrics
                metrics_data["throughput"] = throughput_metrics
            
            # Ajout des métriques de budget
            if self.budget_metrics_service:
                budget_metrics = self.budget_metrics_service.calculer_metriques_budget(self.entreprises)
                metrics_data.update(budget_metrics)
            else:
                pass
            
            # Ajout des métriques d'entreprises
            if self.enterprise_metrics_service:
                enterprise_metrics = self.enterprise_metrics_service.calculer_metriques_entreprises(self.entreprises)
                metrics_data.update(enterprise_metrics)
            else:
                pass
            
            # Ajout des métriques de fournisseurs
            if self.supplier_metrics_service:
                supplier_metrics = self.supplier_metrics_service.calculer_metriques_fournisseurs(self.fournisseurs, self.produits)
                metrics_data.update(supplier_metrics)
            
            # Ajout des métriques de transactions
            if self.transaction_metrics_service:
                transaction_metrics = self.transaction_metrics_service.calculer_metriques_transactions()
                metrics_data.update(transaction_metrics)
            
            # Ajout des métriques d'événements
            if self.event_metrics_service:
                event_metrics = self.event_metrics_service.calculer_metriques_evenements()
                metrics_data.update(event_metrics)
            
            # Ajout des métriques de performance
            if self.performance_metrics_service:
                performance_metrics = self.performance_metrics_service.calculer_metriques_performance()
                metrics_data.update(performance_metrics)
            
            # Ajout des métriques de produits
            if self.product_metrics_service:
                product_metrics = self.product_metrics_service.calculer_metriques_produits(self.produits, self.fournisseurs)
                metrics_data.update(product_metrics)
            
            # Ajout des métriques individuelles avec labels
            if self.individual_metrics_service:
                individual_metrics = self.individual_metrics_service.calculer_metriques_individuales(
                    self.entreprises, self.produits, self.fournisseurs
                )
                metrics_data.update(individual_metrics)
                
                # Ajout des métriques historiques de stock
                stocks_historiques = self.individual_metrics_service._calculer_stocks_historiques(
                    self.entreprises, self.fournisseurs, self.produits, self.tick_actuel
                )
                metrics_data['stocks_historiques'] = stocks_historiques
                
                # Compression automatique si activée
                self.individual_metrics_service._compresser_historique_stocks()
                
                # Ajout des statistiques de performance
                if STOCK_HISTORY_PERFORMANCE_MONITORING:
                    performance_stats = self.individual_metrics_service.get_performance_stats()
                    metrics_data['stock_history_performance'] = performance_stats

            
            # Validation des métriques (APRÈS avoir ajouté toutes les métriques)
            if not self._validate_data(metrics_data, "collecter_metriques"):
                return
            
            # Validation des métriques (APRÈS avoir ajouté toutes les métriques)
            if not self._validate_data(metrics_data, "collecter_metriques"):
                return
            
            # Log des métriques (APRÈS avoir ajouté toutes les métriques)
            with open("logs/metrics.jsonl", "a", encoding="utf-8") as f:
                json_line = json.dumps(metrics_data)
                f.write(json_line + "\n")
            
            # Prometheus exporter avec métriques directes
            if self.prometheus_exporter and isinstance(self.prometheus_exporter, dict):
                try:
                    # Mise à jour des métriques via HTTP
                    response = self.prometheus_exporter['update_tradesim_metrics'](metrics_data)
                    print(f"📊 Métriques mises à jour: budget={metrics_data.get('budget_total', 0)}, tours={metrics_data.get('tours_completes', 0)}, events={metrics_data.get('evenements_appliques', 0)}")
                    print(f"📊 Réponse HTTP: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
                except Exception as e:
                    print(f"⚠️ Erreur mise à jour métriques: {e}")
            else:
                print(f"⚠️ Pas d'exporter disponible: {type(self.prometheus_exporter)}")
            
            # Fin du timer et enregistrement des métriques
            if self.latency_service:
                self.latency_service.end_timer("collecte_metriques")
                self.latency_service.record_throughput("metriques")
                
        except Exception as e:
            self._log_error("prometheus_metrics", str(e))
            
            # Fin du timer même en cas d'erreur
            if self.latency_service:
                self.latency_service.end_timer("collecte_metriques")

    def simulation_tour(self, verbose: Optional[bool] = None) -> Dict[str, Any]:
        """Tour de simulation avec monitoring et validation
        
        ALGORITHME :
        1. Démarrage du timer de latence
        2. Simulation des transactions entre entreprises et fournisseurs
        3. Application des événements selon probabilité
        4. Collecte des métriques et statistiques
        5. Logging des résultats et affichage verbose
        
        Args:
            verbose: Afficher les détails du tour (None = utiliser self.verbose)
            
        Returns:
            Dict contenant : tour, tick, transactions_effectuees, evenements_appliques, 
                           statistiques, duration
            
        PERFORMANCE :
        - Cache LRU pour les statistiques
        - Monitoring des latences
        - Logging structuré
        
        UTILISATION :
        - Tour simple : service.simulation_tour()
        - Avec verbose : service.simulation_tour(verbose=True)
        - Override verbose : service.simulation_tour(verbose=False)
        """
        start_time = time.time()
        
        # Début de la mesure de performance
        if self.performance_metrics_service:
            self.performance_metrics_service.debut_mesure()
        
        try:
            # Simulation des transactions
            transactions_effectuees = self.simuler_transactions()
            
            # Application des événements
            evenements = self.appliquer_evenements(self.tick_actuel)
            
            # Log des événements
            if evenements:
                self.log_event(evenements, "evenements_tour")
            
            # Ajouter le tour au service de budget
            if self.budget_metrics_service:
                self.budget_metrics_service.ajouter_tour(self.entreprises, self.tick_actuel)
            
            # Ajouter le tour au service d'entreprises
            if self.enterprise_metrics_service:
                self.enterprise_metrics_service.ajouter_tour(self.entreprises, self.tick_actuel)
            
            # Ajouter le tour au service de fournisseurs
            if self.supplier_metrics_service:
                self.supplier_metrics_service.ajouter_tour(self.fournisseurs, self.produits, self.tick_actuel)
            
            # Ajouter le tour au service de produits
            if self.product_metrics_service:
                self.product_metrics_service.ajouter_tour(self.produits, self.fournisseurs, self.tick_actuel)
            
            # Ajouter le tour au service de transactions
            if self.transaction_metrics_service:
                self.transaction_metrics_service.ajouter_tour(self.tick_actuel)
            
            # Ajouter le tour au service d'événements
            if self.event_metrics_service:
                self.event_metrics_service.ajouter_tour(self.tick_actuel)
            
            # Finir la mesure de performance
            if self.performance_metrics_service:
                self.performance_metrics_service.fin_mesure(self.tick_actuel)
            
            # Collecte des métriques
            self.collecter_metriques()
            
            # Affichage verbose
            should_display_verbose = verbose if verbose is not None else self.verbose
            if should_display_verbose:
                print(f"\n🔄 Tour {self.tours_completes + 1} - Tick {self.tick_actuel}")
                print(f"📊 Transactions effectuées: {transactions_effectuees}")
                
                if evenements:
                    print(f"🎲 Événements appliqués ({len(evenements)}):")
                    for event in evenements:
                        if isinstance(event, dict):
                            log_humain = event.get('log_humain', str(event))
                            # Nettoyer le log_humain si il contient des données d'entreprise
                            if 'Entreprise(id=' in str(log_humain):
                                # Extraire juste la partie utile du message
                                if 'reçoit +' in str(log_humain):
                                    # Pour les recharges individuelles
                                    parts = str(log_humain).split(' - ')
                                    if len(parts) > 1:
                                        log_humain = parts[1]
                                elif 'RECHARGE -' in str(log_humain):
                                    # Pour les résumés de recharge
                                    parts = str(log_humain).split(' - ')
                                    if len(parts) > 1:
                                        log_humain = parts[1]
                            print(f"• [EVENT] {log_humain}")
                        else:
                            print(f"• [EVENT] {event}")
            
            # Mise à jour des compteurs
            self.tick_actuel += 1
            self.tours_completes += 1
            
            # Test de performance
            duration = time.time() - start_time
            if duration > PERFORMANCE_THRESHOLD:
                self._send_alert("tour_slow", f"Tour de simulation lent: {duration:.3f}s")
            
            return {
                "transactions_effectuees": transactions_effectuees,
                "evenements_appliques": len(evenements),
                "tick": self.tick_actuel,
                "tour": self.tours_completes,
                "duration": duration
            }
            
        except Exception as e:
            self._log_error("simulation_tour", str(e))
            return {"error": str(e)}

    def _calculer_metriques_simulation(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calcul des métriques de simulation basées sur les statistiques"""
        try:
            # Récupération des données de base
            tours_completes = stats.get("tours_completes", 0)
            evenements_appliques = stats.get("evenements_appliques", 0)
            duree_simulation = stats.get("duree_simulation", 0)
            transactions_reussies = stats.get("transactions_reussies", 0)
            transactions_total = stats.get("transactions_total", 0)
            
            # 1. Fréquence des événements (événements par tour)
            frequence_evenements = 0
            if tours_completes > 0:
                frequence_evenements = evenements_appliques / tours_completes
            
            # 2. Taux de succès des transactions (0-1)
            taux_succes_transactions = 0
            if transactions_total > 0:
                taux_succes_transactions = transactions_reussies / transactions_total
            
            # 3. Vitesse de simulation (tours par seconde)
            vitesse_simulation = 0
            if duree_simulation > 0:
                vitesse_simulation = tours_completes / duree_simulation
            
            # 4. Stabilité des prix (coefficient de variation)
            # Calcul basé sur la variation des prix des produits
            stabilite_prix = self._calculer_stabilite_prix()
            
            return {
                "frequence_evenements": round(frequence_evenements, 4),
                "taux_succes_transactions": round(taux_succes_transactions, 4),
                "vitesse_simulation": round(vitesse_simulation, 4),
                "stabilite_prix": round(stabilite_prix, 4)
            }
            
        except Exception as e:
            self._log_error("calcul_metriques_simulation", str(e))
            return {
                "frequence_evenements": 0,
                "taux_succes_transactions": 0,
                "vitesse_simulation": 0,
                "stabilite_prix": 0
            }
    
    def _calculer_stabilite_prix(self) -> float:
        """Calcule la stabilité des prix (coefficient de variation)"""
        try:
            if not hasattr(self, 'produits') or not self.produits:
                return 0.0
            
            # Récupération des prix actuels
            prix_actuels = []
            for produit in self.produits:
                if hasattr(produit, 'prix') and produit.prix > 0:
                    prix_actuels.append(produit.prix)
            
            if len(prix_actuels) < 2:
                return 0.0
            
            # Calcul du coefficient de variation (écart-type / moyenne)
            import statistics
            moyenne = statistics.mean(prix_actuels)
            ecart_type = statistics.stdev(prix_actuels)
            
            if moyenne == 0:
                return 0.0
            
            coefficient_variation = ecart_type / moyenne
            return coefficient_variation
            
        except Exception as e:
            self._log_error("calcul_stabilite_prix", str(e))
            return 0.0

    def reset_simulation(self) -> None:
        """Réinitialise la simulation avec les valeurs de config.py"""
        try:
            from config.config import (
                N_ENTREPRISES_PAR_TOUR, PROBABILITE_SELECTION_ENTREPRISE,
                DUREE_PAUSE_ENTRE_TOURS, QUANTITE_ACHAT_MIN, QUANTITE_ACHAT_MAX,
                RECHARGE_BUDGET_MIN, RECHARGE_BUDGET_MAX, REASSORT_QUANTITE_MIN,
                REASSORT_QUANTITE_MAX, INFLATION_POURCENTAGE_MIN, INFLATION_POURCENTAGE_MAX
            )
            
            # Réinitialiser les compteurs
            self.tick_actuel = 0
            self.tours_completes = 0
            self.evenements_appliques = 0
            self.debut_simulation = time.time()
            self.error_count = 0
            self.total_actions = 0
            self._cache_stats.clear()
            
            # 🔄 RÉINITIALISER LES BUDGETS DES ENTREPRISES
            for entreprise in self.entreprises:
                entreprise.budget = entreprise.budget_initial
            
            # Réinitialiser les paramètres de simulation avec config.py
            self.n_entreprises_par_tour = N_ENTREPRISES_PAR_TOUR
            self.probabilite_selection_entreprise = PROBABILITE_SELECTION_ENTREPRISE
            self.duree_pause_entre_tours = DUREE_PAUSE_ENTRE_TOURS
            
            # Réinitialiser les services de métriques
            if self.budget_metrics_service:
                self.budget_metrics_service.reset()
            if self.enterprise_metrics_service:
                self.enterprise_metrics_service.reset()
            if self.supplier_metrics_service:
                self.supplier_metrics_service.reset()
            if self.transaction_metrics_service:
                self.transaction_metrics_service.reset()
            if self.event_metrics_service:
                self.event_metrics_service.reset()
            if self.performance_metrics_service:
                self.performance_metrics_service.reset()
            if self.product_metrics_service:
                self.product_metrics_service.reset()
            
            if self.verbose:
                print("🔄 Simulation réinitialisée avec les valeurs de config.py")
                
        except Exception as e:
            self._log_error("reset_simulation", str(e))
    
    def run_simulation_tours(self, nombre_tours: int, verbose: bool = False) -> Dict[str, Any]:
        """Exécute une simulation pour un nombre de tours donné"""
        try:
            if verbose:
                print(f"🚀 Lancement de la simulation pour {nombre_tours} tours...")
            
            for tour in range(nombre_tours):
                resultat = self.simulation_tour()
                if "error" in resultat:
                    print(f"❌ Erreur tour {tour}: {resultat['error']}")
                    break
                
                if verbose and tour % 10 == 0:
                    print(f"📊 Tour {tour}/{nombre_tours} - Transactions: {resultat.get('transactions_effectuees', 0)}")
            
            if verbose:
                print("✅ Simulation terminée.")
            
            return self.calculer_statistiques()
            
        except Exception as e:
            self._log_error("run_simulation_tours", str(e))
            return {"error": str(e)}
    
    def run_simulation_infinite(self, verbose: bool = False) -> None:
        """Exécute une simulation infinie (pour CLI interactif)"""
        try:
            if verbose:
                print("🚀 Lancement de la simulation infinie...")
            
            # Simulation vraiment infinie
            tour = 0
            while True:
                resultat = self.simulation_tour()
                if "error" in resultat:
                    print(f"❌ Erreur tour {tour}: {resultat['error']}")
                    break
                
                if verbose and tour % 10 == 0:
                    print(f"📊 Tour {tour} - Transactions: {resultat.get('transactions_effectuees', 0)}")
                
                tour += 1
                time.sleep(0.1)  # Pause courte
                
        except Exception as e:
            self._log_error("run_simulation_infinite", str(e))
    
    def _create_mock_repo(self, data_list):
        """Crée un repository mock thread-safe avec cache
        
        ALGORITHME :
        1. Création d'une classe MockRepo encapsulant les données
        2. Initialisation du cache et du verrou thread-safe
        3. Méthode get_all() avec cache et invalidation automatique
        
        Args:
            data_list: Liste des données à encapsuler (entreprises, fournisseurs, produits)
            
        Returns:
            MockRepo: Repository mock avec accès thread-safe et cache optimisé
            
        PERFORMANCE :
        - Cache avec invalidation toutes les 1 seconde
        - Verrou thread-safe pour éviter les race conditions
        - Copie des données pour isolation
        
        UTILISATION :
        - Accès : repo.get_all() retourne une copie thread-safe
        - Cache : Automatique avec invalidation
        - Thread-safety : Garantie par verrou
        
        Note:
            Retourne des copies pour éviter les mutations concurrentes
            Cache avec invalidation pour optimiser les performances
        """
        class MockRepo:
            def __init__(self, data):
                self._data = data
                self._cache = None
                self._cache_timestamp = 0
                self._lock = threading.Lock()
            
            def get_all(self):
                current_time = time.time()
                with self._lock:
                    if self._cache is None or current_time - self._cache_timestamp > 1.0:
                        # Copie profonde pour éviter les mutations
                        import copy
                        self._cache = copy.deepcopy(self._data)
                        self._cache_timestamp = current_time
                    return self._cache
        return MockRepo(data_list)
    
    @property
    def entreprise_repo(self):
        """Propriété pour accéder aux entreprises (compatibilité tests)"""
        return self._entreprise_repo
    
    @property
    def produit_repo(self):
        """Propriété pour accéder aux produits (compatibilité tests)"""
        return self._produit_repo
    
    @property
    def fournisseur_repo(self):
        """Propriété pour accéder aux fournisseurs (compatibilité tests)"""
        return self._fournisseur_repo

# Instance globale du générateur d'IDs
id_generator = IDGenerator() 