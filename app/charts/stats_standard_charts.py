import os
import matplotlib.pyplot as plt

# Le fichier excel donné par l'SSU était endommagé et illisble
# On l'a nettoyé et gardé uniquement le tableau nécessaire


def plot_appels_par_mois(df):
    year_cols = [col for col in df.columns if "nb appels" in col]
    valid_cols = [col for col in year_cols if df[col].notna().sum() > 0]

    if not valid_cols:
        raise ValueError("Aucune colonne d'appels exploitable trouvée.")

    latest_year = valid_cols[-1]

    data = df[["mois", latest_year]].dropna()

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.plot(data["mois"], data[latest_year], marker="o")
    plt.title(f"Appels reçus par mois durant l'année", pad=20, fontweight='bold', fontsize=15)
    plt.xlabel("Mois")
    plt.ylabel("Nombre d'appels")
    plt.xticks(rotation=45)
    
    # Style premium
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/appels_par_mois.png", bbox_inches="tight", dpi=300)
    plt.close()