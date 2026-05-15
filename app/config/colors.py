# On a crée ce fichier suite à la demande de Mme Isabelle RISS pour harmoniser les couleurs du rapport
# Palette de couleurs principale pour l'harmonisation de l'affichage SSU

SSU_PALETTE = [
    "#00A9CE", # Cyan principal
    "#82C341", # Vert doux
    "#FFB612", # Jaune/Or
    "#EB6B2E", # Orange
    "#9B59B6", # Violet
    "#F06292", # Rose
    "#4A90E2", # Bleu classique
    "#95A5A6", # Gris acier
    "#34495E", # Gris foncé (texte/bords)
    "#E74C3C", # Rouge doux
]

def get_color(index: int) -> str:
    """Retourne une couleur de la palette en fonction de l'index."""
    return SSU_PALETTE[index % len(SSU_PALETTE)]

