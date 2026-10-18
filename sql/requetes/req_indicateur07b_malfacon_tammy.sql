-- req_indicateur07b_malfacon_tammy.sql
-- But : vérifier la « pépite » du 4.3 (malfaçon 32 % → 18 % pendant Tammy)
-- Base SQLite, modèle DDL v5.5

SELECT
    -- On classe chaque mois dans une des 3 périodes
    CASE
        WHEN s.fk_mois_sign = '2023-10'  THEN '1. Tammy (oct. 2023)'
        WHEN t.saison_cyclonique = 1     THEN '2. Autres mois saison cyclonique'
        ELSE                                  '3. Hors saison cyclonique'
    END                                              AS periode,
    COUNT(*)                                         AS n_pannes,
    -- Nombre attendu de malfaçons = somme des probabilités de chaque panne
    ROUND(SUM(c.p_malfacon), 0)                      AS n_malfacons_attendues,
    -- Part attendue de malfaçon, en %
    ROUND(100.0 * SUM(c.p_malfacon) / COUNT(*), 1)   AS pct_malfacon
FROM fait_signalisation AS s
-- La cause donne la probabilité de malfaçon
JOIN dim_cause AS c ON c.code_cause = s.fk_code_cause_sign
-- Le calendrier donne le drapeau saison cyclonique
JOIN dim_temps AS t ON t.mois = s.fk_mois_sign
WHERE s.fk_territoire_sign = 'GLP'   -- Tammy n'a touché que la Guadeloupe
GROUP BY periode
ORDER BY periode;