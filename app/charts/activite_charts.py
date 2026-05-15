import os
import matplotlib.pyplot as plt

from app.config.colors import SSU_PALETTE


# def plot_top_nationalites(activite_stats):
#     data = activite_stats["top_nationalites"]

#     data = data.head(10) 
#     labels = data.index.astype(str) 
#     values = data.values

#     os.makedirs("output/charts", exist_ok=True)

#     plt.figure(figsize=(9, 5))
#     bars = plt.bar(labels, values, color=SSU_PALETTE[0])

#     offset = max(values) * 0.000002

#     for bar in bars:
#         height = bar.get_height() 
#         plt.text(
#             bar.get_x() + bar.get_width() / 2,
#             height + offset,
#             str(int(height)),
#             ha="center",
#             va="bottom",
#             fontsize=9
#         )

#     plt.title("Top nationalités")
#     plt.xlabel("Nationalité")
#     plt.ylabel("Nombre d'étudiants")
#     plt.xticks(rotation=45, ha="right")
#     plt.tight_layout()
#     plt.savefig("output/charts/top_nationalites.png")
#     plt.close()

def plot_top_nationalites_hors_france(activite_stats):
    data = activite_stats["top_nationalites"]

    data = data[data.index != "FRANCE"] # enlever la france
    data = data.head(10) 
    data = data.sort_values(ascending=True)
    labels = data.index.astype(str)
    values = data.values

    os.makedirs("output/charts", exist_ok=True)

    plt.figure(figsize=(9, 5))
    bars = plt.barh(labels, values, color=SSU_PALETTE[1])

    offset = max(values) * 0.000002

    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + offset, # ajouter un petit espace pour que le nombre ne soit pas collé au bar
            bar.get_y() + bar.get_height() / 2, # positionnement vertical (centrer le nombre verticalement par rapport au bar)
            str(int(width)), # convertir le nombre en string
            ha="left", # alignement horizontal
            va="center", # alignement vertical
            fontsize=9
        )


    plt.title("Nationalité des étudiants (hors France)", pad=20, fontweight='bold')
    plt.xlabel("Nombre d'étudiants")
    plt.ylabel("Nationalité")
    
    # Style premium
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/top_nationalites_hors_france.png", bbox_inches="tight", dpi=300)
    plt.close()
