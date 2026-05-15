import pandas as pd

def parse_psy_file(filepath):
    # Charge le fichier Excel en partant de la 4ème ligne comme en-tête
    df = pd.read_excel(filepath, header=3)

    # Supprime les lignes entièrement vides
    df = df.dropna(how="all")
    # Normalise les noms de colonnes : supprime les espaces et met en minuscules
    df.columns = [str(col).strip().lower() for col in df.columns]
    # Supprime les colonnes sans nom générées automatiquement par pandas
    df = df.loc[:, ~df.columns.str.contains("^unnamed", na=False)] # na=False: # Si une cellule est NaN → retourne False

    return df