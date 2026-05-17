"""
Générateur de Tableau de Bord PDF — SSU Université d'Angers
============================================================
Produit un PDF de 5 pages synthétisant le rapport d'activité annuel.
On a utilisé uniquement matplotlib (aucune dépendance supplémentaire).
"""

import os
import matplotlib
matplotlib.use("Agg") # backend non-interactif

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.patches as mpatches
import numpy as np

# ── Couleurs UA ──────────────────────────────────────────────
UA_BLUE       = "#004a8f"
UA_BLUE_LIGHT = "#1a6fc4" 
UA_CYAN       = "#00A9CE"
UA_ACCENT     = "#00b4d8"
WHITE         = "#FFFFFF"
GREY_BG       = "#f0f4f8"
GREY_LIGHT    = "#e2e8f0"
TEXT_DARK      = "#1e293b"
TEXT_SECONDARY = "#64748b"
GREEN         = "#2dc653"
ORANGE        = "#ff9f1c"
ROSE          = "#e63946"
PURPLE        = "#7b2cbf"
TEAL          = "#0fa3b1"

BAR_COLORS = [UA_BLUE, UA_CYAN, GREEN, ORANGE, ROSE, PURPLE, TEAL,
              UA_BLUE_LIGHT, "#64748b", "#a855f7"]

# ── Helpers ──────────────────────────────────────────────────

def _format_number(n):
    """Formate un nombre avec séparateur de milliers."""
    if n is None:
        return "—"
    return f"{int(n):,}".replace(",", " ")


def _add_logo_header(fig, year_label="2025 – 2026"):
    """Ajoute le bandeau d'en-tête avec logos et titre sur chaque page."""
    # Bandeau bleu en haut (Rectangle pour être sûr du rendu)
    rect = mpatches.Rectangle((0, 0.91), 1, 0.09, facecolor=UA_BLUE, transform=fig.transFigure, zorder=0)
    fig.patches.append(rect)

    # Logo SSU (supprimé à la demande de l'utilisateur)
    pass

    # Titre central
    fig.text(0.5, 0.96, "ACTIVITÉ SSU",
                ha="center", va="center", fontsize=15, fontweight="bold",
                color=WHITE, fontfamily="sans-serif")
    fig.text(0.5, 0.93, f"Service de Santé Universitaire — {year_label}",
                ha="center", va="center", fontsize=10, color="#90caf9",
                fontfamily="sans-serif")


def _add_footer(fig, page_num, total_pages=5):
    """Ajoute le pied de page."""
    footer = fig.add_axes([0, 0, 1, 0.025])
    footer.set_xlim(0, 1)
    footer.set_ylim(0, 1)
    footer.set_facecolor(GREY_LIGHT)
    footer.axis("off")
    footer.text(0.5, 0.5, f"SSU — Université d'Angers  |  Page {page_num}/{total_pages}",
                ha="center", va="center", fontsize=7, color=TEXT_SECONDARY)


