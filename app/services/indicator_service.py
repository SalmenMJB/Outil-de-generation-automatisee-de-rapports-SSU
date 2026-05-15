import pandas as pd
from app.utils.cleaning import (
    standardize_simple_labels,
    standardize_etablissement,
)

def compute_stat_activite_indicators(df):
    indicators = {}

    indicators["total_consultations"] = len(df)

    if "id_etu" in df.columns: 
        indicators["etudiants_uniques"] = df["id_etu"].nunique() 

    if "âge" in df.columns:
        indicators["age_moyen"] = df["âge"].dropna().mean() 
 
    if "centre" in df.columns:
        centre = standardize_simple_labels(df["centre"])
        indicators["consultations_par_centre"] = centre.value_counts(dropna=False)

    if "motif" in df.columns:
        motif = standardize_simple_labels(df["motif"])
        motif_counts = motif.value_counts(dropna=False)

        indicators["top_motifs"] = motif_counts.head(10)

        indicators["consultations_medecine_generale"] = motif_counts.get("Consultations médecine générale", 0)
        indicators["consultations_psychologie"] = motif_counts.get("Psychologie", 0)
        indicators["consultations_psychiatrie"] = motif_counts.get("Psychiatrie", 0)
        indicators["consultations_ide"] = motif_counts.get("Consultations IDE", 0)
        indicators["consultations_css"] = motif_counts.get("Centre de planification", 0)
        indicators["consultations_bilans"] = motif_counts.get("Bilan de prévention", 0)

    if "motif réels" in df.columns:
        motif_reels = standardize_simple_labels(df["motif réels"])
        indicators["top_motifs_reels"] = motif_reels.value_counts(dropna=False).head(10)
        indicators["total_amenagements"] = int(motif_reels.str.contains(r"aménagement esh \+ certificat init[i]*al", case=False, na=False, regex=True).sum())


    if "établissement" in df.columns:
        etab = standardize_etablissement(df["établissement"])
        indicators["consultations_par_etablissement"] = etab.value_counts(dropna=False).head(10)

    if "sexe" in df.columns:
        sexe = standardize_simple_labels(df["sexe"])
        indicators["repartition_sexe"] = sexe.value_counts(dropna=False)

    if "nationalité" in df.columns: 
        nationalite = standardize_simple_labels(df["nationalité"])
        indicators["top_nationalites"] = nationalite.value_counts(dropna=False).head(11)

    if "visite effectuée" in df.columns:
        visites = standardize_simple_labels(df["visite effectuée"])
        indicators["visites_effectuees"] = visites.value_counts(dropna=False)

    if "vaccination effectuée" in df.columns:
        vacc = standardize_simple_labels(df["vaccination effectuée"])
        indicators["vaccinations"] = vacc.value_counts(dropna=False)

    if "handicap" in df.columns:
        handicap = standardize_simple_labels(df["handicap"])
        indicators["handicap"] = handicap.value_counts(dropna=False)

    return indicators


def compute_effectifs_indicators(df):
    indicators = {}

    # recup que les colonnes années (là ou il y a '/' comme 2022/2O23)
    year_cols = [col for col in df.columns if "/" in col]

    # calcul du total des effectifs pour chaque année
    for col in year_cols:
        indicators[f"total_{col}"] = df[col].fillna(0).sum()

    # garde uniquement les colonnes d'années qui contiennent au moins une vraie valeur numérique
    valid_year_cols = [
        col for col in year_cols if pd.to_numeric(df[col], errors="coerce").notna().sum() > 0
    ]

    if valid_year_cols:
        # on vise l'année la plus récente 
        latest_year = valid_year_cols[-1]

        # on convertit la colonne en numérique
        df[latest_year] = pd.to_numeric(df[latest_year], errors="coerce")

        # on enregistre les 5 etablissements avec le plus grand effectif sur la dernière année
        indicators["top_etablissement"] = df[["etablissement", latest_year]].dropna(subset=[latest_year]).sort_values(by=latest_year, ascending=False).head(5) # .dropna(subset=[latest_year]) supprime les lignes ou le nombre d'effectif est NaN 

        # pour debug - memoriser quelle année a été utilisée comme dernière année
        indicators["latest_year_used"] = latest_year

    return indicators



def compute_stats_standard_indicators(df):
    indicators = {}

    # détecter colonnes années
    year_cols = [col for col in df.columns if "nb appels" in col]

    # totaux par année
    for col in year_cols:
        indicators[col] = df[col].fillna(0).sum()

    # dernière année exploitable
    valid_year_cols = [col for col in year_cols if df[col].notna().sum() > 0]

    if valid_year_cols:
        latest_year = valid_year_cols[-1]

        indicators["latest_year"] = latest_year

        # total appels année récente
        indicators["total_appels_latest_year"] = df[latest_year].fillna(0).sum()

        # appels pour mois
        indicators["appels_par_mois"] = df[["mois", latest_year]].dropna()

    return indicators

