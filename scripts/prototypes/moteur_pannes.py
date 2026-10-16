# MOTEUR DE SIMULATION DES PANNES FTTH — version commentée
#========================================================
#  moteur_pannes_v2-Tiza.py  —  Cas #3 « Mesurer l'invisible » (FTTH OM)
#  MOTEUR PANNES complet : volume + cause + malfaçon + MTTR.
#  v2 : Tammy 1.7, MTTR log-normale ancree directement sur l'expertise OM.
#
#Objectif
#--------
#Construire un jeu de données synthétique de pannes pour la Guadeloupe (GLP)
#et la Martinique (MTQ), sur les années 2023 à 2025.
#
#Pour chaque panne simulée, le script attribue notamment :
#- une cause tirée depuis p_malfacon_mapping.csv ;
#- une probabilité de malfaçon, utilisée pour tirer 0 (non) ou 1 (oui) ;
#- un identifiant d'abonné simulé ;
#- un délai de réparation (MTTR) en jours ;
#- un territoire, un mois et une origine (base ou cyclone).
#

#ATTENTION
#---------
#Les résultats sont simulés : ce ne sont pas des relevés réels panne par panne.
#Les paramètres (taux de panne, scores, probabilités, médianes de réparation,
#effets cycloniques) influencent directement les résultats.
#Les deux fichiers CSV d'entrée doivent se trouver dans le même dossier que
#ce script, sauf si vous modifiez les chemins de lecture ci-dessous.
#

# ---------------------------------------------------------------------
# 0. IMPORTS ET GRAINE ALÉATOIRE
# ---------------------------------------------------------------------
import numpy as np
import pandas as pd

# La graine rend la simulation reproductible :
# avec les mêmes fichiers d'entrée, paramètres et versions de bibliothèques,
# les tirages aléatoires sont normalement les mêmes.
SEED = 20231020
rng  = np.random.default_rng(SEED)


# ---------------------------------------------------------------------
# PARAMÈTRES GÉNÉRAUX DE LA SIMULATION
# ---------------------------------------------------------------------

# Hypothèse : 2,5 % du stock moyen d'abonnés génère une panne chaque mois.
# Exemple : pour un stock moyen de 100 000 abonnés, cela donne environ
# 100 000 * 0,025 = 2 500 pannes simulées pour le mois.
TAUX_PANNE_MENSUEL = 0.025

# Nombre d'abonnés à la fin de l'année 2022, utilisé comme point de départ
# pour calculer le stock moyen mensuel à partir de 2023.
STOCK_FIN_2022 = {
    "GLP": 52000,  # Guadeloupe
    "MTQ": 36000,  # Martinique
}

# --- Levier 4 : cyclone "mois reels" (Tammy abaisse a 1.7 par decision Tiza) ---
MULT_CYCLONE = {
    ("GLP", "2023-10"): 1.70,  # Tammy : hypothèse fixée à 1,7
    ("GLP", "2023-06"): 1.15,
    ("GLP", "2024-07"): 1.10,
    ("GLP", "2025-08"): 1.20,
    ("MTQ", "2023-06"): 1.20,
    ("MTQ", "2024-07"): 1.25,
    ("MTQ", "2025-08"): 1.10,
}

# Association entre le tronçon technique extrait du code de cause et
# le segment utilisé pour analyser les délais de réparation.
TRONCON_SEGMENT = {
    "NRO": "D1",
    "PM": "D2",
    "PBO": "D3",
    "BPE": "D2",
    "PTO": "D3",
    "BACK": "D0",
    "MULTI": "NA",
}

# --- Levier 5 : MTTR (jours). Medianes OM = dire d'expert terrain (Tiza).
# Médianes de délai de réparation en jours, par segment.
# MTTR signifie ici "Mean Time To Repair", mais le paramètre choisi pour
# chaque segment est une MÉDIANE, pas une moyenne.
#     Ancrage DIRECT OM (pas de x2 : ses observations sont deja ultramarines).
#     Loi log-normale : mediane = exp(mu) -> mu = ln(mediane) ; sigma = etalement du log.
MTTR_MEDIAN_OM = {
    "D0": 1.00,
    "D1": 1.25,
    "D2": 2.75,
    "D3": 3.50,
    "NA": 2.75,
}

