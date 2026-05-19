from app.charts.stat_gyneco import plot_prescriptions_css
import pandas as pd

from app.parsers.bilan_actions import parse_bilan_actions_file
from app.parsers.effectifs import parse_effectifs_file
from app.parsers.stats_standard import parse_stats_standard_file
from app.parsers.stat_activite import parse_stat_activite_file
from app.parsers.pssm import parse_pssm_file
from app.parsers.bilan_actions import parse_bilan_actions_file
from app.parsers.psy import parse_psy_file
from app.parsers.infirmiere import parse_ide_file

from app.charts.psy_charts import plot_delai_attente_psy

from app.services.indicator_service import compute_effectifs_indicators
from app.services.indicator_service import compute_stats_standard_indicators
from app.services.indicator_service import compute_stat_activite_indicators
from app.services.indicator_service import compute_pssm_indicators
from app.services.indicator_service import compute_bilan_actions_indicators
from app.services.indicator_service import compute_css_indicators
from app.services.indicator_service import compute_psy_indicators
from app.services.indicator_service import compute_bilans_professionnels_indicators
 
from app.charts.stats_standard_charts import plot_appels_par_mois
from app.charts.effectifs_charts import plot_evolution_effectifs
from app.charts.etablissements_charts import plot_top_etablissements
from app.charts.pssm_charts import plot_pssm_sessions
from app.charts.pssm_charts import plot_pssm_lastest_year
from app.charts.etablissements_conventionnes_charts import plot_etablissements_conventionnes
from app.charts.amenagements_charts import (
    plot_reparition_amenagements,
    append_current_year_amenagements
)
from app.charts.consultations_charts import plot_recap_consultations
from app.charts.activite_medicale_charts import plot_motifs_medecine_generale_charts
from app.charts.infirmier_charts import plot_repartition_activite_infirmiere
from app.charts.infirmier_charts import plot_activite_infirmiere_compare
from app.charts.psy_charts import plot_duree_suivi
from app.charts.psy_charts import plot_problematique_psy
from app.charts.psy_charts import plot_consultations_psy_par_composante
from app.charts.stat_gyneco import plot_motifs_reels_css
from app.charts.stat_gyneco import plot_motifs_CSS
from app.charts.stat_gyneco import plot_prescriptions_css
from app.charts.dietetique_charts import plot_motifs_consultation_dietetique
from app.charts.activite_charts import (
    # plot_top_nationalites,
    plot_top_nationalites_hors_france,
)
from app.charts.stat_activite_charts import (
    plot_top_motifs,
    plot_repartition_sexe,
)
from app.charts.amenagements_charts import plot_evolution_amenagements
from app.charts.activite_medicale_charts import (
    plot_evolution_activite_medicale,
    plot_repartition_activite_medicale_annee,
    append_current_year_activite_medicale, # fonction qui ajoute les données de l'année en cours au fichier historique pour les comparaisons interannuelles
)
from app.charts.bilans_charts import (
    plot_bilans_par_composante,
    plot_bilans_internationaux,
    plot_bilans_par_filiere,
)
from app.charts.bilan_actions_charts import (
    plot_actions_par_theme,
    plot_consommables_bilan_actions,   
    plot_actions_par_site_lisible,
    plot_actions_par_origine
)
from app.charts.psychiatrie import (
    append_current_year_psychiatrie, # fonction qui ajoute les données de l'année en cours au fichier historique pour les comparaisons interannuelles
    plot_evolution_psychiatrie
)
from app.charts.dashboard_pdf import generate_dashboard_pdf

from app.config.intervenants import MEDECINS, INFIRMIERES

import warnings
warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style, apply openpyxl's default"
)
warnings.filterwarnings(
    "ignore",
    message=".*This pattern is interpreted as a regular expression.*"
)


#### Deux fonctions pour un affichage plus propre dans le terminal ####
def print_section(title: str):
    print(f"\n{'=' * 10} {title} {'=' * 10}\n")

def print_indicators(indicators: dict):
    for key, value in indicators.items():
        print(f"{key} : {value} \n")


