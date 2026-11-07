# ======================================================================================================
# Visuel 6 : v6_cyclone_aerien.py (version de travail d'origine : visuel_06_cyclone_aerien-Tiza-v1.1.py ; seuls les chemins changent)
# Indicateur 8 : MÉCANISME CYCLONE : pannes oct vs sept 2023 (GLP) par tranche d'aérien du PM
# plus le PM est aérien, plus Tammy le frappe
#	Graphique à barres verticales 
# ======================================================================================================
import pandas as pd                 																															# pandas : lecture et manipulation de series et dataframes
import matplotlib.pyplot as plt     																															# pyplot : le module de dessin de Matplotlib
from pathlib import Path            																															# Path : construire des chemins de fichiers propres

RACINE  = Path(__file__).resolve().parents[2]   # racine du dépôt (scripts/visuels/ → ../..), quel que soit le dossier d'où on lance le script
DONNEES = RACINE / "sql" / "requetes"           # résultats des requêtes SQL (res_indicateurNN_….csv)
SORTIE  = RACINE / "images"                     # images publiées dans le dépôt

# Lecture et chargement du fichier de données csv dans un tableau pandas df - tpg = Tranche PM Guadeloue
df_tpg = pd.read_csv(DONNEES / "res_indicateur08_cyclone_tranche-aerienpm.csv", sep=";")

# Chargement des tableaux 
#Tableaux de controle commentés - à enlever en version finale
tpg_tranche						= df_tpg.set_index('tranche')																								# les noms de tranche deviennent l'index
tpg_tranche["ratio"]	= tpg_tranche['oct'] / tpg_tranche['sept'] 
tpg_tranche 					= tpg_tranche.loc[["enterré", "mixte", "aérien"]] 

categories						=	["Enterré\n(< 40 % aérien)", "Mixte\n(40 à 70 %)", "Aérien\n(≥ 70 %)"]

#########GRAPHIQUE#########
fig, ax = plt.subplots(figsize=(9, 6))

ax.set_ylim(0, 2.5)

# Dessine les deux series de barres horizontales empilées gauche/droite
bar_tpg = ax.bar(categories, tpg_tranche["ratio"], color=['#63E6E2','#427570','#000000'], width=0.3) 

# Ajout des étiquettes de ratio 
ax.bar_label(bar_tpg, labels=[f"×{x:.2f}".replace('.', ',') for x in tpg_tranche["ratio"]], padding=3)

ax.axhline(1, linestyle="--", color="grey", label="Mois ordinaire (sept. 2023)")

# Personnalisation des axes et de la légende
ax.set_xlabel('Tranche de PM selon la part d’aérien\nPannes d’oct. 2023 (Tammy et Philippe) ÷ pannes de sept. 2023, Guadeloupe')
ax.set_title("Plus le PM est aérien, plus l'impact cyclonique est important")
ax.set_ylabel('Multiplicateur des pannes')
ax.legend()
           
# Ajustement automatique de la mise en page
fig.tight_layout()                                               																	# range sans chevauchement
# --- Sortie Sauvegarde---------------------------------------------
fig.savefig(SORTIE / "v6_cyclone_aerien.svg", dpi=150, bbox_inches="tight")												# bbox_inches="tight" rogne les marges blanches inutiles							
plt.show()																																												# ouvre les fenêtres de graphiques - à fermer pour que le script se termine
