# ======================================================================================================
# Visuel Planche : planche_share.py (version de travail d'origine : visuel_planche_Tiza-v1.10.py ; seuls les chemins changent)
# Regroupe tout les visuels indicateurs
# ======================================================================================================
import pandas as pd                 																															# pandas : lecture et manipulation de series et dataframes
import matplotlib.pyplot as plt     																															# pyplot : le module de dessin de Matplotlib
import numpy as np																																								# numpy : lecture et manipulation de tableaux
import matplotlib.dates as mdates   																															# outils de Matplotlib pour les axes de dates
import sqlite3                                   																									# module SQLite livré avec Python, rien à installer
from pathlib import Path            																															# Path : construire des chemins de fichiers propres

RACINE  = Path(__file__).resolve().parents[2]   # racine du dépôt (scripts/visuels/ → ../..), quel que soit le dossier d'où on lance le script
DONNEES = RACINE / "sql" / "requetes"           # résultats des requêtes SQL (res_indicateurNN_….csv)
SORTIE  = RACINE / "images"                     # images publiées dans le dépôt

#FONCTIONS DESSINANT LES VISUELS 
def case_vide(ax, nom):
    """Remplissage provisoire : le nom de la case, au centre."""
    ax.set_title(nom)                                    # le titre au-dessus de la case
    ax.text(0.5, 0.5, nom, transform=ax.transAxes,       # au centre de la case, quelles que soient ses données
            ha="center", va="center", fontsize=20, color="grey")

### Fonction dessine_tuile : Copie adaptée de tuile_kpi_reiteration-Tiza-v1.1.py
def dessine_tuile(ax):
	# Lecture et chargement du fichier de données csv dans un tableau pandas df
	df_reit = pd.read_csv(DONNEES / "res_indicateur06_reiteration.csv", sep=";")

	# Chargement des tableaux 
	tx_reiteration=df_reit['taux_reiteration_pct'].iloc[0]
	tx_reiteration_txt=f"{tx_reiteration:.1f} %".replace(".", ",")						# met la virgule à la française

	nb_abotouches=df_reit['touches'].iloc[0]
	nb_abotouches_txt="sur " + f"{nb_abotouches:,}".replace(",", " ") + " abonnés touchés, GLP + MTQ, 2023-2025"		# séparateur de milliers
	libelle="des abonnés touchés par une panne\nen ont connu au moins deux"

	#########TUILE#########
	ax.axis("off")                             # masque le cadre, les graduations et les étiquettes d'axes

	ax.text(0.5, 0.75, tx_reiteration_txt,      # x = 0.5 : le milieu en largeur ; y = 0.75 : un peu au-dessus du milieu
	        transform=ax.transAxes,          		# « 0 à 1 dans le cadre », plutôt que les valeurs des données
	        ha="center", va="center",        		# ha : alignement horizontal ; va : alignement vertical
	        fontsize=40, fontweight="bold",			# taille et police en gras
	        bbox=dict(boxstyle="round", 				# boite aux coins arrondis autour du texte
	        facecolor="whitesmoke", 						# couleur de la boite
	        edgecolor="darkgrey"))   						

	ax.text(0.5, 0.35, libelle,       					# x = 0.5 : le milieu en largeur ; y = 0.35 : un peu au-dessous de la boite
	        transform=ax.transAxes,          		# « 0 à 1 dans le cadre », plutôt que les valeurs des données
	        ha="center", va="center",        		# ha : alignement horizontal ; va : alignement vertical
	        fontsize=18, fontweight="normal")  	# taille et police en epaisseur normale

	ax.text(0.5, 0.12, nb_abotouches_txt,       # x = 0.5 : le milieu en largeur ; y = 0.12 : un peu au-dessous du libellé
	        transform=ax.transAxes,          		# « 0 à 1 dans le cadre », plutôt que les valeurs des données
	        ha="center", va="center",        		# ha : alignement horizontal ; va : alignement vertical
	        fontsize=12, color='grey')  		 		# taille et couleur de la police

###

