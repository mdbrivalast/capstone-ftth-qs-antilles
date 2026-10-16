# =====================================================================
#  moteur_pannes_proto.py  —  Cas #3 « Mesurer l'invisible » (FTTH OM)
#  MOTEUR PANNES (1/2) — prototype en pandas/numpy.
#
#  Principe : le reel fixe l'enveloppe (parc + taux de base ARCEP uplifte
#  OM), l'expert fixe la repartition fine (score + p_malfacon + cyclone).
#  Travaille sur le STOCK d'abonnes (les pannes frappent le parc en vie).
#  Les raccordements (flux) = moteur 2, plus tard.
#
#  Sorties : fait_signalisation (une ligne = une panne signalee) + controles.
#  Reproductible : seed fixe.
# =====================================================================
import numpy as np, pandas as pd

SEED = 20231020                       # clin d'oeil Tammy (20 oct 2023), fige la repro
rng  = np.random.default_rng(SEED)

TAUX_PANNE_MENSUEL = 0.025            # 2,5 %/mois = national 1,79 % x uplift OM 1,4 (FIGE)
STOCK_FIN_2022 = {"GLP": 52000, "MTQ": 36000}   # deduit : stock_2023 - flux_2023

# --- Table cyclonique "mois reels" (MA PROPOSITION, a valider par Tiza) ---
#  Seul Tammy (GLP 2023-10) = vrai pic aerien ; le reste = coupures courant
#  sans destruction => petit facteur. Tout mois absent = 1.0 (rien).
MULT_CYCLONE = {
    ("GLP","2023-10"): 1.80,   # Tammy cat.1, poteaux Desirade, reseau aerien HS  <-- LE pic
    ("GLP","2023-06"): 1.15,   # Gert au large
    ("GLP","2024-07"): 1.10,   # Beryl passe au sud, GLP peu concerne
    ("GLP","2025-08"): 1.20,   # Erin, rafales ~120 km/h, pas de destruction majeure
    ("MTQ","2023-06"): 1.20,   # Bret, vigilance rouge, quasi aucun degat
    ("MTQ","2024-07"): 1.25,   # Beryl frole la Martinique
    ("MTQ","2025-08"): 1.10,   # saison faible
}

TRONCON_SEGMENT = {"NRO":"D1","PM":"D2","PBO":"D3","BPE":"D2",
                   "PTO":"D3","BACK":"D0","MULTI":"NA"}

# ---------------------------------------------------------------------
# 1. Referentiel des causes (dim_cause enrichie) depuis le mapping p_malfacon
# ---------------------------------------------------------------------
dim = pd.read_csv("/tmp/p_malfacon_mapping.csv")   # code_cause, quoi, portee, score, p_malfacon
# troncon = le morceau du milieu du triplet (quoi_<TRONCON>_portee)
dim["troncon"] = [c[len(q)+1:-(len(p)+1)] for c,q,p in
                  zip(dim.code_cause, dim.quoi, dim.portee)]
dim["segment"] = dim.troncon.map(TRONCON_SEGMENT)
dim["sensible_aerien"] = ((dim.quoi=="ENV") &
                          (dim.troncon.isin(["PM","PBO","PTO"]))).astype(int)

# Sous-ensembles de tirage pour le MOTEUR PANNES :
panne   = dim[dim.portee=="PANNE"].copy()                       # 45 triplets
aerien  = panne[panne.sensible_aerien==1].copy()                # surcroit cyclone
print(f"[dim] {len(dim)} triplets | portee PANNE : {len(panne)} | "
      f"dont aeriens sensibles : {len(aerien)} "
      f"({', '.join(aerien.code_cause)})")

# ---------------------------------------------------------------------
# 2. Mensualisation du stock (annuel -> 36 mois), hypothese : flux reparti
#    uniformement, churn neglige. stock_moyen du mois = expose aux pannes.
# ---------------------------------------------------------------------
parc = pd.read_csv("/root/.claude/uploads/834a167c-4bc0-5425-a7a6-db0ab07b9a2b/4b26ae72-parc_annuel_reel.csv")
lignes = []
for terr in ["GLP","MTQ"]:
    stock_fin_prec = STOCK_FIN_2022[terr]
    for annee in [2023,2024,2025]:
        p = parc[(parc.territoire==terr)&(parc.annee==annee)].iloc[0]
        flux_mensuel = p.nb_raccordements_annee/12.0
        for m in range(1,13):
            stock_moyen = stock_fin_prec + flux_mensuel*(m-0.5)   # milieu de mois
            lignes.append({"territoire":terr,"annee":annee,"mois":m,
                           "ym":f"{annee}-{m:02d}",
                           "stock_moyen":stock_moyen})
        stock_fin_prec += flux_mensuel*12   # = stock fin d'annee du CSV
cal = pd.DataFrame(lignes)
# controle : fin 2023 GLP doit retomber sur 85000
chk = STOCK_FIN_2022["GLP"] + parc[(parc.territoire=='GLP')&(parc.annee==2023)].nb_raccordements_annee.iloc[0]
print(f"[mensualisation] controle stock fin 2023 GLP = {chk:.0f} (attendu 85000)")

