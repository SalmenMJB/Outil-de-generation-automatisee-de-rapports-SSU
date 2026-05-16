import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from app.config.colors import SSU_PALETTE


def plot_repartition_activite_infirmiere(df: pd.DataFrame):
    df_filtered = df[df['catégorie'].isin(['Actes infirmiers', 'suivi dossier INFIRMIER'])].copy()

    mapping = { # Ce mapping nous a été demandé par le SSU pour regrouper ainsi les données:
        'Electrocardiogramme': 'Exploration diagnostique',
        'Audiogramme': 'Exploration diagnostique',
        'Visiotest': 'Exploration diagnostique',   
        'Bandelette Urinaire': 'Exploration diagnostique',
        'ECBU': 'Exploration diagnostique',
        'Test Grossesse': 'Exploration diagnostique', 
        'Test de grosswesse (flo)': 'Exploration diagnostique',
        'Test antigénique': 'Exploration diagnostique',
        'Prélèvements urinaire et sanguin IST': 'Exploration diagnostique',
        'Prélèvement sanguin': 'Exploration diagnostique',
        'Tension Arterielle': 'Exploration diagnostique',

        'Pansement/ Strapping': 'Soin',
        "Lavage d'oreilles": 'Soin',
        'Ablation fils': 'Soin',
        'Autres': 'Soin',

        'suivi dossier INFIRMIER': 'Suivi dossier infirmier',
        'Vaccination/ injection': 'Vaccination',
    }

    # ajouter une colonne avec les sous catégories regroupées et met 'Actes infirmiers' pour les autres
    df_filtered['Grouped_Category'] = df_filtered['sous-catégorie'].str.strip().map(mapping).fillna('Actes infirmiers') # .map: applique la fonction de mapping à chaque élément de la colonne 
    df_filtered.loc[df_filtered['catégorie']=='suivi dossier infirmier', 'Grouped_Category'] = 'Suivi dossier infirmier' # ajoute une ligne avec la catégorie 'Suivi dossier infirmier'
    
    category_counts = df_filtered['Grouped_Category'].value_counts()

    labels = category_counts.index.astype(str)
    values = category_counts.values

    plt.figure(figsize=(9, 6))

    plt.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=SSU_PALETTE[:len(values)]
    )

    plt.title("Répartition de l'activité infirmière", pad=20, fontweight='bold', fontsize=15)
    plt.tight_layout()
    plt.savefig("output/charts/repartition_activite_infirmiere.png", bbox_inches="tight", dpi=300)
    plt.close()


def plot_activite_infirmiere_compare(excel_path):
    df = pd.read_excel(excel_path)

    column_names = df.columns.tolist() 

    categories = df.iloc[:, 0]
    values_1 = df.iloc[:, 1]
    values_2 = df.iloc[:, 2]

    x = np.arange(len(categories)) # liste des positions des barres sur l'axe des abscisses
    width = 0.35 # la largeur des barres

    plt.figure(figsize=(9, 5))

    bars1 = plt.bar(x - width/2, values_1, width, label=column_names[1], color=SSU_PALETTE[0])
    bars2 = plt.bar(x + width/2, values_2, width, label=column_names[2], color=SSU_PALETTE[1])

    # valeurs au-dessus
    offset = max(max(values_1), max(values_2)) * 0.00002

    for bars in [bars1, bars2]: 
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height + offset,
                str(int(height)),
                ha="center",
                va="bottom",
                fontsize=8
            )

    plt.xticks(x, categories, rotation=30, ha="right")
    plt.title("Comparaison de l'activité infirmière", pad=20, fontweight='bold', fontsize=15)
    plt.ylabel("Nombre d'actes")
    plt.legend()
    

    plt.gca().spines['top'].set_visible(False) # enleve le trait en haut et à droite
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/activite_infirmiere_compare.png", bbox_inches="tight", dpi=300)
    plt.close()


# def plot_repartition_activite_depuis_reel(df):
#     motifs = df["motif réels"].dropna()

#     categories = {
#         "Entretien / écoute": motifs.str.contains("Entretien|Première écoute", case=False).sum(),
#         "Suivi psy": motifs.str.contains("Suivi santé mentale", case=False).sum(),
#         "Bilans": motifs.str.contains("Bilan", case=False).sum(),
#         "Aménagement": motifs.str.contains("Aménagement", case=False).sum(),
#         "Gynéco / sexualité": motifs.str.contains("gynéco|contraception|IST", case=False).sum(),
#         "Nutrition": motifs.str.contains("nutrition", case=False).sum(),
#         "Autres": len(motifs)
#     }

#     # corriger "Autres"
#     categories["Autres"] = len(motifs) - sum(v for k, v in categories.items() if k != "Autres")

#     labels = list(categories.keys())
#     values = list(categories.values())

#     plt.figure(figsize=(7, 7))

#     def autopct(pct): 
#         total = sum(values)
#         val = int(round(pct * total / 100))
#         return f"{pct:.1f}%"

#     plt.pie(values, labels=labels, autopct=autopct, colors=SSU_PALETTE[:len(values)])
#     plt.title("Répartition des motifs de consultation IDE", pad=20, fontweight='bold', fontsize=15)
#     plt.tight_layout()
#     plt.savefig("output/charts/repartition_activite_reelle_IDE.png", bbox_inches="tight", dpi=300)
#     plt.close()