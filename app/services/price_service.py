"""
Service centralisé pour la gestion des prix des produits.

Ce service centralise toute la logique de gestion des prix pour éviter la duplication
et rendre l'application plus modulaire et maintenable.

MODE CLI : Utilise les données en mémoire
MODE WEB : Utilisera les données de la base de données
"""

from typing import Optional, Dict, Tuple
from models.models import Produit, Fournisseur
from repositories import ProduitRepository, FournisseurRepository


class PriceService:
    """
    Service centralisé pour la gestion des prix des produits.
    
    Responsabilités :
    - Récupérer les prix des produits chez les fournisseurs
    - Définir les prix des produits chez les fournisseurs
    - Calculer les prix minimum/maximum
    - Gérer la logique de prix pour les achats
    """
    
    def __init__(self):
        """Initialise le service avec les repositories nécessaires."""
        self.produit_repo = ProduitRepository()
        self.fournisseur_repo = FournisseurRepository()
        
        # Cache des prix pour optimiser les performances
        self._prix_cache: Dict[Tuple[int, int], float] = {}
    
    def get_prix_produit_fournisseur(self, produit_id: int, fournisseur_id: int) -> Optional[float]:
        """
        Récupère le prix d'un produit chez un fournisseur spécifique.
        
        Args:
            produit_id: ID du produit
            fournisseur_id: ID du fournisseur
            
        Returns:
            Le prix du produit chez ce fournisseur, ou None si non défini
        """
        # Vérifier le cache d'abord
        cache_key = (produit_id, fournisseur_id)
        if cache_key in self._prix_cache:
            return self._prix_cache[cache_key]
        
        # Récupérer le fournisseur
        fournisseur = self.fournisseur_repo.get_by_id(fournisseur_id)
        if not fournisseur:
            return None
        
        # Récupérer le produit
        produit = self.produit_repo.get_by_id(produit_id)
        if not produit:
            return None
        
        # Vérifier si le fournisseur a ce produit en stock
        if produit_id not in fournisseur.stock_produit:
            return None
        
        # Récupérer le prix depuis le dictionnaire global (comme avant)
        from data import prix_par_fournisseur
        prix = prix_par_fournisseur.get((produit_id, fournisseur_id))
        
        # Mettre en cache
        self._prix_cache[cache_key] = prix
        
        return prix
    
    def set_prix_produit_fournisseur(self, produit_id: int, fournisseur_id: int, prix: float) -> bool:
        """
        Définit le prix d'un produit chez un fournisseur spécifique.
        
        Args:
            produit_id: ID du produit
            fournisseur_id: ID du fournisseur
            prix: Nouveau prix à définir
            
        Returns:
            True si le prix a été défini avec succès, False sinon
        """
        # Récupérer le fournisseur
        fournisseur = self.fournisseur_repo.get_by_id(fournisseur_id)
        if not fournisseur:
            return False
        
        # Récupérer le produit
        produit = self.produit_repo.get_by_id(produit_id)
        if not produit:
            return False
        
        # Vérifier que le fournisseur a ce produit en stock
        if produit_id not in fournisseur.stock_produit:
            return False
        
        # Définir le prix dans le dictionnaire global (comme avant)
        from data import prix_par_fournisseur
        prix_par_fournisseur[(produit_id, fournisseur_id)] = prix
        
        # Mettre à jour le cache
        cache_key = (produit_id, fournisseur_id)
        self._prix_cache[cache_key] = prix
        
        return True
    
    def get_prix_minimum(self, produit_id: int) -> Optional[float]:
        """
        Récupère le prix minimum d'un produit chez tous les fournisseurs.
        
        Args:
            produit_id: ID du produit
            
        Returns:
            Le prix minimum, ou None si aucun fournisseur n'a ce produit
        """
        fournisseurs = self.fournisseur_repo.get_all()
        prix_min = None
        
        for fournisseur in fournisseurs:
            prix = self.get_prix_produit_fournisseur(produit_id, fournisseur.id)
            if prix is not None:
                if prix_min is None or prix < prix_min:
                    prix_min = prix
        
        return prix_min
    
    def get_prix_maximum(self, produit_id: int) -> Optional[float]:
        """
        Récupère le prix maximum d'un produit chez tous les fournisseurs.
        
        Args:
            produit_id: ID du produit
            
        Returns:
            Le prix maximum, ou None si aucun fournisseur n'a ce produit
        """
        fournisseurs = self.fournisseur_repo.get_all()
        prix_max = None
        
        for fournisseur in fournisseurs:
            prix = self.get_prix_produit_fournisseur(produit_id, fournisseur.id)
            if prix is not None:
                if prix_max is None or prix > prix_max:
                    prix_max = prix
        
        return prix_max
    
    def get_fournisseurs_avec_produit(self, produit_id: int) -> list[Fournisseur]:
        """
        Récupère tous les fournisseurs qui ont un produit spécifique en stock.
        
        Args:
            produit_id: ID du produit
            
        Returns:
            Liste des fournisseurs ayant ce produit en stock
        """
        fournisseurs = self.fournisseur_repo.get_all()
        return [
            f for f in fournisseurs
            if produit_id in f.stock_produit and f.stock_produit[produit_id] > 0
        ]
    
    def clear_cache(self) -> None:
        """Vide le cache des prix."""
        self._prix_cache.clear()


# Instance globale du service de prix
price_service = PriceService() 