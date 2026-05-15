# ==============================================================
#  build_windows.ps1 — Script de packaging Windows
#  Génère un exécutable standalone RapportSSU.exe
#
#  PRÉREQUIS (à faire une seule fois sur le poste de build) :
#    pip install pyinstaller pillow
#
#  USAGE :
#    Ouvrir PowerShell dans le dossier racine du projet, puis :
#    .\build_windows.ps1
#
#  RÉSULTAT :
#    dist\RapportSSU\RapportSSU.exe  ← à livrer à l'équipe SSU
# ==============================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Build RapportSSU.exe — Université d'Angers / SSU" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# ── Étape 1 : Vérification du venv ───────────────────────────
Write-Host "[1/5] Vérification de l'environnement Python..." -ForegroundColor Yellow

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "      ERREUR : environnement virtuel introuvable." -ForegroundColor Red
    Write-Host "      Créez-le avec : python -m venv .venv" -ForegroundColor Red
    Write-Host "      Puis installez : .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

$Python = ".venv\Scripts\python.exe"
$Pip    = ".venv\Scripts\pip.exe"

# ── Étape 2 : Installation de PyInstaller ────────────────────
Write-Host "[2/5] Installation / vérification de PyInstaller..." -ForegroundColor Yellow
& $Pip install --quiet pyinstaller pillow
if ($LASTEXITCODE -ne 0) {
    Write-Host "      ERREUR lors de l'installation de PyInstaller." -ForegroundColor Red
    exit 1
}
Write-Host "      OK." -ForegroundColor Green

# ── Étape 3 : Conversion icône PNG → ICO ─────────────────────
Write-Host "[3/5] Création de l'icône Windows (.ico)..." -ForegroundColor Yellow

$IconPng = "app\reports\icon.png"
$IconIco = "app\reports\icon.ico"

if (Test-Path $IconPng) {
    & $Python -c @"
from PIL import Image
img = Image.open(r'$IconPng').convert('RGBA')
sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
img.save(r'$IconIco', format='ICO', sizes=sizes)
print('Icone creee : $IconIco')
"@
    if ($LASTEXITCODE -ne 0) {
        Write-Host "      Avertissement : impossible de créer l'icône .ico." -ForegroundColor Yellow
        Write-Host "      L'exe sera généré sans icône personnalisée." -ForegroundColor Yellow
    } else {
        Write-Host "      OK : $IconIco" -ForegroundColor Green
    }
} else {
    Write-Host "      Avertissement : $IconPng introuvable, icône par défaut utilisée." -ForegroundColor Yellow
}

# ── Étape 4 : Nettoyage des anciens builds ────────────────────
Write-Host "[4/5] Nettoyage des anciens builds..." -ForegroundColor Yellow
if (Test-Path "dist\RapportSSU") { Remove-Item -Recurse -Force "dist\RapportSSU" }
if (Test-Path "build\RapportSSU") { Remove-Item -Recurse -Force "build\RapportSSU" }
Write-Host "      OK." -ForegroundColor Green

# ── Étape 5 : Lancement de PyInstaller ───────────────────────
Write-Host "[5/5] Génération de l'exécutable (peut prendre 1-2 minutes)..." -ForegroundColor Yellow
Write-Host ""

& $Python -m PyInstaller rapport_ssu.spec --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  ERREUR : PyInstaller a échoué." -ForegroundColor Red
    Write-Host "  Consultez les messages ci-dessus pour le détail." -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

# ── Résumé ────────────────────────────────────────────────────
Write-Host ""
Write-Host "=====================================================" -ForegroundColor Green
Write-Host "  Build terminé avec succès !" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Exécutable : dist\RapportSSU\RapportSSU.exe"
Write-Host ""
Write-Host "  Pour livrer l'application à l'équipe SSU :"
Write-Host "   1. Copiez le dossier dist\RapportSSU\ sur leur poste"
Write-Host "   2. Copiez également data\ dans ce dossier"
Write-Host "   3. Créez un raccourci vers RapportSSU.exe sur leur Bureau"
Write-Host ""

Read-Host "Appuyez sur Entrée pour fermer"
