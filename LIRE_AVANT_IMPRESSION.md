# Armoire automatisée — prototype mécanique V0.2

**Ce dossier est un avant-projet imprimable pour essais. Ce n'est pas une machine physiquement validée.**

Il contient 67 références STL, leur quantité, l'assemblage STEP pour Fusion, les sources géométriques et deux vues de montage. Toutes les dimensions sont en millimètres.

## Les hypothèses retenues

- Imprimante : Bambu Lab A1 mini, volume nominal 180 × 180 × 180 mm.
- Une boîte factice par case ; boîte de 60 mm de large, 35 mm de haut et 80 mm de profondeur.
- Neuf cases : 3 colonnes × 3 lignes. Chaque case avec son couvercle mesure 90 × 100 × 65 mm (X × Y × Z).
- Structure, chariots, guides de boîtes, paliers, goulotte et bacs imprimés.
- **Tiges lisses Ø8, tiges filetées M8, roulements, écrous, accouplements et moteurs métalliques achetés.** La transmission de cette version est vis–écrou sur les trois axes. Elle remplace la proposition initiale de crémaillère pour le poussoir.
- Interfaces moteurs : NEMA17, entraxe 31 × 31, centrage jusqu'à 23, arbre Ø5, corps de référence 42,3 × 42,3 × 38. Ce choix d'enveloppe ne valide pas le couple nécessaire.
- Le socle assemblé mesure 400 × 700 mm. Avec le moteur X qui déborde à gauche, l'enveloppe représentée atteint environ 443 × 700 × 519 mm. La machine est donc plus profonde que l'esquisse initiale : le support arrière porte le poussoir à course longue.

## Commencer ici

1. Lire `Documentation/guide_montage.md`.
2. Ouvrir `CAO/assemblage_Fusion.step` dans Fusion pour comprendre l'assemblage. Les composants gris préfixés `ACHAT` ne sont pas à imprimer. Les vis de fixation, écrous, rondelles et capteurs ne sont pas tous représentés.
3. Imprimer **seulement** `41_test_alesages.stl`, `42_test_roulements.stl`, une `01_case.stl` et un `02_couvercle.stl`.
4. Vérifier les dimensions des vraies boîtes et composants. Tester les jeux avec vos tiges et roulements. Adapter les alésages si nécessaire avant d'imprimer les chariots.
5. Suivre les étapes de montage ; utiliser `Documentation/nomenclature_impression.csv` pour les quantités.

## Organisation du dossier

- `STL/` : un fichier par référence ; dupliquer selon la nomenclature. Les pièces sont remises à l'origine, dans une orientation de départ pour le tranchage.
- `CAO/assemblage_Fusion.step` : modèle de montage avec solides séparés et composants achetés simplifiés.
- `CAO/generer.py` : source CadQuery 2.7, à exécuter dans un environnement Python avec CadQuery. Ce n'est pas un script Fusion.
- `Documentation/nomenclature_impression.csv` : quantités, encombrements et consignes par pièce. Ouvrable comme texte ; séparateur point-virgule.
- `Documentation/guide_montage.md` : montage, positions, réglages et limites.
- `Documentation/composants_a_acheter.csv` : pièces non imprimées et dimensions de référence.
- `Documentation/vue_avant.png`, `vue_arriere.png` : vues géométriques, panneaux de goulotte masqués pour la lisibilité.
- `Documentation/verification_*.json` et `resume_validation.json` : contrôles géométriques effectués.

Le STEP conserve les solides et leurs positions, pas les esquisses ni l'historique paramétrique natif de Fusion. Le code source permet de régénérer la géométrie ; une modification du source impose de régénérer et revérifier les fichiers.

## Ce qui a été contrôlé

- Validité des solides CAO et réimport du STEP.
- Fermeture des maillages STL (chaque arête appartient à deux triangles).
- Encombrement de chaque STL dans 180 × 180 × 180 mm, hors supports et bordure d'adhérence.
- Absence d'intersection volumique des pièces imprimées dans les positions consignées dans le rapport.
- Absence d'intersection entre les pièces imprimées et les enveloppes nominales des composants achetés dans la position représentée.

Ce ne sont pas des essais de rigidité, d'endurance, de couple, de qualité de glissement ou de chute des boîtes. Aucun G-code n'est fourni ; le tranchage doit être vérifié avec votre buse, filament et profil réels. La visserie détaillée n'a pas fait l'objet d'une simulation de collision.
