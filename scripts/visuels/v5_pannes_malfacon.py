# ======================================================================================================
# Visuel 5 : v5_pannes_malfacon.py (version de travail d'origine : visuel_05_pannes-malfacon-Tiza-v1.3.py ; seuls les chemins et le nom de l'image changent)
# Indicateur 7 : Quantité de malfaçons sur les pannes selon leur causes
#	Graphique à doubles barres horizontales empilées gauche et droite
# ======================================================================================================
import pandas as pd                 																															# pandas : lecture et manipulation de series et dataframes
import matplotlib.pyplot as plt     																															# pyplot : le module de dessin de Matplotlib
from pathlib import Path            																															# Path : construire des chemins de fichiers propres

RACINE  = Path(__file__).resolve().parents[2]   # racine du dépôt (scripts/visuels/ → ../..), quel que soit le dossier d'où on lance le script
DONNEES = RACINE / "sql" / "requetes"           # résultats des requêtes SQL (res_indicateurNN_….csv)
SORTIE  = RACINE / "images"                     # images publiées dans le dépôt

# Lecture et chargement du fichier de données csv dans un tableau pandas df
df_malfacons_pannes = pd.read_csv(DONNEES / "res_indicateur07_malfacon-cause.csv", sep=";").sort_values(by="n_malfacon", ascending=False)

# Chargement des tableaux 
labels_natures=df_malfacons_pannes['quoi']
dfp=df_malfacons_pannes['n_pannes']
dfm=df_malfacons_pannes['n_malfacon']
dfa=df_malfacons_pannes['n_pannes'] - df_malfacons_pannes['n_malfacon'] 
dpct=df_malfacons_pannes['pct_malfacon']
#totaldfp=dfp.sum(axis=0))
#totaldfm=dfm.sum(axis=0))
#totaldfa=dfa.sum(axis=0))
#print(f'{totaldfm} {totaldfa}\n')

# Dictionnaire traduisant les causes (nom cours de la base) en libelle (texte long)
dico_libelles_causes={
"ACCES": "Accessibilité matériel ou locaux",
"CABLE#FIBRE": "Altération câble ou fibre",
"CONT": "Altération ou perte de signal",
"GC": "Travaux de génie civil",
"ENV": "Environnement",
"ROP": "Route optique",
"MAT": "Cause matérielle",
"TECHNICIEN": "Implication technicien",
"CLIENT": "Client/commercial",
"DEPL": "Déploiement d'infrastructure",
"PUBLIC": "Interventions publiques"}

libelles_causes = df_malfacons_pannes["quoi"].map(dico_libelles_causes)														# chaque code est remplacé par sa valeur du dico

#########GRAPHIQUE#########
fig, ax = plt.subplots(figsize=(12, 5))

# Dessine les deux series de barres horizontales empilées gauche/droite
bar_dfm=ax.barh(libelles_causes, dfm, label="Malfaçons - total 44 180", color="firebrick")
bar_dfa=ax.barh(libelles_causes, dfa, left=dfm, label="Autres - total 106 347\nEnsemble des pannes - total 150 527", color="lightgrey")

# Personnalisation des axes et de la légende
ax.set_xlabel('Nombre de pannes\n% = part de malfaçon dans les pannes de chaque cause')
ax.set_title('Malfaçons sur les pannes selon leurs causes : près d’une panne sur trois')

ax.bar_label(bar_dfm, labels=[f"{x:.1f} %".replace('.', ',') for x in dpct], padding=3)						#la virgule à la française

ax.invert_yaxis()
ax.legend()

# Ajustement automatique de la mise en page
fig.tight_layout()                                               																	# range sans chevauchement
# --- Sortie Sauvegarde---------------------------------------------
fig.savefig(SORTIE / "v5_pannes_malfacon.svg", dpi=150, bbox_inches="tight")											# bbox_inches="tight" rogne les marges blanches inutiles
plt.show()																																												# ouvre les fenêtres de graphiques - à fermer pour que le script se termine
