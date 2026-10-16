-- Indicateur 2b : DÉLAI DE MISE EN SERVICE (MES) par territoire
-- Délai = date de mise en service - date de commande, en jours (julianday = n° de jour, la différence donne des jours)
-- Périmètre : raccordements RÉUSSIS uniquement (seuls eux ont une date de mise en service)
-- Résultat attendu (base v1) : GLP 93 000 réussis → 44,6 j · 77,9 % sous 60 j
--                              MTQ 54 000 réussis → 44,9 j · 77,6 % sous 60 j
--                              ensemble : 44,7 j · 77,8 % sous 60 j (national : 85,3 %)
SELECT fk_territoire_racc AS territoire,
       COUNT(*) AS n_reussis,
       ROUND(AVG(julianday(date_mise_en_service) - julianday(date_commande)),1) AS delai_moyen_j,
       ROUND(100.0*SUM(CASE WHEN julianday(date_mise_en_service) - julianday(date_commande) < 60
                            THEN 1 ELSE 0 END)/COUNT(*),1) AS pct_mes_moins_60j
FROM fait_raccordement
WHERE statut = 'reussi'
GROUP BY fk_territoire_racc;
