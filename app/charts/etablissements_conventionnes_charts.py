import matplotlib.pyplot as plt
import numpy as np
from app.config.colors import SSU_PALETTE


def plot_etablissements_conventionnes(df):
    labels = df["etablissement"]
    labels = labels.replace("Institut agro Rennes Angers", "Institut Agro Rennes Angers") # demandé par le SSU

    derniere_annee = df.iloc[:, -1].name # nom de la dernière colonne
    somme = df[derniere_annee].fillna(0).sum()

    pourcentages = []
    for val in df[derniere_annee]:
        calcul = (val/somme)*100
        pourcentages.append(round(calcul,2))

    fig, ax = plt.subplots(figsize=(9, 7))
 
    couleurs = SSU_PALETTE

    wedges, _ = ax.pie( # wedges: tranches, _: on ignore les légendes de pie()
        pourcentages,
        colors=couleurs,
        startangle=85, # pour une orientation proche de la photo
        counterclock=False,
        wedgeprops=dict(edgecolor="white", linewidth=1.2) # bordure blanche entre les tranches
    )

    ax.set(aspect="equal") # pour que le camembert soit un cercle et non une ellipse

    # annotation des tranches avec leur pourcentage
    for wedge, cat, pct in zip(wedges, labels, pourcentages): 
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = np.cos(np.deg2rad(angle))
        y = np.sin(np.deg2rad(angle))

        # position du texte à l'extérieur
        label_x = 1.28 * x
        label_y = 1.28 * y

        ha = "left" if x >= 0 else "right"

        ax.annotate(
            f"{cat}\n{pct:.0f}%",
            xy=(x, y),
            xytext=(label_x, label_y),
            ha=ha,
            va="center",
            fontsize=12,
            bbox=dict(boxstyle="square,pad=0.35", fc="white", ec="#bfbfbf", lw=1), # boîte blanche autour du texte
            arrowprops=dict(arrowstyle="-", color="#9e9e9e", lw=1.2, shrinkA=0, shrinkB=0) # flèche entre la tranche et l'annotation
        )
    plt.title("Effectifs étudiants par établissement conventionné", pad=25, fontweight='bold', fontsize=15)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor("#d9d9d9")
        spine.set_linewidth(1.2)

    plt.tight_layout()


    plt.savefig("output/charts/etablissements_conventionnes.png", dpi=300, bbox_inches="tight")
    #plt.show()