# Dispersion de la loi log-normale.
# Une valeur plus élevée crée davantage de délais très longs.
# Une loi log-normale produit des valeurs positives et une distribution
# asymétrique : quelques réparations peuvent durer bien plus longtemps
# que la médiane.
SIGMA_LOG = 0.45	# -> P90 ~1.8x la mediane, queue vers 5-7 j pour D3
# Dans un mois où un multiplicateur cyclonique est supérieur à 1,
# on multiplie la médiane de réparation par 1,5.
# Ce facteur représente l'hypothèse d'équipes saturées ou d'accès difficiles.
RALLONGE_CYCLONE = 1.5	 # mois cyclonique : equipes saturees/acces coupes (fixe, ajustable)


# ---------------------------------------------------------------------
# LECTURE ET ENRICHISSEMENT DU MAPPING DES CAUSES
# dim_cause enrichie
# ---------------------------------------------------------------------

# Le fichier de mapping décrit les causes possibles.
# Colonnes utilisées plus loin :
# - code_cause : code complet, par exemple ENV_PBO_PANNE ;
# - quoi       : famille de cause, par exemple ENV ;
# - portee     : PANNE, RACCO, RACCOPANNE, etc. ;
# - score      : poids relatif pour le tirage des causes ;
# - p_malfacon : probabilité de malfaçon pour cette cause.
dim = pd.read_csv("./Datasets/p_malfacon_mapping.csv")

# Le tronçon est extrait du code_cause en retirant :
#   1) le préfixe correspondant à "quoi" et le séparateur "_";
#   2) le suffixe correspondant à "portee" et le séparateur "_".
# Exemple : code_cause="ENV_PBO_PANNE" -> tronçon="PBO".
# Cette extraction suppose que les codes respectent bien ce format.
dim["troncon"] = [
    c[len(q) + 1 : -(len(p) + 1)]
    for c, q, p in zip(dim.code_cause, dim.quoi, dim.portee)
]

# Ajout du segment associé au tronçon. Si un tronçon n'est pas présent
# dans TRONCON_SEGMENT, sa valeur de segment sera manquante (NaN).
dim["segment"] = dim.troncon.map(TRONCON_SEGMENT)

# Marqueur valant 1 pour les causes environnementales (ENV) sur les
# tronçons aériens PM, PBO ou PTO ; 0 pour les autres causes.
# Ce marqueur sert à construire le volume de pannes supplémentaires
# attribuées aux mois cycloniques.
dim["sensible_aerien"] = (
    (dim.quoi == "ENV") & (dim.troncon.isin(["PM", "PBO", "PTO"]))
).astype(int)

# Le moteur de volume de base tire uniquement parmi les lignes dont
# la portée est PANNE.
panne = dim[dim.portee == "PANNE"].copy()

# Le surcroît cyclonique tire uniquement parmi les pannes sensibles
# aux tronçons aériens définis juste au-dessus.
aerien = panne[panne.sensible_aerien == 1].copy()

# Affichage de contrôle : permet de vérifier les données enrichies.
#print("CONTROLE — mapping complet :")
#print(dim.to_string(index=False))
#print("\nCONTROLE — causes de portée PANNE :")
#print(panne.to_string(index=False))
#print("\nCONTROLE — causes PANNE sensibles aux tronçons aériens :")
#print(aerien.to_string(index=False))


# ---------------------------------------------------------------------
# CONSTRUCTION DU CALENDRIER ET DU STOCK MOYEN MENSUEL  - Mensualisation du stock
# ---------------------------------------------------------------------

parc = pd.read_csv("./Datasets/parc_annuel_reel.csv")
# La liste cal recevra une ligne par territoire et par mois.
cal=[]
for terr in ["GLP","MTQ"]:
    # Stock de départ pour le territoire concerné.
    sfin=STOCK_FIN_2022[terr]
    for an in [2023,2024,2025]:
        # Récupère la ligne annuelle correspondant au territoire et à l'année.
        # .iloc[0] prend la première ligne trouvée : le CSV doit donc contenir
        # une ligne pour chaque couple territoire/année.
        p=parc[(parc.territoire==terr)&(parc.annee==an)].iloc[0]; fm=p.nb_raccordements_annee/12

        # Nombre de nouveaux raccordements supposé réparti uniformément
        # sur les 12 mois de l'année.
        for m in range(1,13):
            # Estimation du stock moyen pendant le mois.
            # (mois - 0,5) place le calcul au milieu du mois :
            # mois 1 -> stock de départ + une demi-mensualité ;
            # mois 12 -> stock de départ + 11,5 mensualités.
	
            cal.append({"territoire":terr,"ym":f"{an}-{m:02d}","stock_moyen":sfin+fm*(m-0.5)})
        # À la fin de l'année, tous les raccordements annuels sont ajoutés
        # au stock de départ de l'année suivante.
        sfin+=fm*12
# Transformation de la liste de dictionnaires en tableau pandas.
cal=pd.DataFrame(cal)

