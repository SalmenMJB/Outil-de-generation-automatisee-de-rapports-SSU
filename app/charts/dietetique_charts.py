import matplotlib.pyplot as plt
import numpy as np
from app.config.colors import SSU_PALETTE


def plot_motifs_consultation_dietetique(data): # data = stat_activite
    df = data[data["motif"]=="Diététique"]
    motifs = df["motif réels"].value_counts()

    labels = motifs.index.astype(str)
    values = motifs.values

    somme = values.sum()
    pourcentages = []
    for val in values: # calcul des pourcentages
        calcul = (val/somme)*100
        pourcentages.append(round(calcul,2)) 
    
    fig, ax = plt.subplots(figsize=(9, 6)) # subplots: crée une figure et un ensemble d'axes
    couleurs = SSU_PALETTE

    wedges, _ = ax.pie( # wedges, _ : les parts du camembert et le reste
        pourcentages,
        colors=couleurs,
        startangle=85,  # le premier pourcentage commence à 85 degrées
        counterclock=False, # sens horaire
        wedgeprops=dict(edgecolor="white", linewidth=1.2)
    )

    ax.set(aspect="equal") # rend le camembert circulaire

    # boucle pour ajouter les pourcentages sur chaque part
    for wedge, pct in zip(wedges, pourcentages): # zip: fait des duos (wedge, pct) 
        angle = (wedge.theta2 + wedge.theta1) / 2 
        x = 0.7 * np.cos(np.deg2rad(angle)) 
        y = 0.7 * np.sin(np.deg2rad(angle))
        ax.text(
            x, y,
            f"{pct:.0f}%", 
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="black"
        )
    
    # boucle pour ajouter les légendes
    for wedge, cat in zip(wedges, labels): 
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = np.cos(np.deg2rad(angle))
        y = np.sin(np.deg2rad(angle))
        # position du texte à l'extérieur
        label_x = 1.28 * x
        label_y = 1.28 * y

        ha = "left" if x >= 0 else "right"

        ax.annotate( 
            cat,
            xy=(x, y),
            xytext=(label_x, label_y),
            ha=ha,
            va="center",
            fontsize=12,
            bbox=dict(boxstyle="square,pad=0.35", fc="white", ec="#bfbfbf", lw=1), # la boite qui entoure le texte
            arrowprops=dict(arrowstyle="-", color="#9e9e9e", lw=1.2, shrinkA=0, shrinkB=0) # la fleche qui relie le texte au graphique
        )
 
    # on supprime les bordures du graphique
    for spine in ax.spines.values(): 
        spine.set_visible(False)

    plt.title("Motifs de consultation en diététique", pad=30, fontweight='bold', fontsize=15)
    plt.tight_layout()


    plt.savefig("output/charts/motifs_consultation_dietetique.png", dpi=300, bbox_inches="tight")
