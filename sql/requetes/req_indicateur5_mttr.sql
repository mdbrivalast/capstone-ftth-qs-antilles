-- Indicateur 5 : MTTR par segment (moyenne ; médiane calculée à part — pas de fonction native SQLite)
-- Résultat attendu (base v1), moyenne en jours : D0 1,16 · D1 1,44 · D2 3,23 · D3 4,12 · NA 3,19
-- Médianes (calculées à part en Python)      : D0 1,04 · D1 1,29 · D2 2,88 · D3 3,68 · NA 2,86
SELECT rts.segment, rts.libelle, COUNT(*) AS n,
       ROUND(AVG(fs.temps_retablissement),2) AS mttr_moyen_j
FROM fait_signalisation fs
JOIN dim_cause dc            ON dc.code_cause = fs.fk_code_cause_sign
JOIN ref_troncon_segment rts ON rts.troncon   = dc.fk_troncon_reseau
GROUP BY rts.segment, rts.libelle ORDER BY rts.segment;
