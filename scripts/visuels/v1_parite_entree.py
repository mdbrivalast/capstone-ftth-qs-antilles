# ======================================================================================================
# Visuel 1 : v1_parite_entree.py (version de travail d'origine : visuel_01_parite_entree-Tiza-v1.2.py ; seuls les chemins changent) PARITE
# Indicateur 1 : ISSUE DU RACCORDEMENT par territoire (échec / reporté / réussi)
# Parité à l’entrée : GLP et MTQ raccordent pareil (issue, reprise, délai de mise en service)
#	Graphique à doubles barres horizontales 
# ======================================================================================================
import pandas as pd                 																															# pandas : lecture et manipulation de series et dataframes
import matplotlib.pyplot as plt     																															# pyplot : le module de dessin de Matplotlib
from pathlib import Path            																															# Path : construire des chemins de fichiers propres
import numpy as np																																								# numpy : lecture et manipulation de tableaux

RACINE  = Path(__file__).resolve().parents[2]   # racine du dépôt (scripts/visuels/ → ../..), quel que soit le dossier d'où on lance le script
DONNEES = RACINE / "sql" / "requetes"           # résultats des requêtes SQL (res_indicateurNN_….csv)
SORTIE  = RACINE / "images"                     # images publiées dans le dépôt
# Dossier de sortie des images

# --- Chargement -----------------------------------------

# Chargement des tableaux 
# Lecture et chargement du fichier de données csv dans un tableau pandas df
df_issue = pd.read_csv(DONNEES / "res_indicateur01_raccordement_issue.csv", sep=";")							
df_reprise = pd.read_csv(DONNEES / "res_indicateur02_raccordement_reprise.csv", sep=";")					
df_mes = pd.read_csv(DONNEES / "res_indicateur03_delai_mes.csv", sep=";")													

#2 listes des 3 indicateurs par territoire, GLP et MTQ
categories = ['Échecs\nsur les raccordements', 'Reprises malfaçons\nsur les réussis','MES au-delà de 60j']

#GLP
tx_echec_glp = df_issue.set_index("territoire").loc["GLP", "taux_echec_pct"]
tx_reprise_glp = df_reprise.set_index("territoire").loc["GLP", "taux_reprise_pct"]
delai_mes_60j_glp = df_mes.set_index("territoire").loc["GLP", "pct_mes_moins_60j"]
mes_plus60j_glp = 100 - delai_mes_60j_glp

#liste_GLP
valeurs_GLP = [tx_echec_glp, tx_reprise_glp, mes_plus60j_glp]

#MTQ
tx_echec_mtq = df_issue.set_index("territoire").loc["MTQ", "taux_echec_pct"]
tx_reprise_mtq = df_reprise.set_index("territoire").loc["MTQ", "taux_reprise_pct"]
delai_mes_60j_mtq = df_mes.set_index("territoire").loc["MTQ", "pct_mes_moins_60j"]

mes_plus60j_mtq = 100 - delai_mes_60j_mtq
#liste_MTQ
valeurs_MTQ = [tx_echec_mtq, tx_reprise_mtq, mes_plus60j_mtq]

#########Graphique à barres horizontales #########
# position des catégories sur l'axe Y
y = np.arange(len(categories))

# épaisseur de chaque barre
hauteur = 0.35

fig, ax = plt.subplots(figsize=(12, 5))

# Dessine les deux séries de barres horizontales (barh) en decalant la position y vers le haut (- hauteur/2) et vers le bas (+ hauteur/2)
rects1 = ax.barh(y - hauteur/2, valeurs_GLP, hauteur, label='Guadeloupe')
rects2 = ax.barh(y + hauteur/2, valeurs_MTQ, hauteur, label='Martinique')

# Personnalisation des axes et de la légende
ax.set_xlim(0, 25)
ax.set_xlabel('Part (%)\nPas de repère national sourcé pour les reprises')
ax.set_title('Échecs-Reprises-MES : parité sur les territoires et en retrait du national')
ax.set_yticks(y)
ax.set_yticklabels(categories)

ax.bar_label(rects1, labels=[f"{x:.1f} %".replace('.', ',') for x in rects1.datavalues], padding=3)			# la virgule à la française
ax.bar_label(rects2, labels=[f"{x:.1f} %".replace('.', ',') for x in rects2.datavalues], padding=3)

ax.vlines(6.27, ymin=-0.5, ymax=0.5, colors="grey", linestyles="dashed", label="Repère national")
ax.vlines(x=14.7, ymin=1.5, ymax=2.5, colors="grey", linestyles="dashed")
ax.invert_yaxis()
ax.legend()

# Ajustement automatique de la mise en page
fig.tight_layout()
# --- Sortie Sauvegarde---------------------------------------------
fig.savefig(SORTIE / "v1_parite_entree.svg", dpi=150, bbox_inches="tight")														
plt.show()