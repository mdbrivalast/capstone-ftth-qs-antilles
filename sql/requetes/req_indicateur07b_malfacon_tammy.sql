-- Indicateur 7b : part attendue de MALFAÇON en GLP, pendant Tammy et en dehors (appui du 4.3)
-- Part attendue = somme des probabilités p_malfacon des pannes / nombre de pannes
-- req_indicateur07b_malfacon_tammy.sql
-- But : vérifier la « pépite » du 4.3 (malfaçon 32 % → 18 % pendant Tammy)
-- Base SQLite, modèle DDL v5.6
-- Résultat attendu (base v1) : Tammy (oct. 2023) 3 320 pannes → 18,2 %
-- autres mois saison cyclonique 46 780 pannes → 28,7 %

SELECT s.fk_mois_sign AS periode,
       COUNT( * ) AS n_pannes,
       SUM(s.malfacon) AS n_malfacons,
       ROUND(100.0 * SUM(s.malfacon) / COUNT( * ), 1) AS pct_malfacon
  FROM fait_signalisation AS s
 WHERE s.fk_territoire_sign = 'GLP' AND s.fk_mois_sign BETWEEN '2023-08' AND '2023-12' -- Tammy n'a touché que la Guadeloupe
 GROUP BY s.fk_mois_sign
 ORDER BY s.fk_mois_sign;