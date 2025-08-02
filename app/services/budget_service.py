#!/usr/bin/env python3
"""
BudgetService TradeSim - Gestion des budgets
===========================================

Ce service gère les budgets des entreprises et les opérations
financières de la simulation.

Refactorisation (02/08/2025) :
- Utilise les Repository pour l'accès aux données
- Code modulaire et testable
- Interface commune pour CLI et API

Auteur: Assistant IA
Date: 2024-08-02
"""

import random
from typing import Dict, List, Any, Optional
from datetime import datetime

from repositories import EntrepriseRepository
from models import Entreprise


class BudgetService:
    """
    Service de gestion des budgets TradeSim.
    
    Responsabilités :
    - Gérer les budgets des entreprises
    - Effectuer des recharges de budget
    - Calculer des statistiques financières
    - Gérer les opérations financières
    """
    
    def __init__(self):
        """Initialise le service de gestion des budgets"""
        self.entreprise_repo = EntrepriseRepository()
        
        # Historique des opérations financières
        self.operations_financieres = []
    
    def get_budget_entreprise(self, entreprise_id: int) -> Optional[float]:
        """
        Récupère le budget d'une entreprise.
        
        Args:
            entreprise_id: ID de l'entreprise
            
        Returns:
            Budget de l'entreprise ou None si non trouvée
        """
        entreprise = self.entreprise_repo.get_by_id(entreprise_id)
        return entreprise.budget if entreprise else None
    
    def set_budget_entreprise(self, entreprise_id: int, nouveau_budget: float) -> bool:
        """
        Définit le budget d'une entreprise.
        
        Args:
            entreprise_id: ID de l'entreprise
            nouveau_budget: Nouveau budget
            
        Returns:
            True si la mise à jour a réussi
        """
        try:
            entreprise = self.entreprise_repo.get_by_id(entreprise_id)
            if not entreprise:
                return False
            
            ancien_budget = entreprise.budget
            entreprise.budget = nouveau_budget
            self.entreprise_repo.update(entreprise)
            
            # Enregistrer l'opération
            self._enregistrer_operation(entreprise_id, "modification", ancien_budget, nouveau_budget)
            
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du budget: {e}")
            return False
    
    def ajouter_budget(self, entreprise_id: int, montant: float) -> bool:
        """
        Ajoute un montant au budget d'une entreprise.
        
        Args:
            entreprise_id: ID de l'entreprise
            montant: Montant à ajouter
            
        Returns:
            True si l'opération a réussi
        """
        try:
            entreprise = self.entreprise_repo.get_by_id(entreprise_id)
            if not entreprise:
                return False
            
            ancien_budget = entreprise.budget
            nouveau_budget = ancien_budget + montant
            entreprise.budget = nouveau_budget
            self.entreprise_repo.update(entreprise)
            
            # Enregistrer l'opération
            self._enregistrer_operation(entreprise_id, "ajout", ancien_budget, nouveau_budget)
            
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout de budget: {e}")
            return False
    
    def retirer_budget(self, entreprise_id: int, montant: float) -> bool:
        """
        Retire un montant du budget d'une entreprise.
        
        Args:
            entreprise_id: ID de l'entreprise
            montant: Montant à retirer
            
        Returns:
            True si l'opération a réussi
        """
        try:
            entreprise = self.entreprise_repo.get_by_id(entreprise_id)
            if not entreprise:
                return False
            
            if entreprise.budget < montant:
                return False  # Budget insuffisant
            
            ancien_budget = entreprise.budget
            nouveau_budget = ancien_budget - montant
            entreprise.budget = nouveau_budget
            self.entreprise_repo.update(entreprise)
            
            # Enregistrer l'opération
            self._enregistrer_operation(entreprise_id, "retrait", ancien_budget, nouveau_budget)
            
            return True
        except Exception as e:
            print(f"❌ Erreur lors du retrait de budget: {e}")
            return False
    
    def recharge_budget_aleatoire(self, entreprise_id: int, min_montant: float = 200, max_montant: float = 600) -> bool:
        """
        Effectue une recharge aléatoire du budget d'une entreprise.
        
        Args:
            entreprise_id: ID de l'entreprise
            min_montant: Montant minimum de recharge
            max_montant: Montant maximum de recharge
            
        Returns:
            True si la recharge a réussi
        """
        montant = random.randint(int(min_montant), int(max_montant))
        return self.ajouter_budget(entreprise_id, montant)
    
    def recharge_budget_toutes_entreprises(self, min_montant: float = 200, max_montant: float = 600) -> List[bool]:
        """
        Effectue une recharge aléatoire pour toutes les entreprises.
        
        Args:
            min_montant: Montant minimum de recharge
            max_montant: Montant maximum de recharge
            
        Returns:
            Liste des résultats de recharge pour chaque entreprise
        """
        resultats = []
        entreprises = self.entreprise_repo.get_all()
        
        for entreprise in entreprises:
            resultat = self.recharge_budget_aleatoire(entreprise.id, min_montant, max_montant)
            resultats.append(resultat)
        
        return resultats
    
    def get_statistiques_budgets(self) -> Dict[str, Any]:
        """
        Récupère les statistiques des budgets.
        
        Returns:
            Statistiques des budgets
        """
        entreprises = self.entreprise_repo.get_all()
        
        if not entreprises:
            return {
                "nombre_entreprises": 0,
                "budget_total": 0,
                "budget_moyen": 0,
                "budget_min": 0,
                "budget_max": 0,
                "entreprises_solvables": 0
            }
        
        budgets = [e.budget for e in entreprises]
        budgets_initiaux = [e.budget_initial for e in entreprises]
        
        return {
            "nombre_entreprises": len(entreprises),
            "budget_total": sum(budgets),
            "budget_moyen": sum(budgets) / len(budgets),
            "budget_min": min(budgets),
            "budget_max": max(budgets),
            "budget_total_initial": sum(budgets_initiaux),
            "budget_moyen_initial": sum(budgets_initiaux) / len(budgets_initiaux),
            "entreprises_solvables": len([b for b in budgets if b > 0]),
            "evolution_budget": sum(budgets) - sum(budgets_initiaux)
        }
    
    def get_entreprises_en_difficulte(self, seuil: float = 100) -> List[Entreprise]:
        """
        Récupère les entreprises avec un budget faible.
        
        Args:
            seuil: Seuil de budget pour considérer une entreprise en difficulté
            
        Returns:
            Liste des entreprises en difficulté
        """
        entreprises = self.entreprise_repo.get_all()
        return [e for e in entreprises if e.budget <= seuil]
    
    def get_entreprises_prosperes(self, seuil: float = 2000) -> List[Entreprise]:
        """
        Récupère les entreprises avec un budget élevé.
        
        Args:
            seuil: Seuil de budget pour considérer une entreprise prospère
            
        Returns:
            Liste des entreprises prospères
        """
        entreprises = self.entreprise_repo.get_all()
        return [e for e in entreprises if e.budget >= seuil]
    
    def _enregistrer_operation(self, entreprise_id: int, type_operation: str, 
                              ancien_budget: float, nouveau_budget: float):
        """
        Enregistre une opération financière.
        
        Args:
            entreprise_id: ID de l'entreprise
            type_operation: Type d'opération
            ancien_budget: Budget avant l'opération
            nouveau_budget: Budget après l'opération
        """
        operation = {
            "id": len(self.operations_financieres) + 1,
            "entreprise_id": entreprise_id,
            "type": type_operation,
            "ancien_budget": ancien_budget,
            "nouveau_budget": nouveau_budget,
            "difference": nouveau_budget - ancien_budget,
            "date": datetime.now()
        }
        
        self.operations_financieres.append(operation)
    
    def reset_operations(self):
        """Remet l'historique des opérations à zéro"""
        self.operations_financieres = []
        print("✅ Historique des opérations financières remis à zéro")
    
    def afficher_statistiques_budgets(self):
        """Affiche les statistiques des budgets"""
        stats = self.get_statistiques_budgets()
        
        print("\n" + "=" * 60)
        print("💰 STATISTIQUES DES BUDGETS")
        print("=" * 60)
        
        print(f"🏢 Nombre d'entreprises: {stats['nombre_entreprises']}")
        print(f"💰 Budget total: {stats['budget_total']:.2f}€")
        print(f"📊 Budget moyen: {stats['budget_moyen']:.2f}€")
        print(f"📉 Budget minimum: {stats['budget_min']:.2f}€")
        print(f"📈 Budget maximum: {stats['budget_max']:.2f}€")
        print(f"✅ Entreprises solvables: {stats['entreprises_solvables']}")
        print(f"📊 Évolution: {stats['evolution_budget']:.2f}€")
        
        # Entreprises en difficulté
        entreprises_difficulte = self.get_entreprises_en_difficulte()
        if entreprises_difficulte:
            print(f"\n⚠️ Entreprises en difficulté ({len(entreprises_difficulte)}):")
            for entreprise in entreprises_difficulte:
                print(f"  • {entreprise.nom}: {entreprise.budget:.2f}€")
        
        # Entreprises prospères
        entreprises_prosperes = self.get_entreprises_prosperes()
        if entreprises_prosperes:
            print(f"\n💎 Entreprises prospères ({len(entreprises_prosperes)}):")
            for entreprise in entreprises_prosperes:
                print(f"  • {entreprise.nom}: {entreprise.budget:.2f}€")
        
        print("\n" + "=" * 60)
    
    def afficher_operations_recentes(self, nombre: int = 10):
        """
        Affiche les opérations financières récentes.
        
        Args:
            nombre: Nombre d'opérations à afficher
        """
        operations_recentes = self.operations_financieres[-nombre:] if self.operations_financieres else []
        
        if not operations_recentes:
            print("💰 Aucune opération financière récente")
            return
        
        print(f"\n💰 DERNIÈRES OPÉRATIONS FINANCIÈRES ({len(operations_recentes)})")
        print("=" * 80)
        print("│ {:<5} {:<15} {:<15} {:<12} {:<12} {:<12} │".format(
            "ID", "Entreprise", "Type", "Ancien", "Nouveau", "Différence"
        ))
        print("├" + "─" * 80 + "┤")
        
        for operation in operations_recentes:
            entreprise = self.entreprise_repo.get_by_id(operation["entreprise_id"])
            nom_entreprise = entreprise.nom if entreprise else "???"
            
            print("│ {:<5} {:<15} {:<15} {:<12} {:<12} {:<12} │".format(
                operation["id"],
                nom_entreprise[:14],
                operation["type"][:14],
                f"{operation['ancien_budget']:.2f}€",
                f"{operation['nouveau_budget']:.2f}€",
                f"{operation['difference']:.2f}€"
            ))
        
        print("└" + "─" * 80 + "┘")


# Instance globale du service
budget_service = BudgetService() 