### Fonction dessine_v1 : Copie adaptée de visuel_01_parite_entree-Tiza-v1.2.py
def dessine_v1(ax):
	# Chargement des tableaux 
	# Lecture et chargement du fichier de données csv dans un tableau pandas df
	df_issue = pd.read_csv(DONNEES / "res_indicateur01_raccordement_issue.csv", sep=";")							
	df_reprise = pd.read_csv(DONNEES / "res_indicateur02_raccordement_reprise.csv", sep=";")					
	df_mes = pd.read_csv(DONNEES / "res_indicateur03_delai_mes.csv", sep=";")													

	#2 listes des 3 indicateurs par territoire, GLP et MTQ
	categories = ['Échecs\nsur les raccordements', 'Reprises malfaçons\nsur les réussis','Mise en service au-delà de 60j']

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

	# Dessine les deux séries de barres horizontales (barh) en decalant la position y vers le haut (- hauteur/2) et vers le bas (+ hauteur/2)
	rects1 = ax.barh(y - hauteur/2, valeurs_GLP, hauteur, label='Guadeloupe')
	rects2 = ax.barh(y + hauteur/2, valeurs_MTQ, hauteur, label='Martinique')

	# Personnalisation des axes et de la légende
	ax.set_xlim(0, 25)
	ax.set_xlabel('Part (%)\nPas de repère national sourcé pour les reprises')
	ax.set_title('Échecs-Reprises-Mise en service : parité des territoires en retrait du national')
	ax.set_yticks(y)
	ax.set_yticklabels(categories)

	ax.bar_label(rects1, labels=[f"{x:.1f} %".replace('.', ',') for x in rects1.datavalues], padding=3)			# la virgule à la française
	ax.bar_label(rects2, labels=[f"{x:.1f} %".replace('.', ',') for x in rects2.datavalues], padding=3)

	ax.vlines(6.27, ymin=-0.5, ymax=0.5, colors="grey", linestyles="dashed", label="Repère national")
	ax.vlines(x=14.7, ymin=1.5, ymax=2.5, colors="grey", linestyles="dashed")
	ax.invert_yaxis()
	ax.legend()

###