def compute_bilan_actions_indicators(df):
    indicators = {}

    indicators["nombre_actions"] = len(df) # nb de lignes non vides = nb actions

    if "nbre etudiants touchés" in df.columns:
        indicators["total_etudiants_touches"] = (
            pd.to_numeric(df["nbre etudiants touchés"], errors="coerce").fillna(0).sum()
        )
    
    if "etablissement" in df.columns:
        etab = standardize_etablissement(df["etablissement"])
        indicators["actions_par_etablissement"] = etab.value_counts()  # un df

    if "site ua" in df.columns:
        site_ua = standardize_simple_labels(df["site ua"])
        indicators["actions_par_site_ua"] = site_ua.value_counts()  # un df

    if "lieu" in df.columns:
        lieu = standardize_simple_labels(df["lieu"])
        indicators["actions_par_lieu"] = lieu.value_counts() # un df #

    if "thème(s) abordé(s)" in df.columns:
        theme = standardize_simple_labels(df["thème(s) abordé(s)"])
        indicators["actions_par_theme"] = theme.value_counts()
    
    # colonnes quantitatives "consommables/matériel"
    excluded_cols = { # on garde que les consommables
        "numéro action",
        "date",
        "horaire",
        "etablissement",
        "site ua", 
        "lieu",
        "thème(s) abordé(s)", 
        "nbre ssu",
        "nbre ers",
        "partenaires",
        "nbre etudiants touchés",
        "evaluation qualitative",
        "perspectives",
        "images",
    }

    conso_totals = {}

    for col in df.columns:
        if col in excluded_cols: continue # on ignore tout ce qui est pas consommable

        numeric_series = pd.to_numeric(df[col], errors="coerce") # convertir toutes les vals de la colonne en entier
        if numeric_series.notna().sum() > 0: # on garde que les consommables VRAIMENT distribués
            total = numeric_series.sum()
            if total > 0:
                conso_totals[col] = total # exp = preservatifs = 1000
    # on convertit le dictionnaire en série et on trie par ordre décroissant
    conso_series = pd.Series(conso_totals).sort_values(ascending=False)
    rename_map = {
        "gel": "Gel lubrifiant",
        "skin": "Préservatifs sans latex (Skin)"
    }
    conso_series.rename(index=rename_map, inplace=True)
    indicators["consommables_totaux"] = conso_series

    return indicators
 
def compute_pssm_indicators(pssm_sheets):
    indicators = {}
    all_sheets_dfs = []

    for sheet_name, df in pssm_sheets.items():
        temp = df.copy()

        numeric_cols = [
            "etudiants ua",
            "etudiants autres",
            "personnels ua",
            "personnels autres",
            "total / session",
        ]

        for col in numeric_cols:
            if col in temp.columns:
                temp[col] = pd.to_numeric(temp[col], errors="coerce") # ajouter les colonnes numériques au df temporaire (et convertir les erreurs en NaN)
        
        # feuilles avant pssm 2025,26: colonne Dates et feuilles depuis 2026: colonne Date Début et Date Fin
        if "dates" not in temp.columns and "date début" in temp.columns: 
            temp["dates"] = temp["date début"] # on ne va garder que les dates de début

        all_sheets_dfs.append(temp)

    if not all_sheets_dfs:
        return indicators

    all_pssm = pd.concat(all_sheets_dfs, ignore_index=True)  # toutes les feuilles (dfs) concaténées

    # garder les lignes avec une vraie date/session (lignes vides)
    if "dates" in all_pssm.columns:
        all_pssm = all_pssm[all_pssm["dates"].notna()]

    indicators["nombre_sessions"] = len(all_pssm)

    #  Pour les feuilles avant pssm 2025,26:
    for col in ["etudiants ua", "etudiants autres", "personnels ua", "personnels autres"]:
        if col in all_pssm.columns:
            indicators[f"total_{col.replace(' ', '_')}"] = all_pssm[col].fillna(0).sum() # nb de personnes présentes à la session

        if "total / session" in all_pssm.columns:
            indicators["total_participants_declares"] = all_pssm["total / session"].fillna(0).sum()

        if "sheet_name" in all_pssm.columns:
            counts = all_pssm["sheet_name"].value_counts()
            indicators["sessions_annee_civile"] = counts[~counts.index.str.contains(",")] # feuilles dont le nom de la colonne ne contient pas de virgule (ex: 2025,26)
            indicators["sessions_annee_univ"] = counts[counts.index.str.contains(",")] # feuilles dont le nom de la colonne contient une virgule (ex: 2024,25)

        if "lieu" in all_pssm.columns:
            indicators["sessions_par_lieu"] = all_pssm["lieu"].fillna("non renseigné").value_counts()

    return indicators 
 

