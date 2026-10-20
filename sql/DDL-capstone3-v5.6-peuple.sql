-- DDL-capstone3-v5.6-peuple.sql : schéma v5.6 + référentiels (point de départ de la reproduction)
-- Usage : sqlite3 cap3v5.db < DDL-capstone3-v5.6-peuple.sql   puis   python scripts/generateur_faits_cap3.py cap3v5.db
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

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
CREATE TABLE IF NOT EXISTS dim_territoire (
    territoire TEXT PRIMARY KEY CHECK (territoire IN ('GLP', 'MTQ', 'NAT') ), -- GLP=971+977+978, MTQ=972, NAT=national (réserve)
    libelle    TEXT                                               -- pour l'affichage dashboard
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
    sid                  INTEGER PRIMARY KEY,
    date_depot           TEXT    NOT NULL, -- interaction Date cf 20150601-Convention_SAV_FTTH_v21.xlsx
    date_prise_en_charge TEXT,             -- supplierPlannedActionDate cf 20150601-Convention_SAV_FTTH_v21.xlsx
    date_cloture         TEXT,             -- interactionDateComplete cf 20150601-Convention_SAV_FTTH_v21.xlsx
    temps_retablissement REAL,             -- valeur generée en jours / date_cloture − date_depot
    fk_code_cause_sign   TEXT,
    fk_territoire_sign   TEXT,
    fk_id_pm_sign        TEXT,
    fk_mois_sign         TEXT,
    fk_abonne_sign       INTEGER,
    malfacon             INTEGER NOT NULL DEFAULT 0 CHECK (malfacon IN (0, 1) ),
    FOREIGN KEY (fk_code_cause_sign) REFERENCES dim_cause (code_cause),
    FOREIGN KEY (fk_territoire_sign) REFERENCES dim_territoire (territoire),
    FOREIGN KEY (fk_id_pm_sign) REFERENCES dim_pm (id_pm),
    FOREIGN KEY (fk_mois_sign) REFERENCES dim_temps (mois),
    FOREIGN KEY (fk_abonne_sign) REFERENCES dim_abonne (id_abonne) 
);

-- Données : ref_troncon_segment (7 lignes) — ordre d'insertion d'origine conservé (le générateur lit dim_cause dans cet ordre)
INSERT INTO ref_troncon_segment (troncon, segment, libelle) VALUES
  ('NRO', 'D1', 'Transport'),
  ('PM', 'D2', 'Distribution'),
  ('PBO', 'D3', 'Branchement'),
  ('BPE', 'D2', 'Distribution'),
  ('PTO', 'D3', 'Branchement'),
  ('BACK', 'D0', 'Collecte'),
  ('MULTI', 'NA', 'Transverse');

