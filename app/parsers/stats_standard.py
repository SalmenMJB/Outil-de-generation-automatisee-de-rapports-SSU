# Le fichier excel donné par l'SSU était endommagé et illisble
# On l'a nettoyé et gardé uniquement le tableau nécessaire

import pandas as pd

def parse_stats_standard_file(filepath):
    # le vrai header du tableau principal commence à la ligne 4 Excel
    df = pd.read_excel(filepath, header=3)

    # supprimer les lignes totalement vide
    df = df.dropna(how="all")

    # nettoyer les noms de colonnes
    df.columns = [str(col).strip().lower().replace("\n", " ") for col in df.columns]

    # supprimer colonnes inutiles / parasites
    columns_to_drop = [
        col for col in df.columns if "pour info" in col
    ]
    df = df.drop(columns = columns_to_drop, errors="ignore")
    df = df.loc[:, ~df.columns.str.contains("^unnamed", na=False)]

    # garder seulement la partie utile du tableau principal
    if "mois" in df.columns:
        mois_valides = [
            "août", "sept", "oct", "nov", "déc",
            "janv", "févr", "mars", "avr", "mai", "juin", "juil"
        ]
        df = df[df["mois"].isin(mois_valides)]

    # # RENOMMAGE PLUS PROPRE + ssu doivent garder le meme style pour les colonnes
    # On va le commenter pour l'instant, parce que les colonnes que l'SSU vont rajouter ne seront pas considérées dans ce rename_map
    # rename_map = { # les noms de colonnes d'origine sont convertis en miniscule
    #     "nb appels 2020-2021": "appels_2020_2021",
    #     "nb appels 2021-2022": "appels_2021_2022",
    #     "nb appels 2022-2023": "appels_2022_2023",
    #     "nb appels2023-2024": "appels_2023_2024",
    #     "nb appels 2024-2025": "appels_2024_2025",
    #     "nb appels2024-2025": "appels_2024_2025_bis",
    #     "nb appel 2025-2026": "appels_2025_2026",
    #     "m appels reçus/jouren 23/24": "moyenne_jour_2023_2024",
    #     "m appels reçus/jouren 24/25": "moyenne_jour_2024_2025",
    #     "m appels reçus/jour": "moyenne_jour_2025_2026",
    # }
    # df = df.rename(columns = rename_map)

    # Supprimer les colonnes dupliquées (y'avait des colonnes nommés en double)
    df = df.loc[:, ~df.columns.duplicated()]

    # CONVERSION DES COLONNES NUMERIQUES
    for col in df.columns:
        if col != "mois": # sauf la 1ere col des mois
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.reset_index(drop=True)

    return df