### Fonction dessine_v23 : Copie adaptée de visuel_02-03_taux_vs_volume-Tiza-v1.3.py
def dessine_v23(ax_vol, ax_taux):
	# Résultat de l'indicateur 04 : une ligne par territoire × mois
	df = pd.read_csv(DONNEES / "res_indicateur04_taux_pannes.csv", sep=";")

	# "2023-01" est du texte : on le convertit en vraie date pour que Matplotlib place les mois correctement sur l'axe du temps
	df["mois"] = pd.to_datetime(df["mois"], format="%Y-%m")

	# On sépare les deux territoires (filtre booléen, comme en pandas)
	glp = df[df["territoire"] == "GLP"]
	mtq = df[df["territoire"] == "MTQ"]

	# Figure Volume - 2 graphiques empilés (2 lignes, 1 colonne) qui partagent le même axe x (le temps)                 
	# ax_vol = l'étage du HAUT (volume) ; ax = l'étage du BAS (taux)                                    

	# Étage du HAUT : le VOLUME (nombre de pannes dans le mois)
	ax_vol.set_title("Taux ou volume : deux lectures du même réseau\nVolume : nombre de pannes")		# titre de la FEUILLE
	ax_vol.plot(glp["mois"], glp["pannes"], label="Guadeloupe")
	ax_vol.plot(mtq["mois"], mtq["pannes"], label="Martinique")

	# Repère : le volume de pannes du mois de Tammy, pour comparer
	ax_vol.axhline(3320, color="grey", linestyle=":", linewidth=1, label="Volume d'oct. 2023 (Tammy) : 3 320")

	ax_vol.set_ylim(0, 4500)                          																								# volume aussi à partir de zéro
	ax_vol.set_ylabel("Pannes dans le mois")
	#ax_vol.legend(loc="upper left", fontsize=8)

	# Le "locator" choisit OÙ mettre les graduations : ici janvier, avril, juillet, octobre
	ax_vol.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))

	# Le "formatter" choisit COMMENT les écrire : mois/année
	ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))

	# Réglage de la taille des étiquettes : taille 8, inclinées à 45°
	ax_vol.tick_params(axis="x", labelbottom=False)   # garde l'axe partagé, mais n'écrit les dates qu'en bas

	# Bandes grises : saisons cycloniques (juin → novembre); axvspan = "vertical span", une bande verticale entre deux x
	for a in (ax_vol, ax_taux):
		for annee in [2023, 2024, 2025]:
		    a.axvspan(pd.Timestamp(f"{annee}-06-01"),				# début de bande
		               pd.Timestamp(f"{annee}-11-30"),			# fin de bande
		               color="grey", alpha=0.15,						# alpha = transparence (0 invisible, 1 opaque)
		               # une seule entrée dans la légende, pas trois :
		               label="Saison cyclonique (juin-nov.)" if annee == 2023 else None)
	      
	ax_vol.legend(loc="upper left", fontsize=8)

	# Ligne de référence nationale; axhline = "horizontal line", une ligne horizontale sur toute la largeur
	ax_taux.axhline(1.79, color="black", linestyle="--", linewidth=1, label="Moyenne nationale (1,79 %)")
	           
	# Une courbe par territoire : x = les mois, y = le taux de panne
	ax_taux.plot(glp["mois"], glp["taux_panne_pct"], label="Guadeloupe")
	ax_taux.plot(mtq["mois"], mtq["taux_panne_pct"], label="Martinique")

	# L'axe vertical part de zéro
	ax_taux.set_ylim(0, 5)

	# Étiquettes avec flèche sur les pics cycloniques
	ax_taux.annotate("juin 2023\nMTQ : Bret 3,09 %\nGLP : Gert 2,98 %",																		# le texte (\n = retour à la ligne)
		            xy=(pd.Timestamp("2023-06-01"), 3.09),																							# le point VISÉ par la flèche
		            xytext=(pd.Timestamp("2023-02-01"), 3.5),																						# où POSER le texte
		            arrowprops=dict(arrowstyle="->"),																										# le style de flèche
		            fontsize=9)
	ax_taux.annotate("oct. 2023 - Tammy + Philippe\nGLP : 4,38 %",    																			
		            xy=(pd.Timestamp("2023-10-01"), 4.38),        																			
		            xytext=(pd.Timestamp("2023-12-01"), 4.1),     																			
		            arrowprops=dict(arrowstyle="->"),             																			
		            fontsize=9)

	ax_taux.annotate("juil. 2024 - Beryl\nMTQ : 3,19 %\nGLP : 2,82 %",              												
		            xy=(pd.Timestamp("2024-07-01"), 3.19),        																			
	            xytext=(pd.Timestamp("2024-08-01"), 3.3),     																				
	            arrowprops=dict(arrowstyle="->"),             																				
	            fontsize=9)
	            
	ax_taux.annotate("août 2025 - Erin \nMTQ : 2,79 %\nGLP : 3,05 %",                  										
	            xy=(pd.Timestamp("2025-08-01"), 3.05),        																				
	            xytext=(pd.Timestamp("2025-09-01"), 3.1),    																					
	            arrowprops=dict(arrowstyle="->"),             																				
	            fontsize=9)
	                                    
	# Habillage : titre, libellé de l'axe vertical, légende
	ax_taux.set_title("Taux de panne mensuel, 2023-2025")
	ax_taux.set_ylabel("Abonnés en panne (%)")
	ax_taux.legend(loc="lower right", fontsize=8, ncols=2)   # ncols : la légende sur 2 colonnes, donc 2 lignes au lieu de 4

###

### Fonction dessine_v4 : Copie adaptée de visuel_04_mttr-Tiza-v1.3.py
def dessine_v4(ax):
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

	# Dessine les boites à moustache 
	bp=ax.boxplot(data_boxes, orientation="horizontal", tick_labels=data_labels, whis=1.5, showmeans=True, showfliers=False)

	ax.legend([bp["means"][0], bp["medians"][0]],    																									# le 1er triangle et le 1er trait, comme modèles
	          ["MTTR (moyenne)", "Médiane"])         																									# le texte affiché à côté de chaque modèle
	         
	ax.set_title("Délai de rétablissement par segment")
	ax.set_xlabel("Délai (jours)\nPoints isolés masqués : 3,8 % des pannes, jusqu'à 31 jours")
	ax.set_xlim(left=0)

	ax.axhline(4.5, color="black", linestyle="--", linewidth=1)																				# sépare les segments du réseau de NA, qui n'est pas une position).
	
