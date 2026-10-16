-- Indicateurs 2, 3, 4 : RACCORDEMENT par territoire (échec, reporté, reprise)
-- Reprise : dénominateur = raccordements RÉUSSIS uniquement (on ne reprend que ce qu'on a posé)
-- Résultat attendu (base v1) : GLP 114 816 raccordements → échec 11,0 % · reporté 8,0 % · reprise 11,1 %
--                              MTQ  66 672 raccordements → échec 11,0 % · reporté 8,0 % · reprise 11,0 %
SELECT fk_territoire_racc AS territoire,
       COUNT(*) AS n_racc,
       ROUND(100.0*SUM(CASE WHEN statut='echec'   THEN 1 ELSE 0 END)/COUNT(*),1) AS taux_echec_pct,
       ROUND(100.0*SUM(CASE WHEN statut='reporte' THEN 1 ELSE 0 END)/COUNT(*),1) AS taux_reporte_pct,
       ROUND(100.0*SUM(reprise_malfacon)
             /SUM(CASE WHEN statut='reussi' THEN 1 ELSE 0 END),1)                AS taux_reprise_pct
FROM fait_raccordement GROUP BY fk_territoire_racc;

