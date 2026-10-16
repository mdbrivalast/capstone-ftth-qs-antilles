# =====================================================================
#  moteur_pannes_v2.py  —  Cas #3 « Mesurer l'invisible » (FTTH OM)
#  MOTEUR PANNES complet : volume + cause + malfaçon + MTTR.
#  v2 : Tammy 1.7, MTTR log-normale ancree directement sur l'expertise OM.
# =====================================================================
import numpy as np, pandas as pd
SEED = 20231020
rng  = np.random.default_rng(SEED)

TAUX_PANNE_MENSUEL = 0.025
STOCK_FIN_2022 = {"GLP":52000, "MTQ":36000}

# --- Levier 4 : cyclone "mois reels" (Tammy abaisse a 1.7 par decision Tiza) ---
MULT_CYCLONE = {
    ("GLP","2023-10"):1.70, ("GLP","2023-06"):1.15, ("GLP","2024-07"):1.10, ("GLP","2025-08"):1.20,
    ("MTQ","2023-06"):1.20, ("MTQ","2024-07"):1.25, ("MTQ","2025-08"):1.10,
}
TRONCON_SEGMENT = {"NRO":"D1","PM":"D2","PBO":"D3","BPE":"D2","PTO":"D3","BACK":"D0","MULTI":"NA"}

# --- Levier 5 : MTTR (jours). Medianes OM = dire d'expert terrain (Tiza).
#     Ancrage DIRECT OM (pas de x2 : ses observations sont deja ultramarines).
#     Loi log-normale : mediane = exp(mu) -> mu = ln(mediane) ; sigma = etalement du log.
MTTR_MEDIAN_OM = {"D0":1.00, "D1":1.25, "D2":2.75, "D3":3.50, "NA":2.75}
SIGMA_LOG      = 0.45          # -> P90 ~1.8x la mediane, queue vers 5-7 j pour D3
RALLONGE_CYCLONE = 1.5         # mois cyclonique : equipes saturees/acces coupes (fixe, ajustable)

# ---------------------------------------------------------------------
# 1. dim_cause enrichie
# ---------------------------------------------------------------------
dim = pd.read_csv("/tmp/p_malfacon_mapping.csv")
dim["troncon"] = [c[len(q)+1:-(len(p)+1)] for c,q,p in zip(dim.code_cause,dim.quoi,dim.portee)]
dim["segment"] = dim.troncon.map(TRONCON_SEGMENT)
dim["sensible_aerien"] = ((dim.quoi=="ENV")&(dim.troncon.isin(["PM","PBO","PTO"]))).astype(int)
panne  = dim[dim.portee=="PANNE"].copy()
aerien = panne[panne.sensible_aerien==1].copy()

# ---------------------------------------------------------------------
# 2. Mensualisation du stock
# ---------------------------------------------------------------------
parc = pd.read_csv("/root/.claude/uploads/834a167c-4bc0-5425-a7a6-db0ab07b9a2b/4b26ae72-parc_annuel_reel.csv")
cal=[]
for terr in ["GLP","MTQ"]:
    sfin=STOCK_FIN_2022[terr]
    for an in [2023,2024,2025]:
        p=parc[(parc.territoire==terr)&(parc.annee==an)].iloc[0]; fm=p.nb_raccordements_annee/12
        for m in range(1,13):
            cal.append({"territoire":terr,"ym":f"{an}-{m:02d}","stock_moyen":sfin+fm*(m-0.5)})
        sfin+=fm*12
cal=pd.DataFrame(cal)

# ---------------------------------------------------------------------
# 3. Moteur : volume base + surcroit aerien, cause, malfaçon, MTTR
# ---------------------------------------------------------------------
def tire(df,n):
    if n<=0: return []
    return rng.choice(df.index.to_numpy(), size=n, p=(df.score/df.score.sum()).to_numpy())

