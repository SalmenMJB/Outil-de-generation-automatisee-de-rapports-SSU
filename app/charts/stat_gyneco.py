import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from app.config.colors import SSU_PALETTE

def plot_motifs_reels_css(indicators):
    s = indicators["motifs_reels_css"].copy()
    
    new_index = []
    for idx in s.index:
        idx_str = str(idx).strip().lower()
        if idx_str in ["ist", "dépistage ist", "depistage ist"]:
            new_index.append("Dépistage IST")
        else:
            new_index.append(str(idx).capitalize())
            
    s.index = new_index
    data = s.groupby(s.index).sum()
    data = data.sort_values(ascending=False).head(8)
    

    labels = [str(l) for l in data.index]
    values = [float(v) for v in data.values]

    plt.figure(figsize=(9, 5))
    bars = plt.barh(labels, values, color=SSU_PALETTE)
    plt.gca().invert_yaxis()

    offset = max(values)*0.01 if len(values)>0 else 1
    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + offset,
            bar.get_y() + bar.get_height()/2,
            str(int(width)),
            va="center"
        )
    plt.title("Motifs réels des consultations CSS", pad=20, fontweight='bold', fontsize=15)
    plt.xlabel("Nombre de consultations")
    
    # Style premium
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("output/charts/motifs_reels_css.png", bbox_inches="tight", dpi=300)
    plt.close()


def plot_motifs_CSS(df):
    df_gyneco = df[df["motif"]=="Centre de planification"]
    df_medecine_gyneco = df[df["motif"]=="Consultations médecine générale"]

    nb_consultations = df_gyneco.shape[0]
    repartition = df_gyneco["sexe"].value_counts()
    repartition = repartition.rename(index={"M" : "Hommes",
                "F" : "Femmes"})
    # print(repartition)
    # print(nb_consultations)

    motifs = [(r'(?i).*contraception.*', "Contraception"),
    (r'(?i).*(problème gyneco|problème gynéco|dysmenorrhée).*', "Problème gynéco ou sexuel (dont dysménorrhées)"),
    (r'(?i).*IST.*', "Dépistage d'IST et IST"),
    (r'(?i).*DIU.*', "Contrôle DIU"),
    (r'(?i).*(examen|entretien|consultation).*', "Examen ou entretien/consultation"),
    (r'(?i).*(PREP|aménagement|santé mentale|violence|grossesse|autre).*', "Autre (grossesses, violences...)")]

    motifs_medecine = [(r'(?i).*contraception.*', "Contraception"),
    (r'(?i).*(problème gyneco|problème gynéco).*', "Problème gynéco ou sexuel (dont dysménorrhées)"),
    (r'(?i).*IST.*', "Dépistage d'IST et IST"),
    (r'(?i).*grossesse.*', "Autre (grossesses, violences...)")]

    resultats = []
    resultats_medecine = []

    for regex,intitule in motifs:
        nb_occurences = df_gyneco[df_gyneco["motif réels"].str.contains(regex,na=False)].shape[0]
        resultats.append({"motif réels" : intitule,
                            "Nombre par motif" : nb_occurences})

    for regex,intitule in motifs_medecine:
        nb_occurences_medecine = df_medecine_gyneco[df_medecine_gyneco["motif réels"].str.contains(regex,na=False)].shape[0]
        resultats_medecine.append({"motif réels" : intitule,
                            "Nombre par motif" : nb_occurences_medecine})

    df_gyneco = pd.DataFrame(resultats)
    df_medecine_gyneco = pd.DataFrame(resultats_medecine)

    medecine_dict = dict(zip(df_medecine_gyneco["motif réels"], df_medecine_gyneco["Nombre par motif"]))

    for index, row in df_gyneco.iterrows():
        motif = row["motif réels"]
        if motif in medecine_dict:
            df_gyneco.at[index, "Nombre par motif"] += medecine_dict[motif]

    df_gyneco = df_gyneco.sort_values(by="Nombre par motif", ascending=False)

    somme = df_gyneco["Nombre par motif"].sum()
    pourcentages = []
    for val in df_gyneco["Nombre par motif"]:
        calcul = (val/somme)*100
        pourcentages.append(round(calcul,2))

    fig, ax = plt.subplots(figsize=(9, 6))

    couleurs = SSU_PALETTE
    
    wedges, _ = ax.pie(
        pourcentages,
        colors=couleurs,
        startangle=85,
        counterclock=False,
        wedgeprops=dict(edgecolor="white", linewidth=1.2)
    )

    ax.set(aspect="equal")

    # Calcul des positions initiales
    label_data = []
    for wedge, cat, pct in zip(wedges, df_gyneco["motif réels"], pourcentages):
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = np.cos(np.deg2rad(angle))
        y = np.sin(np.deg2rad(angle))
        label_x = 1.2 * x
        label_y = 1.2 * y
        ha = "left" if x >= 0 else "right"
        label_data.append({
            "wedge": wedge, "cat": cat, "pct": pct,
            "x": x, "y": y,
            "label_x": label_x, "label_y": label_y, "ha": ha})

    # Anti-collision : sépare les labels trop proches verticalement
    MIN_GAP = 0.18  # espace minimum entre deux labels (en unités axes)
    MAX_ITER = 20

    for _ in range(MAX_ITER):
        moved = False
        for i in range(len(label_data)):
            for j in range(i + 1, len(label_data)):
                li, lj = label_data[i], label_data[j]
                # Ne corrige que les labels du même côté
                if li["ha"] != lj["ha"]:
                    continue
                dy = abs(li["label_y"] - lj["label_y"])
                if dy < MIN_GAP:
                    overlap = (MIN_GAP - dy) / 2
                    if li["label_y"] >= lj["label_y"]:
                        label_data[i]["label_y"] += overlap
                        label_data[j]["label_y"] -= overlap
                    else:
                        label_data[i]["label_y"] -= overlap
                        label_data[j]["label_y"] += overlap
                    moved = True
        if not moved:
            break
    
    for ld in label_data:
        if ld["cat"] == "Examen ou entretien/consultation":
            ld["label_x"] = 0.2   # pousse à droite
            ld["label_y"] = 1.15   # ajuste la hauteur si besoin
            ld["ha"] = "left"
            break
    # Annotation avec positions corrigées
    for ld in label_data:
        ax.annotate(
            f"{ld['cat']}\n{ld['pct']:.0f}%",
            xy=(ld["x"], ld["y"]),
            xytext=(ld["label_x"], ld["label_y"]),
            ha=ld["ha"],
            va="center",
            fontsize=12,
            bbox=dict(boxstyle="square,pad=0.35", fc="white", ec="#bfbfbf", lw=1),
            arrowprops=dict(arrowstyle="-", color="#9e9e9e", lw=1.2, shrinkA=0, shrinkB=0))

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor("#d9d9d9")
        spine.set_linewidth(1)

    
    plt.title("Répartition des motifs de consultation au CSS", pad=35, fontweight="bold", fontsize=15)
    plt.tight_layout()


    plt.savefig("output/charts/motifs_CSS.png", dpi=300, bbox_inches="tight")
    

