import os
import sys
import subprocess
import platform

##### Ouverture de fichier 
def open_file_with_default_app(filepath: str):
    """Ouvre un fichier avec l'application par défaut du système d'exploitation."""
    if not os.path.exists(filepath):
        print(f"Le fichier n'a pas été trouvé: {filepath}")
        return
 
    current_os = platform.system()

    try:
        if current_os == "Windows":
            # os.startfile() ouvre le fichier avec l'application associée (ex. Word)
            os.startfile(filepath)

        elif current_os == "Darwin": # mac
            # macOS : commande 'open' native
            subprocess.run(["open", filepath], check=True)
        
        else:
            # Linux / unix: xdg-open (standard sur la plupart des distributions)
            subprocess.run(["xdg-open", filepath], check=True)
    except Exception as e:
        print(f"Erreur en ouvrant le fichier: {e}")


##### Vérification des dépendances
def check_dependencies() -> list:
    """Vérifie que les bibliothèques Python nécessaires sont installées.
    
    Retourne une liste vide si l'app est packagée en .exe (tout est déjà embarqué).
    """
    # Dans un exe PyInstaller, toutes les dépendances sont déjà embarquées
    if getattr(sys, "frozen", False):
        return []

    required = {
        "pandas": "pandas",
        "openpyxl": "openpyxl",
        "matplotlib": "matplotlib",
        "docx": "python-docx",
        "PIL": "Pillow",
    }
    missing = []
    for module_name, package_name in required.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(package_name)

    return missing
    

##### Formatage des nombres
def format_number(n) -> str:
    """Formate un nombre entier avec séparateur de milliers (espace insécable fine).

    Utilisé pour afficher les KPIs dans l'interface et les messages de statut.

    Exemples :
        format_number(1234567) → "1 234 567"
        format_number(42.5)    → "42"
        format_number("N/A")   → "N/A"
        format_number(None)    → "N/A"""
    
    if n is None or n == "N/A":
        return "N/A"

    try: 
        n_int = int(float(str(n)))
        return f"{n_int:,}".replace(",", " ")
    except (ValueError, TypeError):
        return str(n)


##### Chemin racine du projet
def get_project_root() -> str:
    """Retourne le chemin absolu de la racine du projet.

    Fonctionne dans deux contextes :
    - Mode normal (python -m ...) : remonte depuis app/ui/utils.py
    - Mode exe PyInstaller        : utilise le dossier de l'exécutable
    """
    if getattr(sys, "frozen", False):
        # PyInstaller : l'exe est dans dist/RapportSSU/RapportSSU.exe
        # Les dossiers data/ et output/ sont créés à côté de l'exe
        return os.path.dirname(sys.executable)
    else:
        # Mode normal : remonter depuis app/ui/utils.py → racine
        current = os.path.abspath(__file__)   # .../app/ui/utils.py
        ui_dir  = os.path.dirname(current)    # .../app/ui/
        app_dir = os.path.dirname(ui_dir)     # .../app/
        root    = os.path.dirname(app_dir)    # .../  (racine)
        return root


def get_resource_path(relative_path: str) -> str:
    """Retourne le chemin absolu d'une ressource embarquée (logos, config...).

    - En mode exe PyInstaller : cherche dans le bundle temporaire (_MEIPASS)
    - En mode normal          : cherche depuis la racine du projet
    """
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = get_project_root()
    return os.path.join(base, relative_path)

##### Création des répertoires de sortie
def ensure_output_dirs():
    """Crée les répertoires de sortie nécessaires s'ils n'existent pas.
    
    Crée output/ et output/charts/ dans la racine du projet
    (ou à côté de l'exe en mode PyInstaller).
    """
    root = get_project_root()
    dirs = [
        os.path.join(root, "output"),
        os.path.join(root, "output", "charts"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True) 