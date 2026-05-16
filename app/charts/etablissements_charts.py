import matplotlib.pyplot as plt
import pandas as pd
from app.config.colors import SSU_PALETTE


def plot_top_etablissements(df):
    # detecter colonnes années
    year_cols = [col for col in df.columns if "/" in col]

    # garder celles qui ont des données
    valid_year_cols = [ 
        col for col in year_cols
        if pd.to_numeric(df[col], errors="coerce").notna().sum() > 0
    ]

    latest_year = valid_year_cols[-1]

    # préparer données
    temp = df[["etablissement", latest_year]].copy() # prendre une copie du dataframe avec seulement les colonnes "etablissement" et l'année la plus récente
    temp[latest_year] = pd.to_numeric(temp[latest_year], errors="coerce")
    temp = temp.dropna(subset=[latest_year])

    # top 10
    temp = temp.sort_values(by=latest_year, ascending=False).head(10)
    
    plt.figure(figsize=(9, 6))
    
    def autopct_format(values): # formatage des pourcentages
        def inner(pct): # appelée pour chaque tranche du camembert
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return f"{val}\n({pct:.1f}%)"
        return inner
        
    plt.pie(
        temp[latest_year], # valeurs
        labels=temp["etablissement"].astype(str), # labels
        autopct=autopct_format(temp[latest_year]), # formatage
        colors=SSU_PALETTE[:len(temp)]
    )

    plt.title(f"Top établissements ({latest_year})", pad=20, fontweight='bold', fontsize=15)
    plt.tight_layout()
    plt.savefig("output/charts/top_etablissements.png", bbox_inches="tight", dpi=300)
    plt.close() 