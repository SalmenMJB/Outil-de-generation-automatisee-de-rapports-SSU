import matplotlib.pyplot as plt


def plot_bilans_medecins_vs_infirmieres(indicators):
    data = { # c'est un map (tableau associatif) => get renvoie l'elt voulu
        "Médecins": indicators.get("bilans_medecins", 0),
        "Infirmières": indicators.get("bilans_infirmieres", 0),
        "Autres": indicators.get("bilans_autres_intervenants", 0)
    }

    labels = list(data.keys())
    values = list(data.values())

    plt.figure(figsize=(8,5))
    bars = plt.bar(labels, values, color="#212E53")

    offset = 0.5

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2,
            height + offset,
            str(int(height)),
            ha = "center",
            va = "bottom"
        )

    plt.title("Bilans de prévention : médecins vs infirmières", pad=20, fontweight='bold', fontsize=15)
    plt.ylabel("Nombre de bilans")
    
    plt.gca().spines['top'].set_visible(False) # gca() = get current axes, set_visible(False) = cache le cadre supérieur et droit
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/bilans_medecins_vs_infirmieres.png", bbox_inches="tight", dpi=300)
    plt.close()

