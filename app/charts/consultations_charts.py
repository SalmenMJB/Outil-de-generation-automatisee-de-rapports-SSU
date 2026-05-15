import os
import matplotlib.pyplot as plt
from app.config.colors import SSU_PALETTE


def plot_recap_consultations(activite_stats):
    motif_counts = activite_stats["top_motifs"]

    # mapping
    data = {
        "Médecine générale": motif_counts.get("Consultations médecine générale", 0),
        "Psychologie": motif_counts.get("Psychologie", 0),
        "Psychiatrie": motif_counts.get("Psychiatrie", 0),
        "Consultations IDE": motif_counts.get("Consultations IDE", 0),
        "Centre de santé sexuelle": motif_counts.get("Centre de planification", 0),
        "Autre (Diététique, Bilans)" : motif_counts.get("Diététique", 0) + motif_counts.get("Bilan de prévention",0)
    }

    # enlever les 0
    data = {k: v for k, v in data.items() if v > 0}

    labels = list(data.keys())
    values = list(data.values())

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(7, 7))

    def autopct_format(values):
        def inner(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return f"{val}"
        return inner

    if len(values) > 0:
        plt.pie(
            values,
            labels=labels,
            autopct=autopct_format(values),
            colors=SSU_PALETTE
        )

    plt.title("Répartition des consultations", pad=20, fontweight='bold', fontsize=15)
    plt.tight_layout()
    plt.savefig("output/charts/recap_consultations.png", bbox_inches="tight", dpi=300)
    plt.close()