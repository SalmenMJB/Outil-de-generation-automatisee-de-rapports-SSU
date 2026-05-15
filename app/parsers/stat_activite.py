import pandas as pd

def parse_stat_activite_file(filepath):
    df = pd.read_excel(filepath, header=4)

    df.dropna(how="all")
    df = df.reset_index(drop=True)

    # nettoyage noms colonnes
    df.columns = [str(col).strip().lower() for col in df.columns]

    return df


