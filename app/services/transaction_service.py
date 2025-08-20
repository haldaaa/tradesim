#!/usr/bin/env python3
"""
TransactionService TradeSim - Gestion des transactions
====================================================

Ce service gère les transactions entre entreprises et fournisseurs.
Il implémente la logique d'achat et de vente des produits.

Refactorisation (02/08/2025) :
- Utilise les Repository pour l'accès aux données
- Code modulaire et testable
- Interface commune pour CLI et API

Auteur: Assistant IA
Date: 2024-08-02
"""

import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from repositories import ProduitRepository, FournisseurRepository, EntrepriseRepository
from models import Produit, Fournisseur, Entreprise, TypeProduit, Transaction
from config.config import (
    QUANTITE_ACHAT_MIN, QUANTITE_ACHAT_MAX,
    QUANTITE_ACHAT_PRIX_ELEVE_MIN, QUANTITE_ACHAT_PRIX_ELEVE_MAX, SEUIL_PRIX_ELEVE
)


class TransactionService:
    """
    Service de gestion des transactions TradeSim.
    
    Responsabilités :
    - Gérer les achats d'entreprises
    - Calculer les prix fournisseurs
    - Mettre à jour les stocks
    - Gérer les budgets
    - Fournir des statistiques de transactions
    """
    
    def __init__(self):
        """Initialise le service de transactions"""
        self.produit_repo = ProduitRepository()
        self.fournisseur_repo = FournisseurRepository()
        self.entreprise_repo = EntrepriseRepository()
        
        # Cache des prix fournisseurs
        self.prix_fournisseurs = {}
        
        # Historique des transactions
        self.transactions = []
    
    def get_prix_produit_fournisseur(self, produit_id: int, fournisseur_id: int) -> Optional[float]:
        """
        Récupère le prix d'un produit chez un fournisseur.
        
        Args:
            produit_id: ID du produit
            fournisseur_id: ID du fournisseur
            
        Returns:
            Prix du produit chez le fournisseur, ou None si non disponible
        """
        from services.price_service import price_service
        return price_service.get_prix_produit_fournisseur(produit_id, fournisseur_id)
    
    def set_prix_produit_fournisseur(self, produit_id: int, fournisseur_id: int, prix: float):
        """
        Définit le prix d'un produit chez un fournisseur.
        
        Args:
            produit_id: ID du produit
            fournisseur_id: ID du fournisseur
            prix: Prix du produit
        """
        from services.price_service import price_service
        price_service.set_prix_produit_fournisseur(produit_id, fournisseur_id, prix)
    
    def calculer_prix_fournisseur(self, produit: Produit, fournisseur: Fournisseur, stock: int) -> float:
        """
        Calcule le prix d'un produit chez un fournisseur.
        
        Args:
            produit: Produit à acheter
            fournisseur: Fournisseur
            stock: Stock disponible
            
        Returns:
            Prix calculé
        """
        prix_base = produit.prix
        
        # Facteurs de calcul du prix
        facteur_stock = 100 / (stock + 1)  # Plus le stock est bas, plus c'est cher
        facteur_fournisseur = random.uniform(0.9, 1.2)  # Variation par fournisseur
        
        prix_final = prix_base * facteur_fournisseur * facteur_stock
        return round(prix_final, 2)
    
    def trouver_fournisseurs_produit(self, produit_id: int) -> List[Tuple[Fournisseur, int, float]]:
        """
        Trouve tous les fournisseurs qui ont un produit en stock.
        
        Args:
            produit_id: ID du produit recherché
            
        Returns:
            Liste de tuples (fournisseur, stock, prix)
        """
        fournisseurs_disponibles = []
        
        for fournisseur in self.fournisseur_repo.get_all():
            if produit_id in fournisseur.stock_produit:
                stock = fournisseur.stock_produit[produit_id]
                if stock > 0:
                    prix = self.get_prix_produit_fournisseur(produit_id, fournisseur.id)
                    if prix is None:
                        # Calculer le prix si pas encore défini
                        produit = self.produit_repo.get_by_id(produit_id)
                        if produit:
                            prix = self.calculer_prix_fournisseur(produit, fournisseur, stock)
                            self.set_prix_produit_fournisseur(produit_id, fournisseur.id, prix)
                    
                    # Vérifier que le prix est valide
                    if prix is not None and prix > 0:
                        fournisseurs_disponibles.append((fournisseur, stock, prix))
        
        return fournisseurs_disponibles
    
    def choisir_fournisseur(self, fournisseurs_disponibles: List[Tuple[Fournisseur, int, float]], 
                           strategie: str = "moins_cher") -> Optional[Tuple[Fournisseur, int, float]]:
        """
        Choisit le meilleur fournisseur selon la stratégie.
        
        Args:
            fournisseurs_disponibles: Liste des fournisseurs disponibles
            strategie: Stratégie de sélection ("moins_cher", "meilleur_rapport", "aleatoire")
            
        Returns:
            Meilleur fournisseur ou None si aucun disponible
        """
        if not fournisseurs_disponibles:
            return None
        
        try:
            if strategie == "moins_cher":
                # Choisir le moins cher
                return min(fournisseurs_disponibles, key=lambda x: x[2])
            
            elif strategie == "meilleur_rapport":
                # Choisir le meilleur rapport qualité/prix (stock élevé, prix bas)
                def score_rapport(fournisseur_info):
                    fournisseur, stock, prix = fournisseur_info
                    return stock / prix if prix > 0 else 0
                
                return max(fournisseurs_disponibles, key=score_rapport)
            
            elif strategie == "aleatoire":
                # Choisir aléatoirement
                return random.choice(fournisseurs_disponibles)
            
            else:
                # Par défaut, le moins cher
                return min(fournisseurs_disponibles, key=lambda x: x[2])
        except Exception as e:
            print(f"⚠️ Erreur lors du choix du fournisseur: {e}")
            # En cas d'erreur, retourner le premier disponible
            return fournisseurs_disponibles[0] if fournisseurs_disponibles else None
    
    def effectuer_achat(self, entreprise: Entreprise, produit_id: int, quantite: int = 1) -> Optional[Transaction]:
        """
        Effectue un achat pour une entreprise.
        
        Args:
            entreprise: Entreprise qui achète
            produit_id: ID du produit à acheter
            quantite: Quantité à acheter
            
        Returns:
            Transaction effectuée ou None si échec
        """
        # Vérifier que le produit existe et est actif
        produit = self.produit_repo.get_by_id(produit_id)
        if not produit or not produit.actif:
            return None
        
        # Trouver les fournisseurs disponibles
        fournisseurs_disponibles = self.trouver_fournisseurs_produit(produit_id)
        if not fournisseurs_disponibles:
            return None
        
        # Choisir le fournisseur selon la stratégie de l'entreprise
        fournisseur_choisi = self.choisir_fournisseur(fournisseurs_disponibles, entreprise.strategie)
        if not fournisseur_choisi:
            return None
        
        fournisseur, stock_disponible, prix_unitaire = fournisseur_choisi
        
        # Vérifier le stock
        if stock_disponible < quantite:
            quantite = stock_disponible  # Acheter le maximum disponible
        
        # Calculer le coût total
        cout_total = prix_unitaire * quantite
        
        # Vérifier le budget de l'entreprise
        if entreprise.budget < cout_total:
            return None
        
        # Effectuer la transaction
        try:
            # Mettre à jour le budget de l'entreprise
            entreprise.budget -= cout_total
            self.entreprise_repo.update(entreprise)
            
            # Mettre à jour le stock du fournisseur
            fournisseur.stock_produit[produit_id] -= quantite
            self.fournisseur_repo.update(fournisseur)
            
            # Créer la transaction
            transaction = Transaction(
                timestamp=datetime.now(),
                entreprise_id=entreprise.id,
                fournisseur_id=fournisseur.id,
                produit_id=produit_id,
                produit_nom=produit.nom,
                quantite=quantite,
                prix_unitaire=prix_unitaire,
                total=cout_total,
                succes=True,
                raison_echec=None
            )
            
            self.transactions.append(transaction)
            
            return transaction
            
        except Exception as e:
            print(f"❌ Erreur lors de la transaction: {e}")
            return None
    
    def simuler_achat_entreprise(self, entreprise: Entreprise) -> List[Transaction]:
        """
        Simule les achats d'une entreprise selon ses préférences.
        
        Args:
            entreprise: Entreprise qui achète
            
        Returns:
            Liste des transactions effectuées
        """
        transactions_effectuees = []
        
        # Récupérer tous les produits actifs
        produits_actifs = [p for p in self.produit_repo.get_all() if p.actif]
        
        # Filtrer selon les types préférés de l'entreprise
        produits_preferes = []
        for produit in produits_actifs:
            if produit.type in entreprise.types_preferes:
                produits_preferes.append(produit)
        
        # Si pas de produits préférés, prendre tous les produits actifs
        if not produits_preferes:
            produits_preferes = produits_actifs
        
        # Essayer d'acheter quelques produits
        for produit in random.sample(produits_preferes, min(3, len(produits_preferes))):
            # Quantité adaptée au prix du produit
            if produit.prix > SEUIL_PRIX_ELEVE:
                # Produit cher : quantités réduites
                quantite = random.randint(QUANTITE_ACHAT_PRIX_ELEVE_MIN, QUANTITE_ACHAT_PRIX_ELEVE_MAX)
            else:
                # Produit normal : quantités standard
                quantite = random.randint(QUANTITE_ACHAT_MIN, QUANTITE_ACHAT_MAX)
            
            transaction = self.effectuer_achat(entreprise, produit.id, quantite)
            if transaction:
                transactions_effectuees.append(transaction)
        
        return transactions_effectuees
    
    def get_statistiques_transactions(self) -> Dict[str, Any]:
        """
        Récupère les statistiques des transactions.
        
        Returns:
            Statistiques des transactions
        """
        if not self.transactions:
            return {
                "nombre_transactions": 0,
                "montant_total": 0,
                "moyenne_prix": 0,
                "entreprises_actives": [],
                "fournisseurs_actifs": []
            }
        
        montant_total = sum(t.cout_total for t in self.transactions)
        moyenne_prix = montant_total / len(self.transactions) if self.transactions else 0
        
        entreprises_actives = list(set(t.entreprise_id for t in self.transactions))
        fournisseurs_actifs = list(set(t.fournisseur_id for t in self.transactions))
        
        return {
            "nombre_transactions": len(self.transactions),
            "montant_total": montant_total,
            "moyenne_prix": moyenne_prix,
            "entreprises_actives": entreprises_actives,
            "fournisseurs_actifs": fournisseurs_actifs,
            "dernieres_transactions": self.transactions[-10:] if self.transactions else []
        }
    
    def reset_transactions(self):
        """Remet l'historique des transactions à zéro"""
        self.transactions = []
        self.prix_fournisseurs = {}
        print("✅ Historique des transactions remis à zéro")
    
    def afficher_transactions_recentes(self, nombre: int = 10):
        """
        Affiche les transactions récentes.
        
        Args:
            nombre: Nombre de transactions à afficher
        """
        transactions_recentes = self.transactions[-nombre:] if self.transactions else []
        
        if not transactions_recentes:
            print("📊 Aucune transaction récente")
            return
        
        print(f"\n📊 DERNIÈRES TRANSACTIONS ({len(transactions_recentes)})")
        print("=" * 80)
        print("│ {:<5} {:<15} {:<20} {:<15} {:<8} {:<12} {:<12} │".format(
            "ID", "Entreprise", "Fournisseur", "Produit", "Qté", "Prix/Unit", "Total"
        ))
        print("├" + "─" * 80 + "┤")
        
        for transaction in transactions_recentes:
            entreprise = self.entreprise_repo.get_by_id(transaction.entreprise_id)
            fournisseur = self.fournisseur_repo.get_by_id(transaction.fournisseur_id)
            produit = self.produit_repo.get_by_id(transaction.produit_id)
            
            nom_entreprise = entreprise.nom if entreprise else "???"
            nom_fournisseur = fournisseur.nom_entreprise if fournisseur else "???"
            nom_produit = produit.nom if produit else "???"
            
            print("│ {:<5} {:<15} {:<20} {:<15} {:<8} {:<12} {:<12} │".format(
                transaction.id,
                nom_entreprise[:14],
                nom_fournisseur[:19],
                nom_produit[:14],
                transaction.quantite,
                f"{transaction.prix_unitaire:.2f}€",
                f"{transaction.cout_total:.2f}€"
            ))
        
        print("└" + "─" * 80 + "┘")


# Instance globale du service
transaction_service = TransactionService() 