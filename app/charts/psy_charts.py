import os
import pandas as pd
import matplotlib.pyplot as plt

from app.config.colors import SSU_PALETTE


def plot_delai_attente_psy(excel_path):
    df = pd.read_excel(excel_path)

    columns_names = df.columns.tolist() 
 
    mois = df.iloc[:, 0].tolist()
    valeurs = df.iloc[:, 1].tolist() # valeurs de l'année en cours
    valeurs_n1 = df.iloc[:, 2].tolist() # valeurs de l'année N-1
 
    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(9, 5))
    offset = 0.5

    # courbe de l'année en cours
    plt.plot(mois, valeurs, marker="o", color=SSU_PALETTE[0], label=columns_names[1])
    # annotation des points
    for x, y in zip(mois, valeurs):
        plt.text(x, y + offset, str(y), ha="center", fontsize=9)

    # courbe de l'année N-1
    plt.plot(mois, valeurs_n1, marker="x", linestyle="--", color=SSU_PALETTE[2], label=columns_names[2])
    # annotation des points
    for x, y in zip(mois, valeurs_n1):
        if pd.notna(y):
            plt.text(x, y - offset - 0.5, str(int(y)), ha="center", fontsize=9, color="black")

    plt.title("Évolution du délai d'attente en psychologie", pad=20, fontweight='bold', fontsize=15)
    plt.xlabel("Mois")
    plt.ylabel("Délai moyen (jours)")
    plt.xticks(rotation=30)
    plt.legend()
    
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/delai_attente_psy.png", bbox_inches="tight", dpi=300)
    plt.close()



def plot_problematique_psy(df):
    data = df["catégorie"].dropna().value_counts()

    # garder les 8 plus grandes catégories
    top_n = 8
    top_data = data.head(top_n)

    autres = data.iloc[top_n:].sum()
    if autres > 0:
        top_data["Autres"] = autres
    

    labels = top_data.index.astype(str)
    values = top_data.values

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(9, 6))

    wedges, texts, autotexts = plt.pie( # wedges: parts du graphique, texts: labels des parts, autotexts: légendes internes
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops=dict(width=0.4), # largeur du graphique
        labeldistance=1.12, # distance entre les labels et les parts
        pctdistance=0.8, # distance entre les légendes internes et les parts
        colors=SSU_PALETTE # couleurs des parts
    )

    plt.title("Motifs de consultations en psychologie", pad=20, fontweight='bold', fontsize=15)
    plt.tight_layout()
    plt.savefig("output/charts/problematique_psy.png", bbox_inches="tight", dpi=300)
    plt.close()


def plot_duree_suivi(df): # celui-ci se base sur le df stat_activite et non sur le df psy
    # filtrer uniquement les consultations psy
    df_psy = df[df["motif"] == "Psychologie"]

    # nb consultations par étudiant
    suivi = df_psy.groupby("id_etu").size() # size() : calcule le nb d'occurrences pour chaque groupe (ici pour chaque id_etu)

    # catégorisation
    bins = [1, 3, 6, 9, 13, float("inf")] # bornes 
    labels = ["1-3", "4-6", "7-9", "10-13", ">13"]

    categories = pd.cut(suivi, bins=bins, labels=labels, right=True) # divise les données en catégories selon les bornes définies

    repartition = categories.value_counts().sort_index() 

    # en %
    repartition_pct = (repartition / repartition.sum()) * 100 

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(8, 5))
    bars = plt.bar(repartition.index.astype(str),  # catégories (1-3, 4-6, etc.)
                    repartition_pct.values, # valeurs en %
                    color=SSU_PALETTE[4])

    # valeurs au-dessus
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.05,
            f"{height:.1f}%",
            ha="center"
        )

    plt.title("Durée de suivi psychologique", pad=20, fontweight='bold', fontsize=15)
    plt.xlabel("Nombre de consultations")
    plt.ylabel("Pourcentage d'étudiants")
    
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/duree_suivi.png", bbox_inches="tight", dpi=300)
    plt.close()


def plot_consultations_psy_par_composante(df): # df du fichier stat_psy
    if "composante" not in df.columns:
        return

    data = df["composante"].dropna().astype(str).str.strip().value_counts()

    # garder les 8 plus grandes composantes
    top_n = 8
    top_data = data.head(top_n)
    
    autres = data.iloc[top_n:].sum()
    if autres > 0:
        top_data["Autres"] = autres

    labels = top_data.index.tolist()
    values = top_data.values.tolist()

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(10, 6))
    bars = plt.barh(labels[::-1], values[::-1], color=SSU_PALETTE[1])

    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + (max(values)*0.01) if max(values) > 0 else width + 0.1,
            bar.get_y() + bar.get_height() / 2,
            str(int(width)),
            ha="left",
            va="center",
            fontsize=9
        )

    plt.title("Consultations psychologiques par composante", pad=20, fontweight='bold', fontsize=15)
    plt.xlabel("Nombre de consultations")
    
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/repartition_psy_composante.png", bbox_inches="tight", dpi=300)
    plt.close()

