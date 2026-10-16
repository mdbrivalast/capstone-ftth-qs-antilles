-- Indicateur 8 : MÉCANISME CYCLONE : pannes oct vs sept 2023 (GLP) par tranche d'aérien du PM
-- Résultat attendu (base v1), ratio oct/sept 2023 en GLP :
--   enterré 1,40 (119 → 167) · mixte 1,52 (570 → 869) · aérien 1,91 (1 195 → 2 284)
--   plus le PM est aérien, plus Tammy le frappe
SELECT CASE WHEN p.part_aerien < 0.4 THEN 'enterré'
            WHEN p.part_aerien < 0.7 THEN 'mixte' ELSE 'aérien' END AS tranche,
       SUM(CASE WHEN fs.fk_mois_sign='2023-09' THEN 1 ELSE 0 END) AS sept,
       SUM(CASE WHEN fs.fk_mois_sign='2023-10' THEN 1 ELSE 0 END) AS oct
FROM fait_signalisation fs
JOIN dim_pm p ON p.id_pm = fs.fk_id_pm_sign
WHERE fs.fk_territoire_sign='GLP' AND fs.fk_mois_sign IN ('2023-09','2023-10')
GROUP BY tranche;
