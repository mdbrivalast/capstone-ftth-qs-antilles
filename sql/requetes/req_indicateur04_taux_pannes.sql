-- Indicateur 4 : TAUX DE PANNE mensuel = pannes / parc actif (parc reconstruit par le flux)
-- Résultat attendu (base v1) : 72 lignes (2 territoires × 36 mois)
--   taux de base ≈ 2,56 %/mois (médiane GLP et MTQ 2,56 %)
--   pic GLP 2023-10 (Tammy) = 4,38 % ; maximum MTQ 2024-07 = 3,19 %
WITH activation AS (
  SELECT a.id_abonne, p.fk_territoire_pm AS territoire,
         COALESCE(MIN(substr(r.date_mise_en_service,1,7)),'2022-12') AS mois_actif
  FROM dim_abonne a
  JOIN dim_pm p                ON p.id_pm = a.fk_id_pm_abo
  LEFT JOIN fait_raccordement r ON r.fk_abonne_racc = a.id_abonne AND r.statut='reussi'
  GROUP BY a.id_abonne),
parc AS (
  SELECT t.mois, act.territoire, COUNT(*) AS parc_actif
  FROM dim_temps t JOIN activation act ON act.mois_actif <= t.mois
  GROUP BY t.mois, act.territoire),
pannes AS (
  SELECT fk_mois_sign AS mois, fk_territoire_sign AS territoire, COUNT(*) AS n
  FROM fait_signalisation GROUP BY 1,2)
SELECT p.territoire, p.mois, pa.n AS pannes, p.parc_actif,
       ROUND(100.0*pa.n/p.parc_actif,2) AS taux_panne_pct
FROM parc p JOIN pannes pa ON pa.mois=p.mois AND pa.territoire=p.territoire
ORDER BY p.territoire, p.mois;
