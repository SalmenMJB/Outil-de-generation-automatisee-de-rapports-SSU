import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from app.config.colors import SSU_PALETTE
# from app.config.intervenants import MEDECINS


def append_current_year_activite_medicale(df, excel_path: str, current_year: str):
    """
    Extrait automatiquement la ligne de l'année en cours à partir des exports Calcium,
    puis met à jour le fichier Excel historique_activite_medicale.xlsx.
    """
    df_motifs = df[df["motif"]=="Consultations médecine générale"] # le df avec les motifs généraux
    df_prevention = df[df["motif"]=="Bilan de prévention"]
    regex_prevention = r'(BAZIN|CHEVÉ|HARTHEISER|ROQUELAURE-CUCHET|ROSSIGNOL|ROUSSEAU|SALOMON DE ST SERNIN|TESSON).*' # noms des médecins
    df_prevention = df_prevention[df_prevention["intervenant"].str.contains(regex_prevention,na=False)] # ne garder que le df avec les bilans faits par les médecins

    # Aménagements
    amenagement_regex = r'(?i).*aménagement.*|.*amenagement.*'
    nb_amenagements = df_motifs[df_motifs["motif réels"].str.contains(amenagement_regex,na=False)].shape[0]

    # Bilan de santé
    bilan_regex = r'(?i).*bilan de santé.*|.*bilan de sante.*'
    nb_bilan = df_motifs[df_motifs["motif réels"].str.contains(bilan_regex,na=False)].shape[0] + df_prevention.shape[0]

    # Santé mentale
    sante_mentale_regex = r'(?i)(.*(première écoute|suivi santé mentale).*)'
    nb_sante_mentale = df_motifs[df_motifs["motif réels"].str.contains(sante_mentale_regex,na=False)].shape[0]

    # Médecine générale
    medecine_generale_regex = r'(?i)(?:(?:^|;)(consultation)(?:;|$))|.*?(médecine générale|autre|urgence).*?' # consultation, médecine générale, autre, urgence
    nb_medecine_generale = df_motifs[df_motifs["motif réels"].str.contains(medecine_generale_regex,na=False)].shape[0]

    # Total médical
    # Calcul demandé : Le "total médecine" correspond au total de toutes les consultations 
    # de médecine générale (soit le nombre de lignes avec ce grand motif principal).
    nb_total_medical = df_motifs.shape[0]

    # vérifier si l'excel existe, sinon le créer
    if os.path.exists(excel_path):
        df_historique = pd.read_excel(excel_path)
    else:
        df_historique = pd.DataFrame(columns=[
            "annee", "total_medical", "medecine_generale", 
            "sante_mentale", "bilans_preventifs", "amenagements"
        ])
    
    new_row = {
        "annee": current_year,
        "total_medical": nb_total_medical,
        "medecine_generale": nb_medecine_generale,
        "sante_mentale": nb_sante_mentale,
        "bilans_preventifs": nb_bilan,
        "amenagements": nb_amenagements
    }
    
    if current_year in df_historique["annee"].values: # si l'année existe, on met à jour les valeurs
        idx = df_historique.index[df_historique["annee"] == current_year][0] # l'index de la ligne qui correspond à l'année
        for key, val in new_row.items():
            df_historique.at[idx, key] = val
    else:
        df_historique = pd.concat([df_historique, pd.DataFrame([new_row])], ignore_index=True) # sinon on ajoute une nouvelle ligne

    df_historique.to_excel(excel_path, index=False)


def plot_evolution_activite_medicale(excel_path: str):
    df = pd.read_excel(excel_path).tail(5)

    years = df["annee"]
    os.makedirs("output/charts", exist_ok=True)

    # ---- Graphique : activités détaillées ----
    plt.figure(figsize=(10, 6))

    rename_map = {
        "sante_mentale": "Santé mentale",
        "bilans_preventifs": "Bilans préventifs",
        "amenagements": "Aménagements"
    }

    i=1
    for col, label in rename_map.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            plt.plot(years, df[col], marker="o", label=label, color=SSU_PALETTE[i])
            i+=1

            # offset = df[col].max() * 0.02 if df[col].notna().any() else 1
            # for x, y in zip(years, df[col]):
            #     if pd.notna(y):
            #         plt.text(x, y + offset, str(int(y)), ha="center", va="bottom", fontsize=8)

    plt.title("Évolution détaillée des activités médicales", pad=20, fontweight='bold')
    plt.xlabel("Année universitaire")
    plt.ylabel("Nombre d'actes / consultations")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    
    # Style premium
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/evolution_activite_medicale_detail.png", bbox_inches="tight", dpi=300)
    plt.close()


