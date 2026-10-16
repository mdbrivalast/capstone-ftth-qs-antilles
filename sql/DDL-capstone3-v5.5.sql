BEGIN TRANSACTION;
PRAGMA foreign_keys = off;

DROP TABLE IF EXISTS fait_signalisation;
DROP TABLE IF EXISTS fait_raccordement;
DROP TABLE IF EXISTS dim_cause;
DROP TABLE IF EXISTS ref_troncon_segment;
DROP TABLE IF EXISTS dim_abonne;
DROP TABLE IF EXISTS dim_pm;
DROP TABLE IF EXISTS dim_temps;
DROP TABLE IF EXISTS ref_parc_annuel;
DROP TABLE IF EXISTS dim_territoire;

-- Tableau : dim_territoire
    territoire TEXT PRIMARY KEY CHECK (territoire IN ('GLP','MTQ','NAT')),  -- GLP=971+977+978, MTQ=972, NAT=national (réserve)
    libelle    TEXT                                            -- pour l'affichage dashboard
);
INSERT INTO dim_territoire (territoire, libelle) VALUES
  ('GLP','Guadeloupe (971+977+978)'),
  ('MTQ','Martinique (972)');

-- Tableau : ref_parc_annuel
CREATE TABLE IF NOT EXISTS ref_parc_annuel (
    territoire             TEXT    NOT NULL,
    annee                  TEXT    NOT NULL,          -- 'YYYY' (cohérent dim_temps.annee)
    nb_locaux_raccordables INTEGER,                   -- réel (cas #1)
    nb_abonnes_ftth        INTEGER,                   -- réel : STOCK fin d'année -> base des pannes
    nb_raccordements_annee INTEGER,                   -- dérivé : FLUX (Δ stock, churn négligé) -> base des échecs de pose
    nb_pm                  INTEGER,                   -- déduit (GLP ~900 terrain, MTQ ~680 homothétie) ; constant sur la fenêtre
    PRIMARY KEY (territoire, annee),
    FOREIGN KEY (territoire) REFERENCES dim_territoire (territoire)
);

-- Tableau : dim_temps
CREATE TABLE IF NOT EXISTS dim_temps (
    mois              TEXT    PRIMARY KEY, -- 'YYYY-MM'
    trimestre         TEXT,                -- T1, T2, T3, T4
    annee             TEXT,                -- YYYY
    saison_cyclonique INTEGER NOT NULL DEFAULT 0 CHECK (saison_cyclonique IN (0, 1)) 
);

-- Tableau : dim_pm
CREATE TABLE IF NOT EXISTS dim_pm (
    id_pm                  TEXT PRIMARY KEY,
    nb_locaux_raccordables INTEGER, -- simulé
    fk_territoire_pm       TEXT,
    part_aerien            REAL,
    FOREIGN KEY (fk_territoire_pm) REFERENCES dim_territoire (territoire) 
);

-- Tableau : dim_abonne
CREATE TABLE IF NOT EXISTS dim_abonne (
    id_abonne    INTEGER PRIMARY KEY,
    fk_id_pm_abo TEXT,
    FOREIGN KEY (fk_id_pm_abo) REFERENCES dim_pm (id_pm) 
);

-- Tableau : ref_troncon_segment
CREATE TABLE IF NOT EXISTS ref_troncon_segment (
    troncon TEXT PRIMARY KEY,                                        -- BACK [D0]/NRO [D1]/PM [D2]/BPE [D2]/PBO [D3]/PTO [D3]/MULTI [NA]
    segment TEXT NOT NULL CHECK (segment IN ('D0', 'D1', 'D2', 'D3', 'NA')), -- D0/D1/D2/D3/NA
    libelle TEXT                                                     -- Collecte/Transport/Distribution/Branchement/Transverse
);

-- Tableau : dim_cause
CREATE TABLE IF NOT EXISTS dim_cause (
    code_cause        TEXT PRIMARY KEY,
    quoi              TEXT NOT NULL CHECK (quoi IN ('ACCES','CABLE#FIBRE','CONT','GC','ENV','ROP','MAT','TECHNICIEN','CLIENT','DEPL','PUBLIC')),
    fk_troncon_reseau TEXT NOT NULL,
    portee            TEXT NOT NULL CHECK (portee IN ('RACCO','PANNE','RACCOPANNE','NON_INCIDENT')),
    sensible_aerien   INTEGER NOT NULL DEFAULT 0 CHECK (sensible_aerien IN (0,1)),
    score             INTEGER CHECK (score IN (2, 3, 4)),   -- poids = fréquence de tirage (4 fort / 3 moyen / 2 faible)
    libelle_cause     TEXT,
    p_malfacon 	      REAL CHECK (p_malfacon BETWEEN 0 AND 1),
    FOREIGN KEY (fk_troncon_reseau) REFERENCES ref_troncon_segment (troncon)
);


-- Tableau : fait_raccordement
CREATE TABLE IF NOT EXISTS fait_raccordement (
    rid                  TEXT    PRIMARY KEY,
    date_commande        TEXT    NOT NULL,
    date_rdv             TEXT,
    date_mise_en_service TEXT,
    fk_id_pm_racc        TEXT,
    reprise_malfacon     INTEGER NOT NULL DEFAULT 0 CHECK (reprise_malfacon IN (0, 1)),
    statut               TEXT    CHECK (statut IN ('reussi', 'echec', 'reporte')),
    fk_cause_echec_racc  TEXT,
    fk_territoire_racc   TEXT,
    fk_mois_racc         TEXT,
    fk_abonne_racc       INTEGER,
    FOREIGN KEY (fk_cause_echec_racc) REFERENCES dim_cause (code_cause),
    FOREIGN KEY (fk_territoire_racc) REFERENCES dim_territoire (territoire),
    FOREIGN KEY (fk_id_pm_racc) REFERENCES dim_pm (id_pm),
    FOREIGN KEY (fk_mois_racc) REFERENCES dim_temps (mois),
    FOREIGN KEY (fk_abonne_racc) REFERENCES dim_abonne (id_abonne) 
);

-- Tableau : fait_signalisation
CREATE TABLE IF NOT EXISTS fait_signalisation (
    sid                  TEXT PRIMARY KEY,
    date_depot           TEXT    NOT NULL, -- interaction Date cf 20150601-Convention_SAV_FTTH_v21.xlsx
    date_prise_en_charge TEXT,             -- supplierPlannedActionDate cf 20150601-Convention_SAV_FTTH_v21.xlsx
    date_cloture         TEXT,             -- interactionDateComplete cf 20150601-Convention_SAV_FTTH_v21.xlsx
    temps_retablissement REAL,             -- valeur generée en jours / date_cloture − date_depot
    fk_code_cause_sign   TEXT,
    fk_territoire_sign   TEXT,
    fk_id_pm_sign        TEXT,
    fk_mois_sign         TEXT,
    fk_abonne_sign       INTEGER,
    FOREIGN KEY (fk_code_cause_sign) REFERENCES dim_cause (code_cause),
    FOREIGN KEY (fk_territoire_sign) REFERENCES dim_territoire (territoire),
    FOREIGN KEY (fk_id_pm_sign) REFERENCES dim_pm (id_pm),
    FOREIGN KEY (fk_mois_sign) REFERENCES dim_temps (mois),
    FOREIGN KEY (fk_abonne_sign) REFERENCES dim_abonne (id_abonne) 
);

PRAGMA foreign_keys = on;
COMMIT TRANSACTION;