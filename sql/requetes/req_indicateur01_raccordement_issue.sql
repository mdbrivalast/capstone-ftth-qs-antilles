-- Indicateur 1 : ISSUE DU RACCORDEMENT par territoire (échec / reporté / réussi)
-- Une seule répartition : les trois taux font 100 % (dénominateur = tous les raccordements)
-- Résultat attendu (base v1) : GLP 114 816 raccordements → échec 11,0 % · reporté 8,0 % · réussi 81,0 %
--                              MTQ  66 672 raccordements → échec 11,0 % · reporté 8,0 % · réussi 81,0 %
SELECT fk_territoire_racc AS territoire,
       COUNT(*) AS n_racc,
       ROUND(100.0*SUM(CASE WHEN statut='echec'   THEN 1 ELSE 0 END)/COUNT(*),1) AS taux_echec_pct,
       ROUND(100.0*SUM(CASE WHEN statut='reporte' THEN 1 ELSE 0 END)/COUNT(*),1) AS taux_reporte_pct,
       ROUND(100.0*SUM(CASE WHEN statut='reussi'  THEN 1 ELSE 0 END)/COUNT(*),1) AS taux_reussi_pct
FROM fait_raccordement
GROUP BY fk_territoire_racc;
