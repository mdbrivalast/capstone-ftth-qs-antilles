-- =====================================================================
-- PATCH v5.4 — Capstone #3 (observatoire qualité FTTH Outre-mer)
-- Objet : option 1 — l'enveloppe réelle devient une table SQL.
--   (1) dim_territoire allégée : on retire les mesures annuelles
--       (nb_locaux_raccordables / nb_abonnes_ftth) + ajout d'un libelle.
--   (2) nouvelle table ref_parc_annuel (réel, ancre #1), grain territoire x année.
--
-- ⚠️  À EXÉCUTER SUR LA BASE DÉJÀ PEUPLÉE (cap3v5.db).
--     Ce patch NE touche PAS dim_cause ni ref_troncon_segment (déjà chargées).
--     NE PAS relancer le DDL complet (ses DROP effaceraient tout).
-- =====================================================================
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- (1) Refonte dim_territoire (table vide -> indolore)
DROP TABLE IF EXISTS dim_territoire;
CREATE TABLE dim_territoire (
    territoire TEXT PRIMARY KEY
                    CHECK (territoire IN ('GLP','MTQ','NAT')),  -- GLP=971+977+978, MTQ=972, NAT=national (réserve)
    libelle    TEXT                                            -- pour l'affichage dashboard
);
INSERT INTO dim_territoire (territoire, libelle) VALUES
  ('GLP','Guadeloupe (971+977+978)'),
  ('MTQ','Martinique (972)');

-- (2) Enveloppe réelle — grain territoire x année
DROP TABLE IF EXISTS ref_parc_annuel;
CREATE TABLE ref_parc_annuel (
    territoire             TEXT    NOT NULL,
    annee                  TEXT    NOT NULL,          -- 'YYYY' (cohérent dim_temps.annee)
    nb_locaux_raccordables INTEGER,                   -- réel (cas #1)
    nb_abonnes_ftth        INTEGER,                   -- réel : STOCK fin d'année -> base des pannes
    nb_raccordements_annee INTEGER,                   -- dérivé : FLUX (Δ stock, churn négligé) -> base des échecs de pose
    nb_pm                  INTEGER,                   -- déduit (GLP ~900 terrain, MTQ ~680 homothétie) ; constant sur la fenêtre
    PRIMARY KEY (territoire, annee),
    FOREIGN KEY (territoire) REFERENCES dim_territoire (territoire)
);
INSERT INTO ref_parc_annuel
  (territoire,annee,nb_locaux_raccordables,nb_abonnes_ftth,nb_raccordements_annee,nb_pm) VALUES
  ('GLP','2023',232647, 85000,33000,900),
  ('GLP','2024',276913,118000,33000,900),
  ('GLP','2025',306124,145000,27000,900),
  ('MTQ','2023',132149, 54000,18000,680),
  ('MTQ','2024',148728, 72000,18000,680),
  ('MTQ','2025',171283, 90000,18000,680);

COMMIT;
PRAGMA foreign_keys = on;
