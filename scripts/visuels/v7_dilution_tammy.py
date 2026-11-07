# ======================================================================================================
# Visuel 7 : v7_dilution_tammy.py (version de travail d'origine : visuel_07_dilution_tammy-Tiza-v1.0.py ; seuls les chemins et le nom de l'image changent)
# Indicateur 7b : part attendue de MALFAÇON en GLP, pendant Tammy et en dehors (appui du 4.3)
# Part attendue = somme des probabilités p_malfacon des pannes / nombre de pannes
#	Graphique à doubles barres verticales empilées
# ======================================================================================================
import pandas as pd                 																															# pandas : lecture et manipulation de series et dataframes
import matplotlib.pyplot as plt     																															# pyplot : le module de dessin de Matplotlib
from pathlib import Path            																															# Path : construire des chemins de fichiers propres

RACINE  = Path(__file__).resolve().parents[2]   # racine du dépôt (scripts/visuels/ → ../..), quel que soit le dossier d'où on lance le script
DONNEES = RACINE / "sql" / "requetes"           # résultats des requêtes SQL (res_indicateurNN_….csv)
SORTIE  = RACINE / "images"                     # images publiées dans le dépôt

# Lecture et chargement du fichier de données csv dans un tableau pandas df
df_dilution = pd.read_csv(DONNEES / "res_indicateur07b_malfacon_tammy.csv", sep=";")

# Chargement des tableaux
mois									=	df_dilution['mois']
n_autres							=	df_dilution['n_pannes'] - df_dilution['n_malfacons']
n_malfacons						=	df_dilution['n_malfacons']
taux									=	df_dilution['pct_malfacon']

# Dictionnaire de traduction des dates numériques en libellé texte
dico_libelles_mois	=	{
"2023-08": "août 2023",
"2023-09": "septembre 2023",
"2023-10": "octobre 2023",
"2023-11": "novembre 2023",
"2023-12": "décembre 2023",
}

libelles_mois = df_dilution["mois"].map(dico_libelles_mois)  																	# chaque code est remplacé par sa valeur du dico
	
#########Graphique à barres verticales #########
fig, ax = plt.subplots(figsize=(9, 7))

# Dessine les deux series de barres horizontales empilées gauche/droite
bar_dfm=ax.bar(libelles_mois, n_malfacons, label="Pannes dues à une malfaçon", color="firebrick")
bar_dfa=ax.bar(libelles_mois, n_autres, bottom=n_malfacons, color="lightgrey", label='Autres pannes')

# Personnalisation des axes et de la légende\n% = part de malfaçon sur le mois
ax.set_xlabel("Guadeloupe : Mois d'août 2023 à décembre 2023\n% = part de malfaçons")
ax.set_ylabel('Nombre de pannes')	
ax.set_title("Stagnation des malfaçons pendant Tammy, alors que les autres pannes explosent")
ax.bar_label(bar_dfm, labels=[f"{x:.1f} %".replace('.', ',') for x in taux], padding=3)						# remplacement du separateur décimal "." de la valeur la valeur numerique par la virgule à la française

# Étiquettes avec flèche sur les pics cycloniques
ax.annotate("Tammy",																																						# le texte (\n = retour à la ligne)
	            xy=("octobre 2023", 2900),																													# le point VISÉ par la flèche
	            xytext=("octobre 2023", 2900),																											# où POSER le texte
	            fontsize=9,
	            color="purple")

# Ajustement automatique de la mise en page
fig.tight_layout()                                               																	# range sans chevauchement
# --- Sortie Sauvegarde---------------------------------------------
fig.savefig(SORTIE / "v7_dilution_tammy.svg", dpi=150, bbox_inches="tight")							# bbox_inches="tight" rogne les marges blanches inutiles							
plt.show()																																												# ouvre les fenêtres de graphiques - à fermer pour que le script se termine
