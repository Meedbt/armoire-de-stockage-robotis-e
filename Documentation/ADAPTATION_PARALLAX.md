# Adaptation V0.3 — Parallax 900-00008

Cette livraison est une **adaptation mécanique nominale**, pas une validation d’interchangeabilité sur votre servo. Les cotes précises de vos oreilles et du palonnier n’ont pas été mesurées. Les enveloppes noires du STEP sont simplifiées ; elles ne sont pas des modèles certifiés du fabricant.

## Pièces à remplacer / ajouter

| V0.2 à retirer | V0.3 à utiliser | Quantité |
|---|---|---:|
| 14_support_moteur_Z | 14_support_servo_Z | 1 |
| 15_entretoise_36 | 15_entretoise_44 | 4 |
| 19_support_moteur_X | 19_support_servo_X | 1 |
| 26_support_moteur_Y | 26_support_servo_Y | 1 |
| 27_entretoise_38 | 27_entretoise_40 | 4 |
| Accouplements achetés 5 → 8 | 45_adaptateur_palonnier_M8 + palonnier réel | 3 |
| Nouveau coupon | 46_coupon_fixation_servo | 1 |

Les autres géométries STL restent identiques à V0.2. Le support capteur 39 passe de 4 à 9 exemplaires en réserve ; son implantation reste à concevoir. La vis Z nominale passe de 315 à **323 mm**, la vis Y de 244 à **246 mm**. La vis X reste de 365 mm. Attendre le montage à blanc avant de couper les tiges.

## Premier lot : coupon 46 et un adaptateur 45

1. Imprimer le coupon 46 à plat et vérifier l’insertion du servo sans forcer.
2. Les hypothèses sont : corps **40,5 × 20 mm**, axe à **10 mm** d’une extrémité du corps ; fenêtre **41,7 × 21,2 mm**. Ce sont des cotes de conception à contrôler, pas une garantie sur chaque version du servo.
3. Les quatre lumières Ø3,6 ont une course de centre de 3 mm. Leurs centres sont U=-14,5 et +35,5 mm par rapport à l’axe, V=±5 mm. Vérifier le passage des boulons et une portée suffisante des rondelles.
4. Vérifier aussi le passage du câble, l’accès au réglage du neutre si présent, et la position de l’axe par rapport aux vis M8. Un déplacement dans les lumières doit conserver la coaxialité : ne pas simplement déplacer le servo pour faire correspondre les trous.
5. Mesurer la distance entre le **plan d’appui des oreilles** et la **face du palonnier en contact avec l’adaptateur** : **16 mm** sont supposés. Si la mesure diffère, corriger les supports/entretoises et l’engagement de la vis dans Fusion ou dans la source ; ne pas mettre le servo en contrainte axiale.
6. Vérifier le palonnier : interface cannelée compatible avec le servo réel, diamètre utile nominal 36 mm, épaisseur nominale 2 mm. Le modèle d’adaptateur prévoit quatre lumières radiales Ø2,4 pour des trous situés à **13–16 mm de l’axe**, à 90°. Au moins deux fixations opposées sont nécessaires ; quatre sont préférables. Si le palonnier fourni ne correspond pas, adapter la bride au palonnier mesuré ou utiliser un palonnier compatible. Ne pas percer près d’un bord fragile.

## Montage de l’adaptateur 45

- Imprimer avec la grande bride sur le plateau. Examiner les supports sous les changements de diamètre intérieurs. Contrôler l’alésage et le logement hexagonal avant montage.
- Insérer un écrou M8 dans le logement hexagonal ouvert côté vis. Logement : 13,4 sur plats, profondeur 7 mm.
- Fixer la bride imprimée au palonnier par des M2 et écrous, hors servo. Épaisseur de bride 4 mm ; la longueur M2x8 suppose un palonnier de 2 mm. Vérifier les dépassements.
- Fixer le palonnier sur la sortie du servo avec **sa vis centrale d’origine**, accessible par le passage central Ø10 depuis l’adaptateur encore libre de la tige.
- Enfiler un contre-écrou M8 sur la tige, puis visser la tige dans l’écrou captif. Engagement nominal de l’extrémité de tige dans l’adaptateur : **12 mm**. Le passage central reste libre derrière pour la vis de palonnier.
- Bloquer le contre-écrou contre la face de l’adaptateur en maintenant l’écrou/ensemble sans forcer sur les engrenages du servo. Ne pas écraser le plastique. Vérifier l’absence de glissement dans les deux sens lors d’un premier essai lent.
- Les roulements et leurs arrêts axiaux doivent reprendre les efforts de la vis. Ne pas faire porter le portique par les roulements internes du servo.

La liaison imprimée est rigide, pas un accouplement flexible. Elle exige un bon alignement ; vérifier le faux-rond et l’absence de point dur en rotation. La résistance et le maintien du serrage restent à tester.

## Positions nominales dans le STEP

| Interface | Z | X | Y |
|---|---:|---:|---:|
| Plan d’appui des oreilles | Z=484 | X=-70 | Y=452 |
| Face bride / palonnier | Z=468 | X=-54 | Y=436 |
| Extrémité de la tige M8 | Z=458 | X=-44 | Y=426 |
| Face de l’adaptateur côté contre-écrou | Z=446 | X=-32 | Y=414 |

## Commande et capteurs : à développer

Le 900-00008 tourne en continu et ne retourne pas la position du chariot. Les neuf supports capteurs sont fournis comme réserve, sans implantation ni cible. Pour automatiser, il faut sélectionner et placer les capteurs (ou encodeurs), définir les distances d’arrêt et les limites, puis écrire la commande. Un simple temps de rotation n’assure pas l’alignement sur une case.

Avec les vis M8 conservées, 50 tr/min donnent théoriquement **62,5 mm/min**, soit environ 86 s entre colonnes et 110 s pour sortir le poussoir. Ces valeurs supposent 50 tr/min réellement atteints ; la charge peut réduire la vitesse. Le couple nécessaire, surtout pour Z, n’a pas été validé. Commencer par un seul axe et soutenir mécaniquement le portique pendant les réglages.

## Sources et distinction avec les hypothèses CAO

- [Fabricant : Parallax 900-00008](https://www.parallax.com/products/parallax-continuous-rotation-servo) : rotation continue, 4–6 V, vitesse annoncée jusqu’à 50 tr/min, masse 42,5 g ; dimensions globales et spécifications susceptibles de varier.
- [Documentation fabricant v2.2, copie Mouser](https://www.mouser.com/datasheet/2/321/900-00008-Continuous-Rotation-Servo-Documentation--273045.pdf) : commande vitesse/sens et calibration ; document historique, à confronter à votre version.

Les entraxes, l’offset d’axe, la position axiale des oreilles et le palonnier de référence sont des hypothèses ajustables de cette CAO. Les mesurer sur votre exemplaire avant de lancer les supports définitifs.
