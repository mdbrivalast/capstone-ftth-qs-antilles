# Calibrage du multiplicateur cyclonique — intensité locale 2023-2025
**Note de calibrage — cas #3 (observatoire qualité FTTH OM), levier 4.**
Préparée le 07/10/2026, puis **validée et appliquée le 09/10/2026** : le calibrage figé est codé dans le générateur du dataset (voir §8).

---

## 1. À quoi sert cette note
Le multiplicateur cyclonique ne doit **pas** être uniforme sur 2023→2025 : s'il colle un gros pic à chaque saison, on simule des cyclones qui n'ont pas eu lieu → faux. Objectif : un **indice d'intensité par (territoire, année)** pour moduler le pic sur la base du réel.

## 2. Contexte climatique (ENSO = El Niño Southern Oscillation)
| Année | Phase ENSO | Activité du bassin atlantique | Lecture pour les Antilles |
|---|---|---|---|
| 2023 | El Niño + eaux (SST) record | Soutenue malgré El Niño : 20 systèmes nommés, 7 ouragans, 3 majeurs | El Niño bride normalement l'Atlantique ; compensé par des eaux record |
| 2024 | Bascule vers La Niña + SST record | Hyperactive — ouragan majeur **précoce** (Beryl, cat. 4-5 dès juillet) | Favorable aux systèmes, mais trajectoires surtout au **sud** |
| 2025 | La Niña faible / neutre | Au-dessus de la normale | Variable |

## 3. Systèmes ayant touché ou frôlé Guadeloupe (971+977+978) & Martinique (972)
| Année | Système (mois) | Cible principale | Intensité d'impact local |
|---|---|---|---|
| 2023 | Bret (juin) | Martinique | vigilance rouge, quasi aucun dégât |
| 2023 | Gert (juin) | Guadeloupe (au large) | boucle, fortes pluies |
| 2023 | Philippe (oct) | Nord de l'arc (Barbuda, St-Martin) | pluies |
| 2023 | **Tammy (20-22 oct, cat. 1)** | **Guadeloupe (terre à La Désirade), St-Martin/St-Barth** | **alerte violette Guadeloupe, rouge Îles du Nord** ; œil à quelques dizaines de km — *épisode vécu directement par l'analyste, au mouillage* |
| 2024 | **Beryl (début juillet, cat. 4-5)** | Sud Petites Antilles (Grenadines dévastées) ; **Martinique vigilance jaune** | Martinique frôlée ; Guadeloupe peu concernée |
| 2025 | **Erin (août, 1er ouragan de la saison)** | **Îles du Nord + Guadeloupe** | alerte, rafales ~120 km/h |

**Lecture d'ensemble** : chaque année a eu au moins un épisode mettant les îles en alerte, mais **aucun coup direct dévastateur** sur la période (rien de comparable à Maria, 2017). « Relativement épargnés », oui — mais pas « rien ».

## 4. Indice d'intensité locale proposé (le 07/10)
Échelle d'ampleur du pic (facteur appliqué en saison juin→nov, par territoire × année) :

| Niveau | Ampleur | Déclencheur type |
|---|---|---|
| Nul | 1,0 | aucun système |
| Faible | ~1,3 | frôlement, vigilance jaune, fortes pluies |
| Modéré | ~1,8 | alerte rouge/violette, cat. 1 à proximité |
| Fort | ~2,5 | coup direct cat. 2-3 |
| Majeur | 4+ | cat. 4-5 direct (type Maria) — *scénario de démonstration* |

> Cette première proposition a été affinée le 09/10 après la vérif météo de Tiza (voir §8 pour les valeurs réellement appliquées, plus basses).

## 5. Implication pour le modèle + angle narratif
- Sur 2023-2025, les pics restent **modérés** → les données révéleront surtout la **vulnérabilité structurelle** (≈75 % de réseau aérien + stock de malfaçons héritées), pas un choc cyclonique.
- **Message pour le financeur RIP (Région Guadeloupe / CTM)** : *trois saisons quasi épargnées = une fausse sécurité. Un réseau à 75 % aérien et fragilisé par les malfaçons de déploiement reste une bombe à retardement. Investir dans la résilience AVANT le prochain système majeur.*
- **Proposition de conception** : caler le multiplicateur 2023-2025 sur l'intensité **réelle** (modérée) **＋** prévoir un **scénario « cyclone majeur » activable** (type Maria) comme démonstration de la capacité de l'observatoire à alerter — sans fausser l'historique.

## 6. Vérifications (soldées le 09/10)
- [x] Vérif météo 2023-2024 : faite par Tiza (sources en §9).
- [x] Détail saison 2025 : Erin confirmé, revu à la baisse (rafales sans destruction aérienne).
- [x] Validation des facteurs d'ampleur par territoire × année : faite, mode « mois réels » retenu (§8).
- [x] Scénario « cyclone majeur » en variante : oui, conservé comme démonstration activable.

