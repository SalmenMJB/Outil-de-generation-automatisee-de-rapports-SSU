import os
import matplotlib.pyplot as plt

from app.config.colors import SSU_PALETTE


def plot_consultations_par_centre(activite_stats):
    data = activite_stats["consultations_par_centre"]

    labels = data.index.astype(str)
    values = data.values

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(9, 5))
    bars = plt.bar(labels, values, color=SSU_PALETTE[0])

    offset = 1
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + offset,
            str(int(height)),
            ha="center",
            va="bottom",
            fontsize=9
        )

    plt.title("Consultations par centre", pad=20, fontweight='bold', fontsize=15)
    plt.xlabel("Centre")
    plt.ylabel("Nombre de consultations")
    plt.xticks(rotation=20, ha="right")
    
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/consultations_par_centre.png", bbox_inches="tight", dpi=300)
    plt.close()


def plot_top_motifs(activite_stats, activite_stats_n_1=None):
    data_current = activite_stats["top_motifs"].head(10).sort_values(ascending=True)
    labels = data_current.index.astype(str)
    values_current = data_current.values

    os.makedirs("output/charts", exist_ok=True)
    plt.figure(figsize=(9, 6))

    if activite_stats_n_1 is not None and "top_motifs" in activite_stats_n_1:
        data_n_1 = activite_stats_n_1["top_motifs"]
        values_n_1 = [data_n_1.get(label, 0) for label in labels]

        import numpy as np
        x = np.arange(len(labels))
        width = 0.35

        bars2 = plt.bar(x - width/2, values_n_1, width, label='Année précédente', color=SSU_PALETTE[4])
        bars1 = plt.bar(x + width/2, values_current, width, label='Année en cours', color=SSU_PALETTE[5])

        offset = max(max(values_current), max(values_n_1)) * 0.002 if max(max(values_current), max(values_n_1)) > 0 else 1

        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    plt.text(
                        bar.get_x() + bar.get_width() / 2,
                        height + offset,
                        str(int(height)),
                        ha="center",
                        va="bottom",
                        fontsize=9
                    )

        plt.xticks(x, labels, rotation=30, ha="right")
        plt.legend()
    else:
        bars = plt.bar(labels, values_current, color=SSU_PALETTE[0])
        offset = max(values_current) * 0.02 if len(values_current) > 0 else 1

        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height + offset,
                str(int(height)),
                ha="center",
                va="bottom",
                fontsize=9
            )
        plt.xticks(rotation=30, ha="right")

    plt.title("Répartition des motifs de consultation", pad=20, fontweight='bold', fontsize=15)
    plt.xlabel("Motif")
    plt.ylabel("Nombre de consultations")
    
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/top_motifs.png", bbox_inches="tight", dpi=300)
    plt.close()


def plot_repartition_sexe(activite_stats):
    data = activite_stats["repartition_sexe"]
    data = data[data.index.notna()]
    data = data.rename(index={"M" : "Hommes","F" : "Femmes"})

    labels = data.index.astype(str)
    values = data.values

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(7, 7))

    def autopct_format(values):
        def inner(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return f"{pct:.1f}%"
        return inner

    plt.pie(
        values,
        labels=labels,
        autopct=autopct_format(values),
        colors=[SSU_PALETTE[2], SSU_PALETTE[0]]
    )

    plt.title("Répartition par sexe", pad=20, fontweight='bold', fontsize=15)
    plt.tight_layout()
    plt.savefig("output/charts/repartition_sexe.png", bbox_inches="tight", dpi=300)
    plt.close()