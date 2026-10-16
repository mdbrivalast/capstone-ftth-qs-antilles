-- Indicateur 6 : Taux de RÉITÉRATION
-- Résultat attendu (base v1) : 105 254 abonnés touchés par au moins 1 panne ; 32,7 % en ont eu 2 ou plus
WITH par_abonne AS (SELECT fk_abonne_sign, COUNT(*) AS n FROM fait_signalisation GROUP BY fk_abonne_sign)
SELECT COUNT(*) AS touches,
       ROUND(100.0*SUM(CASE WHEN n>=2 THEN 1 ELSE 0 END)/COUNT(*),1) AS taux_reiteration_pct
FROM par_abonne;