def main():
    #### Visualisations tableaux ####
    print_section("Activités")
    activite_path = "data/raw/stat_activite.xlsx"
    df_activite = parse_stat_activite_file(activite_path)
    # print(df_activite.head())
    activite_stats = compute_stat_activite_indicators(df_activite)
    print_indicators(activite_stats)

    import os
    activite_n_1_path = "data/raw/stat_activite_n_1.xlsx"
    activite_stats_n_1 = None
    if os.path.exists(activite_n_1_path):
        try:
            df_activite_n_1 = parse_stat_activite_file(activite_n_1_path)
            activite_stats_n_1 = compute_stat_activite_indicators(df_activite_n_1)
            print("Données N-1 chargées avec succès.")
        except Exception as e:
            print(f"Erreur lors du chargement de {activite_n_1_path} : {e}")


    print_section("Effectifs")
    effectifs_path = "data/raw/evolution_etab_conventionnes.xlsx" 
    df_effectifs = parse_effectifs_file(effectifs_path)
    # print(df_effectifs.head())
    effectifs_stats = compute_effectifs_indicators(df_effectifs)
    print_indicators(effectifs_stats) 


    print_section("STATS STANDARD")
    stats_path = "data/raw/stats_standard_ssu.xlsx"
    df_stats = parse_stats_standard_file(stats_path)
    stats_stats = compute_stats_standard_indicators(df_stats)
    print_indicators(stats_stats)


    print_section("BILANS ACTIONS")
    actions_path = "data/raw/bilan_actions.xlsx"
    df_actions = parse_bilan_actions_file(actions_path)
    # print(df_actions.head())
    # print(df_actions.columns.tolist())
    actions_stats = compute_bilan_actions_indicators(df_actions)
    print_indicators(actions_stats)


    print_section("BILANS PAR PROFESSION")
    bilans_prof_stats = compute_bilans_professionnels_indicators(df_activite, MEDECINS, INFIRMIERES)
    print_indicators(bilans_prof_stats)
    print("Intervenant trouvés dans stat_activite: ")
    print(sorted(df_activite["intervenant"].dropna().astype(str).unique()))
    

    # print_section("DSPE (Séances Psy)")
    # dspe_path = "data/raw/seances_dspe.xlsx"
    # df_dspe = parse_dspe_file(dspe_path)
    # # print(df_dspe.head())
    # # print(df_dspe.columns.tolist())


    print_section("PSSM")
    pssm_path = "data/raw/recap_pssm.xlsx"
    pssm_sheets = parse_pssm_file(pssm_path)
    print("Onglets retenus :")
    print(list(pssm_sheets.keys())) 
    pssm_stats = compute_pssm_indicators(pssm_sheets)
    print_indicators(pssm_stats)
    

    print_section("STATS Motifs Psy")
    psy_path = "data/raw/stats_psy.xlsx"
    df_psy = parse_psy_file(psy_path)
    print(df_psy.head())
    print(df_psy.columns.tolist())
    psy_stats = compute_psy_indicators(df_psy)
    print_indicators(psy_stats)
    

    print_section("CSS")
    css_stats = compute_css_indicators(df_activite)
    print_indicators(css_stats)



    #### GRAPHIQUES ####
    plot_recap_consultations(activite_stats)
    print("Graphique généré : output/charts/recap_consultations.png")

    # plot_top_nationalites(activite_stats)
    # print("Graphique généré : output/charts/top_nationalites.png")
    plot_top_nationalites_hors_france(activite_stats)
    print("Graphique généré : output/charts/top_nationalites_hors_france.png")

    # plot_handicap(activite_stats)
    # print("Graphique généré : output/charts/handicap.png")

    # plot_consultations_par_centre(activite_stats)
    # print("Graphique généré : output/charts/consultations_par_centre.png")

    plot_top_motifs(activite_stats, activite_stats_n_1)
    print("Graphique généré : output/charts/top_motifs.png")

    plot_repartition_sexe(activite_stats)
    print("Graphique généré : output/charts/repartition_sexe.png")

    plot_appels_par_mois(df_stats)
    print("Graphique généré : output/charts/appels_par_mois.png")

    plot_evolution_effectifs(df_effectifs)
    print("Graphique généré : output/charts/evolution_effectifs.png")

    plot_top_etablissements(df_effectifs)
    print("Graphique généré : output/charts/top_etablissements.png")

    plot_actions_par_theme(actions_stats)
    print("Graphique généré : output/charts/actions_par_theme.png")
    plot_consommables_bilan_actions(actions_stats)
    print("Graphique généré : output/charts/consommables_bilan_actions.png")
    plot_actions_par_site_lisible(df_actions)
    print("Graphique généré : output/charts/actions_par_site_lisible.png")
    plot_actions_par_origine(df_actions)
    print("Graphique généré : output/charts/actions_par_origine.png")
 

    plot_pssm_sessions(pssm_stats)
    print("Graphique généré : output/charts/pssm_sessions.png")
    plot_pssm_lastest_year(pssm_sheets)
    print("Graphique généré : output/charts/pssm_origine_stagiaires.png")

    plot_motifs_CSS(df_activite)
    print("Graphique généré : output/charts/motifs_css.png")
    plot_motifs_reels_css(css_stats)
    print("Graphique généré: output/charts/motifs_reels_css.png")
    css_path = "data/raw/stats_consultations_css.xlsx"
    plot_prescriptions_css(css_path)
    print("Graphique généré: output/charts/prescriptions_css.png")


    plot_etablissements_conventionnes(df_effectifs)
    print("Graphique généré : output/charts/etablissements_conventionnes.png")
 
    plot_reparition_amenagements(df_activite)
    print("Graphique généré : output/charts/repartition_amenagements.png")

    amenagements_path = "data/processed/evolutions_amenagements.xlsx"
    historique_medical_path = "data/processed/historique_activite_medicale.xlsx"
    # Obtenir l'année DYNAMIQUEMENT depuis les données
    current_year = "Année Inconnue"
    if "date consultation" in df_activite.columns:
        dates = pd.to_datetime(df_activite["date consultation"], errors="coerce").dropna() # Conversion des dates en datetime
        if not dates.empty:
            def extract_academic_year(d):
                return f"{d.year}-{d.year+1}" if d.month >= 8 else f"{d.year-1}-{d.year}" # Formule pour extraire l'année universitaire
            
            academic_years = dates.apply(extract_academic_year)
            if not academic_years.empty:
                current_year = academic_years.mode()[0] # mode = l'année universitaire la plus fréquente
    # Extraire et rajouter l'année en cours de manière automatique
    append_current_year_activite_medicale(df_activite, historique_medical_path, current_year) # Mettre à jour l'évolution de l'activité médicale (automatique)
    append_current_year_amenagements(df_activite, amenagements_path, current_year) # Mettre à jour l'évolution des aménagements (automatique)

    plot_evolution_activite_medicale(historique_medical_path)
    print("Graphique généré : output/charts/evolution_activite_medicale.png")
    plot_repartition_activite_medicale_annee(historique_medical_path)
    print("Graphique généré : output/charts/repartition_activite_medicale.png")

    plot_evolution_amenagements(amenagements_path)
    print("Graphique généré : output/charts/evolutions_amenagements.png")


    df_bilans = df_activite[df_activite["motif"] == "Bilan de prévention"]
    plot_bilans_par_composante(df_bilans)
    print("Graphique généré : output/charts/bilans_par_composante.png")
    plot_bilans_internationaux(df_bilans)
    print("Graphique généré : output/charts/bilans_internationaux.png")
    plot_bilans_par_filiere(df_bilans)
    print("Graphique généré : output/charts/bilans_par_filiere.png")

    plot_motifs_medecine_generale_charts(df_activite)
    print("Graphique généré : output/charts/motifs_medecine_generale.png")

    repartition_infirmiere_path = "data/raw/stat_liste_infirmiere.xlsx"
    df_infirmiere = parse_ide_file(repartition_infirmiere_path)
    plot_repartition_activite_infirmiere(df_infirmiere)
    print("Graphique généré : output/charts/repartition_activite_infirmiere.png")
 
    delai_psy_path = "data/processed/delai_attente_psy.xlsx"
    plot_delai_attente_psy(delai_psy_path)
    print("Graphique généré : output/charts/delai_attente_psy.png")
    plot_problematique_psy(df_psy)
    print("Graphique généré : output/charts/problematique_psy.png")
    plot_consultations_psy_par_composante(df_psy)
    print("Graphique généré : output/charts/repartition_psy_composante.png")

    
    compare_path = "data/processed/activite_infirmiere_compare.xlsx"
    plot_activite_infirmiere_compare(compare_path)
    print("Graphique généré : output/charts/activite_infirmiere_compare.png")

    # plot_repartition_activite_depuis_reel(df_activite)
    # print("Graphique généré : output/charts/repartition_activite_reelle.png")

    plot_duree_suivi(df_activite)
    print("Graphique généré : output/charts/duree_suivi.png")

    plot_motifs_consultation_dietetique(df_activite)
    print("Graphique généré : output/charts/motifs_consultation_dietetique.png")

    evolution_psychiatrie_path = "data/processed/evolution_activite_psychiatrie.xlsx"
    append_current_year_psychiatrie(df_activite, evolution_psychiatrie_path, current_year)
    plot_evolution_psychiatrie(evolution_psychiatrie_path)
    print("Graphique généré : output/charts/evolution_psychiatrie.png")


    # Génération du tableau de bord PDF (version compacte du rapport)
    dashboard_data = { # les données à passer à dashboard_pdf.py
        "demographie": {
            "effectifs": effectifs_stats, 
            "etablissements": df_effectifs.to_dict(orient='records') if not df_effectifs.empty else [] # convertir le dataframe en dictionnaire
        },
        "activite": activite_stats,
        "bilans_prevention": bilans_prof_stats,
        "sante_mentale": {
            "pssm": pssm_stats
        },
        "sante_sexuelle": css_stats,
        "prevention": actions_stats,
        "stats_standard": stats_stats
    }
    # Appeler la fonction de génération du PDF avec l'année en cours dynamique
    generate_dashboard_pdf(
        data=dashboard_data,
        charts_dir="output/charts",
        output_path="output/tableau_de_bord_ssu.pdf",
        year_label=current_year,
    )
   

if __name__ == "__main__":
    main()