###

### Fonction dessine_v5 : Copie adaptée de visuel_05_pannes-malfacon-Tiza-v1.3.py
def dessine_v5(ax):
	# Lecture et chargement du fichier de données csv dans un tableau pandas df
	df_malfacons_pannes = pd.read_csv(DONNEES / "res_indicateur07_malfacon-cause.csv", sep=";").sort_values(by="n_malfacon", ascending=False)

	# Chargement des tableaux 
	labels_natures=df_malfacons_pannes['quoi']
	dfp=df_malfacons_pannes['n_pannes']
	dfm=df_malfacons_pannes['n_malfacon']
	dfa=df_malfacons_pannes['n_pannes'] - df_malfacons_pannes['n_malfacon'] 
	dpct=df_malfacons_pannes['pct_malfacon']

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
	# Dessine les deux series de barres horizontales empilées gauche/droite
	ax.set_xlim(0, 32000)
	
	bar_dfm=ax.barh(libelles_causes, dfm, label="Malfaçons - total 44 180", color="firebrick")
	bar_dfa=ax.barh(libelles_causes, dfa, left=dfm, label="Autres - total 106 347\nEnsemble des pannes - total 150 527", color="lightgrey")

	# Personnalisation des axes et de la légende
	ax.set_xlabel('Nombre de pannes\n% = part de malfaçon dans les pannes de chaque cause')
	ax.set_title('Malfaçons sur les pannes selon leurs causes :\nprès d’une panne sur trois')

	ax.bar_label(bar_dfm, labels=[f"{x:.1f} %".replace('.', ',') for x in dpct], padding=3)						#la virgule à la française
	ax.invert_yaxis()
	ax.legend(loc="lower right", fontsize=8)

###

### Fonction dessine_v6 : Copie adaptée de visuel_06_cyclone_aerien-Tiza-v1.1.py
def dessine_v6(ax):
	# Lecture et chargement du fichier de données csv dans un tableau pandas df - tpg = Tranche PM Guadeloue
	df_tpg = pd.read_csv(DONNEES / "res_indicateur08_cyclone_tranche-aerienpm.csv", sep=";")

	# Chargement des tableaux 
	#Tableaux de controle commentés - à enlever en version finale
	tpg_tranche						= df_tpg.set_index('tranche')																								# les noms de tranche deviennent l'index
	tpg_tranche["ratio"]	= tpg_tranche['oct'] / tpg_tranche['sept'] 
	tpg_tranche 					= tpg_tranche.loc[["enterré", "mixte", "aérien"]] 

	categories						=	["Enterré\n(< 40 % aérien)", "Mixte\n(40 à 70 %)", "Aérien\n(≥ 70 %)"]

	#########GRAPHIQUE#########

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
	           	
###

### Fonction dessine_v7 : Copie adaptée de visuel_07_dilution_tammy-Tiza-v1.0.py
def dessine_v7(ax):
	# Lecture et chargement du fichier de données csv dans un tableau pandas df
	df_dilution = pd.read_csv(DONNEES / "res_indicateur07b_malfacon_tammy.csv", sep=";")

	# Chargement des tableaux
	mois									=	df_dilution['mois']
	n_autres							=	df_dilution['n_pannes'] - df_dilution['n_malfacons']
	n_malfacons						=	df_dilution['n_malfacons']
	taux									=	df_dilution['pct_malfacon']

	# Dictionnaire de traduction des dates numériques en libellé texte
	dico_libelles_mois	=	{
	"2023-08": "août\n2023",
	"2023-09": "sept.\n2023",
	"2023-10": "oct. 2023\n(Tammy)",
	"2023-11": "nov.\n2023",
	"2023-12": "déc.\n2023",
	}
	libelles_mois = df_dilution["mois"].map(dico_libelles_mois)  																	# chaque code est remplacé par sa valeur du dico
		
	#########Graphique à barres verticales #########

	# Dessine les deux series de barres horizontales empilées gauche/droite
	bar_dfm=ax.bar(libelles_mois, n_malfacons, label="Pannes dues à une malfaçon", color="firebrick")
	bar_dfa=ax.bar(libelles_mois, n_autres, bottom=n_malfacons, color="lightgrey", label='Autres pannes')

	# Personnalisation des axes et de la légende\n% = part de malfaçon sur le mois
	ax.set_xlabel("Guadeloupe : Mois d'août 2023 à décembre 2023\n% = part de malfaçons")
	ax.set_ylabel('Nombre de pannes')	
	ax.set_title("Stagnation des malfaçons pendant Tammy, alors que les autres pannes explosent")
	ax.bar_label(bar_dfm, labels=[f"{x:.1f} %".replace('.', ',') for x in taux], padding=3)						# remplacement du separateur décimal "." de la valeur la valeur numerique par la virgule à la française

