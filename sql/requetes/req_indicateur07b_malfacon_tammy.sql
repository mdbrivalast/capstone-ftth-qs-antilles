-- Indicateur 7b : part de MALFAÇON (drapeau malfacon) mois par mois en GLP, août → déc. 2023, autour de Tammy (appui du 4.3)
-- Base SQLite, modèle DDL v5.6
-- Résultat attendu (base v1) : Tammy (oct. 2023) 3 320 pannes → 18,2 %, autres mois : aout 30,4 %; sept. 32,4%; nov. 28,7 %; dec. 28,7 %) 
SELECT s.fk_mois_sign AS mois,
       COUNT( * ) AS n_pannes,
       SUM(s.malfacon) AS n_malfacons,
       ROUND(100.0 * SUM(s.malfacon) / COUNT( * ), 1) AS pct_malfacon
  FROM fait_signalisation AS s
 WHERE s.fk_territoire_sign = 'GLP' AND s.fk_mois_sign BETWEEN '2023-08' AND '2023-12' -- Tammy n'a touché que la Guadeloupe
 GROUP BY s.fk_mois_sign
 ORDER BY s.fk_mois_sign;