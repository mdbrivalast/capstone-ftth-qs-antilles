#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zapm_centroides_om.py
---------------------
Compte les PM (points de mutualisation) fibre optique des territoires d'outre-mer
à partir du shapefile ZAPM de l'Arcep (data.gouv.fr) et exporte, pour chaque ZAPM,
un point représentatif en latitude/longitude (WGS84).

Hypothèse : 1 ZAPM = 1 PM (identifiant RefPM unique). Les points sont des repères
géométriques de la zone, PAS la position réelle du PM.

Colonnes de coordonnées du CSV :
  latitude / longitude          point sur la surface : toujours à l'intérieur de la zone
  lat_centroide / lon_centroide centre géométrique (peut tomber hors de la zone)
  centroide_hors_zone           "oui" si le centroïde est en dehors du polygone

Aucune dépendance externe (bibliothèque standard uniquement) :
    py -3.12 zapm_centroides_om.py

Options :
    py -3.12 zapm_centroides_om.py --shp chemin\\2026T2_ZAPM.shp --sortie resultat.csv
"""

import argparse
import csv
import math
import struct
import sys
from collections import Counter
from pathlib import Path

# --- Paramètres par défaut ---------------------------------------------------
DOSSIER_QGIS = Path.home() / "Documents" / "ANTHROPIC" / "Projects" / "QGIS"   # dossier par défaut, modifiable avec --shp / --sortie
SHP_DEFAUT = DOSSIER_QGIS / "2026t2-zapm" / "2026T2_ZAPM.shp"
SORTIE_DEFAUT = DOSSIER_QGIS / "export_csv" / "ZAPM_outre-mer_points_latlon.csv"

# Codes INSEE départements -> territoires traités
TERRITOIRES = {
    "971": "Guadeloupe",
    "972": "Martinique",
    "977": "Saint-Barthélemy",
    "978": "Saint-Martin",
}

# Champs attributaires repris dans le CSV de sortie
CHAMPS_SORTIE = [
    "CodeOI", "INSEE_DEP", "NOM_DEP", "INSEE_COM", "NOM_COM", "NOM_IRIS",
    "RefPM", "EtatPM", "date_debut", "lgtZAPM", "lgtMadPM", "taux", "couv", "aire",
]

COLONNES_GEO = ["latitude", "longitude", "lat_centroide", "lon_centroide", "centroide_hors_zone"]

RAYON_TERRE = 6378137.0  # sphère WGS84 utilisée par Web Mercator (EPSG:3857)


# --- Lecture du DBF ----------------------------------------------------------
def lire_dbf(chemin):
    """Générateur : (index_enregistrement, dict des attributs) pour chaque ligne non supprimée."""
    with open(chemin, "rb") as f:
        entete = f.read(32)
        nb_enreg = struct.unpack("<I", entete[4:8])[0]
        taille_entete = struct.unpack("<H", entete[8:10])[0]
        taille_enreg = struct.unpack("<H", entete[10:12])[0]

        champs = []
        while True:
            desc = f.read(32)
            if desc[0] == 0x0D:
                break
            champs.append((desc[:11].split(b"\0")[0].decode("ascii"), desc[16]))

        f.seek(taille_entete)
        for i in range(nb_enreg):
            brut = f.read(taille_enreg)
            if brut[0:1] == b"*":  # enregistrement supprimé
                continue
            pos = 1
            ligne = {}
            for nom, longueur in champs:
                ligne[nom] = brut[pos:pos + longueur].decode("utf-8", "replace").strip()
                pos += longueur
            yield i, ligne


# --- Lecture de la géométrie (SHP/SHX) --------------------------------------
def lire_polygone(f_shp, offset_octets):
    """Lit un enregistrement polygone et renvoie la liste des anneaux [(x, y), ...]."""
    f_shp.seek(offset_octets + 8)  # on saute l'en-tête d'enregistrement (numéro + longueur)
    type_forme = struct.unpack("<i", f_shp.read(4))[0]
    if type_forme == 0:  # forme nulle
        return []
    if type_forme not in (5, 15, 25):  # Polygon, PolygonZ, PolygonM
        raise ValueError(f"Type de forme non géré : {type_forme}")
    f_shp.read(32)  # boîte englobante
    nb_parties, nb_points = struct.unpack("<ii", f_shp.read(8))
    parties = list(struct.unpack(f"<{nb_parties}i", f_shp.read(4 * nb_parties)))
    coords = struct.unpack(f"<{2 * nb_points}d", f_shp.read(16 * nb_points))
    points = list(zip(coords[0::2], coords[1::2]))
    parties.append(nb_points)
    return [points[parties[k]:parties[k + 1]] for k in range(nb_parties)]


def centroide_polygone(anneaux):
    """
    Centroïde pondéré par la surface (anneaux extérieurs + trous, orientations opposées
    dans un shapefile : les surfaces signées se compensent). Renvoie (x, y) ou None.
    """
    if not anneaux:
        return None
    x0, y0 = anneaux[0][0]  # décalage pour limiter les erreurs d'arrondi
    aire_tot = cx_tot = cy_tot = 0.0
    for anneau in anneaux:
        a = cx = cy = 0.0
        for (xa, ya), (xb, yb) in zip(anneau, anneau[1:]):
            xa -= x0; ya -= y0; xb -= x0; yb -= y0
            croise = xa * yb - xb * ya
            a += croise
            cx += (xa + xb) * croise
            cy += (ya + yb) * croise
        a /= 2.0
        if a == 0:
            continue
        aire_tot += a
        cx_tot += cx / 6.0  # = centroïde_x * aire_signée
        cy_tot += cy / 6.0
    if aire_tot == 0:
        # zone dégénérée : moyenne simple des sommets
        pts = [p for an in anneaux for p in an]
        return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
    return (x0 + cx_tot / aire_tot, y0 + cy_tot / aire_tot)


def point_dans_polygone(x, y, anneaux):
    """Test point-dans-polygone par règle pair/impair (les trous sont donc exclus)."""
    dedans = False
    for anneau in anneaux:
        for (xa, ya), (xb, yb) in zip(anneau, anneau[1:]):
            if (ya > y) != (yb > y) and x < xa + (y - ya) * (xb - xa) / (yb - ya):
                dedans = not dedans
    return dedans


def point_sur_surface(anneaux):
    """
    Point garanti à l'intérieur de la zone (même principe que « Point sur la surface » de QGIS) :
    on trace une ligne horizontale à mi-hauteur, entre deux ordonnées de sommets (donc sans
    toucher aucun sommet), on relève les intersections avec tous les anneaux, et on prend le
    milieu du plus long segment situé dedans.
    """
    if not anneaux:
        return None
    ordonnees = sorted({p[1] for an in anneaux for p in an})
    if len(ordonnees) < 2:
        return None
    milieu = (ordonnees[0] + ordonnees[-1]) / 2.0
    # hauteurs candidates (entre deux ordonnées consécutives de sommets), de la plus proche
    # du milieu de la zone à la plus éloignée : utile si la zone est en plusieurs morceaux
    # et que la ligne du milieu passe dans le vide entre deux d'entre eux
    candidats = sorted(((a + b) / 2.0 for a, b in zip(ordonnees, ordonnees[1:])),
                       key=lambda v: abs(v - milieu))
    for y in candidats:
        xs = []
        for anneau in anneaux:
            for (xa, ya), (xb, yb) in zip(anneau, anneau[1:]):
                if (ya > y) != (yb > y):
                    xs.append(xa + (y - ya) * (xb - xa) / (yb - ya))
        xs.sort()
        # intersections prises deux par deux : [entrée, sortie] = segments à l'intérieur
        segments = list(zip(xs[0::2], xs[1::2]))
        if segments:
            debut, fin = max(segments, key=lambda s: s[1] - s[0])
            return ((debut + fin) / 2.0, y)
    return None


def mercator_vers_wgs84(x, y):
    """Web Mercator (EPSG:3857) -> (latitude, longitude) en degrés."""
    lon = math.degrees(x / RAYON_TERRE)
    lat = math.degrees(2.0 * math.atan(math.exp(y / RAYON_TERRE)) - math.pi / 2.0)
    return lat, lon


# --- Programme principal -----------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Centroïdes lat/lon des ZAPM d'outre-mer")
    parser.add_argument("--shp", type=Path, default=SHP_DEFAUT, help="chemin du fichier .shp")
    parser.add_argument("--sortie", type=Path, default=SORTIE_DEFAUT, help="CSV de sortie")
    args = parser.parse_args()

    shp, shx, dbf = args.shp, args.shp.with_suffix(".shx"), args.shp.with_suffix(".dbf")
    for p in (shp, shx, dbf):
        if not p.exists():
            sys.exit(f"Fichier introuvable : {p}")

    # Vérification de la projection : le script suppose du Web Mercator
    prj = args.shp.with_suffix(".prj")
    if prj.exists() and "Mercator_Auxiliary_Sphere" not in prj.read_text(errors="ignore"):
        sys.exit("Projection inattendue (.prj) : ce script ne gère que Web Mercator (EPSG:3857).")

    # L'index SHX donne la position de chaque enregistrement du SHP (accès direct)
    with open(shx, "rb") as f:
        shx_data = f.read()

    def offset_enreg(i):
        return struct.unpack(">i", shx_data[100 + 8 * i:104 + 8 * i])[0] * 2

    lignes = []
    with open(shp, "rb") as f_shp:
        for i, attrs in lire_dbf(dbf):
            if attrs["INSEE_DEP"] not in TERRITOIRES:
                continue
            anneaux = lire_polygone(f_shp, offset_enreg(i))
            c = centroide_polygone(anneaux)
            p = point_sur_surface(anneaux)
            if c is None or p is None:
                print(f"  Attention : géométrie vide ou dégénérée pour {attrs['RefPM']}", file=sys.stderr)
                lat = lon = lat_c = lon_c = hors = ""
            else:
                lat, lon = (round(v, 6) for v in mercator_vers_wgs84(*p))
                lat_c, lon_c = (round(v, 6) for v in mercator_vers_wgs84(*c))
                hors = "non" if point_dans_polygone(c[0], c[1], anneaux) else "oui"
            lignes.append({**{k: attrs[k] for k in CHAMPS_SORTIE},
                           "latitude": lat, "longitude": lon,
                           "lat_centroide": lat_c, "lon_centroide": lon_c,
                           "centroide_hors_zone": hors})

    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    with open(args.sortie, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=CHAMPS_SORTIE + COLONNES_GEO, delimiter=";")
        w.writeheader()
        w.writerows(lignes)

    # Récapitulatif
    total = Counter(l["INSEE_DEP"] for l in lignes)
    deploye = Counter(l["INSEE_DEP"] for l in lignes if l["EtatPM"] == "deploye")
    print(f"{'Territoire':<18}{'PM (ZAPM)':>10}{'déployés':>10}")
    for code, nom in TERRITOIRES.items():
        print(f"{nom:<18}{total[code]:>10}{deploye[code]:>10}")
    print(f"{'TOTAL':<18}{sum(total.values()):>10}{sum(deploye.values()):>10}")
    hors_zone = sum(1 for l in lignes if l["centroide_hors_zone"] == "oui")
    print(f"\nCentroïdes tombant hors de leur zone : {hors_zone} sur {len(lignes)}")
    print(f"Fichier écrit : {args.sortie}")


if __name__ == "__main__":
    main()
