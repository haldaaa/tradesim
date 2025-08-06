#!/usr/bin/env python3
"""
Names Data TradeSim - Données de noms réalistes pour TradeSim
============================================================

Ce module contient les listes de noms réalistes pour :
- 40 entreprises avec pays et continents
- 40 fournisseurs avec pays et continents  
- 60 produits (20 par type : produit_fini, consommable, matiere_premiere)

Responsabilités :
- Fournir des noms réalistes et diversifiés
- Assurer la cohérence géographique (pays/continent)
- Permettre la sélection aléatoire sans doublons
- Faciliter l'évolution vers le mode Web

Structure :
- ENTREPRISES_DATA : Liste de dicts avec nom, pays, continent
- FOURNISSEURS_DATA : Liste de dicts avec nom, pays, continent
- PRODUITS_DATA : Liste de dicts avec nom, type

Auteur: Assistant IA
Date: 2025-01-27
"""

# -------------------------
# Entreprises (40 entreprises)
# -------------------------
ENTREPRISES_DATA = [
    # Europe
    {"nom": "TechCorp", "pays": "France", "continent": "Europe"},
    {"nom": "BuildTech", "pays": "Allemagne", "continent": "Europe"},
    {"nom": "NordicSolutions", "pays": "Suède", "continent": "Europe"},
    {"nom": "MediterraneanTech", "pays": "Espagne", "continent": "Europe"},
    {"nom": "AlpineCorp", "pays": "Suisse", "continent": "Europe"},
    {"nom": "DutchInnovation", "pays": "Pays-Bas", "continent": "Europe"},
    {"nom": "BelgianTech", "pays": "Belgique", "continent": "Europe"},
    {"nom": "NordicTools", "pays": "Norvège", "continent": "Europe"},
    {"nom": "DanishDesign", "pays": "Danemark", "continent": "Europe"},
    {"nom": "PolishCorp", "pays": "Pologne", "continent": "Europe"},
    {"nom": "CzechTech", "pays": "République tchèque", "continent": "Europe"},
    {"nom": "ItalianDesign", "pays": "Italie", "continent": "Europe"},
    {"nom": "AustrianTech", "pays": "Autriche", "continent": "Europe"},
    {"nom": "FinnishCorp", "pays": "Finlande", "continent": "Europe"},
    
    # Asie
    {"nom": "AsiaTech", "pays": "Chine", "continent": "Asie"},
    {"nom": "PacificCorp", "pays": "Japon", "continent": "Asie"},
    {"nom": "KoreanInnovation", "pays": "Corée du Sud", "continent": "Asie"},
    {"nom": "IndianTech", "pays": "Inde", "continent": "Asie"},
    {"nom": "SingaporeCorp", "pays": "Singapour", "continent": "Asie"},
    {"nom": "ThaiTech", "pays": "Thaïlande", "continent": "Asie"},
    {"nom": "VietnameseCorp", "pays": "Vietnam", "continent": "Asie"},
    {"nom": "MalaysianTech", "pays": "Malaisie", "continent": "Asie"},
    {"nom": "IndonesianCorp", "pays": "Indonésie", "continent": "Asie"},
    {"nom": "TaiwanTech", "pays": "Taïwan", "continent": "Asie"},
    {"nom": "PhilippineCorp", "pays": "Philippines", "continent": "Asie"},
    
    # Amérique du Nord
    {"nom": "USCorp", "pays": "États-Unis", "continent": "Amérique du Nord"},
    {"nom": "CanadaTech", "pays": "Canada", "continent": "Amérique du Nord"},
    {"nom": "MexicanCorp", "pays": "Mexique", "continent": "Amérique du Nord"},
    {"nom": "AmericanInnovation", "pays": "États-Unis", "continent": "Amérique du Nord"},
    {"nom": "CanadianDesign", "pays": "Canada", "continent": "Amérique du Nord"},
    
    # Amérique du Sud
    {"nom": "BrazilianTech", "pays": "Brésil", "continent": "Amérique du Sud"},
    {"nom": "ArgentineCorp", "pays": "Argentine", "continent": "Amérique du Sud"},
    {"nom": "ChileanTech", "pays": "Chili", "continent": "Amérique du Sud"},
    {"nom": "ColombianCorp", "pays": "Colombie", "continent": "Amérique du Sud"},
    {"nom": "PeruvianTech", "pays": "Pérou", "continent": "Amérique du Sud"},
    
    # Afrique
    {"nom": "SouthAfricanCorp", "pays": "Afrique du Sud", "continent": "Afrique"},
    {"nom": "EgyptianTech", "pays": "Égypte", "continent": "Afrique"},
    {"nom": "MoroccanCorp", "pays": "Maroc", "continent": "Afrique"},
    {"nom": "NigerianTech", "pays": "Nigeria", "continent": "Afrique"},
    {"nom": "KenyanCorp", "pays": "Kenya", "continent": "Afrique"},
    
    # Océanie
    {"nom": "AustralianTech", "pays": "Australie", "continent": "Océanie"},
    {"nom": "NewZealandCorp", "pays": "Nouvelle-Zélande", "continent": "Océanie"}
]

