# =============================================================
#  PyInstaller — Fichier de configuration de build
#  Rapport SSU – Université d'Angers
#
#  USAGE (sur Windows, depuis la racine du projet) :
#      pyinstaller rapport_ssu.spec
#
#  Le résultat est dans : dist\RapportSSU\RapportSSU.exe
# =============================================================

import sys
from pathlib import Path

block_cipher = None

# ── Chemin de base Python (contient DLLs et dossier tcl/) ────────────
PYTHON_BASE = Path(r"C:\Users\Salmen\AppData\Local\Python\pythoncore-3.14-64")

# ── Fichiers de données à embarquer dans l'exe ──────────────
# Format : (source, destination_dans_le_bundle)
added_files = [
    # Logos et icône pour la page de titre du rapport Word
    ("app/reports/logo_ssu.png",  "app/reports"),
    ("app/reports/logo_ua.png",   "app/reports"),
    ("app/reports/icon.png",      "app/reports"),

    # Template de la page de garde Word (embarqué dans l'exe)
    ("app/reports/template_page_de_garde.docx", "app/reports"),

    # Données historiques pré-remplies (mises à jour automatiquement)
    ("data/processed",            "data/processed"),

    # Données brutes par défaut (l'équipe SSU peut les remplacer)
    ("data/raw",                  "data/raw"),

    # Données Tcl/Tk nécessaires pour Tkinter (non incluses automatiquement sur Python MS Store)
    (str(PYTHON_BASE / "tcl" / "tcl8.6"), "tcl/tcl8.6"),
    (str(PYTHON_BASE / "tcl" / "tk8.6"),  "tcl/tk8.6"),
]

# Binaires Tkinter ajoutés explicitement (non détectés par le hook sur Python MS Store)
tk_binaries = [
    (str(PYTHON_BASE / "DLLs" / "_tkinter.pyd"), "."),
    (str(PYTHON_BASE / "DLLs" / "tcl86t.dll"),   "."),
    (str(PYTHON_BASE / "DLLs" / "tk86t.dll"),    "."),
]

a = Analysis(
    # Point d'entrée de l'application
    ["app/ui/tkinter_app.py"],

    pathex=["."],
    binaries=tk_binaries,
    datas=added_files,

    # Imports cachés non détectés automatiquement par PyInstaller
    hiddenimports=[
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "PIL._tkinter_finder",
        "openpyxl.cell._writer",
        "matplotlib.backends.backend_tkagg",
        "pandas._libs.tslibs.timedeltas",
        "pandas._libs.tslibs.nattype",
        "pandas._libs.tslibs.np_datetime",
        "docx",
    ],

    hookspath=[],
    hooksconfig={},
    runtime_hooks=["pyi_rth_tkinter_fix.py"],

    # Exclure les modules inutiles pour alléger le .exe
    excludes=[
        "IPython", "jupyter", "notebook", "scipy",
        "sklearn", "tensorflow", "torch",
        "wx", "PyQt5", "PyQt6", "PySide2", "PySide6",
    ],

    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,     # Mode dossier (plus rapide au démarrage qu'un .exe unique)
    name="RapportSSU",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                  # Compression UPX si disponible (réduit la taille)
    console=False,              # Temporairement True pour voir l'erreur au lancement
    icon="app/reports/icon.ico",  # Icône Windows (.ico, généré par build_windows.ps1)
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="RapportSSU",         # → dist/RapportSSU/
)