def plot_repartition_activite_medicale_annee(excel_path: str):
    df = pd.read_excel(excel_path)

    if df.empty:
        raise ValueError("Le fichier Excel est vide.")

    latest = df.iloc[-1] # la dernière ligne (année)

    data = {
        "Médecine générale": pd.to_numeric(pd.Series([latest["medecine_generale"]]), errors="coerce").iloc[0],
        "Santé mentale": pd.to_numeric(pd.Series([latest["sante_mentale"]]), errors="coerce").iloc[0],
        "Bilans préventifs": pd.to_numeric(pd.Series([latest["bilans_preventifs"]]), errors="coerce").iloc[0],
        "Aménagements": pd.to_numeric(pd.Series([latest["amenagements"]]), errors="coerce").iloc[0],
    }

    data = {k: v for k, v in data.items() if pd.notna(v)} # creer un dictionnaire qui prend en compte les valeurs non nulles

    labels = list(data.keys())
    values = list(data.values())

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(9, 4))
    bars = plt.bar(labels, values, color=SSU_PALETTE)

    offset = max(values) * 0.002 if values else 1
    for bar in bars:
        height = bar.get_height()
        plt.text( # affiche les valeurs au dessus de chaque barre (centrés)
            bar.get_x() + bar.get_width() / 2,
            height + offset,
            str(int(height)),
            ha="center",
            va="bottom",
            fontsize=9
        )

    plt.title(f"Répartition de l'activité médicale ({latest['annee']})", fontweight='bold', pad=0)
    plt.xlabel("Type d'activité")
    plt.ylabel("Nombre d'actes / consultations")
    plt.xticks(rotation=30, ha="right")
    
    # Style premium
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/repartition_activite_medicale.png", bbox_inches="tight", dpi=300)
    plt.close()

