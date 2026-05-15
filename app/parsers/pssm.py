import pandas as pd

def parse_pssm_file(filepath) -> dict[str, pd.DataFrame]:
    sheets = pd.read_excel(filepath, sheet_name=None) # sheet_name=None pour lire toutes les feuilles du fichier
    # sheets est un dict de  type: { "nom de feuille" : données de chaque feuille (df) }

    parsed_sheets = {}

    for sheet_name, df in sheets.items():
        df = df.dropna(how="all")
        df.columns = [str(col).strip().lower() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains("^unnamed", na=False)] # exclure les colonnes unnamed
        df = df.reset_index(drop=True)

        # y a t il au moins une colonne dates, début, fin
        has_dates = any(col in df.columns for col in ["dates", "date", "date début", "date fin", "date de début", "date de fin"]) 

        # garder seulement les feuilles qui ressemblent à un tableau de sessions
        if has_dates:
            df["sheet_name"] = sheet_name # ajouter le nom de la feuille dans le df
            parsed_sheets[sheet_name] = df

    return parsed_sheets    