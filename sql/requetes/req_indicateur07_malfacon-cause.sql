-- Indicateur 7 : CAUSES par nature (QUOI) + part de malfaçon de chaque nature
-- AVG(malfacon) = proportion de pannes flaggées malfaçon (malfacon vaut 0 ou 1)
-- Résultat attendu (base v1) : 11 natures, 150 527 pannes au total
--   les plus fréquentes : CABLE#FIBRE 22 939 · CONT 22 761 · GC 19 158
--   malfaçon la plus forte : ROP 80,1 % ; ENV et PUBLIC 0 % (causes non humaines)
SELECT dc.quoi,
       COUNT(*)          AS n_pannes,      				-- toutes les pannes de la nature
       SUM(fs.malfacon)  AS n_malfacon,    				-- somme de 0 et de 1 = somme seulement celles où malfacon = 1
       ROUND(100.0*AVG(fs.malfacon),1) AS pct_malfacon 			-- la proportion malfacon (SUM) / pannes (COUNT)
FROM fait_signalisation fs
JOIN dim_cause dc ON dc.code_cause = fs.fk_code_cause_sign   -- rattache chaque panne à sa cause
GROUP BY dc.quoi ORDER BY n_pannes DESC;