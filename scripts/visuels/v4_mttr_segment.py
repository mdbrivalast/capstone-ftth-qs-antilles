# ======================================================================================================
# Visuel 4 : v4_mttr_segment.py (version de travail d'origine : visuel_04_mttr-Tiza-v1.3.py ; seuls les chemins changent) MTTR 
# Indicateur 5 : MTTR par segment (moyenne ; médiane calculée à part — pas de fonction native SQLite)
# Résultat attendu (base v1), moyenne en jours : D0 1,16 · D1 1,44 · D2 3,23 · D3 4,12 · NA 3,19
# Médianes (calculées à part en Python)      : D0 1,04 · D1 1,29 · D2 2,88 · D3 3,68 · NA 2,86
# Graphique de boite à moustache
# ======================================================================================================
import pandas as pd                 																															# pandas : lecture et manipulation du tableau
import matplotlib.pyplot as plt     																															# pyplot : le module de dessin de Matplotlib
from pathlib import Path            																															# Path : construire des chemins de fichiers propres
import sqlite3                                   																									# module SQLite livré avec Python, rien à installer

RACINE  = Path(__file__).resolve().parents[2]   # racine du dépôt (scripts/visuels/ → ../..), quel que soit le dossier d'où on lance le script
DONNEES = RACINE / "sql" / "requetes"           # résultats des requêtes SQL (res_indicateurNN_….csv)
SORTIE  = RACINE / "images"                     # images publiées dans le dépôt
# Dossier de sortie des images

# Connexion à la base, rangée dans le même dossier que le script
con = sqlite3.connect(RACINE / "cap3v5.db")
segments = ['D0', 'D1', 'D2', 'D3','NA']
data_boxes=[]
data_labels=[]

# La requete est recrée dans le script à partir du fichier requete sql req_indicateur05_mttr.sql pour y ajouter les libellés des segments 
for s in segments:
	query="""SELECT fs.temps_retablissement AS delai_j, rts.libelle AS libelle
	FROM fait_signalisation fs
	JOIN dim_cause dc ON dc.code_cause = fs.fk_code_cause_sign
	JOIN ref_troncon_segment rts ON rts.troncon = dc.fk_troncon_reseau
	WHERE rts.segment = ?;"""
	df=pd.read_sql(query, con, params=(s,))
	data_boxes.append(df['delai_j'].to_numpy())
	libelle_segment = df['libelle'].iloc[0]																													#recupere la valeur libéllé correspondant au segment.
	effectif_txt = len(df)
	effectif_txt=f"{effectif_txt:,}".replace(",", " ")																							# ":," = "mets un séparateur de milliers" (convention anglaise), puis remplace la virgule par une espace '16 073'
	data_labels.append(f"{s} - {libelle_segment}\n{effectif_txt} pannes")

con.close()

fig, ax = plt.subplots()

# Dessine les boites à moustache 
bp=ax.boxplot(data_boxes, orientation="horizontal", tick_labels=data_labels, whis=1.5, showmeans=True, showfliers=False)

ax.legend([bp["means"][0], bp["medians"][0]],    																									# le 1er triangle et le 1er trait, comme modèles
          ["MTTR (moyenne)", "Médiane"])         																									# le texte affiché à côté de chaque modèle
         
ax.set_title("Délai de rétablissement par segment")
ax.set_xlabel("Délai (jours)\nPoints isolés masqués : 3,8 % des pannes, jusqu'à 31 jours")
ax.set_xlim(left=0)

ax.axhline(4.5, color="black", linestyle="--", linewidth=1)																				# sépare les segments du réseau de NA, qui n'est pas une position).

# Ajustement automatique de la mise en page
fig.tight_layout()
# --- Sortie Sauvegarde---------------------------------------------
fig.savefig(SORTIE / "v4_mttr_segment.svg", dpi=150, bbox_inches="tight")															# bbox_inches="tight" rogne les marges blanches inutiles
plt.show()																																												# ouvre les fenêtres de graphiques - à fermer pour que le script se termine		
