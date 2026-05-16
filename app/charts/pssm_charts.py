import matplotlib.pyplot as plt
import pandas as pd
import re
from app.config.colors import SSU_PALETTE


def plot_pssm_sessions(indicators):
    data_civile = indicators.get("sessions_annee_civile", pd.Series()) # pd.Series() permet de ne pas avoir d'erreur si les données ne sont pas trouvées
    data_univ = indicators.get("sessions_annee_univ", pd.Series())

    def extract_year(name): # fonction qui permet d'extraire l'année de la colonne (ex: 2025/2026 -> 2025)
        match = re.search(r'\d{4}', str(name)) # permet d'extraire l'année de la colonne
        return int(match.group()) if match else 0 

    if not data_civile.empty:
        data_civile = data_civile.loc[sorted(data_civile.index, key=extract_year)].tail(4) # trier par année et garder les 4 dernières
        
    if not data_univ.empty:
        data_univ = data_univ.loc[sorted(data_univ.index, key=extract_year)].tail(4) # trier par année et garder les 4 dernières

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5)) # création de deux sous-graphiques

    # Sous-graphique 1 : Années civiles
    if not data_civile.empty:
        labels_civile = data_civile.index.astype(str)
        values_civile = data_civile.values
        bars1 = ax1.bar(labels_civile, values_civile, color=SSU_PALETTE[2])
        
        for bar in bars1:
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                str(int(height)),
                ha='center',
                va='bottom'
            )
        ax1.set_title("Sessions PSSM par année civile", pad=15, fontweight='bold', fontsize=15)
        ax1.set_xlabel("Année civile")
        ax1.set_ylabel("Nombre de sessions")
        ax1.tick_params(axis='x', rotation=45) 
        ax1.spines['top'].set_visible(False) # cache le cadre supérieur et droit
        ax1.spines['right'].set_visible(False)

    # Sous-graphique 2 : Années universitaires
    if not data_univ.empty:
        labels_univ = data_univ.index.astype(str)
        values_univ = data_univ.values
        bars2 = ax2.bar(labels_univ, values_univ, color=SSU_PALETTE[0])
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                str(int(height)),
                ha='center',
                va='bottom'
            )
        ax2.set_title("Sessions PSSM par année universitaire", pad=15, fontweight='bold', fontsize=15)
        ax2.set_xlabel("Année universitaire")
        ax2.set_ylabel("Nombre de sessions")
        ax2.tick_params(axis='x', rotation=45)
        ax2.spines['top'].set_visible(False) # cache le cadre supérieur et droit
        ax2.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig("output/charts/pssm_sessions.png", bbox_inches="tight", dpi=300)
    plt.close()


def plot_pssm_lastest_year(dfs):
    data = dfs[list(dfs.keys())[-1]] # permet de prendre les données de la dernière année
    pssm_etab = data["etab"].value_counts()
    
    rename_map = {
        "Personnels" : "Personnels Université d'Angers",
        "UA" : "Étudiants Université d'Angers",
        "Institut agro" : "Institut Agro Rennes Angers"
    }
    pssm_etab.index = pssm_etab.index.map(lambda x: rename_map.get(x, x)) # permet de renommer les catégories, si x n'est pas dans rename_map, on garde x
    labels = pssm_etab.index.astype(str)
    values = pssm_etab.values

    plt.figure(figsize=(7, 6))


    plt.pie(
        values,
        labels=labels,
        startangle=90,
        autopct='%.1f%%',
        colors=SSU_PALETTE[:len(values)]
    )

    plt.title("Établissement d'origine des stagiaires", pad=20, fontweight='bold', fontsize=15)
    plt.tight_layout()
    plt.savefig("output/charts/pssm_origine_stagiaires.png", bbox_inches="tight", dpi=300)
    plt.close()