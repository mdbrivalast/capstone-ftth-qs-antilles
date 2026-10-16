-- Indicateur 2 : REPRISE POUR MALFAÇON par territoire
-- Dénominateur = raccordements RÉUSSIS uniquement (on ne reprend que ce qu'on a posé) ;
-- sur le total des raccordements, le taux tomberait à ~9 % et serait trompeur
-- Résultat attendu (base v1) : GLP 93 000 réussis → reprise 11,1 %
--                              MTQ 54 000 réussis → reprise 11,0 %
SELECT fk_territoire_racc AS territoire,
       SUM(CASE WHEN statut='reussi' THEN 1 ELSE 0 END) AS n_reussis,
       SUM(reprise_malfacon) AS n_reprises,
       ROUND(100.0*SUM(reprise_malfacon)
             /SUM(CASE WHEN statut='reussi' THEN 1 ELSE 0 END),1) AS taux_reprise_pct
FROM fait_raccordement
GROUP BY fk_territoire_racc;