def plot_prescriptions_css(excel_path):
    data = pd.read_excel(excel_path, sheet_name="Gynécologie")
    data.columns = [str(c).strip() for c in data.columns]
    
    if "Sous catégorie" not in data.columns:
        data = pd.read_excel(excel_path, sheet_name="Gynécologie", header=1)
        data.columns = [str(c).strip() for c in data.columns]

    # Filtrage
    cibles = ["pilule", "implant", "anneau", "patch", "stérilet", "vaccins", "préservatif", "contraception d'urgence"]
    data_filtered = data[data["Sous catégorie"].str.lower().isin(cibles)].copy()
    data_filtered["Nombre"] = pd.to_numeric(data_filtered["Nombre"], errors='coerce').fillna(0)
    stats = data_filtered.groupby("Sous catégorie")["Nombre"].sum()
    stats = stats[stats > 0]

    # Ordre amélioré (pour que les petites parts soient séparées par des grosses)
    ordre_voulu = ["Pilule", "Anneau", "Préservatif", "Patch", "Implant", "Contraception d'urgence", "Stérilet", "Vaccins"]
    final_keys = [k for item in ordre_voulu for k in stats.index if k.lower() == item.lower()]
    stats = stats.reindex(final_keys)

    if not stats.empty:
        fig, ax = plt.subplots(figsize=(10, 7), subplot_kw=dict(aspect="equal"))
        
        # Couleurs
        couleurs = SSU_PALETTE[:len(stats)]
        
        # Création du camembert
        wedges, _ = ax.pie(stats, colors=couleurs, startangle=140, 
                          wedgeprops=dict(edgecolor='white', linewidth=1.5))

        # Traits de liaison
        kw = dict(arrowprops=dict(arrowstyle="-", color="#777777", linewidth=1), zorder=0, va="center")

        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1)/2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            xtxt = 1.15 * np.sign(x)
            ytxt = 1.2 * y
            
            connectionstyle = f"angle,angleA=0,angleB={ang}"
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            
            label = f"{stats.index[i]} ({int(stats.values[i])})"
            
            ax.annotate(label, xy=(x, y), xytext=(xtxt, ytxt),
                        horizontalalignment=horizontalalignment, **kw, 
                        fontsize=11, fontweight='500')

        plt.title("Répartition des prescriptions au CSS", fontsize=15, fontweight='bold', pad=30)
        
        plt.tight_layout()
        save_path = "output/charts/prescriptions_css.png"
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()