# REGLE POUR VISER CSS: motif="Centre de planification"
# Puis détail dans motif réels (d'après Mme Isabelle RISS)
def compute_css_indicators(df):
    indicators = {}

    df_css = df[df["motif"] == "Centre de planification"].copy()
    
    indicators["total_consultations_css"] =  len(df_css) # nb lignes css

    if "motif réels" in df_css.columns:
        motifs_reels = standardize_simple_labels(df_css["motif réels"])
        indicators["motifs_reels_css"] = motifs_reels.value_counts()

    if "établissement" in df_css.columns:
        etab = standardize_etablissement(df_css["établissement"])
        indicators["css_par_etablissement"] = etab.value_counts()

    if "sexe" in df_css.columns:
        sexe = standardize_simple_labels(df_css["sexe"])
        indicators["css_par_sexe"] = sexe.value_counts()

    return indicators

def extract_nom_intervenant(value):
    """Extrait le nom de famille en majuscule à partir d'un nom complet"""
    if pd.isna(value):
        return None

    text = str(value).strip()
    if text == "":
        return None
    
    return text.split()[0].upper() 

def compute_bilans_professionnels_indicators(df, medecins, infirmieres):
    indicators = {}

    # garder uniquement les BILANS DE PREVENTION
    df_bilans = df[df["motif"] == "Bilan de prévention"].copy()

    indicators["total_bilans"] = len(df_bilans) # nb lignes = nb bilans

    if "intervenant" in df_bilans.columns:
        # nettoyage léger
        df_bilans["intervenant_clean"] = standardize_simple_labels(df_bilans["intervenant"]) # ajouter une nouvelle colonne + appliquer la fonction de nettoyage
        df_bilans["nom_intervenant"] = df_bilans["intervenant_clean"].apply(extract_nom_intervenant) # ajouter une nouvelle colonne + appliquer la fonction d'extraction

        medecins_nom = [extract_nom_intervenant(x) for x in medecins]
        infirmieres_nom = [extract_nom_intervenant(x) for x in infirmieres]

        df_med = df_bilans[df_bilans["nom_intervenant"].isin(medecins_nom)]
        df_inf = df_bilans[df_bilans["nom_intervenant"].isin(infirmieres_nom)]

        indicators["bilans_medecins"] = len(df_med)
        indicators["bilans_infirmieres"] = len(df_inf)
        indicators["bilans_autres_intervenants"] = len(df_bilans) - len(df_med) - len(df_inf)
        
        # détail des intervenants inconnus
        inconnus = df_bilans[~df_bilans["nom_intervenant"].isin(medecins_nom + infirmieres_nom)]

        if len(inconnus) > 0:
            indicators["intervenants_inconnus"] = inconnus["intervenant_clean"].value_counts()
        
        # bilans internationaux chez les médecins
        if "nationalité" in df_med.columns:
            nationalites = standardize_simple_labels(df_med["nationalité"])
            indicators["bilans_internationaux_medecins"] = (nationalites.str.upper() != "FRANCE").sum()

        # répartition par centre
        if "centre" in df_bilans.columns:
            centres = standardize_simple_labels(df_bilans["centre"])
            indicators["bilans_par_centre"] = centres.value_counts()

    return indicators

def compute_psy_indicators(df):
    indicators = {}

    df.columns = [str(col).strip().lower() for col in df.columns]

    indicators["total_seances_psy"] = len(df)

    # répartition par problématique
    if "catégorie" in df.columns:
        data = df["catégorie"].dropna()
        # nettoyage texte
        data = data.astype(str).str.strip()

        indicators["repartition_problematique"] = data.value_counts()

    # répartition par sous-problématique
    if "sous-catégorie" in df.columns:
        data = df["sous-catégorie"].dropna()
        # nettoyage texte
        data = data.astype(str).str.strip()

        indicators["repartition_problematiques_detaillee"] = data.value_counts()

    # répartition consultations par composante
    if "composante" in df.columns:
        data = df["composante"].dropna()
        # nettoyage texte
        data = data.astype(str).str.strip()

        indicators["repartition_par_composante"] = data.value_counts()

    # répartition consultations par sexe
    if "sexe" in df.columns:
        data = df["sexe"].dropna()
        # nettoyage texte
        data = data.astype(str).str.strip()

        indicators["repartition_par_sexe"] = data.value_counts()

    return indicators

