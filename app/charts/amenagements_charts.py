import pandas as pd
import matplotlib.pyplot as plt
import os
from app.config.colors import SSU_PALETTE

def plot_evolution_amenagements(path_excel):
    data = pd.read_excel(path_excel).tail(10)


    years = data["Année"]  # colonne des années
    values = data["Total"] # colonne des nombres d'aménagements

    plt.figure(figsize=(9, 5))
    plt.plot(years, values, marker="o", color=SSU_PALETTE[0])

    offset = max(values) * 0.01

    for x, y in zip(years, values): # zip: combine les années avec les nombres d'aménagements (comme un dictionnaire)
        plt.text(x, y + offset, str(y), ha="center", va="bottom", fontsize=9)

    plt.title("Étudiants disposant d'aménagements (examen et/ou études)", pad=20, fontweight='bold')
    plt.xlabel("Année universitaire")
    plt.ylabel("Nombre d'étudiants")
    plt.xticks(rotation=45, ha="right")
    
    # Style premium
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/evolution_amenagements.png", bbox_inches="tight", dpi=300)
    plt.close()


def plot_reparition_amenagements(df):
    motif_regex = r'.*Aménagement ESH.*'
    compte_par_etablissement = (df[df["motif réels"].str.contains(motif_regex,case=False, na=False)].groupby("établissement").size().reset_index(name="Nombre amenagements"))
    
    
    compte_par_etablissement["établissement"] = compte_par_etablissement["établissement"].replace({
        "Université d\'Angers" : "UA",
        "Lycée de Pouillé" : "Campus de Pouillé"})

    compte_par_etablissement = compte_par_etablissement.sort_values(by="Nombre amenagements", ascending=False)
    
    plt.figure(figsize=(9, 5))
    bars = plt.bar(compte_par_etablissement["établissement"],
        compte_par_etablissement["Nombre amenagements"],
        color=SSU_PALETTE[1])

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.,
            height,
            f'{int(height)}',
            ha='center',
            va='bottom')

    plt.title("Nombre d'aménagements ESH par établissement", pad=20, fontweight='bold')
    plt.xlabel("Établissement")
    plt.ylabel("Nombre d'aménagements")
    plt.xticks(rotation=45, ha='right')
    
    # Style premium
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/repartition_amenagements.png", dpi=300, bbox_inches="tight")
    plt.close()


def append_current_year_amenagements(df_activite, historical_path, current_year):
    """
    Automate l'extraction du nombre d'aménagements ESH pour l'année en cours
    et met à jour le fichier historique.
    """
    motif_regex = r"aménagement esh \+ certificat init[i]*al"
    
    # On compte le nombre total d'aménagements accordés (on garde les doublons)
    count = df_activite[df_activite["motif réels"].str.contains(motif_regex, case=False, na=False)]["id_etu"].nunique()   
    
    if os.path.exists(historical_path):
        data = pd.read_excel(historical_path)
    else:
        data = pd.DataFrame(columns=["Année", "Total"])
    
    # Vérifier si l'année est déjà présente
    if current_year in data["Année"].values:
        data.loc[data["Année"] == current_year, "Total"] = count
    else:
        new_row = pd.DataFrame([{"Année": current_year, "Total": count}])
        data = pd.concat([data, new_row], ignore_index=True)
    
    data.to_excel(historical_path, index=False)
    print(f"Historique des aménagements mis à jour pour {current_year} : {count} étudiants.")
    