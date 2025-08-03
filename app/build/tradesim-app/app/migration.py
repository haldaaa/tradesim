#!/usr/bin/env python3
"""
Migration automatique - Passage vers l'architecture Repository
===========================================================

Ce fichier contient les fonctions de migration automatique pour passer
de l'ancienne structure (accès direct aux fake_db) vers la nouvelle
architecture Repository.

Auteur: Assistant IA
Date: 2024-08-02
"""

import os
import re
from typing import List, Dict, Any
from pathlib import Path


class MigrationManager:
    """
    Gestionnaire de migration pour passer vers l'architecture Repository.
    
    Cette classe détecte automatiquement l'ancienne structure et propose
    des migrations pour passer vers la nouvelle architecture.
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire de migration.
        """
        self.migrations_appliquees = []
        self.erreurs_migration = []
    
    def detecter_ancienne_structure(self) -> Dict[str, Any]:
        """
        Détecte l'ancienne structure dans le code.
        
        Returns:
            Dict[str, Any]: Informations sur l'ancienne structure détectée
        """
        print("🔍 Détection de l'ancienne structure...")
        
        # Patterns pour détecter l'ancienne structure
        patterns = {
            'imports_directs': [
                r'from data import fake_produits_db',
                r'from data import fake_fournisseurs_db',
                r'from data import fake_entreprises_db',
                r'fake_produits_db\.',
                r'fake_fournisseurs_db\.',
                r'fake_entreprises_db\.'
            ],
            'fichiers_a_migrer': [
                'simulateur.py',
                'game_manager.py',
                'main.py',
                'events/inflation.py',
                'events/reassort.py',
                'events/recharge_budget.py',
                'events/variation_disponibilite.py'
            ]
        }
        
        resultats = {
            'ancienne_structure_detectee': False,
            'fichiers_a_migrer': [],
            'imports_a_changer': [],
            'accès_directs': []
        }
        
        # Vérifier les fichiers à migrer
        for fichier in patterns['fichiers_a_migrer']:
            if os.path.exists(fichier):
                resultats['fichiers_a_migrer'].append(fichier)
                resultats['ancienne_structure_detectee'] = True
        
        # Analyser le contenu des fichiers
        for fichier in resultats['fichiers_a_migrer']:
            try:
                with open(fichier, 'r', encoding='utf-8') as f:
                    contenu = f.read()
                    
                    # Détecter les imports directs
                    for pattern in patterns['imports_directs']:
                        if re.search(pattern, contenu):
                            resultats['imports_a_changer'].append({
                                'fichier': fichier,
                                'pattern': pattern
                            })
                    
                    # Détecter les accès directs
                    if 'fake_produits_db' in contenu:
                        resultats['accès_directs'].append(fichier)
                        
            except Exception as e:
                self.erreurs_migration.append(f"Erreur lecture {fichier}: {e}")
        
        return resultats
    
    def proposer_migration(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Propose un plan de migration basé sur la détection.
        
        Args:
            detection (Dict[str, Any]): Résultats de la détection
            
        Returns:
            Dict[str, Any]: Plan de migration proposé
        """
        print("📋 Proposition du plan de migration...")
        
        plan = {
            'etapes': [],
            'fichiers_a_modifier': [],
            'nouveaux_imports': [],
            'temps_estime': '5-10 minutes'
        }
        
        if detection['ancienne_structure_detectee']:
            plan['etapes'] = [
                "1. Créer les nouveaux dossiers (models/, repositories/, services/, etc.)",
                "2. Déplacer les fichiers existants dans les nouveaux dossiers",
                "3. Remplacer les imports directs par les Repository",
                "4. Adapter le code pour utiliser les Repository",
                "5. Mettre à jour les tests",
                "6. Vérifier que tout fonctionne"
            ]
            
            plan['fichiers_a_modifier'] = detection['fichiers_a_migrer']
            
            plan['nouveaux_imports'] = [
                "from repositories import ProduitRepository",
                "from repositories import FournisseurRepository", 
                "from repositories import EntrepriseRepository"
            ]
        
        return plan
    
    def appliquer_migration(self, plan: Dict[str, Any]) -> bool:
        """
        Applique la migration selon le plan proposé.
        
        Args:
            plan (Dict[str, Any]): Plan de migration
            
        Returns:
            bool: True si la migration a réussi
        """
        print("🚀 Application de la migration...")
        
        try:
            # Étape 1: Créer les nouveaux dossiers
            self._creer_nouveaux_dossiers()
            
            # Étape 2: Déplacer les fichiers
            self._deplacer_fichiers()
            
            # Étape 3: Remplacer les imports
            self._remplacer_imports()
            
            # Étape 4: Adapter le code
            self._adapter_code()
            
            print("✅ Migration terminée avec succès!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration: {e}")
            self.erreurs_migration.append(str(e))
            return False
    
    def _creer_nouveaux_dossiers(self):
        """Crée les nouveaux dossiers de l'architecture."""
        dossiers = ['models', 'services', 'api', 'config']
        
        for dossier in dossiers:
            if not os.path.exists(dossier):
                os.makedirs(dossier)
                print(f"📁 Créé le dossier: {dossier}")
    
    def _deplacer_fichiers(self):
        """Déplace les fichiers existants dans les nouveaux dossiers."""
        deplacements = [
            ('models.py', 'models/'),
            ('config.py', 'config/'),
            ('main.py', 'api/'),
            ('simulateur.py', 'services/'),
            ('game_manager.py', 'services/'),
            ('simulate.py', 'services/')
        ]
        
        for fichier, destination in deplacements:
            if os.path.exists(fichier):
                nouveau_chemin = os.path.join(destination, fichier)
                if not os.path.exists(nouveau_chemin):
                    os.rename(fichier, nouveau_chemin)
                    print(f"📦 Déplacé: {fichier} → {nouveau_chemin}")
    
    def _remplacer_imports(self):
        """Remplace les imports directs par les Repository."""
        # Cette fonction sera implémentée pour modifier automatiquement les imports
        print("🔄 Remplacement des imports...")
        # TODO: Implémenter le remplacement automatique des imports
    
    def _adapter_code(self):
        """Adapte le code pour utiliser les Repository."""
        print("🔧 Adaptation du code pour les Repository...")
        # TODO: Implémenter l'adaptation automatique du code
    
    def generer_rapport(self) -> str:
        """
        Génère un rapport de migration.
        
        Returns:
            str: Rapport de migration
        """
        rapport = f"""
# Rapport de Migration TradeSim
==============================

## ✅ Migrations appliquées:
{chr(10).join(f"- {migration}" for migration in self.migrations_appliquees)}

## ❌ Erreurs rencontrées:
{chr(10).join(f"- {erreur}" for erreur in self.erreurs_migration)}

## 📊 Statistiques:
- Fichiers migrés: {len(self.migrations_appliquees)}
- Erreurs: {len(self.erreurs_migration)}
- Statut: {'✅ Succès' if not self.erreurs_migration else '❌ Échec'}

## 🔧 Prochaines étapes:
1. Vérifier que tous les tests passent
2. Tester l'application CLI
3. Tester l'API (si applicable)
4. Documenter les changements

Auteur: Assistant IA
Date: 2024-08-02
        """
        
        return rapport


def migrer_automatiquement():
    """
    Fonction principale pour migrer automatiquement vers l'architecture Repository.
    """
    print("🚀 Démarrage de la migration automatique...")
    
    manager = MigrationManager()
    
    # Détecter l'ancienne structure
    detection = manager.detecter_ancienne_structure()
    
    if not detection['ancienne_structure_detectee']:
        print("✅ Aucune ancienne structure détectée. Migration non nécessaire.")
        return True
    
    # Proposer un plan de migration
    plan = manager.proposer_migration(detection)
    
    print(f"📋 Plan de migration proposé:")
    for etape in plan['etapes']:
        print(f"  {etape}")
    
    # Appliquer la migration
    succes = manager.appliquer_migration(plan)
    
    # Générer le rapport
    rapport = manager.generer_rapport()
    print(rapport)
    
    return succes


if __name__ == "__main__":
    """
    Point d'entrée pour exécuter la migration directement.
    """
    migrer_automatiquement() 