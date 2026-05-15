====== STRUCTURE DU PROJET:

ssu-report-tool/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   │
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── calcium_standard.py
│   │   ├── activites_ide.py
│   │   ├── seances_dspe.py
│   │   └── effectifs.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── import_service.py
│   │   ├── indicator_service.py
│   │   ├── chart_service.py
│   │   └── report_service.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── excel_helpers.py
│   │   ├── cleaning.py
│   │   └── logging_utils.py
│   │
│   └── templates/
│       ├── report.html
│       ├── sections/
│       │   ├── intro.html
│       │   ├── medecine.html
│       │   ├── ide.html
│       │   ├── dspe.html
│       │   └── effectifs.html
│       └── assets/
│           └── style.css
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── output/
│   ├── reports/
│   └── charts/
│
├── tests/
│   ├── test_parsers.py
│   ├── test_indicators.py
│   └── test_report.py
│
├── requirements.txt
├── README.md
└── .gitignore


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
    C’est super important dans votre cas.
    Exemple :
        calcium_standard.py : pour les exports statistiques standards
        activites_ide.py : pour le fichier IDE
        seances_dspe.py : pour le fichier DSPE
        effectifs.py : pour le fichier effectifs
    Chaque parser doit savoir :
        ouvrir le bon fichier
        ignorer les mauvaises lignes
        nettoyer les colonnes
        retourner un DataFrame propre

**app/services/**
    Ici, tu mets la logique métier.
    Par exemple : 
        _import_service.py_
            coordonne l’import de plusieurs fichiers
        _indicator_service.py_
            calcule les KPI (chiffres clés (indicateurs)):
                nombre de consultations
                évolution annuelle
                répartition par service
                etc.
    _chart_service.py_
        génère les graphiques
    _report_service.py_
        prépare le HTML puis le PDF

**app/models/**
    Pas forcément une “base de données” tout de suite.
    Tu peux y mettre des structures de données simples :
        noms de colonnes normalisés
        objets métier
        formats attendus

**app/utils/**
    Fonctions utilitaires réutilisables.
    Exemples :
        trouver la vraie ligne d’en-tête
        nettoyer les colonnes Unnamed
        convertir des nombres
        gérer les dates

**app/templates/**
    Si vous générez le rapport en HTML avec Jinja2.
    Tu peux avoir :
        un template principal
        des sous-sections par service
        un CSS pour le rendu PDF

**data/raw/**
    Les fichiers bruts importés, jamais modifiés.

**data/processed/**
    Les données nettoyées ou intermédiaires.

**data/sample**
Des petits fichiers d’exemple pour tester sans utiliser les vrais à chaque fois.

**output/**
    Tout ce que l’outil produit :
        graphiques
        rapport PDF
        exports intermédiaires

**tests/**
    Même si vous n’en faites pas beaucoup, mets au moins quelques tests simples.
    Ça fera très sérieux et très utile.