#print("\nCONTROLE — calendrier mensuel et stock moyen :")
#print(cal.to_string(index=False))


# ---------------------------------------------------------------------
# FONCTION DE TIRAGE DES CAUSES
# Moteur : volume base + surcroit aerien, cause, malfaçon, MTTR
# ---------------------------------------------------------------------
def tire(df,n):
    if n<=0: return []
    return rng.choice(df.index.to_numpy(), size=n, p=(df.score/df.score.sum()).to_numpy())

# ---------------------------------------------------------------------
# MOTEUR PRINCIPAL : SIMULATION DES PANNES MOIS PAR MOIS
# ---------------------------------------------------------------------

# Chaque élément de faits sera un tableau contenant les pannes simulées
# pour un mois et un territoire. On les réunira à la fin.
faits=[]
for _,r in cal.iterrows():
    terr,ym,stock=r.territoire,r.ym,r.stock_moyen
    # A. Volume de pannes de base :
    # stock moyen multiplié par le taux mensuel, arrondi à l'entier.
    n_base=int(round(stock*TAUX_PANNE_MENSUEL))
    # B. Effet du mois cyclonique.
    # Si le couple (territoire, mois) n'est pas dans le dictionnaire,
    # le multiplicateur vaut 1 et aucun supplément n'est ajouté.
    mult=MULT_CYCLONE.get((terr,ym),1.0)
    # Nombre de pannes supplémentaires liées au cyclone.
    # Exemple : n_base=1000 et multiplicateur=1,7 -> supplément=700.
    n_cyclo=int(round(n_base*(mult-1)))
    # C. Tirage des causes :
    # - n_base causes parmi toutes les causes de portée PANNE ;
    # - n_cyclone causes supplémentaires parmi les pannes aériennes ciblées.
    # Les deux listes d'index sont concaténées.
    idx=list(tire(panne,n_base))+list(tire(aerien,n_cyclo))
    # Si aucun événement n'a été généré, passer au mois suivant.
    if not idx: continue
    # Sélection des lignes de mapping correspondantes.
    # Un même index peut apparaître plusieurs fois : c'est normal,
    # car une cause peut être tirée plusieurs fois.
    sub=dim.loc[idx].copy()
    sub["malfacon"]=(rng.random(len(sub))<sub.p_malfacon.to_numpy()).astype(int)
    # D. Tirage de la malfaçon pour chaque panne.
    # rng.random(...) génère un nombre entre 0 et 1 pour chaque ligne.
    # Si ce nombre est inférieur à p_malfacon, malfacon vaut 1 ; sinon 0.
    # Exemple : p_malfacon=0,40 signifie 40 % de chance pour chaque tirage.
    # E. Identifiant d'abonné synthétique.
    # Entier entre 1 et int(stock), borne supérieure exclue par integers().
    # Ce n'est PAS un véritable identifiant client et il n'est pas garanti
    # qu'un abonné n'apparaisse qu'une seule fois dans les pannes simulées.
    sub["abonne_id"]=rng.integers(1,int(stock)+1,size=len(sub))
    # MTTR : log-normale par segment, rallongee les mois cycloniques
    # F. Calcul du délai de réparation.
    # On récupère la médiane de référence associée au segment de chaque panne.
    med=sub.segment.map(MTTR_MEDIAN_OM).to_numpy()

    # Pendant un mois cyclonique (multiplicateur > 1), on augmente les
    # médianes de référence par le facteur RALLONGE_CYCLONE.
    if mult>1.0: med=med*RALLONGE_CYCLONE

    # Tirage dans une loi log-normale :
    # - le premier paramètre est ln(médiane) ;
    # - SIGMA_LOG contrôle la dispersion ;
    # - les valeurs obtenues sont positives et souvent asymétriques.
    # On arrondit ensuite le délai à deux décimales.
    sub["mttr_jours"]=np.round(rng.lognormal(np.log(med),SIGMA_LOG),2)
    sub["territoire"]=terr; sub["ym"]=ym; sub["origine"]=["base"]*n_base+["cyclone"]*n_cyclo

    # G. Métadonnées pour pouvoir filtrer les résultats par territoire,
    # mois et origine de la panne.

    # Les n_base premiers événements viennent du tirage de base ; les
    # n_cyclone suivants viennent du tirage supplémentaire cyclonique.
    faits.append(sub)

# Fusion de tous les mois/territoires en un seul tableau.
# ignore_index=True crée un index continu de 0 à nombre_de_lignes - 1.
fait=pd.concat(faits,ignore_index=True)

