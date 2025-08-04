# Dossier Data

## **Rôle du dossier**

Ce dossier contient les fichiers de données persistantes de l'application TradeSim.

## **Contenu**

### **Fichiers de parties**
- `partie_YYYY-MM-DD_HH-MM.json` : État complet d'une partie de jeu
  - Produits, fournisseurs, entreprises
  - Prix des produits chez chaque fournisseur
  - Budgets et stocks actuels
  - Métadonnées (date de création, version)

## **Structure des fichiers JSON**

```json
{
  "metadata": {
    "date_creation": "2025-08-04T13:34:45",
    "version": "0.1"
  },
  "produits": [...],
  "fournisseurs": [...],
  "entreprises": [...],
  "prix": {"1_2": 100.50, "2_3": 200.75}
}
```

## **Gestion des erreurs**

- Si un fichier JSON est corrompu → erreur `[SYSTEME]` et arrêt
- Pas de backup automatique pour éviter la complexité
- L'utilisateur peut sauvegarder manuellement avant `--new-game`

## **Mise à jour automatique**

Ce fichier README est automatiquement mis à jour quand des fichiers sont créés ou modifiés dans ce dossier.

---
*Dernière mise à jour : 2025-08-04* 