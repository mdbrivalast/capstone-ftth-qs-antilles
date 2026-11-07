# Changelog — Observatoire qualité FttH outre-mer
## [2026-11-07] — version 1 finalisée (baseline `observatoire-ftth-qs-antilles_v1`)
### Ajouté
- `scripts/visuels/` : les 7 visuels du Share, la tuile KPI et la planche (Matplotlib). Copies des versions de travail ; seuls les chemins (racine du dépôt, `sql/requetes/`, `images/`) et trois noms d'image changent.
- `images/` : visuels en SVG (`v0` à `v7`, `planche_share.svg`), régénérés depuis le dépôt.
- `data/ref_evenements_cycloniques.csv` : tempêtes et cyclones 2023-2025, source des étiquettes des pics (visuel 2+3).

### Modifié
- Indicateur 7b : calculé désormais avec le drapeau `malfacon`, mois par mois (GLP, août → déc. 2023 : 18,2 % en octobre). Les chiffres du 18/10 (17,7 / 29,2 / 29,9 %) venaient de la part **attendue** (somme des `p_malfacon`) et ne sont plus utilisés.
- Indicateur 8 : libellés de tranche accentués (`enterré`, `aérien`).
- En-têtes des requêtes 04 (médiane 2,56 %) et 07b (définition) corrigés.
- `README.md` : version finale (résumé, démarche, visuels, reproduction en DDL v5.6, sources).
- `notebooks/observatoire_qs_kaggle.ipynb` : notebook Kaggle qui clone le tag v1, régénère la base, rejoue les 9 requêtes (toutes identiques aux résultats publiés) et redessine les visuels.
- `docs/FTTH-Antilles-qualite-de-service.pdf` : rapport complet.
## [2026-10-19]
- Mise à jour base de donnée v5.6 : fichier DDL-capstone3-v5.6.sql avce l'ajout de la colonne malfacon dans la table fait_signalement. 
- Ajout du fichier de peuplement DDL-capstone3-v5.6.sql-peuple.sql. 

### Contrôlé
- Reproductibilité : base régénérée depuis `DDL-capstone3-v5.6-peuple.sql` + générateur, contenu identique table par table à la base de l'analyse.

- Ajout de l'image du réseau FTTH 
 
## [2026-10-18]
### Ajouté
- `sql/requetes/res_indicateurNN_<titre>.csv` : résultats exportés des 8 indicateurs (+ 7b) sur la base v1.
- `sql/requetes/req_indicateur07b_malfacon_tammy.sql` (+ résultat) : part de malfaçon pendant Tammy (GLP 2023-10 : 17,7 %) contre 29,2 % le reste de la saison cyclonique et 29,9 % hors saison.

### Modifié
- `README.md` : structure du dépôt mise à jour (`sql/patches/`, `sql/requetes/`, `images/`) + tableau des 8 indicateurs ; `prototypes/moteur_pannes.py` décrit comme maquette de réglage.
- Rapport d'analyse v4 : PROCESS découpé en 3.1 / 3.2 / 3.3, tableau de contrôle des 8 indicateurs en 4.0, annexes refaites avec les 9 requêtes.

### Limite connue
- La colonne `malfacon` de `fait_signalisation` existe dans la base peuplée mais pas encore dans le DDL v5.5 → à intégrer en v5.6.

## [2026-10-16]
### Ajouté
- `sql/requetes/req_indicateur01` à `08` : requêtes SQL commentées des 8 indicateurs qualité.

### Contrôlé
- Reproductibilité : base régénérée depuis `DDL-capstone3-v5.5-peuple.sql` + générateur, contenu identique table par table à la base de l'analyse.

## [2026-10-15]
- renommage des fichiers DDL
- organisation arborescence du projet
- rédaction des section 1 (Demander) 2(Données) du rapport d'analyse v3.

## [2026-10-09]
### Ajouté
- `scripts/generateur_faits_cap3.py` : générateur unifié (dim_temps, dim_pm, dim_abonne, fait_raccordement, fait_signalisation), seed figé, idempotent.
- `fait_signalisation.malfacon` (flag 0/1, `ALTER TABLE` dans le générateur).
- Base v1 peuplée : 36 mois · 1 580 PM · 235 000 abonnés · 181 488 raccordements · 150 527 pannes, `foreign_key_check` = 0 violation.
- `docs/note-methodo-simulation.md` ; `docs/calibrage_cyclonique_2023-2025.md` mis à jour.

## [2026-10-07]
### Modifié
- `fait_signalisation.sid` : INTEGER → TEXT PRIMARY KEY (cohérence avec `rid` ; id parlants `SIG-`/`RAC-`). DDL → v5.3.
- `dim_territoire` allégée : `nb_locaux_raccordables`/`nb_abonnes_ftth` retirées (→ `ref_parc_annuel`), ajout `libelle`.

### Ajouté
- Peuplement exécuté : `ref_troncon_segment` (7 lignes) + `dim_cause` (135 triplets).

## [2026-10-06]
### Ajouté
- `dim_cause` : colonnes `quoi` + `score` ; CHECK `portee` ; `fk_troncon_reseau NOT NULL` (DDL v5.1).
- Renommage `CABLE-FIBRE` → `CABLE#FIBRE` (DDL v5.2).
- Table `ref_parc_annuel` (enveloppe réelle, grain territoire×année) + 6 lignes — via `patch_v5.4_parc_annuel.sql`. DDL → v5.4.
- `parc_annuel_reel.csv` (source de l'enveloppe, dérivée du cas #1).
- `dim_cause` : colonnes `p_malfacon` ; (DDL v5.5).
  
### Figé
- `sensible_aerien = 1` sur les 9 triplets ENV {PM, PBO, PTO}.
