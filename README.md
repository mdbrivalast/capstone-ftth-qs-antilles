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
│   └── patches/                        # évolutions successives du schéma (v5.4, v5.5)
├── scripts/
│   ├── generateur_faits_cap3.py    # générateur des données simulées (seed figé)
│   ├── zapm_centroides_om.py       # comptage des PM outre-mer depuis le shapefile ZAPM de l'Arcep
│   └── prototypes/moteur_pannes.py # prototype CSV du moteur de pannes (cheminement : voir git log de ce fichier)
├── docs/                           # note méthodologique, calibrage cyclonique, vérification sourcée des cyclones
└── CHANGELOG.md                    # historique des versions du modèle
```

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
