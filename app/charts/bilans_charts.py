import os
import matplotlib.pyplot as plt
from app.config.colors import SSU_PALETTE


def plot_bilans_par_composante(df_bilans):
    data = df_bilans.copy() # copie du dataframe pour éviter de modifier l'original
    data = data["composante"].value_counts().sort_values(ascending=True)

    labels = data.index.astype(str)
    values = data.values

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(9, 6)) 
    bars = plt.barh(labels, values, color=SSU_PALETTE[0])

    offset = max(values) * 0.01

    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + offset, # position x
            bar.get_y() + bar.get_height() / 2, # position y
            str(int(width)), # valeur
            va="center", # alignement vertical
            fontsize=9
        )

    plt.title("Bilans de santé préventifs par composante et école", pad=20, fontweight='bold', fontsize=15)
    
    plt.gca().spines['top'].set_visible(False) # supprimer les bordures: haute et droite
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout() # éviter que les éléments du graphique se chevauchent
    plt.savefig("output/charts/bilans_par_composante.png", bbox_inches="tight", dpi=300) # bbox_inches="tight" permet d'éviter que les éléments du graphique ne soient coupés
    plt.close()


def plot_bilans_internationaux(df_bilans):
    df_bilans = df_bilans.copy() # copie du dataframe pour éviter de modifier l'original
    # Faire le tri des étudiants selon leur nationalité
    df_bilans["type_etudiant"] = df_bilans["nationalité"].apply( # ajout de la colonne type_etudiant
        lambda x: "International" if x != "FRANCE" else "France" # si la nationalité n'est pas la france, on met international, sinon france
    )

    data = df_bilans["type_etudiant"].value_counts()

    labels = data.index
    values = data.values

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(6, 6))

    def autopct_format(values):
        def inner(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return f"{val}\n({pct:.1f}%)"
        return inner

    plt.pie(
        values,
        labels=labels,
        autopct=autopct_format(values),
        colors=[SSU_PALETTE[1], SSU_PALETTE[2]]
    )

    plt.title("Bilans : étudiants internationaux vs français", pad=20, fontweight='bold', fontsize=15)
    plt.tight_layout()
    plt.savefig("output/charts/bilans_internationaux.png", bbox_inches="tight", dpi=300)
    plt.close()


def plot_bilans_par_filiere(df_bilans):
    data = df_bilans.copy() # copie du dataframe pour éviter de modifier l'original
    data = data["section"].value_counts().head(12).sort_values(ascending=True) # value_counts() retourne un dataframe avec les valeurs et leur nombre d'occurences

    labels = data.index.astype(str) 
    values = data.values

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(9, 6))
    bars = plt.barh(labels, values, color=SSU_PALETTE)

    offset = max(values) * 0.01

    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + offset, # x
            bar.get_y() + bar.get_height() / 2, # y
            str(int(width)), # valeur
            va="center", # alignement vertical
            fontsize=9
        )

    plt.title("Bilans de santé préventifs par filière", pad=20, fontweight='bold', fontsize=15)
    
    plt.gca().spines['top'].set_visible(False) # supprimer les bordures: haute et droite
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/bilans_par_filiere.png", bbox_inches="tight", dpi=300)
    plt.close()