faits=[]
for _,r in cal.iterrows():
    terr,ym,stock=r.territoire,r.ym,r.stock_moyen
    n_base=int(round(stock*TAUX_PANNE_MENSUEL))
    mult=MULT_CYCLONE.get((terr,ym),1.0)
    n_cyclo=int(round(n_base*(mult-1)))
    idx=list(tire(panne,n_base))+list(tire(aerien,n_cyclo))
    if not idx: continue
    sub=dim.loc[idx].copy()
    sub["malfacon"]=(rng.random(len(sub))<sub.p_malfacon.to_numpy()).astype(int)
    sub["abonne_id"]=rng.integers(1,int(stock)+1,size=len(sub))
    # MTTR : log-normale par segment, rallongee les mois cycloniques
    med=sub.segment.map(MTTR_MEDIAN_OM).to_numpy()
    if mult>1.0: med=med*RALLONGE_CYCLONE
    sub["mttr_jours"]=np.round(rng.lognormal(np.log(med),SIGMA_LOG),2)
    sub["territoire"]=terr; sub["ym"]=ym; sub["origine"]=["base"]*n_base+["cyclone"]*n_cyclo
    faits.append(sub)
fait=pd.concat(faits,ignore_index=True)
fait.insert(0,"sig_id",["SIG-"+str(i+1).zfill(7) for i in range(len(fait))])

# ---------------------------------------------------------------------
# 4. CONTROLES
# ---------------------------------------------------------------------
print("=== RAPPEL (inchange par le MTTR) ===")
print(f"  pannes totales : {len(fait):,} | part malfaçon globale : {fait.malfacon.mean():.1%}")
oct23=fait[(fait.territoire=='GLP')&(fait.ym=='2023-10')]
print(f"  GLP 2023-10 (Tammy 1.7) : {len(oct23)} pannes | part malfaçon {oct23.malfacon.mean():.1%}  (formule 0.29/1.7={0.29/1.7:.0%})")

print("\n=== MTTR par segment (jours) : mediane vs moyenne vs P90 ===")
g=fait.groupby("segment").mttr_jours
rec=pd.DataFrame({"mediane":g.median(),"moyenne":g.mean(),"P90":g.quantile(.9),"n":g.size()}).round(2)
print(rec.reindex(["D0","D1","D2","D3","NA"]).to_string())
print(f"\n  -> GLOBAL : mediane {fait.mttr_jours.median():.2f} j | moyenne {fait.mttr_jours.mean():.2f} j "
      f"(moyenne > mediane = l'asymetrie que tu voyais)")

print("\n=== Indicateurs de delai (facon observatoire) ===")
print(f"  repare sous 48h (<=2j) : {(fait.mttr_jours<=2).mean():.1%}")
print(f"  au-dela de 5 jours     : {(fait.mttr_jours>5).mean():.1%}  (tes cas 'parfois plus')")

print("\n=== Effet cyclone sur le DELAI (GLP, D3 branchement) ===")
d3=fait[(fait.territoire=='GLP')&(fait.segment=='D3')]
for lbl,ym in [("mois normal (2023-09)","2023-09"),("Tammy (2023-10)","2023-10")]:
    s=d3[d3.ym==ym]
    print(f"  {lbl:22s}: MTTR median {s.mttr_jours.median():.2f} j sur {len(s)} pannes D3")

# histogramme des delais (buckets) pour le graphe
import numpy as np
buckets=pd.cut(fait.mttr_jours,[0,1,2,3,4,5,6,7,100],
               labels=["0-1","1-2","2-3","3-4","4-5","5-6","6-7","7+"])
h=(buckets.value_counts(normalize=True).reindex(["0-1","1-2","2-3","3-4","4-5","5-6","6-7","7+"])*100).round(1)
print("\n=== Distribution des MTTR (% des pannes) ===")
print(h.to_string())

fait.to_csv("fait_signalisation_v2.csv",index=False)
print(f"\n[fichier] fait_signalisation_v2.csv ({len(fait):,} lignes, colonne mttr_jours ajoutee)")
print("HIST:", list(h.values))