-- Données : dim_cause (135 lignes) — ordre d'insertion d'origine conservé (le générateur lit dim_cause dans cet ordre)
INSERT INTO dim_cause (code_cause, quoi, fk_troncon_reseau, portee, sensible_aerien, score, libelle_cause, p_malfacon) VALUES
  ('ACCES_NRO_RACCO', 'ACCES', 'NRO', 'RACCO', 0, 4, 'Cause d''accessibilité matériel ou locaux — Nœud de Raccordement Optique — Raccordement et branchement abonné', 0.15),
  ('ACCES_NRO_PANNE', 'ACCES', 'NRO', 'PANNE', 0, 4, 'Cause d''accessibilité matériel ou locaux — Nœud de Raccordement Optique — Panne abonné', 0.15),
  ('ACCES_NRO_RACCOPANNE', 'ACCES', 'NRO', 'RACCOPANNE', 0, 4, 'Cause d''accessibilité matériel ou locaux — Nœud de Raccordement Optique — Panne au moment du raccordement', 0.15),
  ('ACCES_PM_RACCO', 'ACCES', 'PM', 'RACCO', 0, 4, 'Cause d''accessibilité matériel ou locaux — Point de mutualisation — Raccordement et branchement abonné', 0.15),
  ('ACCES_PM_PANNE', 'ACCES', 'PM', 'PANNE', 0, 4, 'Cause d''accessibilité matériel ou locaux — Point de mutualisation — Panne abonné', 0.15),
  ('ACCES_PM_RACCOPANNE', 'ACCES', 'PM', 'RACCOPANNE', 0, 4, 'Cause d''accessibilité matériel ou locaux — Point de mutualisation — Panne au moment du raccordement', 0.15),
  ('ACCES_PBO_RACCO', 'ACCES', 'PBO', 'RACCO', 0, 4, 'Cause d''accessibilité matériel ou locaux — Point de Branchement Optique — Raccordement et branchement abonné', 0.15),
  ('ACCES_PBO_PANNE', 'ACCES', 'PBO', 'PANNE', 0, 4, 'Cause d''accessibilité matériel ou locaux — Point de Branchement Optique — Panne abonné', 0.15),
  ('ACCES_PBO_RACCOPANNE', 'ACCES', 'PBO', 'RACCOPANNE', 0, 4, 'Cause d''accessibilité matériel ou locaux — Point de Branchement Optique — Panne au moment du raccordement', 0.15),
  ('ACCES_BPE_RACCO', 'ACCES', 'BPE', 'RACCO', 0, 4, 'Cause d''accessibilité matériel ou locaux — Boitier de Protection d''Etage — Raccordement et branchement abonné', 0.15),
  ('ACCES_BPE_PANNE', 'ACCES', 'BPE', 'PANNE', 0, 4, 'Cause d''accessibilité matériel ou locaux — Boitier de Protection d''Etage — Panne abonné', 0.15),
  ('ACCES_BPE_RACCOPANNE', 'ACCES', 'BPE', 'RACCOPANNE', 0, 4, 'Cause d''accessibilité matériel ou locaux — Boitier de Protection d''Etage — Panne au moment du raccordement', 0.15),
  ('ACCES_PTO_RACCO', 'ACCES', 'PTO', 'RACCO', 0, 4, 'Cause d''accessibilité matériel ou locaux — Point de Terminaison Optique Abonné — Raccordement et branchement abonné', 0.15),
  ('ACCES_PTO_PANNE', 'ACCES', 'PTO', 'PANNE', 0, 4, 'Cause d''accessibilité matériel ou locaux — Point de Terminaison Optique Abonné — Panne abonné', 0.15),
  ('ACCES_PTO_RACCOPANNE', 'ACCES', 'PTO', 'RACCOPANNE', 0, 4, 'Cause d''accessibilité matériel ou locaux — Point de Terminaison Optique Abonné — Panne au moment du raccordement', 0.15),
  ('CABLE#FIBRE_NRO_RACCO', 'CABLE#FIBRE', 'NRO', 'RACCO', 0, 4, 'Cause altération câble ou fibre — Nœud de Raccordement Optique — Raccordement et branchement abonné', 0.4),
  ('CABLE#FIBRE_NRO_PANNE', 'CABLE#FIBRE', 'NRO', 'PANNE', 0, 4, 'Cause altération câble ou fibre — Nœud de Raccordement Optique — Panne abonné', 0.4),
  ('CABLE#FIBRE_NRO_RACCOPANNE', 'CABLE#FIBRE', 'NRO', 'RACCOPANNE', 0, 4, 'Cause altération câble ou fibre — Nœud de Raccordement Optique — Panne au moment du raccordement', 0.4),
  ('CABLE#FIBRE_PM_RACCO', 'CABLE#FIBRE', 'PM', 'RACCO', 0, 4, 'Cause altération câble ou fibre — Point de mutualisation — Raccordement et branchement abonné', 0.4),
  ('CABLE#FIBRE_PM_PANNE', 'CABLE#FIBRE', 'PM', 'PANNE', 0, 4, 'Cause altération câble ou fibre — Point de mutualisation — Panne abonné', 0.4),
  ('CABLE#FIBRE_PM_RACCOPANNE', 'CABLE#FIBRE', 'PM', 'RACCOPANNE', 0, 4, 'Cause altération câble ou fibre — Point de mutualisation — Panne au moment du raccordement', 0.4),
  ('CABLE#FIBRE_PBO_RACCO', 'CABLE#FIBRE', 'PBO', 'RACCO', 0, 4, 'Cause altération câble ou fibre — Point de Branchement Optique — Raccordement et branchement abonné', 0.4),
  ('CABLE#FIBRE_PBO_PANNE', 'CABLE#FIBRE', 'PBO', 'PANNE', 0, 4, 'Cause altération câble ou fibre — Point de Branchement Optique — Panne abonné', 0.4),
  ('CABLE#FIBRE_PBO_RACCOPANNE', 'CABLE#FIBRE', 'PBO', 'RACCOPANNE', 0, 4, 'Cause altération câble ou fibre — Point de Branchement Optique — Panne au moment du raccordement', 0.4),
  ('CABLE#FIBRE_BPE_RACCO', 'CABLE#FIBRE', 'BPE', 'RACCO', 0, 4, 'Cause altération câble ou fibre — Boitier de Protection d''Etage — Raccordement et branchement abonné', 0.4),
  ('CABLE#FIBRE_BPE_PANNE', 'CABLE#FIBRE', 'BPE', 'PANNE', 0, 4, 'Cause altération câble ou fibre — Boitier de Protection d''Etage — Panne abonné', 0.4),
  ('CABLE#FIBRE_BPE_RACCOPANNE', 'CABLE#FIBRE', 'BPE', 'RACCOPANNE', 0, 4, 'Cause altération câble ou fibre — Boitier de Protection d''Etage — Panne au moment du raccordement', 0.4),
  ('CABLE#FIBRE_PTO_RACCO', 'CABLE#FIBRE', 'PTO', 'RACCO', 0, 4, 'Cause altération câble ou fibre — Point de Terminaison Optique Abonné — Raccordement et branchement abonné', 0.4),
  ('CABLE#FIBRE_PTO_PANNE', 'CABLE#FIBRE', 'PTO', 'PANNE', 0, 4, 'Cause altération câble ou fibre — Point de Terminaison Optique Abonné — Panne abonné', 0.4),
  ('CABLE#FIBRE_PTO_RACCOPANNE', 'CABLE#FIBRE', 'PTO', 'RACCOPANNE', 0, 4, 'Cause altération câble ou fibre — Point de Terminaison Optique Abonné — Panne au moment du raccordement', 0.4),
  ('CABLE#FIBRE_BACK_RACCO', 'CABLE#FIBRE', 'BACK', 'RACCO', 0, 4, 'Cause altération câble ou fibre — Collecte-épine dorsale du réseau — Raccordement et branchement abonné', 0.4),
  ('CABLE#FIBRE_BACK_PANNE', 'CABLE#FIBRE', 'BACK', 'PANNE', 0, 4, 'Cause altération câble ou fibre — Collecte-épine dorsale du réseau — Panne abonné', 0.4),
  ('CABLE#FIBRE_BACK_RACCOPANNE', 'CABLE#FIBRE', 'BACK', 'RACCOPANNE', 0, 4, 'Cause altération câble ou fibre — Collecte-épine dorsale du réseau — Panne au moment du raccordement', 0.4),
  ('CONT_NRO_RACCO', 'CONT', 'NRO', 'RACCO', 0, 4, 'Cause d''altération ou perte de signal — Nœud de Raccordement Optique — Raccordement et branchement abonné', 0.45),
  ('CONT_NRO_PANNE', 'CONT', 'NRO', 'PANNE', 0, 4, 'Cause d''altération ou perte de signal — Nœud de Raccordement Optique — Panne abonné', 0.45),
  ('CONT_NRO_RACCOPANNE', 'CONT', 'NRO', 'RACCOPANNE', 0, 4, 'Cause d''altération ou perte de signal — Nœud de Raccordement Optique — Panne au moment du raccordement', 0.45),
  ('CONT_PM_RACCO', 'CONT', 'PM', 'RACCO', 0, 4, 'Cause d''altération ou perte de signal — Point de mutualisation — Raccordement et branchement abonné', 0.45),
  ('CONT_PM_PANNE', 'CONT', 'PM', 'PANNE', 0, 4, 'Cause d''altération ou perte de signal — Point de mutualisation — Panne abonné', 0.45),
  ('CONT_PM_RACCOPANNE', 'CONT', 'PM', 'RACCOPANNE', 0, 4, 'Cause d''altération ou perte de signal — Point de mutualisation — Panne au moment du raccordement', 0.45),
  ('CONT_PBO_RACCO', 'CONT', 'PBO', 'RACCO', 0, 4, 'Cause d''altération ou perte de signal — Point de Branchement Optique — Raccordement et branchement abonné', 0.45),
  ('CONT_PBO_PANNE', 'CONT', 'PBO', 'PANNE', 0, 4, 'Cause d''altération ou perte de signal — Point de Branchement Optique — Panne abonné', 0.45),
  ('CONT_PBO_RACCOPANNE', 'CONT', 'PBO', 'RACCOPANNE', 0, 4, 'Cause d''altération ou perte de signal — Point de Branchement Optique — Panne au moment du raccordement', 0.45),
  ('CONT_BPE_RACCO', 'CONT', 'BPE', 'RACCO', 0, 4, 'Cause d''altération ou perte de signal — Boitier de Protection d''Etage — Raccordement et branchement abonné', 0.45),
  ('CONT_BPE_PANNE', 'CONT', 'BPE', 'PANNE', 0, 4, 'Cause d''altération ou perte de signal — Boitier de Protection d''Etage — Panne abonné', 0.45),
  ('CONT_BPE_RACCOPANNE', 'CONT', 'BPE', 'RACCOPANNE', 0, 4, 'Cause d''altération ou perte de signal — Boitier de Protection d''Etage — Panne au moment du raccordement', 0.45),
  ('CONT_PTO_RACCO', 'CONT', 'PTO', 'RACCO', 0, 4, 'Cause d''altération ou perte de signal — Point de Terminaison Optique Abonné — Raccordement et branchement abonné', 0.45),
  ('CONT_PTO_PANNE', 'CONT', 'PTO', 'PANNE', 0, 4, 'Cause d''altération ou perte de signal — Point de Terminaison Optique Abonné — Panne abonné', 0.45),
  ('CONT_PTO_RACCOPANNE', 'CONT', 'PTO', 'RACCOPANNE', 0, 4, 'Cause d''altération ou perte de signal — Point de Terminaison Optique Abonné — Panne au moment du raccordement', 0.45),
  ('CONT_BACK_RACCO', 'CONT', 'BACK', 'RACCO', 0, 4, 'Cause d''altération ou perte de signal — Collecte-épine dorsale du réseau — Raccordement et branchement abonné', 0.45),
  ('CONT_BACK_PANNE', 'CONT', 'BACK', 'PANNE', 0, 4, 'Cause d''altération ou perte de signal — Collecte-épine dorsale du réseau — Panne abonné', 0.45),
  ('CONT_BACK_RACCOPANNE', 'CONT', 'BACK', 'RACCOPANNE', 0, 4, 'Cause d''altération ou perte de signal — Collecte-épine dorsale du réseau — Panne au moment du raccordement', 0.45),
  ('GC_PM_RACCO', 'GC', 'PM', 'RACCO', 0, 4, 'Cause impliquant des travaux de génie civil — Point de mutualisation — Raccordement et branchement abonné', 0.1),
  ('GC_PM_PANNE', 'GC', 'PM', 'PANNE', 0, 4, 'Cause impliquant des travaux de génie civil — Point de mutualisation — Panne abonné', 0.1),
  ('GC_PM_RACCOPANNE', 'GC', 'PM', 'RACCOPANNE', 0, 4, 'Cause impliquant des travaux de génie civil — Point de mutualisation — Panne au moment du raccordement', 0.1),
  ('GC_PBO_RACCO', 'GC', 'PBO', 'RACCO', 0, 4, 'Cause impliquant des travaux de génie civil — Point de Branchement Optique — Raccordement et branchement abonné', 0.1),
  ('GC_PBO_PANNE', 'GC', 'PBO', 'PANNE', 0, 4, 'Cause impliquant des travaux de génie civil — Point de Branchement Optique — Panne abonné', 0.1),
  ('GC_PBO_RACCOPANNE', 'GC', 'PBO', 'RACCOPANNE', 0, 4, 'Cause impliquant des travaux de génie civil — Point de Branchement Optique — Panne au moment du raccordement', 0.1),
  ('GC_BPE_RACCO', 'GC', 'BPE', 'RACCO', 0, 4, 'Cause impliquant des travaux de génie civil — Boitier de Protection d''Etage — Raccordement et branchement abonné', 0.1),
  ('GC_BPE_PANNE', 'GC', 'BPE', 'PANNE', 0, 4, 'Cause impliquant des travaux de génie civil — Boitier de Protection d''Etage — Panne abonné', 0.1),
  ('GC_BPE_RACCOPANNE', 'GC', 'BPE', 'RACCOPANNE', 0, 4, 'Cause impliquant des travaux de génie civil — Boitier de Protection d''Etage — Panne au moment du raccordement', 0.1),
  ('GC_PTO_RACCO', 'GC', 'PTO', 'RACCO', 0, 4, 'Cause impliquant des travaux de génie civil — Point de Terminaison Optique Abonné — Raccordement et branchement abonné', 0.1),
  ('GC_PTO_PANNE', 'GC', 'PTO', 'PANNE', 0, 4, 'Cause impliquant des travaux de génie civil — Point de Terminaison Optique Abonné — Panne abonné', 0.1),
  ('GC_PTO_RACCOPANNE', 'GC', 'PTO', 'RACCOPANNE', 0, 4, 'Cause impliquant des travaux de génie civil — Point de Terminaison Optique Abonné — Panne au moment du raccordement', 0.1),
  ('GC_BACK_RACCO', 'GC', 'BACK', 'RACCO', 0, 4, 'Cause impliquant des travaux de génie civil — Collecte-épine dorsale du réseau — Raccordement et branchement abonné', 0.1),
  ('GC_BACK_PANNE', 'GC', 'BACK', 'PANNE', 0, 4, 'Cause impliquant des travaux de génie civil — Collecte-épine dorsale du réseau — Panne abonné', 0.1),
  ('GC_BACK_RACCOPANNE', 'GC', 'BACK', 'RACCOPANNE', 0, 4, 'Cause impliquant des travaux de génie civil — Collecte-épine dorsale du réseau — Panne au moment du raccordement', 0.1),
  ('ENV_PM_RACCO', 'ENV', 'PM', 'RACCO', 1, 4, 'Cause environnementale sur les appuis ou naturel — Point de mutualisation — Raccordement et branchement abonné', 0.0),
  ('ENV_PM_PANNE', 'ENV', 'PM', 'PANNE', 1, 4, 'Cause environnementale sur les appuis ou naturel — Point de mutualisation — Panne abonné', 0.0),
  ('ENV_PM_RACCOPANNE', 'ENV', 'PM', 'RACCOPANNE', 1, 4, 'Cause environnementale sur les appuis ou naturel — Point de mutualisation — Panne au moment du raccordement', 0.0),
  ('ENV_PBO_RACCO', 'ENV', 'PBO', 'RACCO', 1, 4, 'Cause environnementale sur les appuis ou naturel — Point de Branchement Optique — Raccordement et branchement abonné', 0.0),
  ('ENV_PBO_PANNE', 'ENV', 'PBO', 'PANNE', 1, 3, 'Cause environnementale sur les appuis ou naturel — Point de Branchement Optique — Panne abonné', 0.0),
  ('ENV_PBO_RACCOPANNE', 'ENV', 'PBO', 'RACCOPANNE', 1, 3, 'Cause environnementale sur les appuis ou naturel — Point de Branchement Optique — Panne au moment du raccordement', 0.0),
  ('ENV_BPE_RACCO', 'ENV', 'BPE', 'RACCO', 0, 3, 'Cause environnementale sur les appuis ou naturel — Boitier de Protection d''Etage — Raccordement et branchement abonné', 0.0),
  ('ENV_BPE_PANNE', 'ENV', 'BPE', 'PANNE', 0, 3, 'Cause environnementale sur les appuis ou naturel — Boitier de Protection d''Etage — Panne abonné', 0.0),
  ('ENV_BPE_RACCOPANNE', 'ENV', 'BPE', 'RACCOPANNE', 0, 3, 'Cause environnementale sur les appuis ou naturel — Boitier de Protection d''Etage — Panne au moment du raccordement', 0.0),
  ('ENV_PTO_RACCO', 'ENV', 'PTO', 'RACCO', 1, 3, 'Cause environnementale sur les appuis ou naturel — Point de Terminaison Optique Abonné — Raccordement et branchement abonné', 0.0),
  ('ENV_PTO_PANNE', 'ENV', 'PTO', 'PANNE', 1, 3, 'Cause environnementale sur les appuis ou naturel — Point de Terminaison Optique Abonné — Panne abonné', 0.0),
  ('ENV_PTO_RACCOPANNE', 'ENV', 'PTO', 'RACCOPANNE', 1, 3, 'Cause environnementale sur les appuis ou naturel — Point de Terminaison Optique Abonné — Panne au moment du raccordement', 0.0),
  ('ROP_NRO_RACCO', 'ROP', 'NRO', 'RACCO', 0, 3, 'Cause impliquant la route optique — Nœud de Raccordement Optique — Raccordement et branchement abonné', 0.8),
  ('ROP_NRO_PANNE', 'ROP', 'NRO', 'PANNE', 0, 3, 'Cause impliquant la route optique — Nœud de Raccordement Optique — Panne abonné', 0.8),
  ('ROP_NRO_RACCOPANNE', 'ROP', 'NRO', 'RACCOPANNE', 0, 3, 'Cause impliquant la route optique — Nœud de Raccordement Optique — Panne au moment du raccordement', 0.8),
  ('ROP_PM_RACCO', 'ROP', 'PM', 'RACCO', 0, 3, 'Cause impliquant la route optique — Point de mutualisation — Raccordement et branchement abonné', 0.8),
  ('ROP_PM_PANNE', 'ROP', 'PM', 'PANNE', 0, 3, 'Cause impliquant la route optique — Point de mutualisation — Panne abonné', 0.8),
  ('ROP_PM_RACCOPANNE', 'ROP', 'PM', 'RACCOPANNE', 0, 3, 'Cause impliquant la route optique — Point de mutualisation — Panne au moment du raccordement', 0.8),
  ('MAT_NRO_RACCO', 'MAT', 'NRO', 'RACCO', 0, 3, 'Cause impactant le matériel — Nœud de Raccordement Optique — Raccordement et branchement abonné', 0.35),
  ('MAT_NRO_PANNE', 'MAT', 'NRO', 'PANNE', 0, 3, 'Cause impactant le matériel — Nœud de Raccordement Optique — Panne abonné', 0.35),
  ('MAT_NRO_RACCOPANNE', 'MAT', 'NRO', 'RACCOPANNE', 0, 3, 'Cause impactant le matériel — Nœud de Raccordement Optique — Panne au moment du raccordement', 0.35),
  ('MAT_PM_RACCO', 'MAT', 'PM', 'RACCO', 0, 3, 'Cause impactant le matériel — Point de mutualisation — Raccordement et branchement abonné', 0.35),
  ('MAT_PM_PANNE', 'MAT', 'PM', 'PANNE', 0, 3, 'Cause impactant le matériel — Point de mutualisation — Panne abonné', 0.35),
  ('MAT_PM_RACCOPANNE', 'MAT', 'PM', 'RACCOPANNE', 0, 3, 'Cause impactant le matériel — Point de mutualisation — Panne au moment du raccordement', 0.35),
  ('MAT_PBO_RACCO', 'MAT', 'PBO', 'RACCO', 0, 3, 'Cause impactant le matériel — Point de Branchement Optique — Raccordement et branchement abonné', 0.35),
  ('MAT_PBO_PANNE', 'MAT', 'PBO', 'PANNE', 0, 3, 'Cause impactant le matériel — Point de Branchement Optique — Panne abonné', 0.35),
  ('MAT_PBO_RACCOPANNE', 'MAT', 'PBO', 'RACCOPANNE', 0, 3, 'Cause impactant le matériel — Point de Branchement Optique — Panne au moment du raccordement', 0.35),
  ('MAT_BPE_RACCO', 'MAT', 'BPE', 'RACCO', 0, 3, 'Cause impactant le matériel — Boitier de Protection d''Etage — Raccordement et branchement abonné', 0.35),
  ('MAT_BPE_PANNE', 'MAT', 'BPE', 'PANNE', 0, 3, 'Cause impactant le matériel — Boitier de Protection d''Etage — Panne abonné', 0.35),
  ('MAT_BPE_RACCOPANNE', 'MAT', 'BPE', 'RACCOPANNE', 0, 3, 'Cause impactant le matériel — Boitier de Protection d''Etage — Panne au moment du raccordement', 0.35),
  ('MAT_PTO_RACCO', 'MAT', 'PTO', 'RACCO', 0, 3, 'Cause impactant le matériel — Point de Terminaison Optique Abonné — Raccordement et branchement abonné', 0.35),
  ('MAT_PTO_PANNE', 'MAT', 'PTO', 'PANNE', 0, 3, 'Cause impactant le matériel — Point de Terminaison Optique Abonné — Panne abonné', 0.35),
  ('MAT_PTO_RACCOPANNE', 'MAT', 'PTO', 'RACCOPANNE', 0, 3, 'Cause impactant le matériel — Point de Terminaison Optique Abonné — Panne au moment du raccordement', 0.35),
  ('TECHNICIEN_MULTI_RACCO', 'TECHNICIEN', 'MULTI', 'RACCO', 0, 3, 'Cause impliquant le technicien — Transverse — Raccordement et branchement abonné', 0.5),
  ('TECHNICIEN_MULTI_PANNE', 'TECHNICIEN', 'MULTI', 'PANNE', 0, 3, 'Cause impliquant le technicien — Transverse — Panne abonné', 0.5),
  ('TECHNICIEN_MULTI_RACCOPANNE', 'TECHNICIEN', 'MULTI', 'RACCOPANNE', 0, 3, 'Cause impliquant le technicien — Transverse — Panne au moment du raccordement', 0.5),
  ('CLIENT_PTO_RACCO', 'CLIENT', 'PTO', 'RACCO', 0, 3, 'Cause commerciales ou humaines — Point de Terminaison Optique Abonné — Raccordement et branchement abonné', 0.05),
  ('CLIENT_PTO_PANNE', 'CLIENT', 'PTO', 'PANNE', 0, 3, 'Cause commerciales ou humaines — Point de Terminaison Optique Abonné — Panne abonné', 0.05),
  ('CLIENT_PTO_NON_INCIDENT', 'CLIENT', 'PTO', 'NON_INCIDENT', 0, 3, 'Cause commerciales ou humaines — Point de Terminaison Optique Abonné — Fausse alerte', 0.05),
  ('DEPL_NRO_RACCO', 'DEPL', 'NRO', 'RACCO', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Nœud de Raccordement Optique — Raccordement et branchement abonné', 0.5),
  ('DEPL_NRO_PANNE', 'DEPL', 'NRO', 'PANNE', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Nœud de Raccordement Optique — Panne abonné', 0.5),
  ('DEPL_NRO_RACCOPANNE', 'DEPL', 'NRO', 'RACCOPANNE', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Nœud de Raccordement Optique — Panne au moment du raccordement', 0.5),
  ('DEPL_PM_RACCO', 'DEPL', 'PM', 'RACCO', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Point de mutualisation — Raccordement et branchement abonné', 0.5),
  ('DEPL_PM_PANNE', 'DEPL', 'PM', 'PANNE', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Point de mutualisation — Panne abonné', 0.5),
  ('DEPL_PM_RACCOPANNE', 'DEPL', 'PM', 'RACCOPANNE', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Point de mutualisation — Panne au moment du raccordement', 0.5),
  ('DEPL_PBO_RACCO', 'DEPL', 'PBO', 'RACCO', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Point de Branchement Optique — Raccordement et branchement abonné', 0.5),
  ('DEPL_PBO_PANNE', 'DEPL', 'PBO', 'PANNE', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Point de Branchement Optique — Panne abonné', 0.5),
  ('DEPL_PBO_RACCOPANNE', 'DEPL', 'PBO', 'RACCOPANNE', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Point de Branchement Optique — Panne au moment du raccordement', 0.5),
  ('DEPL_BPE_RACCO', 'DEPL', 'BPE', 'RACCO', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Boitier de Protection d''Etage — Raccordement et branchement abonné', 0.5),
  ('DEPL_BPE_PANNE', 'DEPL', 'BPE', 'PANNE', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Boitier de Protection d''Etage — Panne abonné', 0.5),
  ('DEPL_BPE_RACCOPANNE', 'DEPL', 'BPE', 'RACCOPANNE', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Boitier de Protection d''Etage — Panne au moment du raccordement', 0.5),
  ('DEPL_PTO_RACCO', 'DEPL', 'PTO', 'RACCO', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Point de Terminaison Optique Abonné — Raccordement et branchement abonné', 0.5),
  ('DEPL_PTO_PANNE', 'DEPL', 'PTO', 'PANNE', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Point de Terminaison Optique Abonné — Panne abonné', 0.5),
  ('DEPL_PTO_RACCOPANNE', 'DEPL', 'PTO', 'RACCOPANNE', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Point de Terminaison Optique Abonné — Panne au moment du raccordement', 0.5),
  ('DEPL_BACK_RACCO', 'DEPL', 'BACK', 'RACCO', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Collecte-épine dorsale du réseau — Raccordement et branchement abonné', 0.5),
  ('DEPL_BACK_PANNE', 'DEPL', 'BACK', 'PANNE', 0, 3, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Collecte-épine dorsale du réseau — Panne abonné', 0.5),
  ('DEPL_BACK_RACCOPANNE', 'DEPL', 'BACK', 'RACCOPANNE', 0, 2, 'Cause impliquant le déploiement d''infrastructure non finalisé ou conforme — Collecte-épine dorsale du réseau — Panne au moment du raccordement', 0.5),
  ('PUBLIC_PM_RACCO', 'PUBLIC', 'PM', 'RACCO', 0, 2, 'Cause impliquant des interventions publiques — Point de mutualisation — Raccordement et branchement abonné', 0.0),
  ('PUBLIC_PM_PANNE', 'PUBLIC', 'PM', 'PANNE', 0, 2, 'Cause impliquant des interventions publiques — Point de mutualisation — Panne abonné', 0.0),
  ('PUBLIC_PM_NON_INCIDENT', 'PUBLIC', 'PM', 'NON_INCIDENT', 0, 2, 'Cause impliquant des interventions publiques — Point de mutualisation — Fausse alerte', 0.0),
  ('PUBLIC_PBO_RACCO', 'PUBLIC', 'PBO', 'RACCO', 0, 2, 'Cause impliquant des interventions publiques — Point de Branchement Optique — Raccordement et branchement abonné', 0.0),
  ('PUBLIC_PBO_PANNE', 'PUBLIC', 'PBO', 'PANNE', 0, 2, 'Cause impliquant des interventions publiques — Point de Branchement Optique — Panne abonné', 0.0),
  ('PUBLIC_PBO_NON_INCIDENT', 'PUBLIC', 'PBO', 'NON_INCIDENT', 0, 2, 'Cause impliquant des interventions publiques — Point de Branchement Optique — Fausse alerte', 0.0),
  ('PUBLIC_BACK_RACCO', 'PUBLIC', 'BACK', 'RACCO', 0, 2, 'Cause impliquant des interventions publiques — Collecte-épine dorsale du réseau — Raccordement et branchement abonné', 0.0),
  ('PUBLIC_BACK_PANNE', 'PUBLIC', 'BACK', 'PANNE', 0, 2, 'Cause impliquant des interventions publiques — Collecte-épine dorsale du réseau — Panne abonné', 0.0),
  ('PUBLIC_BACK_NON_INCIDENT', 'PUBLIC', 'BACK', 'NON_INCIDENT', 0, 2, 'Cause impliquant des interventions publiques — Collecte-épine dorsale du réseau — Fausse alerte', 0.0),
  ('PUBLIC_MULTI_RACCO', 'PUBLIC', 'MULTI', 'RACCO', 0, 2, 'Cause impliquant des interventions publiques — Transverse — Raccordement et branchement abonné', 0.0),
  ('PUBLIC_MULTI_PANNE', 'PUBLIC', 'MULTI', 'PANNE', 0, 2, 'Cause impliquant des interventions publiques — Transverse — Panne abonné', 0.0),
  ('PUBLIC_MULTI_NON_INCIDENT', 'PUBLIC', 'MULTI', 'NON_INCIDENT', 0, 2, 'Cause impliquant des interventions publiques — Transverse — Fausse alerte', 0.0);

-- Données : ref_parc_annuel (6 lignes) — ordre d'insertion d'origine conservé (le générateur lit dim_cause dans cet ordre)
INSERT INTO ref_parc_annuel (territoire, annee, nb_locaux_raccordables, nb_abonnes_ftth, nb_raccordements_annee, nb_pm) VALUES
  ('GLP', '2023', 232647, 85000, 33000, 900),
  ('GLP', '2024', 276913, 118000, 33000, 900),
  ('GLP', '2025', 306124, 145000, 27000, 900),
  ('MTQ', '2023', 132149, 54000, 18000, 680),
  ('MTQ', '2024', 148728, 72000, 18000, 680),
  ('MTQ', '2025', 171283, 90000, 18000, 680);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
