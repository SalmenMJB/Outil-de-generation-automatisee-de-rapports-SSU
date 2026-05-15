"""Interface graphique Tkinter pour le générateur de rapports SSU"""
import threading
import os
from app.ui.utils import ensure_output_dirs

import matplotlib
matplotlib.use('Agg') # Forcer l'utilisation du backend non-interactif pour éviter les crashs de thread (RuntimeError)

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


class SSUReportApp:
    """
    Classe principale de l'application Tkinter.
    Gère toute l'interface graphique et la communication avec le module
    de génération de rapport (report_builder).
    """
    # couleurs
    COLOR_CYAN       = "#00A9CE"   
    COLOR_CYAN_DARK  = "#007A96"   
    COLOR_GREY       = "#E8E8E8"   
    COLOR_WHITE      = "#FFFFFF"   
    COLOR_BLACK      = "#000000"   
    COLOR_SUCCESS    = "#27AE60"   
    COLOR_ERROR      = "#E74C3C"   

    # Chemins par défaut des fichiers Excel 
    DEFAULT_PATHS = {
        "stat_activite":  "data/raw/stat_activite.xlsx",
        "effectifs":      "data/raw/evolution_etab_conventionnes.xlsx",
        "stats_standard": "data/raw/stats_standard_ssu.xlsx",
        "bilan_actions":  "data/raw/bilan_actions.xlsx",
        "pssm":           "data/raw/recap_pssm.xlsx",
        "dspe":           "data/raw/seances_dspe.xlsx",
        "liste_infirmiere": "data/raw/stat_liste_infirmiere.xlsx",
        "stat_activite_n_1": "data/raw/stat_activite_n_1.xlsx",
    }

    # Labels lisibles pour chaque fichier 
    FILE_LABELS = {
        "stat_activite":  "Activité globale",
        "effectifs":      "Effectifs étudiants",
        "stats_standard": "Stats standard SSU",
        "bilan_actions":  "Bilans actions ERS",
        "pssm":           "Sessions PSSM",
        "dspe":           "Séances DSPE",
        "liste_infirmiere": "Liste Activité Infirmière",
        "stat_activite_n_1": "Activité N-1 (Comparaison)",
    }

    def __init__(self, root):
        """
        Initialise l'application avec la fenêtre root fournie.
        """
        self.root = root
        self.root.title("Générateur de Rapport SSU – Université d'Angers")
        self.root.geometry("920x860")
        self.root.resizable(True, True)
        self.root.configure(bg=self.COLOR_WHITE)

        # Variables d'état 
        # Quand la variable change, le widget se met à jour automatiquement, et vice versa.

        # Dict des chemins de fichiers Excel, pré-remplis avec les valeurs par défaut
        self.file_vars = {
            key: tk.StringVar(value=path)
            for key, path in self.DEFAULT_PATHS.items()
        }

        # Dossier de sortie du rapport Word généré
        self.output_dir_var = tk.StringVar(value="output")

        # Progression de la génération (0 à 100) — lié à la ProgressBar
        self.progress_var = tk.IntVar(value=0)

        # Message d'état affiché sous la barre de progression
        self.status_var = tk.StringVar(value="Prêt à générer le rapport.")

        # anti double-clic : True pendant la génération, False sinon
        self.is_generating = False

        # Chemin du dernier rapport Word généré (pour le bouton "Ouvrir le rapport")
        self.last_output_path = None

        # Chemin du dernier dashboard PDF généré (pour le bouton "Ouvrir le dashboard")
        self.last_dashboard_path = None

        # Option : régénérer les graphiques avant la génération
        self.regen_charts_var = tk.BooleanVar(value=True)

        # Centrage de la fenêtre 
        self._center_window()

        # Construction de l'interface 
        self._build_ui()

        # création des répertoires de sortie 
        ensure_output_dirs()

    def _center_window(self):
        """
        Centre la fenêtre au milieu de l'écran.
        """
        self.root.update_idletasks()
        w, h = 920, 860
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        """
        Construit l'ensemble de l'interface graphique.
        """
        # En-tete
        frame_header = tk.Frame(self.root, bg=self.COLOR_CYAN, pady=18)
        frame_header.pack(fill=tk.X)

        tk.Label(
            frame_header,
            text="Générateur de Rapport SSU",
            font=("Calibri", 20, "bold"),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_CYAN
        ).pack()

        tk.Label(
            frame_header,
            text="Service de Santé Universitaire – Université d'Angers",
            font=("Calibri", 11, "italic"),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_CYAN
        ).pack()

        # Corps principal
        frame_body = tk.Frame(self.root, bg=self.COLOR_WHITE, padx=24, pady=10)
        frame_body.pack(fill=tk.BOTH, expand=True)

        # Section : Sélection des fichiers Excel 
        tk.Label(
            frame_body,
            text="Fichiers Excel sources :",
            font=("Calibri", 12, "bold"),
            fg=self.COLOR_CYAN,
            bg=self.COLOR_WHITE,
            anchor="w"
        ).pack(fill=tk.X, pady=(8, 2))

        tk.Label(
            frame_body,
            text="Pré-remplis avec les chemins des fichiers principaux du projet (data/raw/).",
            font=("Calibri", 9, "italic"),
            fg="#888888",
            bg=self.COLOR_WHITE,
            anchor="w"
        ).pack(fill=tk.X, pady=(0, 6))

        # crée une ligne de sélection pour chaque fichier Excel
        self.file_entries = {}
        for key, label in self.FILE_LABELS.items():
            self._add_file_selector(frame_body, key, label)

        ttk.Separator(frame_body, orient="horizontal").pack(fill=tk.X, pady=10)

        # Section : Dossier de sortie 
        tk.Label(
            frame_body,
            text="Dossier de sortie du rapport :",
            font=("Calibri", 12, "bold"),
            fg=self.COLOR_CYAN,
            bg=self.COLOR_WHITE,
            anchor="w"
        ).pack(fill=tk.X, pady=(0, 5))

        self._add_folder_selector(frame_body)

        ttk.Separator(frame_body, orient="horizontal").pack(fill=tk.X, pady=10)

        # Section : Options 
        tk.Label(
            frame_body,
            text="Options :",
            font=("Calibri", 12, "bold"),
            fg=self.COLOR_CYAN,
            bg=self.COLOR_WHITE,
            anchor="w"
        ).pack(fill=tk.X, pady=(0, 5))

        # Checkbox pour régénérer les graphiques
        # (si les données Excel ont changé depuis la dernière génération)
        tk.Checkbutton(
            frame_body,
            text="Régénérer les graphiques (recommandé si les données ont changé)",
            variable=self.regen_charts_var,
            font=("Calibri", 10),
            fg=self.COLOR_BLACK,
            bg=self.COLOR_WHITE,
            activebackground=self.COLOR_WHITE,
            anchor="w"
        ).pack(fill=tk.X, pady=(0, 5))

        ttk.Separator(frame_body, orient="horizontal").pack(fill=tk.X, pady=10)

        # Section : Barre de progression 
        tk.Label(
            frame_body,
            text="Progression :",
            font=("Calibri", 12, "bold"),
            fg=self.COLOR_CYAN,
            bg=self.COLOR_WHITE,
            anchor="w"
        ).pack(fill=tk.X, pady=(0, 5))

        # Barre de progression "déterministe" (montre un % réel)
        # Variable liée : self.progress_var (IntVar, 0-100)
        self.progress_bar = ttk.Progressbar(
            frame_body,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=5)

        # Label affichant l'étape en cours
        self.status_label = tk.Label(
            frame_body,
            textvariable=self.status_var,
            font=("Calibri", 10, "italic"),
            fg="#555555",
            bg=self.COLOR_WHITE,
            anchor="w",
            wraplength=720   
        )
        self.status_label.pack(fill=tk.X, pady=(0, 8))

        # Boutons d'action 
        frame_buttons = tk.Frame(self.root, bg=self.COLOR_WHITE, pady=12, padx=24)
        frame_buttons.pack(fill=tk.X)

        # bouton principal qui lance la génération du rapport
        self.btn_generate = tk.Button(
            frame_buttons,
            text="GÉNÉRER LE RAPPORT",
            font=("Calibri", 13, "bold"),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_CYAN,
            activeforeground=self.COLOR_WHITE,
            activebackground=self.COLOR_CYAN_DARK,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self._on_generate_click
        )
        self.btn_generate.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        # Bouton secondaire : ouvre le rapport Word généré
        self.btn_open = tk.Button(
            frame_buttons,
            text="📄 Ouvrir le rapport",
            font=("Calibri", 11),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_SUCCESS,
            activeforeground=self.COLOR_WHITE,
            activebackground="#1E8449",
            relief=tk.FLAT,
            padx=15,
            pady=10,
            cursor="hand2",
            command=self._on_open_report
        )
        # pas de pack() ici → le bouton est invisible jusqu'à la 1ère génération réussie (caché au départ)

        # Bouton tertiaire : ouvre le dashboard PDF
        self.btn_open_dashboard = tk.Button(
            frame_buttons,
            text="📊 Ouvrir le dashboard",
            font=("Calibri", 11),
            fg=self.COLOR_WHITE,
            bg="#2980B9",
            activeforeground=self.COLOR_WHITE,
            activebackground="#1A5276",
            relief=tk.FLAT,
            padx=15,
            pady=10,
            cursor="hand2",
            command=self._on_open_dashboard
        )
        # pas de pack() ici → le bouton est invisible jusqu'à la 1ère génération réussie (caché au départ)

    def _add_file_selector(self, parent, key: str, label: str):
        """
        Ajoute une ligne de sélection de fichier Excel dans le formulaire.
        """
        frame = tk.Frame(parent, bg=self.COLOR_WHITE, pady=3)
        frame.pack(fill=tk.X)

        # Label (largeur fixe à 22 caractères pour alignement des champs)
        tk.Label(
            frame,
            text=f"{label} :",
            font=("Calibri", 9),
            fg=self.COLOR_BLACK,
            bg=self.COLOR_WHITE,
            width=22,
            anchor="w"
        ).pack(side=tk.LEFT)

        # Champ texte lié à la StringVar correspondante
        entry = tk.Entry(
            frame,
            textvariable=self.file_vars[key],
            font=("Calibri", 9),
            fg="#333333",
            bg=self.COLOR_GREY,
            relief=tk.FLAT,
        )
        entry.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
        self.file_entries[key] = entry  

        # bouton "Parcourir…"
        tk.Button(
            frame,
            text="Parcourir…",
            font=("Calibri", 9),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_CYAN,
            activebackground=self.COLOR_CYAN_DARK,
            relief=tk.FLAT,
            padx=8,
            cursor="hand2",
            command=lambda k=key: self._browse_file(k)   # capture k par valeur
        ).pack(side=tk.LEFT)

    def _add_folder_selector(self, parent):
        """
        Ajoute le sélecteur de dossier de sortie.
        """
        frame = tk.Frame(parent, bg=self.COLOR_WHITE, pady=3)
        frame.pack(fill=tk.X)

        tk.Label(
            frame,
            text="Dossier de sortie :",
            font=("Calibri", 9),
            fg=self.COLOR_BLACK,
            bg=self.COLOR_WHITE,
            width=22,
            anchor="w"
        ).pack(side=tk.LEFT)

        tk.Entry(
            frame,
            textvariable=self.output_dir_var,
            font=("Calibri", 9),
            fg="#333333",
            bg=self.COLOR_GREY,
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)

        tk.Button(
            frame,
            text="Parcourir…",
            font=("Calibri", 9),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_CYAN,
            activebackground=self.COLOR_CYAN_DARK,
            relief=tk.FLAT,
            padx=8,
            cursor="hand2",
            command=self._browse_output_folder
        ).pack(side=tk.LEFT)

    # Gestionnaires d'événements des boutons "Parcourir" 
    def _browse_file(self, key: str):
        """
        Ouvre un dialogue de sélection de fichier Excel.
        Filtre sur les extensions .xlsx et .xls.
        Met à jour la StringVar correspondante uniquement si l'utilisateur
        """
        current_path = self.file_vars[key].get()
        initial_dir  = os.path.dirname(current_path) if current_path else "."

        path = filedialog.askopenfilename(
            title=f"Sélectionner : {self.FILE_LABELS[key]}",
            filetypes=[
                ("Fichiers Excel", "*.xlsx *.xls"),
                ("Tous les fichiers", "*.*")
            ],
            initialdir=initial_dir
        )

        if path:  # filedialog retourne "" si l'utilisateur annule
            self.file_vars[key].set(path)

    def _browse_output_folder(self):
        """
        Ouvre un dialogue de sélection de dossier pour la sortie.
        Met à jour output_dir_var si l'utilisateur a sélectionné un dossier.
        """
        current = self.output_dir_var.get()
        folder = filedialog.askdirectory(
            title="Sélectionner le dossier de sortie",
            initialdir=current if current else "."
        )
        if folder:
            self.output_dir_var.set(folder)

    # Gestion de la génération 
    def _on_generate_click(self):
        """
        Appelée quand l'utilisateur clique sur "Générer le rapport".
        """
        if self.is_generating: # éviter les clics quand la génération est déjà en cours
            return

        # Avertissement si des fichiers sont introuvables (non bloquant)
        missing = self._validate_files() # renvoie une liste des fichiers manquants
        if missing:
            messagebox.showwarning(
                "Fichiers manquants",
                "Les fichiers suivants sont introuvables :\n\n" +
                "\n".join(f"  • {self.FILE_LABELS[k]}" for k in missing) +
                "\n\nLes sections correspondantes seront générées sans données "
                "(placeholders textuels à la place des graphiques manquants)."
            )

        # Passage en mode "génération"
        self.is_generating = True
        self.btn_generate.config(
            text="Génération en cours...",
            state=tk.DISABLED,
            bg="#AAAAAA"
        )
        self.progress_var.set(0)
        self.btn_open.pack_forget()           # Cacher le bouton d'ouverture précédent
        self.btn_open_dashboard.pack_forget() # Cacher le bouton dashboard précédent

        # Thread daemon : se termine automatiquement si l'application se ferme
        t = threading.Thread(target=self._run_generation, daemon=True)
        t.start()

    def _validate_files(self) -> list:
        """
        Vérifie que les fichiers Excel sélectionnés existent bien sur le disque.
        """
        missing = []
        for key, var in self.file_vars.items():
            path = var.get().strip()
            if path and not os.path.exists(path):
                missing.append(key)
        return missing

    def _run_generation(self):
        """
        Exécutée dans un thread séparé.
        """
        try:
            from app.ui.utils import get_project_root
            # [CRITIQUE] Sur Windows, les FileDialog de Tkinter changent secrètement le CWD (Current Working Directory).
            # Cela fait planter toutes les écritures avec des chemins relatifs (comme "data/processed/...").
            # On force le retour à la racine du projet avant toute opération :
            os.chdir(get_project_root())

            from app.reports.report_builder import build_report

            # Construction du dict des chemins de fichiers
            file_paths = {
                key: var.get().strip()
                for key, var in self.file_vars.items()
            }

            # Construction du chemin de sortie complet
            output_dir      = self.output_dir_var.get().strip() or "output"
            output_path     = os.path.join(output_dir, "rapport_ssu.docx")
            dashboard_path  = os.path.join(output_dir, "tableau_de_bord_ssu.pdf")

            # Lancement de la génération avec callback de progression
            result_path = build_report(
                file_paths         = file_paths,
                output_path        = output_path,
                regenerate_charts  = self.regen_charts_var.get(),
                progress_callback  = self._update_progress_from_thread
            )

            # Succès → mettre à jour l'UI dans le thread principal
            self.last_output_path = result_path
            self.last_dashboard_path = dashboard_path if os.path.exists(dashboard_path) else None
            self.root.after(0, self._on_generation_success, result_path)

        except Exception as e:
            import traceback
            error_msg    = str(e)
            traceback_str = traceback.format_exc()
            # Erreur → afficher dans le thread principal
            self.root.after(0, self._on_generation_error, error_msg, traceback_str)

    def _update_progress_from_thread(self, step: str, pct: int):
        """
        Planifie une mise à jour de la barre de progression depuis le thread worker.
        """
        self.root.after(0, self._update_progress_ui, step, pct)

    def _update_progress_ui(self, step: str, pct: int):
        """
        Met à jour les widgets de progression (à appeler depuis le thread principal).
        """
        self.progress_var.set(pct)
        self.status_var.set(f"  {step}")
        self.root.update_idletasks()  # Force le rafraîchissement visuel immédiat

    def _on_generation_success(self, word_path: str):
        """
        Appelée (dans le thread principal) quand la génération réussit.
        """
        self.is_generating = False
        self.progress_var.set(100)
        self.status_var.set(f"Rapport généré avec succès !")

        # Réactivation du bouton de génération
        self.btn_generate.config(
            text="GÉNÉRER LE RAPPORT",
            state=tk.NORMAL,
            bg=self.COLOR_CYAN
        )

        # Affichage des boutons d'ouverture
        self.btn_open.pack(side=tk.LEFT, padx=(5, 0))
        # N'afficher le bouton dashboard que si le PDF a bien été généré
        if self.last_dashboard_path:
            self.btn_open_dashboard.pack(side=tk.LEFT, padx=(5, 0))

        # Boîte de dialogue de confirmation
        messagebox.showinfo(
            "Rapport généré",
            f"Le rapport a été généré avec succès !\n\n"
            f"Fichier : {word_path}"
        )

    def _on_generation_error(self, error: str, traceback_str: str):
        """
        Appelée (dans le thread principal) quand la génération échoue.
        """
        self.is_generating = False
        self.status_var.set(f"Erreur : {error}")

        # Réactivation du bouton
        self.btn_generate.config(
            text="GÉNÉRER LE RAPPORT",
            state=tk.NORMAL,
            bg=self.COLOR_CYAN
        )

        # Log dans le terminal (utile pour le débogage)
        print(f"\n[ERREUR] Génération échouée :\n{traceback_str}")

        # Boîte de dialogue d'erreur
        messagebox.showerror(
            "Erreur de génération",
            f"Une erreur est survenue lors de la génération :\n\n{error}\n\n"
            f"Consultez le terminal pour le détail complet."
        )

    def _on_open_report(self):
        """
        Appelée quand l'utilisateur clique sur "Ouvrir le rapport" (Word).
        """
        if not self.last_output_path or not os.path.exists(self.last_output_path):
            messagebox.showwarning(
                "Fichier introuvable",
                "Le fichier rapport est introuvable.\n"
                "Veuillez régénérer le rapport."
            )
            return

        from app.ui.utils import open_file_with_default_app
        open_file_with_default_app(self.last_output_path)

    def _on_open_dashboard(self):
        """
        Appelée quand l'utilisateur clique sur "Ouvrir le dashboard" (PDF).
        """
        if not self.last_dashboard_path or not os.path.exists(self.last_dashboard_path):
            messagebox.showwarning(
                "Fichier introuvable",
                "Le fichier dashboard PDF est introuvable.\n"
                "Veuillez régénérer le rapport."
            )
            return

        from app.ui.utils import open_file_with_default_app
        open_file_with_default_app(self.last_dashboard_path)


def run_app():
    """
    Point d'entrée public pour lancer l'application Tkinter.
    """
    if not TKINTER_AVAILABLE:
        print("ERREUR : Tkinter n'est pas disponible sur ce système.")
        print("Sur Linux, installez-le avec :")
        print("  sudo apt-get install python3-tk")
        return

    # Vérification des dépendances avant de lancer l'UI
    from app.ui.utils import check_dependencies
    missing = check_dependencies()
    if missing:
        print(f"ERREUR : Bibliothèques manquantes : {', '.join(missing)}")
        print(f"Installez-les avec : pip install {' '.join(missing)}")
        return

    # Création de la fenêtre principale
    root = tk.Tk()
    app  = SSUReportApp(root)

    # Lancement de la boucle d'événements
    # Cette ligne bloque jusqu'à la fermeture de la fenêtre
    root.mainloop()


if __name__ == "__main__":
    run_app()