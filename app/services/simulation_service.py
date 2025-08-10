#!/usr/bin/env python3
"""
Service de simulation principal avec monitoring Prometheus et optimisations
Système principal de production avec IDs uniques et traçabilité complète
"""

import json
import time
from datetime import datetime, timezone
from collections import defaultdict
from functools import lru_cache
from typing import List, Dict, Any, Optional

from config import (
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
    METRICS_COLLECTION_INTERVAL, METRICS_RETENTION_DAYS
)

from models.models import Entreprise, Fournisseur, Produit, TypeProduit
from events.inflation import appliquer_inflation
from events.recharge_budget import appliquer_recharge_budget
from events.reassort import evenement_reassort
from events.variation_disponibilite import appliquer_variation_disponibilite

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
    
    def __init__(self, entreprises: List[Entreprise], fournisseurs: List[Fournisseur], 
                 produits: List[Produit], verbose: bool = False):
        self.entreprises = entreprises
        self.fournisseurs = fournisseurs
        self.produits = produits
        self.verbose = verbose
        
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
        if MONITORING_AVAILABLE:
            try:
                self.prometheus_exporter = PrometheusExporter()
                print("📊 Monitoring Prometheus activé")
            except Exception as e:
                self._log_error("prometheus_init", str(e))

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
        stock_total_actuel = sum(
            sum(entreprise.stocks.get(produit.nom, 0) for produit in self.produits)
            for entreprise in self.entreprises
        )
        
        # Validation des données calculées
        stats_data = {
            'budget_total': budget_total_actuel,
            'stock_total': stock_total_actuel,
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
            # Validation des données d'entrée
            input_data = {
                'budget': entreprise.budget,
                'prix': fournisseur.prix_produits.get(produit.nom, 0),
                'stock_disponible': fournisseur.stocks.get(produit.nom, 0)
            }
            
            if not self._validate_data(input_data, "acheter_produit"):
                return False
            
            # Logique d'achat existante
            stock_actuel = entreprise.stocks.get(produit.nom, 0)
            prix = fournisseur.prix_produits.get(produit.nom, 0)
            stock_disponible = fournisseur.stocks.get(produit.nom, 0)
            
            if stock_disponible <= 0 or prix <= 0:
                if self.verbose:
                    print(f"❌ {entreprise.nom} ne peut pas acheter {produit.nom} chez {fournisseur.nom_entreprise}")
                    print(f"\t- Stock disponible: {stock_disponible} | Prix: {prix}€")
                return False
            
            # Calcul de la quantité d'achat
            quantite_max_budget = int(entreprise.budget / prix)
            quantite_max_stock = stock_disponible
            quantite_achat = min(quantite_max_budget, quantite_max_stock, 99)
            
            if quantite_achat <= 0:
                if self.verbose:
                    print(f"❌ {entreprise.nom} ne peut pas acheter {produit.nom} chez {fournisseur.nom_entreprise}")
                    print(f"\t- Budget insuffisant ou stock épuisé")
                return False
            
            # Mise à jour des données
            montant_total = quantite_achat * prix
            entreprise.budget -= montant_total
            entreprise.stocks[produit.nom] = stock_actuel + quantite_achat
            fournisseur.stocks[produit.nom] = stock_disponible - quantite_achat
            
            # Validation des données après modification
            output_data = {
                'budget': entreprise.budget,
                'stock_entreprise': entreprise.stocks[produit.nom],
                'stock_fournisseur': fournisseur.stocks[produit.nom]
            }
            
            if not self._validate_data(output_data, "apres_achat"):
                return False
            
            # Affichage détaillé
            if self.verbose:
                print(f"🎯 {entreprise.nom} achète {quantite_achat} {produit.nom} chez {fournisseur.nom_entreprise} (stratégie: {strategie}) :")
                print(f"\t- 💰 Prix unitaire: {prix:.2f}€ | Total: {montant_total:.2f}€ | Budget restant: {entreprise.budget:.2f}€")
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
        """Simulation des transactions avec monitoring"""
        transactions_effectuees = 0
        
        for entreprise in self.entreprises:
            for produit in self.produits:
                # Trouver le fournisseur le moins cher
                fournisseur_moins_cher = min(
                    self.fournisseurs,
                    key=lambda f: f.prix_produits.get(produit.nom, float('inf'))
                )
                
                if self.acheter_produit_detaille(entreprise, produit, fournisseur_moins_cher, "moins_cher"):
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
                logs = appliquer_inflation(self.fournisseurs)
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
            
            # Variation disponibilité
            if self._valider_probabilite(PROBABILITE_EVENEMENT.get('variation_disponibilite', 0)):
                logs = appliquer_variation_disponibilite(self.fournisseurs, self.produits)
                if logs:
                    evenements_appliques.extend(logs)
                    self.evenements_appliques += 1
        
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
            
            metrics_data = {
                "action_id": metric_id,
                "session_id": self.id_generator.get_session_id(),
                "tick": self.tick_actuel,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "timestamp_humain": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "type": "metrics",
                "budget_total": stats.get("budget_total_actuel", 0),
                "stock_total": stats.get("stock_total_actuel", 0),
                "tours_completes": stats.get("tours_completes", 0),
                "evenements_appliques": stats.get("evenements_appliques", 0),
                "duree_simulation": stats.get("duree_simulation", 0),
                "error_count": self.error_count,
                "total_actions": self.total_actions,
                "error_rate": self.error_count / max(self.total_actions, 1)
            }
            
            # Validation des métriques
            if not self._validate_data(metrics_data, "collecter_metriques"):
                return
            
            # Log des métriques
            with open("logs/metrics.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(metrics_data) + "\n")
            
            # Ajout des métriques de latence et throughput
            if self.latency_service:
                latency_metrics = self.latency_service.get_all_latency_metrics()
                throughput_metrics = self.latency_service.get_all_throughput_metrics()
                
                metrics_data["latency"] = latency_metrics
                metrics_data["throughput"] = throughput_metrics
            
            # Prometheus exporter avec métriques de latence
            if self.prometheus_exporter:
                # Métriques de base
                self.prometheus_exporter.update_metrics(
                    budget_total=stats.get("budget_total_actuel", 0),
                    stock_total=stats.get("stock_total_actuel", 0),
                    tours_completes=stats.get("tours_completes", 0),
                    evenements_appliques=stats.get("evenements_appliques", 0),
                    temps_simulation_tour_seconds=stats.get("duree_simulation", 0)
                )
                
                # Métriques de latence et throughput
                if self.latency_service:
                    self.prometheus_exporter.update_tradesim_metrics(metrics_data)
            
            # Fin du timer et enregistrement des métriques
            if self.latency_service:
                self.latency_service.end_timer("collecte_metriques")
                self.latency_service.record_throughput("metriques")
                
        except Exception as e:
            self._log_error("prometheus_metrics", str(e))
            
            # Fin du timer même en cas d'erreur
            if self.latency_service:
                self.latency_service.end_timer("collecte_metriques")

    def simulation_tour(self) -> Dict[str, Any]:
        """Tour de simulation avec monitoring et validation"""
        start_time = time.time()
        
        try:
            # Simulation des transactions
            transactions_effectuees = self.simuler_transactions()
            
            # Application des événements
            evenements = self.appliquer_evenements(self.tick_actuel)
            
            # Log des événements
            if evenements:
                self.log_event(evenements, "evenements_tour")
            
            # Collecte des métriques
            self.collecter_metriques()
            
            # Affichage verbose
            if self.verbose:
                print(f"\n🔄 Tour {self.tours_completes + 1} - Tick {self.tick_actuel}")
                print(f"📊 Transactions effectuées: {transactions_effectuees}")
                
                if evenements:
                    print(f"🎲 Événements appliqués ({len(evenements)}):")
                    for event in evenements:
                        if isinstance(event, dict):
                            log_humain = event.get('log_humain', str(event))
                            probabilite = event.get('probabilite', 'N/A')
                            print(f"• {log_humain} (probabilité: {probabilite})")
                        else:
                            print(f"• Événement: {event}")
            
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

# Instance globale du générateur d'IDs
id_generator = IDGenerator() 