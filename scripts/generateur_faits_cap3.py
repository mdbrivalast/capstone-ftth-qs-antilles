#!/usr/bin/env python3
# =====================================================================
#  generateur_faits_cap3.py
#  Cas #3 « Mesurer l'invisible » — observatoire qualite FTTH Outre-mer.
#
#  Peuple les tables VIDES de cap3v5 (dim_temps, dim_pm, dim_abonne,
#  fait_raccordement, fait_signalisation) a partir des tables de
#  reference deja presentes (dim_cause, dim_territoire, ref_parc_annuel,
#  ref_troncon_segment). Ajoute aussi la colonne `malfacon` a
#  fait_signalisation si absente.
#
#  Principe : le REEL fixe l'enveloppe (parc annuel, taux de base ARCEP
#  uplifte OM), l'EXPERT fixe la repartition fine (score, p_malfacon,
#  multiplicateur cyclonique, medianes MTTR). Tout est parametre ci-dessous.
#
#  Reproductible : SEED fige la generation (meme sortie a chaque run).
#
#  ⚠️ AVANT DE LANCER : faire une COPIE de la base (le script vide puis
#     re-remplit les 5 tables de faits/dims ci-dessus). Usage :
#         python3 generateur_faits_cap3.py cap3v5.db
# =====================================================================

import sqlite3
import sys
import numpy as np
import pandas as pd

# Récupération du nom de la base de données depuis les arguments (par défaut : cap3v5.db)
DB = sys.argv[1] if len(sys.argv) > 1 else "cap3v5.db"
SEED = 20231020                         # Graine fixe pour garantir la reproductibilité (clin d'œil à Tammy : 20/10/2023)

# ---- PARAMÈTRES MÉTIER ET HYPOTHÈSES EXPERTES (LEVIERS) ----
# ---- Levier 2 : taux de base (figes, uplift OM inclus) --------------
TAUX_PANNE_MENSUEL   = 0.025            # Taux de panne mensuel de base (national ~1,79% x uplift OM 1,4)
P_SUCCESS, P_ECHEC, P_REPORTE = 0.81, 0.11, 0.08   # Probabilités raccordement (échec OM ~11% vs ~6-8% national)
P_REPRISE_MALFACON   = 0.11            # Probabilité de reprise de malfaçon sur raccordement : ARCEP 7-9% x uplift OM
MES_MEDIANE_J, MES_SIGMA = 30.0, 0.90 # Paramètres de la loi log-normale pour la mise en service (~78% sous 60j)

# ---- Levier 3 : MTTR par segment réseau en jours (medianes OM = dire d'expert Maritza) --
#  Ancrage DIRECT OM (pas de x2 : ce sont des observations ultramarines).
#  Loi log-normale : mediane = exp(mu) ; SIGMA = etalement (queue longue).
MTTR_MEDIANE_OM = {"D0":1.00, "D1":1.25, "D2":2.75, "D3":3.50, "NA":2.75}
MTTR_SIGMA      = 0.45				# Étalement (queue longue pour les pannes complexes)
RALLONGE_CYCLONE_MTTR = 1.5         # Multiplicateur de délai en mois cyclonique (équipes saturées / accès coupés)

# ---- Levier 4 : multiplicateur cyclonique "mois reels" (valide Maritza) -
#  Seul Tammy (GLP 2023-10) = vrai pic aerien (1.7) ; le reste = coupures
#  sans destruction (1.1-1.25). Repartition PM-level ponderee part_aerien.
# Multiplicateurs cycloniques par territoire et par mois (pics de pannes aériennes)
MULT_CYCLONE = {
    ("GLP","2023-10"):1.70, ("GLP","2023-06"):1.15, ("GLP","2024-07"):1.10, ("GLP","2025-08"):1.20,
    ("MTQ","2023-06"):1.20, ("MTQ","2024-07"):1.25, ("MTQ","2025-08"):1.10,
}
# ---- dim_pm : part_aerien par PM (Beta -> moyenne ~0.75, heterogene) - Paramètres de distribution des Points de Mutualisation (PM)
PART_AERIEN_BETA = (3.0, 1.0)          # Beta(a,b) : moyenne a/(a+b)=0.75
PM_TAILLE_SIGMA  = 0.35                # dispersion log-normale de la taille des PM

