import pandas as pd


def normalize_text(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def standardize_simple_labels(colonne: pd.Series, default: str = "Non renseigné") -> pd.Series:
    cleaned = colonne.apply(normalize_text).fillna(default)
    cleaned = cleaned.str.replace(r"\s+", " ", regex=True) # garder un seul espace
    return cleaned


def standardize_etablissement(colonne: pd.Series) -> pd.Series:
    s = standardize_simple_labels(colonne)
    s_lower = s.str.lower()

    mapping = {
        "ua": "UA",
        "université d'angers": "UA",
        "universite d'angers": "UA",

        "uco": "UCO",
        "u.c.o": "UCO",

        "esa": "ESA",
        "ensam": "ENSAM",
        "talm": "TALM",
        "arifts": "ARIFTS",
        "iforis": "IFORIS",
        "iforis cnam": "IFORIS",
        "cnam-iforis": "IFORIS",
        "istom": "ISTOM",
        "etsco": "ETSCO",

        "institut agro rennes angers": "Institut agro Rennes Angers",
        "agro campus ouest": "Institut agro Rennes Angers",
        "agrocampus ouest": "Institut agro Rennes Angers",

        "autre": "Autre établissement",
        "autres": "Autre établissement",

        "non renseigné": "Non renseigné",
        "non renseigne": "Non renseigné",
    }

    result = []
    for original, lowered in zip(s, s_lower): # on parcourt les deux colones en meme temps 
        result.append(mapping.get(lowered, original))

    return pd.Series(result, index=colonne.index)

