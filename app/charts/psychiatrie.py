import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from app.services.indicator_service import compute_stat_activite_indicators
import os
from app.config.colors import SSU_PALETTE


def append_current_year_psychiatrie(df, excel_path: str, current_year: str):
    """
    Extrait automatiquement la ligne de l'année en cours à partir des exports Calcium,
    puis met à jour le fichier Excel historique.
    """
    df_psychiatrie = df[df["motif"]=="Psychiatrie"]

    if os.path.exists(excel_path):
        df_historique = pd.read_excel(excel_path)
    else:
        df_historique = pd.DataFrame(columns=[
            "Année", "Nombre de consultations", "Nombre total étudiants", 
            "Nombre moyen de consultations par étudiants"
        ])
    
    somme_psychiatrie = compute_stat_activite_indicators(df)["consultations_psychiatrie"]
    etudiants_unique = df_psychiatrie["id_etu"].nunique()

    new_row = {
        "Année": current_year,
        "Nombre de consultations": somme_psychiatrie,
        "Nombre total étudiants": etudiants_unique,
        "Nombre moyen de consultations par étudiants": round(somme_psychiatrie/etudiants_unique, 2),
    }
    
    if current_year in df_historique["Année"].values:
        idx = df_historique.index[df_historique["Année"] == current_year][0]
        for key, val in new_row.items():
            df_historique.at[idx, key] = val
    else:
        df_historique = pd.concat([df_historique, pd.DataFrame([new_row])], ignore_index=True)

    df_historique.to_excel(excel_path, index=False)


def plot_evolution_psychiatrie(psychiatrie_path):
    df = pd.read_excel(psychiatrie_path)
    df = df.sort_values("Année").reset_index(drop=True)

    colonnes = {"Nombre de consultations" : (SSU_PALETTE[0], "-"),
                "Nombre total étudiants" : (SSU_PALETTE[1], "--"),
                "Nombre moyen de consultations par étudiants" : (SSU_PALETTE[2], "-.")}

    fig, ax = plt.subplots(figsize=(9, 5))

    for col, (color, linestyle) in colonnes.items():
        base = df[col].iloc[0]
        index = (df[col] / base) * 100
        ax.plot(df["Année"], index, label=col, color=color,
                linestyle=linestyle, linewidth=2, marker="o", markersize=5)

    ax.axhline(100, color="gray", linestyle=":", linewidth=1, alpha=0.6)
    ax.set_ylabel("Indice (base 100 = première année)", fontsize=10)
    ax.set_title("Évolution des indicateurs psychiatrie (base 100)", pad=20, fontweight='bold', fontsize=15)
    ax.tick_params(axis="x", rotation=45, labelsize=9)
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig("output/charts/evolution_psychiatrie.png", dpi=300, bbox_inches="tight")
    plt.close()