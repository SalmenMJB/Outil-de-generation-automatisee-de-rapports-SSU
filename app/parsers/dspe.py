import pandas as pd

def parse_dspe_file(filepath)-> pd.DataFrame:
    df = pd.read_excel(filepath)

    # supprimer les lignes entièrement vides
    df = df.dropna(how="all").reset_index(drop=True)

    # normaliser noms de colonnes
    df.columns = [str(col).lower().strip() for col in df.columns]

    # supprimer colonnes unnamed
    df = df.loc[:, ~df.columns.str.contains("^unnamed", na=False)]

    return df

    
    