def plot_motifs_medecine_generale_charts(df):
    df_motifs = df[df["motif"]=="Consultations médecine générale"]
    df_prevention = df[df["motif"]=="Bilan de prévention"]
    regex_prevention = r'(BAZIN|CHEVÉ|HARTHEISER|ROQUELAURE-CUCHET|ROSSIGNOL|ROUSSEAU|SALOMON DE ST SERNIN|TESSON).*' # noms des medecins
    df_prevention = df_prevention[df_prevention["intervenant"].str.contains(regex_prevention,na=False)]

    ### Aménagements ###
    amenagement_regex = r'(?i).*aménagement.*'
    df_amenagements = df_motifs[df_motifs["motif réels"].str.contains(amenagement_regex,na=False)]
    nb_amenagements = df_amenagements.shape[0]
    df_amenagements_total = pd.DataFrame({"motif réels" : ["Aménagement d'études supérieures"], "Nombre par motif" : [nb_amenagements]}) # créer dataframe avec les données amenagements
    
    ### Bilan de santé ###
    bilan_regex = r'(?i).*bilan de santé.*'
    df_bilan = df_motifs[df_motifs["motif réels"].str.contains(bilan_regex,na=False)]
    nb_bilan = df_bilan.shape[0] + df_prevention.shape[0]
    df_bilan_total = pd.DataFrame({"motif réels" : ["Bilan de santé préventifs"], "Nombre par motif" : [nb_bilan]}) # créer dataframe avec les données bilan de santé

    ### Santé mentale ###
    sante_mentale_regex = r'(?i)(.*(première écoute|suivi santé mentale).*)'
    df_sante_mentale = df_motifs[df_motifs["motif réels"].str.contains(sante_mentale_regex,na=False)]
    nb_sante_mentale = df_sante_mentale.shape[0]
    df_sante_mentale_total = pd.DataFrame({"motif réels" : ["Santé mentale"], "Nombre par motif" : [nb_sante_mentale]}) # créer dataframe avec les données santé mentale

    ### Médecine générale ###
    medecine_generale_regex = r'(?i)(?:(?:^|;)(consultation)(?:;|$))|.*?(médecine générale|autre|urgence).*?'
    df_medecine_generale = df_motifs[df_motifs["motif réels"].str.contains(medecine_generale_regex,na=False)]
    nb_medecine_generale = df_medecine_generale.shape[0]
    df_medecine_generale_total = pd.DataFrame({"motif réels" : ["Médecine générale"], "Nombre par motif" : [nb_medecine_generale]}) # créer dataframe avec les données médecine générale

    df_total = pd.concat([df_amenagements_total,df_bilan_total,df_sante_mentale_total,df_medecine_generale_total],ignore_index=True) # concataine les 4 dataframe en 1 seul (2 colonnes)

    # Sinon:
    # df_total = pd.DataFrame({
    #     "motif réels": [
    #         "Aménagement d'études supérieures",
    #         "Bilan de santé préventifs",
    #         "Santé mentale",
    #         "Médecine générale"
    #     ],
    #     "Nombre par motif": [
    #         df_motifs[df_motifs["motif réels"].str.contains(r'(?i).*aménagement.*', na=False)].shape[0],
    #         df_motifs[df_motifs["motif réels"].str.contains(r'(?i).*bilan de santé.*', na=False)].shape[0] + df_prevention.shape[0],
    #         df_motifs[df_motifs["motif réels"].str.contains(r'(?i)(.*(première écoute|suivi santé mentale).*)', na=False)].shape[0],
    #         df_motifs[df_motifs["motif réels"].str.contains(r'(?i)(?:(?:^|;)(consultation)(?:;|$))|.*?(médecine générale|autre|urgence).*?', na=False)].shape[0]
    #     ]
    # })
    
    somme = df_total["Nombre par motif"].sum() # total pour le calcul du pourcentage
    pourcentages = (df_total["Nombre par motif"] / somme * 100).round(2).tolist()

    plt.figure(figsize=(9, 6))
    couleurs = [
        SSU_PALETTE[0],
        SSU_PALETTE[1],
        SSU_PALETTE[2],
        SSU_PALETTE[3],
    ]
    
    wedges, _ = plt.pie( # wedges = tranches du camembert, _ = labels(on les met pas car on les mettra nous-mêmes)
        pourcentages,
        colors=couleurs,
        startangle=85, # commence à 85° (en haut à droite)
        counterclock=False, # sens horaire
        wedgeprops=dict(edgecolor="white", linewidth=1.2) # contours blancs entre les tranches
    )

    plt.gca().set(aspect="equal") # rend le camembert circulaire

    for wedge, cat, val in zip(wedges, df_total["motif réels"], df_total["Nombre par motif"]): # pour afficher les données du graphique
        angle = (wedge.theta2 + wedge.theta1) / 2 # angle de la tranche
        x = np.cos(np.deg2rad(angle)) # position x de la tranche
        y = np.sin(np.deg2rad(angle)) # position y de la tranche

        # position du texte à l'extérieur
        label_x = 1.28 * x
        label_y = 1.28 * y

        ha = "left" if x >= 0 else "right"

        plt.gca().annotate(
            f"{cat}\n{val}",
            xy=(x, y),
            xytext=(label_x, label_y),
            ha=ha,
            va="center",
            fontsize=12,
            bbox=dict(boxstyle="square,pad=0.35", fc="white", ec="#bfbfbf", lw=1),
            arrowprops=dict(arrowstyle="-", color="#9e9e9e", lw=1.2, shrinkA=0, shrinkB=0)
        )

    for spine in plt.gca().spines.values():
        spine.set_visible(True)
        spine.set_edgecolor("#d9d9d9")
        spine.set_linewidth(1)

    plt.title("Répartition des motifs de consultation en médecine générale", pad=25, fontweight='bold')
    plt.tight_layout()


    plt.savefig("output/charts/motifs_medecine_generale.png", dpi=300, bbox_inches="tight")
