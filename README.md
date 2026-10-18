# capstone-ftth-qs-antilles
Case study Data Analyst — FttH aux Antilles :  quelle vision sur la qualité de service et où agir ?
**Cas d'étude Data Analyst · Capstone3 **
Par Maritza Brival

En cours

---

## La question

## Les données (Prepare)

## Nettoyage & transformation (Process)

## Analyse (Analyze)

## Visualisation (Share)

## Recommandations (Act)

## Structure du dépôt

```
├── data/
│   ├── arcep/                      # CSV bruts de l'observatoire qualité FttH de l'Arcep (data.gouv.fr, juillet 2026)
│   ├── parc_annuel_reel.csv        # enveloppe réelle (locaux, abonnés, raccordements, PM) dérivée du cas #1
│   └── p_malfacon_mapping.csv      # propension de malfaçon par triplet de cause
├── sql/
│   ├── DDL-capstone3-v5.5.sql          # schéma seul (modèle en étoile)
│   ├── DDL-capstone3-v5.5-peuple.sql   # schéma + référentiels (point de départ de la reproduction)
│   ├── peuplement_dim_cause.sql, peuplement_dim_temps.sql, ref_troncon_segment.sql
│   ├── patches/                        # évolutions successives du schéma
│   │   ├── patch_v5.4_parc_annuel.sql
│   │   └── patch_v5.5_p_malfacon.sql
│   └── requetes/                       # les 8 indicateurs qualité (+ 7b) : requête et résultat exporté
│       ├── req_indicateurNN_<titre>.sql    # requête SQL commentée (01 à 08, + 07b)
│       └── res_indicateurNN_<titre>.csv    # résultat de la requête sur la base v1
├── scripts/
│   ├── generateur_faits_cap3.py    # générateur des données simulées (seed figé)
│   ├── zapm_centroides_om.py       # comptage des PM outre-mer depuis le shapefile ZAPM de l'Arcep
│   └── prototypes/moteur_pannes.py # maquette du moteur de pannes (territoire × mois, sortie CSV) qui a servi à tester les réglages
├── docs/                           # note méthodologique, calibrage cyclonique, vérification sourcée des cyclones, schéma (.dot)
├── images/                         # schéma du modèle en étoile (PNG, SVG)
└── CHANGELOG.md                    # historique des versions du modèle
```

### Les 8 indicateurs (`sql/requetes/`)

| # | Indicateur | Fichiers |
|---|---|---|
| 1 | Issue des raccordements | `req_/res_indicateur01_raccordement_issue` |
| 2 | Reprise des malfaçons au raccordement | `req_/res_indicateur02_raccordement_reprise` |
| 3 | Délai de mise en service | `req_/res_indicateur03_delai_mes` |
| 4 | Taux de pannes mensuel | `req_/res_indicateur04_taux_pannes` |
| 5 | MTTR par segment | `req_/res_indicateur05_mttr` |
| 6 | Réitération (abonnés à ≥ 2 pannes) | `req_/res_indicateur06_reiteration` |
| 7 | Malfaçon par cause | `req_/res_indicateur07_malfacon-cause` |
| 7b | Malfaçon pendant Tammy (appui du 4.3) | `req_/res_indicateur07b_malfacon_tammy` |
| 8 | Effet cyclone par tranche d'aérien des PM | `req_/res_indicateur08_cyclone_tranche-aerienpm` |

La base SQLite n'est pas versionnée : elle se régénère à l'identique (voir ci-dessous).

## Reproduire l'analyse

Prérequis : Python 3 avec `pandas` et `numpy`.

```bash
# 1. Créer une base neuve à partir du schéma + référentiels
#    (avec l'outil sqlite3 en ligne de commande)
sqlite3 cap3v5.db < sql/DDL-capstone3-v5.5-peuple.sql
#    ou, sans sqlite3, avec Python seul :
python -c "import sqlite3; c=sqlite3.connect('cap3v5.db'); c.executescript(open('sql/DDL-capstone3-v5.5-peuple.sql', encoding='utf-8').read()); c.commit()"

# 2. Générer les données simulées (seed figé = même résultat à chaque exécution)
python scripts/generateur_faits_cap3.py cap3v5.db
```

Résultat attendu (contrôlé le 16/10/2026, contenu identique table par table à la base de l'analyse) :

| Table | Lignes |
|---|---|
| dim_temps | 36 |
| dim_pm | 1 580 |
| dim_abonne | 235 000 |
| fait_raccordement | 181 488 |
| fait_signalisation | 150 527 |

Le script se termine par un `foreign_key_check` qui doit afficher 0 violation.

## Code

## Sources

## À propos
