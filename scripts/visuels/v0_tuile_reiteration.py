# ======================================================================================================
# Visuel 0 : v0_tuile_reiteration.py (version de travail d'origine : tuile_kpi_reiteration-Tiza-v1.1.py ; seuls les chemins changent)
# Indicateur 6 : Taux de réitération : part des abonnés touchés qui ont eu au moins 2 pannes, 2023-2025
# ======================================================================================================
import pandas as pd                 																															# pandas : lecture et manipulation de series et dataframes
import matplotlib.pyplot as plt     																															# pyplot : le module de dessin de Matplotlib
from pathlib import Path            																															# Path : construire des chemins de fichiers propres

RACINE  = Path(__file__).resolve().parents[2]   # racine du dépôt (scripts/visuels/ → ../..), quel que soit le dossier d'où on lance le script
DONNEES = RACINE / "sql" / "requetes"           # résultats des requêtes SQL (res_indicateurNN_….csv)
SORTIE  = RACINE / "images"                     # images publiées dans le dépôt

# Lecture et chargement du fichier de données csv dans un tableau pandas df
df_reit = pd.read_csv(DONNEES / "res_indicateur06_reiteration.csv", sep=";")

# Chargement des tableaux 
tx_reiteration=df_reit['taux_reiteration_pct'].iloc[0]
tx_reiteration_txt=f"{tx_reiteration:.1f} %".replace(".", ",")						# met la virgule à la française

nb_abotouches=df_reit['touches'].iloc[0]
nb_abotouches_txt="sur " + f"{nb_abotouches:,}".replace(",", " ") + " abonnés touchés, GLP + MTQ, 2023-2025"		# séparateur de milliers
libelle="des abonnés touchés par une panne\nen ont connu au moins deux"

#########TUILE#########
fig, ax = plt.subplots(figsize=(6, 3.5))   # une feuille plus large que haute, format tuile
ax.axis("off")                             # masque le cadre, les graduations et les étiquettes d'axes

ax.text(0.5, 0.75, tx_reiteration_txt,      # x = 0.5 : le milieu en largeur ; y = 0.75 : un peu au-dessus du milieu
        transform=ax.transAxes,          		# « 0 à 1 dans le cadre », plutôt que les valeurs des données
        ha="center", va="center",        		# ha : alignement horizontal ; va : alignement vertical
        fontsize=50, fontweight="bold",			# taille et police en gras
        bbox=dict(boxstyle="round", 				# boite aux coins arrondis autour du texte
        facecolor="whitesmoke", 						# couleur de la boite
        edgecolor="darkgrey"))   						

ax.text(0.5, 0.35, libelle,       					# x = 0.5 : le milieu en largeur ; y = 0.35 : un peu au-dessous de la boite
        transform=ax.transAxes,          		# « 0 à 1 dans le cadre », plutôt que les valeurs des données
        ha="center", va="center",        		# ha : alignement horizontal ; va : alignement vertical
        fontsize=25, fontweight="normal")  	# taille et police en epaisseur normale

ax.text(0.5, 0.12, nb_abotouches_txt,            		# x = 0.5 : le milieu en largeur ; y = 0.12 : un peu au-dessous du libellé
        transform=ax.transAxes,          		# « 0 à 1 dans le cadre », plutôt que les valeurs des données
        ha="center", va="center",        		# ha : alignement horizontal ; va : alignement vertical
        fontsize=15, color='grey')  		 		# taille et couleur de la police

# Ajustement automatique de la mise en page
# --- Sortie Sauvegarde---------------------------------------------
fig.savefig(SORTIE / "v0_tuile_reiteration.svg", dpi=150, bbox_inches="tight")										# bbox_inches="tight" rogne les marges blanches inutiles
plt.show()																																												# ouvre les fenêtres de graphiques - à fermer pour que le script se termine