###

### Fonction dessine_note
def dessine_note(ax):
	# Lecture et chargement du fichier de données csv dans un tableau pandas df
	note_txt="Données : \nsimulées (base v1, graine figée), \ncalées sur des ancres réelles (Arcep, cas #1) \net sur mon expérience terrain\n\nPérimètre : \nGLP = 971 + 977 + 978, MTQ = 972, sur 2023-2025\n\nPlus de détail : \nle rapport (sections 4 et 5) \net le code sur GitHub."

	#########TUILE#########
	ax.axis("off")                             # masque le cadre, les graduations et les étiquettes d'axes

	ax.text(0.02, 0.98, note_txt,      					# x = 0.5 : le milieu en largeur ; y = 0.75 : un peu au-dessus du milieu
	        transform=ax.transAxes,          		# « 0 à 1 dans le cadre », plutôt que les valeurs des données
	        ha="left", va="top",        				# ha : alignement horizontal ; va : alignement vertical
	        fontsize=12, fontweight="normal",		# taille et police en normal
	        bbox=dict(boxstyle="round", 				# boite aux coins arrondis autour du texte
	        facecolor="whitesmoke", 						# couleur de la boite
	        edgecolor="darkgrey"))   						

###

#########GRIDSPEC#########
fig 			= plt.figure(figsize=(20, 12), layout="constrained")	# la feuille ; "constrained" gère les espaces entre case

gs 				= fig.add_gridspec(3, 3, height_ratios=[1, 1.4, 1])   # 3 lignes × 3 colonnes ; la ligne du milieu, plus haute, pour le V2+3

ax_tuile	= fig.add_subplot(gs[0, 0])        										# une case : ligne 0, colonne 0
ax_v1    	= fig.add_subplot(gs[0, 1])        										# ligne 0, colonne 1
ax_v4			= fig.add_subplot(gs[0, 2])     											# ligne 0, colonne 2

sous 			= gs[1, 0:2].subgridspec(2, 1)                    		# ligne 1, colonnes 0 à 2 (2 exclue !) fusionnées, puis coupées en 2 étages
ax_vol  	= fig.add_subplot(sous[0])                     				# étage du haut : le volume
ax_taux 	= fig.add_subplot(sous[1], sharex=ax_vol)      				# étage du bas : le taux, axe x partagé avec celui du haut

ax_v5   	= fig.add_subplot(gs[1, 2])     											# ligne 1, colonne 2
ax_v6   	= fig.add_subplot(gs[2, 0])     											# ligne 2, colonne 0
ax_v7   	= fig.add_subplot(gs[2, 1])     											# ligne 2, colonne 1
ax_note 	= fig.add_subplot(gs[2, 2])     											# ligne 2, colonne 2

dessine_tuile(ax_tuile)
dessine_v1(ax_v1)
dessine_v23(ax_vol, ax_taux)
dessine_v4(ax_v4)
dessine_v5(ax_v5)
dessine_v6(ax_v6)
dessine_v7(ax_v7)
dessine_note(ax_note)

fig.suptitle("Observatoire qualité FttH Antilles · cas #3\n"
             "On paie pour déployer, mais la qualité ne suit pas : malfaçons chroniques et aérien exposé aux cyclones",
             fontsize=18)
fig.savefig(SORTIE / "planche_share.svg", dpi=150)            	# une seule sauvegarde, à la fin
