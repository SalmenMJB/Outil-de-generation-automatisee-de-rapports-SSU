======= À quoi sert chaque dossier:

**app/**
C’est le cœur du projet.
    _app/main.py_
        Le point d’entrée principal.
        C’est lui qui lance le pipeline :
            lecture des fichiers
            parsing
            calculs
            génération des graphiques
            génération du rapport

**app/parsers/**
    Un fichier par type d’Excel.
    Chaque parser doit savoir :
        ouvrir le bon fichier
        ignorer les mauvaises lignes
        nettoyer les colonnes
        retourner un DataFrame propre

**app/services/**
    Le cerveau du projet:
    indicator_service.py: calculeret gérer les indicateurs
    word_builder.py: fonctions de base pour report_generator.py

**app/utils/**
    Fonctions utilitaires réutilisables.
    Exemples :
        trouver la vraie ligne d’en-tête
        nettoyer les colonnes Unnamed
        convertir des nombres
        gérer les dates

**data/raw/**
    Les fichiers bruts venant du SSU/Calcium.

**data/processed/**
    Les données nettoyées ou intermédiaires.

**output/**
    Tout ce que l’outil produit :
        graphiques
        rapports PDF et Word
