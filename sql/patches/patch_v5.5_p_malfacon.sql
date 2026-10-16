-- =====================================================================
--  patch_v5.5_p_malfacon.sql
--  Ajoute la colonne p_malfacon a dim_cause (levier malfaçon, cas #3).
--
--  Semantique : p_malfacon = P(flag malfaçon = 1 | la cause est ce triplet)
--               = part des incidents de ce triplet qui sont une malfaçon.
--               Definition A hybride (main humaine evitable), plate par nature (v2).
--               Modulation par portee : PARKEE (a affiner apres 1er dataset).
--
--  Calibrage attendu : part de malfaçon des PANNES ~= 30 %
--                       (cf. ancre terrain 1/3-1/2, dip en mois cyclonique).
--  A executer UNE fois sur la base (ex. cap3v5.db).
-- =====================================================================

ALTER TABLE dim_cause ADD COLUMN p_malfacon REAL
      CHECK (p_malfacon BETWEEN 0 AND 1);

UPDATE dim_cause SET p_malfacon = 0.80 WHERE quoi = 'ROP';  -- route optique (erreur amont OC/BE)
UPDATE dim_cause SET p_malfacon = 0.50 WHERE quoi = 'TECHNICIEN';  -- technicien (comportement/competences vs empeche)
UPDATE dim_cause SET p_malfacon = 0.50 WHERE quoi = 'DEPL';  -- deploiement (non conforme vs non finalise/systeme)
UPDATE dim_cause SET p_malfacon = 0.45 WHERE quoi = 'CONT';  -- continuite/signal
UPDATE dim_cause SET p_malfacon = 0.40 WHERE quoi = 'CABLE#FIBRE';  -- cable/fibre (pose vs externe)
UPDATE dim_cause SET p_malfacon = 0.35 WHERE quoi = 'MAT';  -- materiel (mal pose vs defaut usine)
UPDATE dim_cause SET p_malfacon = 0.15 WHERE quoi = 'ACCES';  -- acces (surtout empeche/circonstanciel)
UPDATE dim_cause SET p_malfacon = 0.10 WHERE quoi = 'GC';  -- genie civil (souvent un tiers)
UPDATE dim_cause SET p_malfacon = 0.05 WHERE quoi = 'CLIENT';  -- client (pas une malfaçon reseau)
UPDATE dim_cause SET p_malfacon = 0.00 WHERE quoi = 'ENV';  -- environnemental (fortuit/externe)
UPDATE dim_cause SET p_malfacon = 0.00 WHERE quoi = 'PUBLIC';  -- intervention publique (externe)

-- --- Controles ---
-- 1) Aucun triplet laisse a NULL (les 11 natures couvrent les 135) :
SELECT 'NULL restants' AS controle, COUNT(*) AS n
FROM dim_cause WHERE p_malfacon IS NULL;

-- 2) Recap par nature :
SELECT quoi, ROUND(p_malfacon,2) AS p_malfacon, COUNT(*) AS nb_triplets
FROM dim_cause GROUP BY quoi, p_malfacon ORDER BY p_malfacon DESC;

-- 3) Part de malfaçon attendue par portee (moyenne ponderee par score) :
SELECT portee,
       ROUND(SUM(score*p_malfacon)*1.0/SUM(score),3) AS part_malfacon_attendue,
       COUNT(*) AS nb_triplets
FROM dim_cause GROUP BY portee ORDER BY part_malfacon_attendue DESC;
