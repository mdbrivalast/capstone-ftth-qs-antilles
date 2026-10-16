# Changelog — Capstone #3 (observatoire qualité FTTH Outre-mer)

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

## [2026-10-15]
- renommage des fichiers DDL
- organisation arborescence du projet
- rédaction des section 1 (Demander) 2(Données) du rapport d'analyse v3.
  
### Figé
- `sensible_aerien = 1` sur les 9 triplets ENV {PM, PBO, PTO}.