# Ajout d'un identifiant technique unique pour chaque ligne de panne.
# Exemple : SIG-0000001, SIG-0000002, etc.
fait.insert(0,"sig_id",["SIG-"+str(i+1).zfill(7) for i in range(len(fait))])

# ---------------------------------------------------------------------
# CONTRÔLES ET INDICATEURS RÉCAPITULATIFS
# ---------------------------------------------------------------------

print("=== RAPPEL (inchange par le MTTR) ===")
print(f"  pannes totales : {len(fait):,} | part malfaçon globale : {fait.malfacon.mean():.1%}")
# Filtre sur la Guadeloupe en octobre 2023, mois paramétré pour Tammy.
oct23=fait[(fait.territoire=='GLP')&(fait.ym=='2023-10')]
print(f"  GLP 2023-10 (Tammy 1.7) : {len(oct23)} pannes | part malfaçon {oct23.malfacon.mean():.1%}  (formule 0.29/1.7={0.29/1.7:.0%})")

print("\n=== MTTR par segment (jours) : mediane vs moyenne vs P90 ===")

# groupby regroupe les pannes par segment.
# median() : valeur qui partage les observations en deux moitiés ;
# mean()   : moyenne arithmétique ;
# quantile(0.9) : 90 % des délais sont inférieurs ou égaux à cette valeur ;
# size()   : nombre de pannes dans le segment.
g=fait.groupby("segment").mttr_jours
rec=pd.DataFrame({"mediane":g.median(),"moyenne":g.mean(),"P90":g.quantile(.9),"n":g.size()}).round(2)
# Présente les segments dans un ordre choisi.
print(rec.reindex(["D0","D1","D2","D3","NA"]).to_string())
print(f"\n  -> GLOBAL : mediane {fait.mttr_jours.median():.2f} j | moyenne {fait.mttr_jours.mean():.2f} j "
      f"(moyenne > mediane = l'asymetrie que tu voyais)")

print("\n=== Indicateurs de delai (facon observatoire) ===")
# Proportion de pannes dont le délai simulé ne dépasse pas deux jours.
print(f"  repare sous 48h (<=2j) : {(fait.mttr_jours<=2).mean():.1%}")
# Proportion de pannes dont le délai simulé dépasse cinq jours.
print(f"  au-dela de 5 jours     : {(fait.mttr_jours>5).mean():.1%}  (tes cas 'parfois plus')")

# Comparaison des délais D3 en Guadeloupe entre septembre 2023 (mois normal)
# et octobre 2023 (mois paramétré pour Tammy).
print("\n=== Effet cyclone sur le DELAI (GLP, D3 branchement) ===")
d3=fait[(fait.territoire=='GLP')&(fait.segment=='D3')]
for lbl,ym in [("mois normal (2023-09)","2023-09"),("Tammy (2023-10)","2023-10")]:
    s=d3[d3.ym==ym]
    # Si le filtre ne renvoie aucune ligne, la médiane serait NaN.
    print(f"  {lbl:22s}: MTTR median {s.mttr_jours.median():.2f} j sur {len(s)} pannes D3")

# ---------------------------------------------------------------------
#  DISTRIBUTION DES DÉLAIS EN TRANCHES (POUR UN GRAPHIQUE)
# ---------------------------------------------------------------------
# histogramme des delais (buckets) pour le graphe
buckets=pd.cut(fait.mttr_jours,[0,1,2,3,4,5,6,7,100],
               labels=["0-1","1-2","2-3","3-4","4-5","5-6","6-7","7+"])
# value_counts(normalize=True) calcule la proportion de chaque tranche.
# reindex(...) impose l'ordre souhaité, même si une tranche est vide.
# Multiplication par 100 et arrondi à une décimale : pourcentages affichés.
h=(buckets.value_counts(normalize=True).reindex(["0-1","1-2","2-3","3-4","4-5","5-6","6-7","7+"])*100).round(1)
print("\n=== Distribution des MTTR (% des pannes) ===")
print(h.to_string())


# ---------------------------------------------------------------------
# EXPORT DU RÉSULTAT
# ---------------------------------------------------------------------

# Exporte le tableau final dans un fichier CSV.
# index=False évite d'ajouter une colonne d'index pandas inutile.
# Le fichier sera créé dans le dossier depuis lequel le script est lancé.
fait.to_csv("./Datasets/fait_signalisation_v2-tiza.csv",index=False)
print(f"\n[fichier] fait_signalisation_v2-tiza.csv ({len(fait):,} lignes, colonne mttr_jours ajoutee)")
# Affiche les pourcentages des tranches dans l'ordre du tableau histogramme.
print("HIST:", list(h.values))