# -------------------------
# Fournisseurs (40 fournisseurs)
# -------------------------
FOURNISSEURS_DATA = [
    # Europe
    {"nom": "EuroSupply", "pays": "France", "continent": "Europe"},
    {"nom": "GermanDistrib", "pays": "Allemagne", "continent": "Europe"},
    {"nom": "SwedishTools", "pays": "Suède", "continent": "Europe"},
    {"nom": "SpanishImport", "pays": "Espagne", "continent": "Europe"},
    {"nom": "SwissPrecision", "pays": "Suisse", "continent": "Europe"},
    {"nom": "DutchTrading", "pays": "Pays-Bas", "continent": "Europe"},
    {"nom": "BelgianSupply", "pays": "Belgique", "continent": "Europe"},
    {"nom": "NorwegianTools", "pays": "Norvège", "continent": "Europe"},
    {"nom": "DanishSupply", "pays": "Danemark", "continent": "Europe"},
    {"nom": "PolishDistrib", "pays": "Pologne", "continent": "Europe"},
    {"nom": "CzechImport", "pays": "République tchèque", "continent": "Europe"},
    {"nom": "ItalianSupply", "pays": "Italie", "continent": "Europe"},
    {"nom": "AustrianTools", "pays": "Autriche", "continent": "Europe"},
    {"nom": "FinnishDistrib", "pays": "Finlande", "continent": "Europe"},
    
    # Asie
    {"nom": "AsiaImport", "pays": "Chine", "continent": "Asie"},
    {"nom": "PacificSupply", "pays": "Japon", "continent": "Asie"},
    {"nom": "KoreanDistrib", "pays": "Corée du Sud", "continent": "Asie"},
    {"nom": "IndianImport", "pays": "Inde", "continent": "Asie"},
    {"nom": "SingaporeSupply", "pays": "Singapour", "continent": "Asie"},
    {"nom": "ThaiDistrib", "pays": "Thaïlande", "continent": "Asie"},
    {"nom": "VietnameseImport", "pays": "Vietnam", "continent": "Asie"},
    {"nom": "MalaysianSupply", "pays": "Malaisie", "continent": "Asie"},
    {"nom": "IndonesianDistrib", "pays": "Indonésie", "continent": "Asie"},
    {"nom": "TaiwanImport", "pays": "Taïwan", "continent": "Asie"},
    {"nom": "PhilippineSupply", "pays": "Philippines", "continent": "Asie"},
    
    # Amérique du Nord
    {"nom": "USSupply", "pays": "États-Unis", "continent": "Amérique du Nord"},
    {"nom": "CanadaDistrib", "pays": "Canada", "continent": "Amérique du Nord"},
    {"nom": "MexicanImport", "pays": "Mexique", "continent": "Amérique du Nord"},
    {"nom": "AmericanTools", "pays": "États-Unis", "continent": "Amérique du Nord"},
    {"nom": "CanadianSupply", "pays": "Canada", "continent": "Amérique du Nord"},
    
    # Amérique du Sud
    {"nom": "BrazilianImport", "pays": "Brésil", "continent": "Amérique du Sud"},
    {"nom": "ArgentineSupply", "pays": "Argentine", "continent": "Amérique du Sud"},
    {"nom": "ChileanDistrib", "pays": "Chili", "continent": "Amérique du Sud"},
    {"nom": "ColombianImport", "pays": "Colombie", "continent": "Amérique du Sud"},
    {"nom": "PeruvianSupply", "pays": "Pérou", "continent": "Amérique du Sud"},
    
    # Afrique
    {"nom": "SouthAfricanImport", "pays": "Afrique du Sud", "continent": "Afrique"},
    {"nom": "EgyptianSupply", "pays": "Égypte", "continent": "Afrique"},
    {"nom": "MoroccanDistrib", "pays": "Maroc", "continent": "Afrique"},
    {"nom": "NigerianImport", "pays": "Nigeria", "continent": "Afrique"},
    {"nom": "KenyanSupply", "pays": "Kenya", "continent": "Afrique"},
    
    # Océanie
    {"nom": "AustralianImport", "pays": "Australie", "continent": "Océanie"},
    {"nom": "NewZealandSupply", "pays": "Nouvelle-Zélande", "continent": "Océanie"}
]

