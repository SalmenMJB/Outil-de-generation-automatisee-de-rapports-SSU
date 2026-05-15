import pandas as pd

def parse_ide_file(filepath: str) -> pd.DataFrame:
    df = pd.read_excel(filepath, header=3)

    df.dropna(how="all", inplace=True)
    df = df.reset_index(drop=True)

    # nettoyage noms colonnes
    df.columns = [str(col).strip().lower() for col in df.columns]

    return df
