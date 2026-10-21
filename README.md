# Armoire robotisée — prototype étudiant

Une maquette d’armoire de stockage automatisée : sélectionner une case, positionner un robot derrière celle-ci et pousser une boîte vers la zone de récupération.

**Version mécanique V0.2 — prototype non construit, essais physiques à réaliser.** Les fichiers sont une base de développement pour un projet étudiant, pas un dispositif de distribution de médicaments validé. Utiliser des boîtes factices pour les essais.

![Vue avant de la conception](Documentation/vue_avant.png)

## Principe

- Une armoire de **9 cases (3 × 3)** reçoit les boîtes.
- Deux axes positionnent le chariot : **X horizontal et Z vertical**.
- Un troisième axe **Y** actionne le poussoir.
- Une goulotte et des bacs récupèrent les boîtes à l’avant.

La structure est imprimable par éléments sur une **Bambu Lab A1 mini**. Le mécanisme est hybride : pièces imprimées, guidages métalliques, vis M8 et moteurs achetés séparément.

## Caractéristiques de cette version

| Élément | Définition |
|---|---|
| Cases assemblées | Pas de 90 × 100 × 65 mm ; bloc de 270 × 100 × 195 mm |
| Boîtes factices prévues | 60 mm de largeur × 80 mm de profondeur × 35 mm de hauteur |
| Socle | 400 × 700 mm, assemblé à partir de 20 tuiles |
| Encombrement approximatif | 443 × 700 × 519 mm, moteurs compris |
| Poussoir | Course nominale de 115 mm |
| Guidages / transmission | Tiges Ø8 mm / vis M8 au pas de 1,25 mm |
| Motorisation de référence | 3 moteurs NEMA 17 ; dimensions détaillées dans la nomenclature |
| Impression | 67 références STL ; 213 exemplaires selon la nomenclature, accessoires et coupons compris |
| CAO | Source CadQuery et assemblage STEP ouvrable dans Fusion |

## Fichiers

| Dossier | Contenu |
|---|---|
| `STL/` | Une référence par fichier, à multiplier selon la nomenclature |
| `CAO/` | Générateur Python CadQuery et assemblage STEP |
| `Documentation/` | Montage, achats, quantités, vues et rapports géométriques |
| `tools/` | Contrôle reproductible des fichiers livrés |
| `.github/` | Vérification automatique et modèle de signalement |

## Vérifications et limites

Les rapports de la V0.2 indiquent 67 maillages fermés, 222 solides STEP réimportés valides et 10 positions contrôlées sans intersection entre pièces imprimées. Ce sont des **contrôles géométriques ponctuels** : ils ne constituent pas une validation continue du mouvement, des efforts, du couple moteur, de la rigidité, de la chute des boîtes ou de la visserie réelle.

Le contrôle automatique du dépôt vérifie les STL binaires, leurs arêtes, les dimensions et la cohérence de la nomenclature. Il ne refait pas les contrôles de mouvement. Les rapports archivés concernent la conception V0.2 livrée ; ils doivent être renouvelés après toute modification géométrique.

**Aucun firmware, schéma de câblage validé ni interface de commande fonctionnelle n’est inclus.** Ces étapes figurent dans la [feuille de route](ROADMAP.md).


## Licence

Aucune licence de réutilisation n’est définie dans cette version. L’équipe doit choisir une licence et préciser les auteurs avant de présenter le projet comme open source. Aucun fichier `LICENSE` n’a été ajouté automatiquement.
