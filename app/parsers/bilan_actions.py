import pandas as pd

# CE FICHIER CONTIENT 2 FEUILLES: une principale (à utiliser) et une autre appelée "liste menu déroulant" (à ignorer)

def parse_bilan_actions_file(filepath: str) -> pd.DataFrame:
    # on lit la 1ere feuille utile
    fichier = pd.ExcelFile(filepath)
    sheet_name = fichier.sheet_names[0]
    
    df = pd.read_excel(filepath, sheet_name=sheet_name)

    # supprimer les lignes entierement vides
    df = df.dropna(how="all").reset_index(drop=True)

    # normaliser les noms de colonnes
    df.columns = [str(col).lower().strip() for col in df.columns]

    # supprimer les colonnes unnamed, les NaN sont traités comme False pour éviter les erreurs
    df = df.loc[:, ~df.columns.str.contains("^unnamed", na=False)]

    return df
