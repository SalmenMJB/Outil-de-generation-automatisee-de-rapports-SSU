import matplotlib.pyplot as plt
import numpy as np
from app.config.colors import SSU_PALETTE


def plot_motifs_consultation_dietetique(data):
    df = data[data["motif"]=="Diététique"]
    motifs = df["motif réels"].value_counts()
    labels = motifs.index.astype(str)
    values = motifs.values
    somme = values.sum()
    pourcentages = []
    for val in values:
        calcul = (val/somme)*100
        pourcentages.append(round(calcul,2))
    
    fig, ax = plt.subplots(figsize=(9, 6))

    couleurs = SSU_PALETTE
    
    wedges, _ = ax.pie(
        pourcentages,
        colors=couleurs,
        startangle=85,
        counterclock=False,
        wedgeprops=dict(edgecolor="white", linewidth=1.2)
    )

    ax.set(aspect="equal")

    for wedge, pct in zip(wedges, pourcentages):
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
            bbox=dict(boxstyle="square,pad=0.35", fc="white", ec="#bfbfbf", lw=1),
            arrowprops=dict(arrowstyle="-", color="#9e9e9e", lw=1.2, shrinkA=0, shrinkB=0)
        )

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor("#d9d9d9")
        spine.set_linewidth(1)

    plt.title("Motifs de consultation en diététique", pad=30, fontweight='bold', fontsize=15)
    plt.tight_layout()


    plt.savefig("output/charts/motifs_consultation_dietetique.png", dpi=300, bbox_inches="tight")
