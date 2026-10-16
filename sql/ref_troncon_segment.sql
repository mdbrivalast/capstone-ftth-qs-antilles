--
-- Fichier généré avec Letos v4.0.3 le Mon Oct 5 15:53:36 2026
--
-- Encodage texte utilisé : UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Tableau : ref_troncon_segment
DROP TABLE IF EXISTS ref_troncon_segment;

CREATE TABLE IF NOT EXISTS ref_troncon_segment (
    troncon TEXT,
    segment TEXT,
    libelle TEXT
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
