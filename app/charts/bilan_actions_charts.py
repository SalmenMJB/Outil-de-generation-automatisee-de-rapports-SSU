import os
import matplotlib.pyplot as plt
import pandas as pd

from app.config.colors import SSU_PALETTE


def plot_actions_par_theme(indicators: dict):
    data = indicators["actions_par_theme"].head(10) # on garde que les 10 1ers pour un graphique lisible
    data = data.sort_values(ascending=True)

    labels = data.index.astype(str) # convertir en string les étiquettes de l'index
    values = data.values # renvoie un np array

    os.makedirs("output/charts", exist_ok=True) # créer le dossier s'il n'existe pas

    plt.figure(figsize=(9, 5))
    bars = plt.barh(labels, values, color=SSU_PALETTE[0]) # barh: barres horizontales
    
    offset = max(values)*0.01 if len(values) > 0 else 0
    for bar in bars:
        width = bar.get_width()
        plt.text(width + offset, bar.get_y() + bar.get_height() / 2, str(int(width)), va="center")

    plt.title("Actions de prévention par thème", pad=20, fontweight='bold', fontsize=15)
    plt.xlabel("Nombre d'actions")
    
    plt.gca().spines['top'].set_visible(False) # enlever les bordures du graphique
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/actions_par_theme.png", bbox_inches="tight", dpi=300)
    plt.close()

    
def plot_consommables_bilan_actions(indicators: dict):
    data = indicators["consommables_totaux"].head(12)

    labels = data.index.astype(str)  # convertir en string les étiquettes de l'index
    values = data.values

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(9, 5))
    bars = plt.bar(labels, values, color=SSU_PALETTE[1])

    offset = max(values)*0.002 if len(values) > 0 else 1
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + offset,
            str(int(height)),
            ha="center", # horizontal alignment
            va="bottom", #vertical alignment
            fontsize=8
        )

    plt.title("Consommables distribués", pad=20, fontweight='bold', fontsize=15)
    plt.xlabel("Quantité")
    plt.xticks(rotation=35, ha="right")
    

    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/consommables_bilans_actions.png", bbox_inches="tight", dpi=300)
    plt.close()


def plot_actions_par_site_lisible(df_actions):
    df = df_actions.copy()

    def recategoriser(row): # on regroupe les sites de l'UA pour avoir un graphique plus lisible
        etab = str(row["etablissement"]).lower().strip()
        if etab == "ua" or "universit" in etab: # Si l'établissement est l'UA
            site = str(row["site ua"]).strip()
            site_lower = site.lower()
            # if site_lower == "nan" or not site:
            #     return "UA - Site non précisé" #None si on veut pas garder les sites non précisés
            if "saumur" in site_lower:
                return "UA - Saumur"
            elif "cholet" in site_lower:
                return "UA - Cholet"
            else:
                return "UA - Angers"
        else:
            return "Établissements conventionnés"

            
    df["categorie_groupee"] = df.apply(recategoriser, axis=1)  # ajoute une colone + applique la fonction à chaque ligne
    
    data = df["categorie_groupee"].value_counts()
    
    # Tri croissant pour barres horizontales lisibles
    data = data.sort_values(ascending=True)

    labels = data.index.astype(str) 
    values = data.values
    
    plt.figure(figsize=(9, 5))

    colors = [SSU_PALETTE[2] if "conventionnés" in str(label) else SSU_PALETTE[0] for label in labels] # colorier différemment conventionné vs UA
    
    bars = plt.barh(labels, values, color=colors)

    offset = max(values) * 0.01 if len(values) > 0 else 1

    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + offset, 
            bar.get_y() + bar.get_height() / 2,
            str(int(width)),
            va="center"
        )
    
    plt.title("Actions par établissement et site universitaire", pad=20, fontweight='bold', fontsize=15)
    plt.xlabel("Nombre d'actions")
    
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/actions_par_site_lisible.png", bbox_inches="tight", dpi=300)
    plt.close()


def plot_actions_par_origine(df_actions):
    """
    Nouveau graphique demandé par l'SSU pour voir l'origine des étudiants.
    Combine etablissement et site ua si c'est l'UA.
    """
    df = df_actions.copy()

    def get_origine(row):
        etab = str(row["etablissement"]).strip()
        site = str(row["site ua"]).strip()
        
        if str(etab).lower() in ["ua", "université d'angers", "universite angers", "universite d'angers"]:
            if not site or site.lower() == "nan":
                return "UA - Non précisé"
            return f"UA - {site}"
        
        if not etab or etab.lower() == "nan": # si pas d'etablissement ou "nan"
            return "Non renseigné"
            
        return etab

    df["origine_etudiant"] = df.apply(get_origine, axis=1) # ajoute une colone + applique la fonction à chaque ligne
    data = df["origine_etudiant"].value_counts().head(15) # Top 15 pour la lisibilité

    labels = data.index.astype(str)
    values = data.values

    data = data.sort_values(ascending=True)
    labels = data.index.astype(str)
    values = data.values

    plt.figure(figsize=(10, 7))
    bars = plt.barh(labels, values, color=SSU_PALETTE[0])

    offset = max(values) * 0.01 if len(values) > 0 else 1
    for bar in bars:
        width = bar.get_width()
        plt.text(width + offset, bar.get_y() + bar.get_height()/2, str(int(width)), va="center", fontsize=9)

    plt.title("Origine des étudiants (Actions de prévention)", pad=20, fontweight='bold', fontsize=15)
    plt.xlabel("Nombre d'actions")
    
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/actions_par_origine.png", bbox_inches="tight", dpi=300)
    plt.close()