def _draw_kpi_card(ax, value, label, color=UA_BLUE, icon=""):
    """Dessine une carte KPI stylisée dans un axes donné."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Fond blanc arrondi
    fancy = mpatches.FancyBboxPatch((0.03, 0.05), 0.94, 0.9,
                                    boxstyle="round,pad=0.05",
                                    facecolor=WHITE, edgecolor=GREY_LIGHT,
                                    linewidth=1.2)
    ax.add_patch(fancy)

    # Barre colorée en haut
    bar = mpatches.FancyBboxPatch((0.03, 0.85), 0.94, 0.10,
                                  boxstyle="round,pad=0.02",
                                  facecolor=color, edgecolor="none")
    ax.add_patch(bar)

    # Valeur
    ax.text(0.5, 0.52, _format_number(value),
            ha="center", va="center", fontsize=22, fontweight="bold",
            color=TEXT_DARK, fontfamily="sans-serif")

    # Label
    ax.text(0.5, 0.22, label,
            ha="center", va="center", fontsize=7.5, color=TEXT_SECONDARY,
            fontfamily="sans-serif", wrap=True)


def _draw_horizontal_bars(ax, data_dict, title="", max_items=7, colors=None):
    """Dessine un bar chart horizontal stylisé."""
    if colors is None:
        colors = BAR_COLORS

    if data_dict is None:
        ax.axis("off")
        return

    # Handle if it's a dict or items list
    items = list(data_dict.items()) if hasattr(data_dict, 'items') else []
    items = items[:max_items]
    
    if not items:
        ax.axis("off")
        return

    labels = [str(k) for k, _ in items]
    values = []
    for _, v in items:
        try:
            values.append(float(v) if v is not None else 0)
        except (ValueError, TypeError):
            values.append(0)

    # Inverser pour afficher le plus grand en haut
    labels = labels[::-1]
    values = values[::-1]
    bar_colors = [colors[i % len(colors)] for i in range(len(labels))][::-1]

    y_pos = np.arange(len(labels))
    max_val = max(values) if values and max(values) > 0 else 1
    bars = ax.barh(y_pos, values, color=bar_colors, height=0.6, edgecolor="none")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=7, color=TEXT_DARK, fontfamily="sans-serif")
    ax.set_xlim(0, max_val * 1.15)

    # Valeurs sur les barres
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + max_val * 0.02, bar.get_y() + bar.get_height() / 2,
                _format_number(val), va="center", fontsize=7, fontweight="bold",
                color=TEXT_DARK, fontfamily="sans-serif")

    ax.set_title(title, fontsize=9, fontweight="bold", color=TEXT_DARK, pad=8,
                 fontfamily="sans-serif", loc="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(GREY_LIGHT)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", colors=TEXT_SECONDARY, labelsize=6)
    ax.tick_params(axis="y", length=0)
    ax.set_facecolor(WHITE)


def _embed_chart_image(ax, chart_path, title=""):
    """Insère une image PNG de graphique existant dans un axes."""
    ax.set_title(title, fontsize=9, fontweight="bold", color=TEXT_DARK, pad=6,
                 fontfamily="sans-serif", loc="left")
    if chart_path and os.path.exists(chart_path):
        try:
            img = mpimg.imread(chart_path)
            ax.imshow(img, aspect="equal")
        except Exception:
            ax.text(0.5, 0.5, "Erreur lecture\nimage", ha="center", va="center",
                    fontsize=9, color=TEXT_SECONDARY, style="italic")
    else:
        ax.text(0.5, 0.5, "Graphique\nnon disponible", ha="center", va="center",
                fontsize=9, color=TEXT_SECONDARY, style="italic")
    ax.axis("off")


def _section_title(fig, y, text, icon=""):
    """Ajoute un titre de section coloré."""
    fig.text(0.04, y, f"{icon}  {text}", fontsize=11, fontweight="bold",
             color=UA_BLUE, fontfamily="sans-serif")
    # Ligne de séparation
    line = fig.add_axes([0.04, y - 0.008, 0.92, 0.002])
    line.set_facecolor(UA_CYAN)
    line.axis("off")


# ── Pages du PDF ─────────────────────────────────────────────

def _page1_overview(pdf, data, charts_dir, year_label):
    """Page 1 : Vue d'ensemble & Démographie"""
    fig = plt.figure(figsize=(8.27, 11.69))  # A4
    fig.set_facecolor(GREY_BG)
    _add_logo_header(fig, year_label)
    _add_footer(fig, 1)

    act = data.get("activite", {})
    prev = data.get("prevention", {})
    pssm = data.get("sante_mentale", {}).get("pssm", {})
    css = data.get("sante_sexuelle", {})

    # Section : Chiffres clés
    _section_title(fig, 0.88, "CHIFFRES CLÉS DE L'ANNÉE", "---")

    kpis = [
        (act.get("total_consultations"), "Consultations\ntotales", UA_BLUE),
        (act.get("etudiants_uniques"), "Étudiants\naccompagnés", UA_CYAN),
        (act.get("consultations_bilans"), "Bilans de\nprévention", GREEN),
        (prev.get("nombre_actions"), "Actions de\nprévention", ORANGE),
        (pssm.get("nombre_sessions"), "Sessions\nPSSM", PURPLE),
        (css.get("total_consultations_css"), "Consultations\nCSS", ROSE),
    ]

    for i, (val, label, color) in enumerate(kpis):
        ax = fig.add_axes([0.04 + (i % 3) * 0.32, 0.715 - (i // 3) * 0.14, 0.28, 0.13])
        _draw_kpi_card(ax, val, label, color)

    # Section : Répartition des consultations
    _section_title(fig, 0.55, "RÉPARTITION PAR TYPE DE CONSULTATION", "---")

    ax_motifs = fig.add_axes([0.06, 0.29, 0.42, 0.23])
    _embed_chart_image(ax_motifs, os.path.join(charts_dir, "top_motifs.png"),
                       "Top motifs de consultation")

    # Graphique : Répartition sexe
    ax_sexe = fig.add_axes([0.52, 0.29, 0.42, 0.23])
    _embed_chart_image(ax_sexe, os.path.join(charts_dir, "repartition_sexe.png"),
                       "Répartition par sexe")

    # Section : Démographie
    _section_title(fig, 0.25, "DÉMOGRAPHIE ÉTUDIANTE", "---")

    ax_nat = fig.add_axes([0.06, 0.035, 0.42, 0.19])
    _embed_chart_image(ax_nat, os.path.join(charts_dir, "top_nationalites_hors_france.png"),
                       "Top nationalités (hors France)")

    ax_etab = fig.add_axes([0.52, 0.035, 0.42, 0.19])
    _embed_chart_image(ax_etab, os.path.join(charts_dir, "etablissements_conventionnes.png"),
                       "Principaux établissements")

    pdf.savefig(fig, facecolor=fig.get_facecolor(), dpi=500)
    plt.close(fig)


def _page2_medical(pdf, data, charts_dir, year_label):
    """Page 2 : Suivi Médical & Aménagements"""
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.set_facecolor(GREY_BG)
    _add_logo_header(fig, year_label)
    _add_footer(fig, 2)

    act = data.get("activite", {})
    bilans = data.get("bilans_prevention", {})

    # Section : Activité médicale
    _section_title(fig, 0.88, "ACTIVITÉ MÉDICALE", "---")

    med_kpis = [
        (act.get("consultations_medecine_generale"), "Médecine\ngénérale", UA_BLUE),
        (bilans.get("bilans_medecins"), "Bilans par\nmédecins", GREEN),
        (bilans.get("bilans_infirmieres"), "Bilans par\ninfirmières", ORANGE),
    ]

    for i, (val, label, color) in enumerate(med_kpis):
        ax = fig.add_axes([0.04 + i * 0.235, 0.75, 0.21, 0.10])
        _draw_kpi_card(ax, val, label, color)

    # Graphiques
    ax1 = fig.add_axes([0.06, 0.49, 0.42, 0.22])
    _embed_chart_image(ax1, os.path.join(charts_dir, "motifs_medecine_generale.png"),
                       "Récapitulatif des consultations")

    ax2 = fig.add_axes([0.52, 0.49, 0.42, 0.22])
    _embed_chart_image(ax2, os.path.join(charts_dir, "evolution_activite_medicale_detail.png"),
                       "Évolution de l'activité médicale")

    # Section : Aménagements & Bilans
    _section_title(fig, 0.45, "AMÉNAGEMENTS & BILANS DE PRÉVENTION", "---")

    ax3 = fig.add_axes([0.06, 0.22, 0.42, 0.20])
    _embed_chart_image(ax3, os.path.join(charts_dir, "repartition_amenagements.png"),
                       "Répartition des aménagements")

    ax4 = fig.add_axes([0.52, 0.22, 0.42, 0.20])
    _embed_chart_image(ax4, os.path.join(charts_dir, "evolution_amenagements.png"),
                       "Évolution des aménagements")

    ax5 = fig.add_axes([0.06, 0.03, 0.42, 0.18])
    _embed_chart_image(ax5, os.path.join(charts_dir, "bilans_par_composante.png"),
                       "Bilans par composante")

    ax6 = fig.add_axes([0.52, 0.03, 0.42, 0.18])
    _embed_chart_image(ax6, os.path.join(charts_dir, "bilans_internationaux.png"),
                       "Bilans internationaux")

    pdf.savefig(fig, facecolor=fig.get_facecolor(), dpi=500)
    plt.close(fig)


def _page3_mental(pdf, data, charts_dir, year_label):
    """Page 3 : Santé Mentale & PSSM"""
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.set_facecolor(GREY_BG)
    _add_logo_header(fig, year_label)
    _add_footer(fig, 3)

    act = data.get("activite", {})
    pssm = data.get("sante_mentale", {}).get("pssm", {})

    # Section : Santé Mentale
    _section_title(fig, 0.88, "SANTÉ MENTALE", "---")

    mental_kpis = [
        (act.get("consultations_psychologie"), "Consultations\npsychologie", PURPLE),
        (act.get("consultations_psychiatrie"), "Consultations\npsychiatrie", ROSE),
    ]

    for i, (val, label, color) in enumerate(mental_kpis):
        ax = fig.add_axes([0.04 + i * 0.235, 0.75, 0.21, 0.10])
        _draw_kpi_card(ax, val, label, color)

    ax1 = fig.add_axes([0.06, 0.51, 0.42, 0.20])
    _embed_chart_image(ax1, os.path.join(charts_dir, "evolution_psychiatrie.png"),
                       "Évolution psychiatrie")

    ax2 = fig.add_axes([0.52, 0.51, 0.42, 0.20])
    _embed_chart_image(ax2, os.path.join(charts_dir, "problematique_psy.png"),
                       "Problématiques psychologiques")

    # Section : PSSM
    _section_title(fig, 0.47, "FORMATION PREMIERS SECOURS SANTÉ MENTALE", "---")

    pssm_kpis = [
        (pssm.get("nombre_sessions"), "Sessions\nPSSM", TEAL),
        (pssm.get("total_etudiants_ua"), "Étudiants UA\nformés PSSM", GREEN),
    ]

    for i, (val, label, color) in enumerate(pssm_kpis):
        ax = fig.add_axes([0.04 + i * 0.235, 0.34, 0.21, 0.10])
        _draw_kpi_card(ax, val, label, color)

    ax3 = fig.add_axes([0.06, 0.11, 0.42, 0.20])
    _embed_chart_image(ax3, os.path.join(charts_dir, "pssm_sessions.png"),
                       "Nombre de sessions PSSM par année")

    ax4 = fig.add_axes([0.52, 0.11, 0.42, 0.20])
    _embed_chart_image(ax4, os.path.join(charts_dir, "pssm_origine_stagiaires.png"),
                       "Origine des stagiaires")
    
    pdf.savefig(fig, facecolor=fig.get_facecolor(), dpi=500)
    plt.close(fig)
    

def _page4_IDE_CSS(pdf, data, charts_dir, year_label):
    """Page 4 : IDE & Santé Sexuelle"""
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.set_facecolor(GREY_BG)
    _add_logo_header(fig, year_label)
    _add_footer(fig, 4)
    act = data.get("activite", {})
    css = data.get("sante_sexuelle", {})

    # Section : IDE
    _section_title(fig, 0.88, "ACTIVITÉ INFIRMIERE (IDE)", "---")

    ide_kpis = [
        (act.get("consultations_ide"), "Consultations\nIDE", UA_CYAN),
    ]

    for i, (val, label, color) in enumerate(ide_kpis):
        ax = fig.add_axes([0.04 + i * 0.235, 0.75, 0.21, 0.10])
        _draw_kpi_card(ax, val, label, color)

    ax1 = fig.add_axes([0.06, 0.51, 0.42, 0.20])
    _embed_chart_image(ax1, os.path.join(charts_dir, "activite_infirmiere_compare.png"),
                       "Évolution activité infirmière")

    ax2 = fig.add_axes([0.52, 0.51, 0.42, 0.20])
    _embed_chart_image(ax2, os.path.join(charts_dir, "repartition_activite_infirmiere.png"),
                       "Motifs de consultation IDE")


    # Section : Santé Sexuelle
    _section_title(fig, 0.47, "CENTRE DE SANTÉ SEXUELLE (CSS)", "---")

    css_kpis = [
        (css.get("total_consultations_css"), "Consultations\nCSS", PURPLE),
        (css.get("motifs_reels_css", {}).get("contraception", 0), "Contraception", ROSE),
        (css.get("motifs_reels_css", {}).get("Dépistage IST", 0), "Dépistage\nIST", TEAL),
    ]

    for i, (val, label, color) in enumerate(css_kpis):
        ax = fig.add_axes([0.04 + i * 0.32, 0.34, 0.28, 0.10])
        _draw_kpi_card(ax, val, label, color)

    ax3 = fig.add_axes([0.06, 0.11, 0.42, 0.20])
    _embed_chart_image(ax3, os.path.join(charts_dir, "motifs_reels_css.png"),
                       "Motifs de consultation CSS")

    ax4 = fig.add_axes([0.52, 0.11, 0.42, 0.20])
    _embed_chart_image(ax4, os.path.join(charts_dir, "prescriptions_css.png"),
                       "Prescriptions CSS")

    pdf.savefig(fig, facecolor=fig.get_facecolor(), dpi=500)
    plt.close(fig)

def _page5_prevention(pdf, data, charts_dir, year_label):
    """Page 5 : Prévention & Actions sur les campus"""
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.set_facecolor(GREY_BG)
    _add_logo_header(fig, year_label)
    _add_footer(fig, 5)

    prev = data.get("prevention", {})
    stats = data.get("stats_standard", {})

    # Section : Prévention
    _section_title(fig, 0.88, "ACTIONS DE PRÉVENTION SUR LES CAMPUS", "---")

    prev_kpis = [
        (prev.get("nombre_actions"), "Actions\nmenées", ORANGE),
        (prev.get("total_etudiants_touches"), "Étudiants\ntouchés", GREEN),
        (stats.get("total_appels_latest_year"), "Appels\ntéléphoniques", UA_BLUE),
    ]

    for i, (val, label, color) in enumerate(prev_kpis):
        ax = fig.add_axes([0.04 + i * 0.32, 0.75, 0.28, 0.10])
        _draw_kpi_card(ax, val, label, color)

    # Graphiques
    ax1 = fig.add_axes([0.06, 0.50, 0.42, 0.21])
    _embed_chart_image(ax1, os.path.join(charts_dir, "actions_par_theme.png"),
                       "Actions par thématique")

    ax2 = fig.add_axes([0.52, 0.50, 0.42, 0.21])
    _embed_chart_image(ax2, os.path.join(charts_dir, "actions_par_site_lisible.png"),
                       "Actions par site / campus")

    # Consommables
    _section_title(fig, 0.46, "CONSOMMABLES DISTRIBUÉS", "---")

    # On commence très bas (0.05) et on donne une grande hauteur (0.38)
    ax3 = fig.add_axes([0.06, 0.05, 0.88, 0.38])
    _embed_chart_image(ax3, os.path.join(charts_dir, "consommables_bilans_actions.png"),
                       "")

    pdf.savefig(fig, facecolor=fig.get_facecolor(), dpi=500)
    plt.close(fig)


# ── Point d'entrée public ────────────────────────────────────

def generate_dashboard_pdf(data: dict, charts_dir: str = "output/charts",
                           output_path: str = "output/tableau_de_bord_ssu.pdf",
                           year_label: str = "2025 – 2026"):
    """
    Génère le tableau de bord PDF de 5 pages.

    Args:
        data: Dictionnaire contenant tous les indicateurs calculés (même structure que dashboard_data.json).
        charts_dir: Chemin vers le dossier contenant les graphiques PNG.
        output_path: Chemin du fichier PDF de sortie.
        year_label: Libellé de l'année universitaire.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with PdfPages(output_path) as pdf:
        _page1_overview(pdf, data, charts_dir, year_label)
        _page2_medical(pdf, data, charts_dir, year_label)
        _page3_mental(pdf, data, charts_dir, year_label)
        _page4_IDE_CSS(pdf, data, charts_dir, year_label)
        _page5_prevention(pdf, data, charts_dir, year_label)

    print(f"Tableau de bord PDF généré : {output_path}")