# Génération de la chronologie mensuelle sur 3 ans (2023 à 2025)
MOIS = [f"{a}-{m:02d}" for a in (2023,2024,2025) for m in range(1,13)]
MIDX = {ym:i for i,ym in enumerate(MOIS)}

def main():
    rng = np.random.default_rng(SEED)
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # -----------------------------------------------------------------
    # ÉTAPE 0 : PRÉPARATION ET NETTOYAGE DES TABLES
    # -----------------------------------------------------------------
    # 0) colonne malfacon sur fait_signalisation (idempotent)
    cols = [r[1] for r in cur.execute("PRAGMA table_info(fait_signalisation)")]
    if "malfacon" not in cols:
        cur.execute("ALTER TABLE fait_signalisation ADD COLUMN malfacon "
                    "INTEGER NOT NULL DEFAULT 0 CHECK(malfacon IN (0,1))")
        print("[+] colonne malfacon ajoutee a fait_signalisation")
    # vider les tables a (re)peupler — rejouable proprement
    for t in ["fait_signalisation","fait_raccordement","dim_abonne","dim_pm","dim_temps"]:
        cur.execute(f"DELETE FROM {t}")
    con.commit()

    # Chargement des tables de référence depuis la base SQLite (valeurs exactes)
    parc = {(r[0],r[1]):{"loc":r[2],"abo":r[3],"flux":r[4],"npm":r[5]} for r in cur.execute(
        "SELECT territoire,annee,nb_locaux_raccordables,nb_abonnes_ftth,nb_raccordements_annee,nb_pm FROM ref_parc_annuel")}
    seg = {r[0]:r[1] for r in cur.execute("SELECT troncon,segment FROM ref_troncon_segment")}
    terrs = [r[0] for r in cur.execute("SELECT territoire FROM dim_territoire WHERE territoire IN ('GLP','MTQ')")]
    
    # Estimation du stock initial fin 2022 par déduction (stock 2023 - flux 2023)
    stock_init = {t: parc[(t,'2023')]["abo"] - parc[(t,'2023')]["flux"] for t in terrs}

    # -----------------------------------------------------------------
    # ÉTAPE 1 : REMPLISSAGE DE `dim_temps`
    # -----------------------------------------------------------------
    cur.executemany("INSERT INTO dim_temps VALUES (?,?,?,?)",
        [(ym, f"{ym[:4]}-T{(int(ym[5:7])-1)//3+1}", ym[:4], 1 if 6<=int(ym[5:7])<=11 else 0) for ym in MOIS])

    # -----------------------------------------------------------------
    # ÉTAPE 2 : REMPLISSAGE DE `dim_pm` (Points de Mutualisation) 
	# (taille log-normale normalisee au parc 2025 ; part_aerien Beta)
    # -----------------------------------------------------------------
    PM = {}
    for t in terrs:
        npm, loc_tot = parc[(t,'2025')]["npm"], parc[(t,'2025')]["loc"]
        # Génération de la taille des PM (loi log-normale normalisée au nombre de locaux total)
        tail = rng.lognormal(0, PM_TAILLE_SIGMA, npm)
        tail = np.maximum(np.round(tail/tail.sum()*loc_tot), 50).astype(int)
        tail[-1] += loc_tot - tail.sum()  # Ajustement du delta d'arrondi sur le dernier PM
        
        # Attribution de la part de réseau aérien via la loi Bêta
        pa = np.round(rng.beta(*PART_AERIEN_BETA, npm), 3)
        ids = [f"{t}-PM-{i+1:04d}" for i in range(npm)]
        cur.executemany("INSERT INTO dim_pm VALUES (?,?,?,?)",
                         [(ids[i], int(tail[i]), t, float(pa[i])) for i in range(npm)])
        
        idv = np.array(ids)
        wb = tail / tail.sum()          # Poids par taille de PM
        wa = (tail * pa) / (tail * pa).sum()  # Poids pondéré par la part aérienne
        PM[t] = (idv, wb, wa)
    con.commit()

    # -----------------------------------------------------------------
    # ÉTAPE 3 : RACCORDEMENTS & `dim_abonne` (Création du parc actif)
	# (le flux fabrique les abonnes)
    # -----------------------------------------------------------------
    cz = cur.execute("SELECT code_cause,score FROM dim_cause WHERE portee IN ('RACCO','RACCOPANNE')").fetchall()
    cz_id = np.array([c[0] for c in cz])
    cz_w = np.array([c[1] for c in cz], float)
    cz_w /= cz_w.sum()  # Normalisation des poids de causes
    
    abonnes = []
    abpm = {}                  # abpm: pid -> [ (aidx, id) ] Dictionnaire de suivi pour relier abonné <-> PM et date d'activation
    racco = []
    aid = 0
    rid = 0
    
    jour = lambda ym: pd.Timestamp(f"{ym}-{rng.integers(1,29):02d}")
    def add_ab(pid, aidx):
        nonlocal aid
        aid += 1
        abonnes.append((aid, pid))
        abpm.setdefault(pid, []).append((aidx, aid))
        return aid

    # Injection du stock initial pré-2023 (aidx = -1, actifs dès le jour 1)
    for t in terrs:
        idv, wb, _ = PM[t]
        for pid in rng.choice(idv, size=stock_init[t], p=wb):
            add_ab(str(pid), -1)

    # Simulation des flux de raccordement mensuels
    for t in terrs:
        idv,wb,_=PM[t]
        for ym in MOIS:
            ns = int(round(parc[(t, ym[:4])]["flux"] / 12))  # Volume de succès mensuel
            ne = int(round(ns * P_ECHEC / P_SUCCESS))        # Volume d'échecs
            nr = int(round(ns * P_REPORTE / P_SUCCESS))      # Volume reporté
            
            stat = ["reussi"] * ns + ["echec"] * ne + ["reporte"] * nr
            pmsel = rng.choice(idv, size=len(stat), p=wb)
            
            for i, st in enumerate(stat):
                rid += 1
                dc = jour(ym)
                drdv = (dc + pd.Timedelta(days=int(rng.integers(2, 11)))).strftime("%Y-%m-%d")
                
                if st == "reussi":
                    ab = add_ab(str(pmsel[i]), MIDX[ym])
                    dmes = (dc + pd.Timedelta(days=max(1, int(rng.lognormal(np.log(MES_MEDIANE_J), MES_SIGMA))))).strftime("%Y-%m-%d")
                    rep = int(rng.random() < P_REPRISE_MALFACON)
                    cause = None
                else:
                    ab = None
                    dmes = None
                    rep = 0
                    cause = str(rng.choice(cz_id, p=cz_w))
                    
                racco.append((f"RAC-{rid:07d}", dc.strftime("%Y-%m-%d"), drdv, dmes, str(pmsel[i]),
                              rep, st, cause, t, ym, ab))
                              
    cur.executemany("INSERT INTO dim_abonne (id_abonne, fk_id_pm_abo) VALUES (?,?)", abonnes)
    cur.executemany("""INSERT INTO fait_raccordement (rid, date_commande, date_rdv, date_mise_en_service,
        fk_id_pm_racc, reprise_malfacon, statut, fk_cause_echec_racc, fk_territoire_racc, fk_mois_racc, fk_abonne_racc)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", racco)
    con.commit()
    # Indexation triée des abonnés par PM pour le tirage des pannes sur abonnés actifs
    for pid in abpm:
        a = sorted(abpm[pid])
        abpm[pid] = (np.array([x[0] for x in a]), np.array([x[1] for x in a]))

    # -----------------------------------------------------------------
    # ÉTAPE 4 : PANNES & SIGNALISATIONS (`fait_signalisation`)
    # -----------------------------------------------------------------
    # Récupération de la dimension des causes de pannes - pannes au grain fin (cyclone PM-level ; abonne actif du PM)
    dcp=pd.read_sql("SELECT code_cause,fk_troncon_reseau tr,score,p_malfacon,sensible_aerien FROM dim_cause WHERE portee='PANNE'",con)
    dcp["segment"]=dcp.tr.map(seg)
    aer = dcp[dcp.sensible_aerien == 1]  # Sous-ensemble des pannes aériennes sensibles aux intempéries
    pw=(dcp.score/dcp.score.sum()).to_numpy(); aw=(aer.score/aer.score.sum()).to_numpy()
    
    def tire_ab(pid,m):
        e = abpm.get(pid)
        if e is None:
            return None
        aidx, ids = e
        k = np.searchsorted(aidx, m, side="right")
        return int(ids[rng.integers(0, k)]) if k > 0 else None
    faits = []
    sid = 0
    # Boucle temporelle et territoriale pour générer les signalisations de pannes
    for t in terrs:
        idv, wb, wa = PM[t]
        sfin = stock_init[t]
        
        for ym in MOIS:
            an = ym[:4]
            fm = parc[(t, an)]["flux"] / 12
            m_in = int(ym[5:7])
            stock = sfin + fm * (m_in - 0.5)  # Stock moyen lissé à mi-mois
            
            # 1. Calcul du volume de pannes de base + surcroît cyclonique éventuel
            nb = int(round(stock * TAUX_PANNE_MENSUEL))                 # Pannes nominales (2.5% du parc)
            mult = MULT_CYCLONE.get((t, ym), 1.0)                       # Multiplicateur météo (ex: Tammy = 1.7)
            nc = int(round(nb * (mult - 1)))                            # Surcroît de pannes induit par le cyclone
            
            pmb = rng.choice(idv, size=nb, p=wb)
            cb = rng.choice(dcp.index, size=nb, p=pw)
            
            pmc = rng.choice(idv, size=nc, p=wa)
            cc = rng.choice(aer.index, size=nc, p=aw)
            
            allpm = np.concatenate([pmb, pmc])
            allc = np.concatenate([cb, cc])
            m = MIDX[ym]
            
            for j in range(len(allpm)):
                sid += 1
                row = dcp.loc[allc[j]]
                
                # Calcul du MTTR (loi log-normale, rallongé si mois cyclonique)
                med = MTTR_MEDIANE_OM[row.segment] * (RALLONGE_CYCLONE_MTTR if mult > 1 else 1.0)
                mttr = round(float(rng.lognormal(np.log(med), MTTR_SIGMA)), 2)
                
                dep = jour(ym)
                clo = dep + pd.Timedelta(days=mttr)
                pri = dep + pd.Timedelta(hours=int(rng.integers(2, 24)))
                
                faits.append((sid, dep.strftime("%Y-%m-%d"), pri.strftime("%Y-%m-%d %H:%M"), clo.strftime("%Y-%m-%d"),
                              mttr, row.code_cause, t, str(allpm[j]), ym, tire_ab(str(allpm[j]), m),
                              int(rng.random() < row.p_malfacon)))
                              
            if m_in == 12:
                sfin += fm * 12
                
    cur.executemany("""INSERT INTO fait_signalisation (sid, date_depot, date_prise_en_charge, date_cloture,
        temps_retablissement, fk_code_cause_sign, fk_territoire_sign, fk_id_pm_sign, fk_mois_sign, fk_abonne_sign, malfacon)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", faits)
    con.commit()

    # -----------------------------------------------------------------
    # ÉTAPE 5 : CONTRÔLE FINAL ET BILAN
    # -----------------------------------------------------------------
    fk=cur.execute("PRAGMA foreign_key_check").fetchall()
    print(f"[OK] peuplement termine. foreign_key_check : {len(fk)} violation(s).")
    for t in ["dim_temps","dim_pm","dim_abonne","fait_raccordement","fait_signalisation"]:
        print(f"     {t:20s}= {cur.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:>7}")
    con.close()

if __name__ == "__main__":
    main()