# ---------------------------------------------------------------------
# 3. MOTEUR PANNES : par (territoire, mois) -> volume base + surcroit aerien
# ---------------------------------------------------------------------
def tire(sous_df, n):
    """Tire n triplets dans sous_df, proportionnellement au score."""
    if n<=0: return []
    pr = sous_df.score.to_numpy()/sous_df.score.sum()
    return rng.choice(sous_df.index.to_numpy(), size=n, p=pr)

faits=[]
recap=[]
for _,r in cal.iterrows():
    terr, ym = r.territoire, r.ym
    stock = r.stock_moyen
    n_base  = int(round(stock*TAUX_PANNE_MENSUEL))                 # pannes "normales"
    mult    = MULT_CYCLONE.get((terr,ym),1.0)
    n_cyclo = int(round(n_base*(mult-1.0)))                        # surcroit 100% aerien
    recap.append({"territoire":terr,"ym":ym,"stock_moyen":stock,
                  "n_base":n_base,"mult":mult,"n_cyclo":n_cyclo,
                  "n_total":n_base+n_cyclo})
    idx = list(tire(panne, n_base)) + list(tire(aerien, n_cyclo))
    if not idx: continue
    sub = dim.loc[idx].copy()
    # flag malfacon ~ Bernoulli(p_malfacon)  (ENV=0 -> le surcroit ne cree jamais de malfacon)
    sub["malfacon"] = (rng.random(len(sub)) < sub.p_malfacon.to_numpy()).astype(int)
    # abonne_id dans le pool du stock courant -> collisions = reiteration
    sub["abonne_id"] = rng.integers(1, int(stock)+1, size=len(sub))
    sub["territoire"]=terr; sub["ym"]=ym; sub["origine"]= ["base"]*n_base+["cyclone"]*n_cyclo
    faits.append(sub)

fait = pd.concat(faits, ignore_index=True)
fait.insert(0,"sig_id",["SIG-"+str(i+1).zfill(7) for i in range(len(fait))])
recap=pd.DataFrame(recap)

# ---------------------------------------------------------------------
# 4. CONTROLES DE COHERENCE (le ROCCC de sortie)
# ---------------------------------------------------------------------
print("\n=== VOLUMES (pannes generees) ===")
print(fait.groupby(["territoire","annee" if "annee" in fait else fait.ym.str[:4]]).size()
      if False else
      fait.assign(an=fait.ym.str[:4]).groupby(["territoire","an"]).size().unstack())

print("\n=== PART DE MALFAÇON ===")
print(f"  globale toutes pannes : {fait.malfacon.mean():.1%}  (cible ~30 %)")
oct23 = fait[(fait.territoire=='GLP')&(fait.ym=='2023-10')]
sep23 = fait[(fait.territoire=='GLP')&(fait.ym=='2023-09')]
print(f"  GLP 2023-09 (mois normal) : {sep23.malfacon.mean():.1%}  sur {len(sep23)} pannes")
print(f"  GLP 2023-10 (Tammy)       : {oct23.malfacon.mean():.1%}  sur {len(oct23)} pannes  <-- doit PLONGER")

print("\n=== REITERATION (abonnes avec >=2 pannes) ===")
for terr in ["GLP","MTQ"]:
    f=fait[fait.territoire==terr]
    vc=f.groupby("abonne_id").size()
    print(f"  {terr}: {len(f)} pannes / {f.abonne_id.nunique()} abonnes touches | "
          f"part a >=2 pannes = {(vc>=2).mean():.1%}")

print("\n=== REPARTITION PAR SEGMENT (D1 amont -> D3 branchement) ===")
print((fait.segment.value_counts(normalize=True).sort_index()*100).round(1).to_string())

print("\n=== PIC CYCLONIQUE : recap GLP 2023 (base vs surcroit aerien) ===")
g23=recap[(recap.territoire=='GLP')&(recap.ym.str[:4]=='2023')][["ym","stock_moyen","n_base","mult","n_cyclo","n_total"]]
print(g23.to_string(index=False, float_format=lambda x:f"{x:,.0f}"))

# ---------------------------------------------------------------------
# 5. Sauvegardes (CSV plats) + courbe mensuelle pour le chat
# ---------------------------------------------------------------------
fait.to_csv("fait_signalisation_proto.csv", index=False)
mens = fait.assign().groupby(["territoire","ym"]).agg(
        pannes=("sig_id","size"), part_malfacon=("malfacon","mean")).reset_index()
mens.to_csv("agrege_mensuel_proto.csv", index=False)
print(f"\n[fichiers] fait_signalisation_proto.csv ({len(fait):,} lignes) + agrege_mensuel_proto.csv")

# series pour le graphe
for terr in ["GLP","MTQ"]:
    s=mens[mens.territoire==terr].sort_values("ym")
    print(f"SERIE {terr} pannes:", list(s.pannes))
print("MOIS:", list(mens[mens.territoire=='GLP'].sort_values('ym').ym))
