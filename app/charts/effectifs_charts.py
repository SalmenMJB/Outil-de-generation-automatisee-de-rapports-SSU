import os
import matplotlib.pyplot as plt
import pandas as pd


def plot_evolution_effectifs(df):
    year_cols = [col for col in df.columns if "/" in col]

    if not year_cols:
        raise ValueError("Aucune colonne d'année trouvée dans le fichier effectifs.")

    totals = {}
    for col in year_cols:
        totals[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).sum()

    # retirer les années totalement vides
    totals = {year: total for year, total in totals.items() if total > 0}

    if not totals:
        raise ValueError("Aucune donnée exploitable pour les effectifs.")

    years = list(totals.keys())
    values = list(totals.values())

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.plot(years, values, marker="o")
    for x, y in zip(years, values):
        plt.text(x, y+5, str(int(y)), ha='center', va='bottom')
    plt.title("Évolution des effectifs des établissements conventionnés", pad=20, fontweight='bold', fontsize=15)
    plt.xlabel("Année universitaire")
    plt.ylabel("Nombre d'étudiants")
    plt.xticks(rotation=45)
    
    # Style premium
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/evolution_effectifs.png", bbox_inches="tight", dpi=300)
    plt.close()

