# Note méthodologique — la simulation en clair

*Encadré pour les phases Process et Analyze du cas d'étude. Écrit pour un lecteur décideur (financeur RIP), pas pour un statisticien.*

Cet observatoire repose sur un jeu de données **synthétique**, c'est-à-dire fabriqué. La raison est simple : les chiffres de qualité FTTH pour l'outre-mer n'existent pas en open data, l'ARCEP l'a confirmé par écrit. Fabriquer ne signifie pas inventer au hasard. La méthode tient en une règle : le réel fixe les volumes, l'expérience de terrain fixe la répartition.

## Le réel fixe l'enveloppe

Les totaux viennent de sources publiques : parc d'abonnés et locaux raccordables par territoire (observatoire ARCEP), taux de panne et d'échec de raccordement au niveau national, nombre de points de mutualisation (comptage sur la carte ARCEP). Ces chiffres bornent la simulation, on ne les touche pas.

## L'expérience répartit le détail

À l'intérieur de ces totaux, le détail (quelle cause, quel segment du réseau, combien de jours de réparation) suit des règles tirées de l'expérience d'un technicien fibre aux Antilles, avec un ajustement outre-mer assumé : humidité, salinité, réseau à 75 % aérien. Chaque hypothèse est écrite et réglable, et étiquetée comme estimation d'expert tant qu'aucune donnée réelle ne vient la remplacer.

## Le tirage aléatoire (méthode Monte-Carlo)

Chaque panne et chaque raccordement est tiré au sort selon ces probabilités, comme un dé pipé qui respecte les fréquences observées sur le terrain. Répété pour 150 000 pannes, le procédé reconstruit des distributions crédibles au lieu d'une moyenne plate. Le tirage part d'une graine fixe : relancer le script redonne exactement le même jeu de données, donc n'importe qui peut le rejouer et vérifier.

## La loi log-normale pour les délais

Un délai de réparation n'est jamais symétrique. La plupart des interventions se bouclent vite, quelques-unes traînent des jours. La loi log-normale reproduit cette forme, un pic bas suivi d'une traîne vers la droite. Une courbe en cloche classique donnerait des délais négatifs, ce qui n'aurait aucun sens pour un temps d'intervention.

## La médiane plutôt que la moyenne

Sur ces délais, les quelques réparations très longues tirent la moyenne vers le haut et faussent l'image du cas courant. La médiane, la valeur qui partage la population en deux, colle mieux à ce que vit l'abonné ordinaire. L'observatoire communique donc en médiane et garde la moyenne comme signal des cas extrêmes.

## Ce que la méthode garantit

Un lecteur peut rejouer le jeu de données, lire chaque hypothèse une par une, et substituer une donnée réelle à une estimation dès qu'elle est publiée. Les chiffres sont présentés comme synthétiques, jamais comme des mesures relevées sur le réseau.