# -------------------------
# Produits (60 produits - 20 par type)
# -------------------------
PRODUITS_DATA = [
    # Matières premières (20 produits)
    {"nom": "Acier", "type": "matiere_premiere"},
    {"nom": "Bois", "type": "matiere_premiere"},
    {"nom": "Aluminium", "type": "matiere_premiere"},
    {"nom": "Cuivre", "type": "matiere_premiere"},
    {"nom": "Plastique", "type": "matiere_premiere"},
    {"nom": "Verre", "type": "matiere_premiere"},
    {"nom": "Caoutchouc", "type": "matiere_premiere"},
    {"nom": "Coton", "type": "matiere_premiere"},
    {"nom": "Laine", "type": "matiere_premiere"},
    {"nom": "Soie", "type": "matiere_premiere"},
    {"nom": "Papier", "type": "matiere_premiere"},
    {"nom": "Ciment", "type": "matiere_premiere"},
    {"nom": "Béton", "type": "matiere_premiere"},
    {"nom": "Granit", "type": "matiere_premiere"},
    {"nom": "Marbre", "type": "matiere_premiere"},
    {"nom": "Sable", "type": "matiere_premiere"},
    {"nom": "Argile", "type": "matiere_premiere"},
    {"nom": "Pierre", "type": "matiere_premiere"},
    {"nom": "Métal", "type": "matiere_premiere"},
    {"nom": "Tissu", "type": "matiere_premiere"},
    
    # Consommables (20 produits)
    {"nom": "Huile", "type": "consommable"},
    {"nom": "Carburant", "type": "consommable"},
    {"nom": "Électricité", "type": "consommable"},
    {"nom": "Eau", "type": "consommable"},
    {"nom": "Gaz", "type": "consommable"},
    {"nom": "Produits chimiques", "type": "consommable"},
    {"nom": "Peinture", "type": "consommable"},
    {"nom": "Colle", "type": "consommable"},
    {"nom": "Vernis", "type": "consommable"},
    {"nom": "Solvant", "type": "consommable"},
    {"nom": "Acide", "type": "consommable"},
    {"nom": "Base", "type": "consommable"},
    {"nom": "Catalyseur", "type": "consommable"},
    {"nom": "Inhibiteur", "type": "consommable"},
    {"nom": "Stabilisant", "type": "consommable"},
    {"nom": "Antioxydant", "type": "consommable"},
    {"nom": "Plastifiant", "type": "consommable"},
    {"nom": "Pigment", "type": "consommable"},
    {"nom": "Additif", "type": "consommable"},
    {"nom": "Lubrifiant", "type": "consommable"},
    
    # Produits finis (20 produits)
    {"nom": "Téléphone", "type": "produit_fini"},
    {"nom": "Ordinateur", "type": "produit_fini"},
    {"nom": "Voiture", "type": "produit_fini"},
    {"nom": "Meuble", "type": "produit_fini"},
    {"nom": "Vêtement", "type": "produit_fini"},
    {"nom": "Chaussure", "type": "produit_fini"},
    {"nom": "Livre", "type": "produit_fini"},
    {"nom": "Jouet", "type": "produit_fini"},
    {"nom": "Appareil électroménager", "type": "produit_fini"},
    {"nom": "Outillage", "type": "produit_fini"},
    {"nom": "Instrument de musique", "type": "produit_fini"},
    {"nom": "Équipement sportif", "type": "produit_fini"},
    {"nom": "Bijou", "type": "produit_fini"},
    {"nom": "Montre", "type": "produit_fini"},
    {"nom": "Sac", "type": "produit_fini"},
    {"nom": "Lunettes", "type": "produit_fini"},
    {"nom": "Parfum", "type": "produit_fini"},
    {"nom": "Cosmétique", "type": "produit_fini"},
    {"nom": "Médicament", "type": "produit_fini"},
    {"nom": "Aliment", "type": "produit_fini"},
    {"nom": "Boisson", "type": "produit_fini"}
] 