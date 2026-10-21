# Contribuer

Le projet est au stade de conception. Distinguer clairement une observation CAO d’un résultat obtenu sur un montage réel.

## Proposer une modification

1. Décrire le problème avec le nom de la pièce et la version concernée.
2. Indiquer les dimensions mesurées et les composants utilisés.
3. Modifier la source `CAO/generer.py`, puis régénérer les fichiers concernés dans une copie de travail.
4. Mettre à jour nomenclatures, guide et changelog.
5. Exécuter `python tools/check_release.py`.
6. Examiner l’assemblage et les courses ; renouveler les rapports géométriques affectés. Les anciens rapports ne valident pas une nouvelle géométrie.
7. Présenter la modification dans une pull request, en séparant contrôles logiciels et essais physiques.

Pour un retour d’impression, préciser matériau, imprimante, buse, hauteur de couche, orientation, supports, paramètres influant sur les jeux et photographies utiles. Ne pas inclure de données personnelles ou de secrets dans les fichiers.
