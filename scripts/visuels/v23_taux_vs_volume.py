# ======================================================================================================
# Visuel 2+3 : v23_taux_vs_volume.py (version de travail d'origine : visuel_02-03_taux_vs_volume-Tiza-v1.3.py ; seuls les chemins et le nom de l'image changent) taux de panne vs volume
# Indicateur 4 : ISSUE DU RACCORDEMENT par territoire (échec / reporté / réussi)
# TAUX DE PANNE mensuel = pannes / parc actif (parc reconstruit par le flux)
# Graphique de courbes
# ======================================================================================================
import pandas as pd                 																															# pandas : lecture et manipulation du tableau
import matplotlib.pyplot as plt     																															# pyplot : le module de dessin de Matplotlib
import matplotlib.dates as mdates   																															# outils de Matplotlib pour les axes de dates
from pathlib import Path            																															# Path : construire des chemins de fichiers propres

RACINE  = Path(__file__).resolve().parents[2]   # racine du dépôt (scripts/visuels/ → ../..), quel que soit le dossier d'où on lance le script
DONNEES = RACINE / "sql" / "requetes"           # résultats des requêtes SQL (res_indicateurNN_….csv)
SORTIE  = RACINE / "images"                     # images publiées dans le dépôt
# Dossier de sortie des images

# --- Chargement -----------------------------------------
# Résultat de l'indicateur 04 : une ligne par territoire × mois
df = pd.read_csv(DONNEES / "res_indicateur04_taux_pannes.csv", sep=";")

# "2023-01" est du texte : on le convertit en vraie date pour que Matplotlib place les mois correctement sur l'axe du temps
df["mois"] = pd.to_datetime(df["mois"], format="%Y-%m")

# On sépare les deux territoires (filtre booléen, comme en pandas)
glp = df[df["territoire"] == "GLP"]
mtq = df[df["territoire"] == "MTQ"]

# Figure Volume - 2 graphiques empilés (2 lignes, 1 colonne) qui partagent le même axe x (le temps)                 
# ax_vol = l'étage du HAUT (volume) ; ax = l'étage du BAS (taux)                                    
fig, (ax_vol, ax) = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [1, 1.4]})	

# Étage du HAUT : le VOLUME (nombre de pannes dans le mois)
ax_vol.plot(glp["mois"], glp["pannes"], label="Guadeloupe")
ax_vol.plot(mtq["mois"], mtq["pannes"], label="Martinique")

# Repère : le volume de pannes du mois de Tammy, pour comparer
ax_vol.axhline(3320, color="grey", linestyle=":", linewidth=1, label="Volume d'oct. 2023 (Tammy) : 3 320")

ax_vol.set_ylim(0, 4500)                          																								# volume aussi à partir de zéro
ax_vol.set_ylabel("Pannes dans le mois")
ax_vol.set_title("Volume : nombre de pannes")
#ax_vol.legend(loc="upper left", fontsize=8)

# Le "locator" choisit OÙ mettre les graduations : ici janvier, avril, juillet, octobre
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))

# Le "formatter" choisit COMMENT les écrire : mois/année
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))

# Réglage de la taille des étiquettes : taille 8, inclinées à 45°
ax.tick_params(axis="x", labelsize=8, rotation=45)

# Bandes grises : saisons cycloniques (juin → novembre); axvspan = "vertical span", une bande verticale entre deux x
for a in (ax_vol, ax):
	for annee in [2023, 2024, 2025]:
	    a.axvspan(pd.Timestamp(f"{annee}-06-01"),				# début de bande
	               pd.Timestamp(f"{annee}-11-30"),			# fin de bande
	               color="grey", alpha=0.15,						# alpha = transparence (0 invisible, 1 opaque)
	               # une seule entrée dans la légende, pas trois :
	               label="Saison cyclonique (juin-nov.)" if annee == 2023 else None)
      
ax_vol.legend(loc="upper left", fontsize=8)

# Ligne de référence nationale; axhline = "horizontal line", une ligne horizontale sur toute la largeur
ax.axhline(1.79, color="black", linestyle="--", linewidth=1, label="Moyenne nationale (1,79 %)")
           
# Une courbe par territoire : x = les mois, y = le taux de panne
ax.plot(glp["mois"], glp["taux_panne_pct"], label="Guadeloupe")
ax.plot(mtq["mois"], mtq["taux_panne_pct"], label="Martinique")

# L'axe vertical part de zéro
ax.set_ylim(0, 5)

# Étiquettes avec flèche sur les pics cycloniques
ax.annotate("juin 2023\nMTQ : Bret 3,09 %\nGLP : Gert 2,98 %",																		# le texte (\n = retour à la ligne)
	            xy=(pd.Timestamp("2023-06-01"), 3.09),																							# le point VISÉ par la flèche
	            xytext=(pd.Timestamp("2023-02-01"), 3.5),																						# où POSER le texte
	            arrowprops=dict(arrowstyle="->"),																										# le style de flèche
	            fontsize=9)
ax.annotate("oct. 2023 - Tammy + Philippe\nGLP : 4,38 %",    																			
	            xy=(pd.Timestamp("2023-10-01"), 4.38),        																			
	            xytext=(pd.Timestamp("2023-12-01"), 4.1),     																			
	            arrowprops=dict(arrowstyle="->"),             																			
	            fontsize=9)

ax.annotate("juil. 2024 - Beryl\nMTQ : 3,19 %\nGLP : 2,82 %",              												
	            xy=(pd.Timestamp("2024-07-01"), 3.19),        																			
            xytext=(pd.Timestamp("2024-08-01"), 3.3),     																				
            arrowprops=dict(arrowstyle="->"),             																				
            fontsize=9)
            
ax.annotate("août 2025 - Erin \nMTQ : 2,79 %\nGLP : 3,05 %",                  										
            xy=(pd.Timestamp("2025-08-01"), 3.05),        																				
            xytext=(pd.Timestamp("2025-09-01"), 3.1),    																					
            arrowprops=dict(arrowstyle="->"),             																				
            fontsize=9)
                                    
# Habillage : titre, libellé de l'axe vertical, légende
ax.set_title("Taux de panne mensuel, 2023-2025")
ax.set_ylabel("Abonnés en panne dans le mois (%)")
ax.legend()

fig.suptitle("Taux ou volume : deux lectures du même réseau")																			# titre de la FEUILLE

# Ajustement automatique de la mise en page
fig.tight_layout()                                               																	# range sans chevauchement
# --- Sortie Sauvegarde---------------------------------------------
fig.savefig(SORTIE / "v23_taux_vs_volume.svg", dpi=150, bbox_inches="tight")															# bbox_inches="tight" rogne les marges blanches inutiles
plt.show()																																												# ouvre les fenêtres de graphiques - à fermer pour que le script se termine