## 7. Sources
- Données qualité FTTH & confirmation du trou OM : [data.gouv.fr — Qualité des réseaux en fibre optique](https://www.data.gouv.fr/fr/datasets/qualite-des-reseaux-en-fibre-optique/)
- Bilan 2023 : [RCI — « Les Antilles françaises relativement épargnées »](https://rci.fm/deuxiles/infos/Risques-naturels/Saison-cyclonique-les-Antilles-francaises-relativement-epargnees)
- Beryl 2024 : [RCI — Beryl cat. 4](https://rci.fm/deuxiles/infos/Risques-naturels/Beryl-sest-renforce-en-ouragan-de-categorie-4) · [L'Info Durable — la Martinique se prépare](https://www.linfodurable.fr/la-martinique-se-prepare-au-passage-de-louragan-beryl-lundi-46013)
- Erin 2025 : [24matins — alerte Guadeloupe / Îles du Nord](https://www.24matins.fr/ouragan-erin-alerte-pour-la-guadeloupe-saint-martin-et-saint-barthelemy-face-a-des-rafales-de-120-km-h-1394167)
- Contexte ENSO / activité : [EOS — Busy hurricane season expected in 2025](https://eos.org/articles/busy-hurricane-season-expected-in-2025)

---

## 8. Calibrage retenu et appliqué (09/10/2026)

Après la vérif météo de Tiza et deux sessions de travail, voici ce qui a été figé, puis codé dans le générateur du dataset.

**Mode « mois réels », pas de lissage sur la saison.** Le facteur s'applique au mois exact de l'événement. Un seul système a détruit de l'aérien sur la période : Tammy (Guadeloupe, octobre 2023). Les autres ont coupé le courant sans casser poteaux ni câbles, donc leur facteur reste bas.

**Distinction qui gouverne tout le levier (dire d'expert de Tiza) : l'impact aérien n'est pas la coupure de courant.** Un cyclone qui arrache poteaux et câbles crée des pannes réseau qui durent. Une coupure EDF seule n'en crée pas : dès le courant revenu, la ligne refonctionne.

Table appliquée (tout mois absent vaut 1,0) :

| Territoire | Mois | Facteur | Événement |
|---|---|---|---|
| GLP | 2023-10 | **1,70** | Tammy — seul vrai pic ; abaissé de 1,8 à 1,7 car l'impact est localisé (Désirade, Îles du Nord), pas un cat. majeur sur tout le territoire |
| GLP | 2023-06 | 1,15 | Gert au large |
| GLP | 2024-07 | 1,10 | Beryl passe au sud |
| GLP | 2025-08 | 1,20 | Erin, rafales sans destruction |
| MTQ | 2023-06 | 1,20 | Bret |
| MTQ | 2024-07 | 1,25 | Beryl frôle la Martinique |
| MTQ | 2025-08 | 1,10 | saison faible |

**Le surcroît frappe par PM, pas par territoire.** Les pannes cycloniques en plus se répartissent sur les PM proportionnellement à leur part d'aérien (`dim_pm.part_aerien`). Un PM enterré encaisse peu, un PM tout-aérien beaucoup. Contrôle sur le dataset : le ratio de pannes octobre/septembre 2023 monte de 1,7 (PM peu aériens) à 2,2 (PM très aériens).

**Effet émergent sur la malfaçon.** Le surcroît cyclonique tire uniquement des causes environnementales (ENV), dont la probabilité de malfaçon est nulle. Du coup, pendant Tammy, la part des pannes imputables à une malfaçon tombe de 29 % à 17 %. Le cyclone gonfle le volume sans être une vague de malfaçons.

**MTTR rallongé les mois cycloniques** (facteur 1,5) : équipes saturées, accès coupés.

### Deux observations de terrain versées au dossier

**Surtension au rétablissement.** Quand le courant revient après un blackout, les surtensions grillent du matériel. Tiza a vu des poteaux grésiller et cracher des étincelles au loin depuis le lagon. Le danger ne tient pas qu'à la coupure, le redémarrage pèse autant. Ça recoupe le mécanisme déjà retenu des box foudroyées au PTO via le couplage fibre / secteur EDF.

**NRO et NRA sur secours solaire.** Certains nœuds sont alimentés en photovoltaïque (Tiza l'a constaté en stage 2025). Même quand EDF tombe à l'échelle de l'île — lors d'un blackout de grève, toute la Guadeloupe est restée coupée 24 à 48 h, numéros d'urgence compris — ces nœuds tiennent. Ça renforce la règle « coupure de courant ≠ panne réseau » et explique pourquoi l'amont résiste au cyclone (NRO en D1, collecte en D0) alors que l'aérien en aval souffre (PM, PBO, PTO). Le modèle le reflète déjà : aucune cause ENV n'existe au NRO, et le NRO est hors du flag `sensible_aerien`.


---

### Piste v2 — délai de reprise par segment (ajoutée le 10/10/2026)

**Constat v1 (contrôle du 10/10).** Dans la base v1, une `reprise_malfacon=1` ne porte **aucun surcoût de délai** : délai MES moyen 44,2 j (reprise) vs 44,8 j (pose propre), médiane 30 j des deux côtés, MES<60 j ~78 % identique. La v1 capture donc le **taux** de reprise (11,1 % des réussis = l'indicateur ARCEP) mais pas le **temps** qu'une reprise ajoute. `fait_raccordement` n'a par ailleurs pas de colonne segment.

**Piste v2 (dire d'expert Tiza).** Faire porter à `reprise=1` un **délai additionnel dépendant du segment**, ancré sur l'observation terrain : une reprise en portée PM (**D2**) prend **2-3 semaines** (planifier → préparer → intervenir). Effet attendu : le MES<60 j des reprises passerait sous celui des poses propres, et la queue log-normale des délais se peuplerait des reprises (réaliste).

**Distinction à garder (deux horloges).** Reprise de raccordement = intervention **planifiée, non urgente** → **semaines**. MTTR d'une panne = rétablissement d'un abonné actif **sous SLA, urgent** → **jours**. Ne pas confondre les deux temps.
