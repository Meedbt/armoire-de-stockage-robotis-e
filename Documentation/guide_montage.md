# Guide de montage — V0.3 Parallax

**Lire d’abord ADAPTATION_PARALLAX.md. Montage nominal à confirmer avec le servo et son palonnier réels.**

## 1. Repère et principe

X : largeur, vers la droite. Y : profondeur, vers l'arrière. Z : hauteur.
La face avant du stockage est à Y=0 ; l'arrière à Y=100. Le bloc de stockage va de X=0 à 270 et de Z=180 à 375.

Le portique Z porte deux tiges horizontales X et leur vis. Le chariot X porte le poussoir Y. Les tiges lisses guident ; les vis M8 entraînent via les écrous captifs. L'écrou doit être immobilisé en rotation par son logement hexagonal.

Les glissières sont les alésages imprimés des chariots : cette version n'utilise pas de roulements linéaires LM8UU. Le frottement doit être vérifié à la main. Ne pas forcer un moteur pour rattraper un guidage coincé.

Les trois colonnes de réception et les panneaux de goulotte se démontent. Le réapprovisionnement des cases se fait manuellement, par l'avant après dépose des panneaux nécessaires.

## 2. Impression par lots

Les orientations STL sont des points de départ. Vérifier le premier niveau de matière dans le trancheur et les supports avant chaque référence.

| Lot | Pièces | Essai avant de continuer |
|---|---|---|
| A | 46, un 45, puis 41, 42, une 01 et une 02 | Passage des tiges/roulements, taille de la boîte, couvercle |
| B | 20, 21, 25, 28, 29, 30, puis 22 à 27 | Glissement Y, assemblage de la tige, course de 115 mm |
| C | 16, 17, 18, 19 | Guidage X, engagement des vis, passage de la course |
| D | Socle 43/44, pieds 04 à 10, consoles 11/12, moteur Z 14/15 | Équerrage et glissement vertical à la main |
| E | Reste des 01/02/03 ; 31 à 38 | Éjection d'une boîte et descente depuis chaque étage |
| F | 39/40 | Position des capteurs et cheminement des câbles |

Réglages initiaux à ajuster : couches de 0,20 mm, 4 périmètres, 5 couches supérieures/inférieures. Le PLA convient pour les premières éprouvettes et pièces fixes de démonstration ; déterminer le matériau final après essais. Démarrer à 20–25 % de remplissage pour cases/panneaux, 35–40 % pour chariots/consoles. Les parois minces sont déjà définies par la géométrie. Ne pas extrapoler la résistance uniquement à partir du taux de remplissage.

- Corps de case : fond sur le plateau. Le haut de l'ouverture arrière demande un pont d'environ 30 mm ; inspecter son rendu. Des supports localisés peuvent être nécessaires.
- Couvercle : face supérieure sur le plateau ; petites languettes vers le haut.
- Plaques/éclisses : face large sur le plateau.
- Colonnes : debout, sans supports internes. Vérifier l'adhérence.
- Chariots : les orientations proposées rendent certains alésages verticaux ; des supports restent nécessaires pour les passages transversaux. Garder les surfaces de glissement propres.
- Tiges du poussoir : les deux pièces sont orientées sur le côté. Vérifier la languette à mi-bois et la bride ; retirer soigneusement les supports.
- Bacs : orientation sur le côté proposée ; vérifier les supports des parois et des pieds. Ne pas lancer les trois sans avoir validé un exemplaire.

Le modèle laisse 0,25 mm de jeu radial dans les guidages de déplacement Ø8,5. Ce n'est pas une précision garantie. Les éprouvettes précisent le jeu réel obtenu par votre impression.

## 3. Assemblage du socle

Les 20 tuiles `44_socle_Cx_Ry` forment 4 colonnes × 5 rangées. C1 est à gauche (X=-65) et R1 à l'avant (Y=-210). La colonne augmente avec X ; la rangée augmente avec Y.

Insérer les écrous M4 dans les logements hexagonaux sous les tuiles **avant** de fermer le montage. Les 31 liaisons `43` se placent sous le socle, dans le STEP de Z=-5 à Z=0. Utiliser des M4x10 à tête fraisée par dessous ; ne pas laisser des pointes dépasser et heurter les pieds fixés sur la face supérieure. Le socle repose sur ses liaisons inférieures.

Les tuiles sont ajourées et leurs trous de montage varient : ne pas imprimer vingt fois le même fichier. Les rangées de trous et renforts sont spécifiques à chaque position.

## 4. Stockage, pieds et liaisons

Assembler quatre pieds : deux gauches `04+05`, deux droits `06+07`. Les pieds avant sont centrés à Y=20 et les pieds arrière à Y=80. Les pieds hauts reposent sur les pieds bas à Z=96 ; deux éclisses `08` maintiennent chaque jonction. Les avant-trous sont destinés à des M3, vissées modérément dans le plastique. Ne pas utiliser une vis trop longue qui traverse une surface de guidage.

Fixer les embases au socle par les perçages M4. Le dessus des pieds arrive à Z=180. Les oreilles hautes se vissent aux côtés des cases de la rangée basse à Z=195.

Assembler les cases côte à côte avec les trous latéraux : M3x12 et écrous accessibles depuis l'intérieur. Chaque interface entre deux cases utilise quatre vis (Y=20/80, Z local=15/50). Les couvercles s'emboîtent par leurs languettes ; ils ne sont pas collés.

Empiler les trois rangées. Les huit éclisses `03` relient les côtés extérieurs des rangées : quatre à la jonction Z=245 et quatre à Z=310. Elles utilisent les trous à 15 et 50 mm des cases. Les modules intermédiaires sont retenus par leurs voisins latéraux.

## 5. Colonnes et guidage Z

Chaque colonne est composée de trois `09_colonne_140`, empilées de Z=6 à 426. Colonnes aux centres X=-45 et X=315, Y=190. Les jonctions sont à Z=146 et 286, avec une éclisse `08` de chaque côté.

Les quatre équerres `10` fixent les colonnes au socle. Les vis transversales du tube sont des M3 avec écrous accessibles dans son ouverture. Monter ces écrous avant l'empilage.

Fixer les consoles inférieures `11` et supérieures `12` aux faces avant des colonnes. Les consoles inférieures portent les guides à Z=142–150, les supérieures à Z=426–434. Le trou M4 de fixation du tube peut nécessiter une reprise au diamètre 4,5, les avant-trous du tube restant volontairement petits.

Les deux tiges lisses Z sont Ø8 × 300, aux centres (X,Y)=(-25,145) et (295,145). Leur bas est à Z=142. Enfiler les chariots Z avant les consoles du haut. Vérifier le parallélisme, puis bloquer les tiges avec les vis de pression M3 des consoles. Si les deux tiges ne coulissent pas librement avec l'ensemble X installé, corriger l'alignement avant de motoriser.

La vis Z est une tige filetée M8, longueur nominale 323, entre Z=135 et 458, centre X=-10,Y=205. Elle passe dans deux 608 des consoles gauches. L'écrou moteur est captif dans le haut du chariot Z gauche ; fermer par `18`. Le logement symétrique du chariot droit reste vide.

Les retenues `13` maintiennent les bagues extérieures. **Prévoir des entretoises axiales métalliques sur les bagues intérieures**, par exemple diamètre intérieur 8,2, extérieur 10 à 11, longueur environ 5. Un écrou ou une rondelle ne doit pas frotter sur une retenue imprimée ni sur le joint du roulement. Régler l'immobilisation axiale de la vis par écrous/contre-écrous sans précharger excessivement les roulements. Le moteur ne doit pas porter à lui seul le poids du portique.

Le support `14_support_servo_Z` et quatre entretoises `15_entretoise_44` placent le plan d’appui des oreilles du servo à Z=484. La pièce 45 va de Z=446 à 468 et le palonnier nominal de Z=468 à 470. La vis M8 pénètre de 12 mm dans l’adaptateur. Voir la séquence d’assemblage et les cotes à contrôler dans ADAPTATION_PARALLAX.md. Quatre M4x65 sont prévus pour le support, sous réserve des rondelles et de l’écrou choisis.

Soutenir le portique pendant ces opérations. Une retenue temporaire mécanique est nécessaire lorsque les vis/accouplements sont démontés ; ne pas compter sur le moteur coupé pour retenir l'ensemble.

## 6. Axe X

Monter deux tiges lisses Ø8 × 345 entre les chariots Z, de X=-40 à 305, Y=165. Elles se trouvent à ±30 mm de la hauteur du poussoir. Enfiler le chariot `20` avant de bloquer les guides. Les petits trous transversaux des chariots Z permettent le blocage par vis M3.

La vis X est à Y=230, 55 mm au-dessus du poussoir. Longueur nominale M8=365, de X=-44 à 321. Les deux 608 se logent côté intérieur des chariots Z. Les retenues `13` sont orientées suivant X. Positionner l'écrou M8 dans le côté gauche de `20` et fermer par `18`.

Le servo se fixe au nouveau support `19_support_servo_X`, lui-même fixé au chariot Z gauche avec deux M4x40. Le plan d’appui des oreilles est à X=-70, le corps du servo s’étend vers X négatif. L’adaptateur 45 s’étend de X=-54 à -32, avec un contre-écrou entre X=-32 et -25,5. Le dégagement Ø26 du chariot est conservé. Fixer les oreilles avec des boulons M3, rondelles et écrous ; ne pas appliquer les anciennes consignes de taraudage NEMA17.

## 7. Axe Y et tige de poussée

Fixer `21` sur la face arrière de `20` avec quatre M3x16. Le roulement 608 avant se place dans `20`, et la platine `21` le retient. Le passage central de la platine est destiné à la tige de poussée.

Les deux tiges lisses Y sont Ø8 × 226, de Y=185 à 411 ; leurs centres sont à X local=±15, Z local=-22 par rapport au poussoir. Elles s'engagent dans les logements du chariot X, passent dans le chariot Y `28`, puis dans `25`. Deux vis de pression M3 dans les avant-trous sous la platine arrière assurent leur retenue axiale ; les serrer juste au contact des tiges.

Assembler les deux longerons latéraux, chacun constitué d'un `22` et d'un `23`. L'éclisse `24` les relie avec des boulons M3 et écrous. Ils se vissent aux platines avant/arrière par leurs avant-trous longitudinaux. Les longerons prennent place à l'extérieur de la course du chariot Y.

La vis Y est une M8 de longueur nominale 246, de Y=180 à 426, située 25 mm au-dessus du poussoir. Monter le 608 arrière, sa retenue `13`, l'écrou M8 de `28` et sa retenue `18`. Régler les jeux axiaux comme pour Z.

Le servo Y est porté par `26_support_servo_Y` et quatre `27_entretoise_40`, avec quatre M4x60 dont la longueur engagée est à contrôler. Le plan d’appui des oreilles est à Y=452. L’adaptateur 45 s’étend de Y=414 à 436 ; le palonnier nominal de Y=436 à 438. Le corps est derrière le poussoir et se déplace avec X et Z.

Assembler `29` et `30` par leur joint à mi-bois de 30 mm. Utiliser deux M3x10 à tête basse compatible avec les lamages Ø6,2 et deux écrous M3. Les têtes et écrous doivent rester dans le contour extérieur : cette jonction traverse l'ouverture de la case. La palette ne doit pas accrocher le carton.

Visser la bride de `30` au chariot Y avec quatre M3x16. Au repos, la face de poussée est à Y=110 ; en fin de course elle est à Y=-5. Le déplacement est de 115 mm. Le chariot Y passe de Y=340–360 à Y=225–245. Vérifier ce mouvement à la main, avec la vis déconnectée si nécessaire.

**Toujours rentrer le poussoir avant un déplacement X ou Z.** Le programme et les capteurs devront imposer cette séquence.

## 8. Goulotte et bacs

Fixer les trois rampes `31` côte à côte au socle. Le plan descend de Z=140 à l'arrière (Y=0) à Z=30 à l'avant (Y=-110), à 45°. Les nervures sont intégrées ; il n'y a pas de cale séparée à fabriquer.

Monter trois panneaux latéraux `33` de chaque côté et six panneaux avant `32`. Les jonctions utilisent les `34`, les angles utilisent les `35`. Les grandes faces des panneaux avant se trouvent à Y=-113 à -110. L'ouverture inférieure reste libre entre la sortie du plan incliné et le bas des panneaux avant.

Les quatre attaches `36` et quatre cales `37` relient les panneaux latéraux aux cases. Positions : Z=215 et 345, trou de case Y=40. Les attaches sont à l'extérieur de la descente ; les cales de 3 mm compensent le décalage des parois.

Les trois bacs `38` se fixent au socle devant les rampes. La face arrière de chaque bac reste ouverte pour recevoir les boîtes. Tester une descente depuis chaque colonne et chaque hauteur. La cinématique de chute n'est pas simulée : si une boîte tourne et se coince, il faut adapter les panneaux et les sorties avant les essais automatiques.

## 9. Capteurs et câbles

Neuf supports `39` sont fournis en réserve pour une architecture possible : trois positions X, trois positions Z, deux positions Y et un passage de boîte. Ils ne sont pas implantés dans l’assemblage. Capteurs, cibles, fixations finales et distances d’arrêt restent à définir. Leur nombre ne constitue pas une protection complète contre les dépassements. Un encodeur par axe avec origines et limites est une autre possibilité. Le servo continu ne fournit pas la position au contrôleur ; les temporisations seules ne suffisent pas pour l’alignement.

Installer les six attaches `40` sur des surfaces fixes adéquates et y passer des colliers. Conserver une boucle libre pour chaque axe. Vérifier à la main que rien ne tire en position haute et dans les colonnes extrêmes. L'électronique de commande et son éventuel boîtier ne sont pas définis dans cette version.

## 10. Positions et réglages

| Position | X global | Z global du poussoir |
|---|---:|---:|
| Colonne gauche | 45 | selon ligne |
| Colonne centrale | 135 | selon ligne |
| Colonne droite | 225 | selon ligne |
| Ligne basse | selon colonne | 200,5 |
| Ligne centrale | selon colonne | 265,5 |
| Ligne haute | selon colonne | 330,5 |

Le centre du poussoir est 20,5 mm au-dessus du dessous de chaque case. Cette cote dépend de la boîte retenue (35 mm de haut sur fond de 3).

Une position de prise d'origine à X=43, Z=200,5, poussoir rétracté, est vérifiée géométriquement. Cela donne 2 mm de décalage en X par rapport à la première colonne ; l'origine Z coïncide avec la hauteur de la première ligne. Il faut régler les capteurs et leurs distances d'arrêt sur le matériel réel ; ces coordonnées ne remplacent pas des fins de course. Ne pas chercher une butée en forçant le moteur.

Avec du M8 à pas de 1,25 mm, la translation théorique est de 1,25 mm par tour. À 50 tr/min, on obtient théoriquement 62,5 mm/min ; il n’y a pas de conversion en pas/mm pour ces servos continus. Ce montage vise une démonstration lente ; vitesse, accélération et couple restent à déterminer par essai.

## 11. Visserie et pièces réelles

La liste des pièces achetées donne les dimensions nominales. Les longueurs de tiges sont des cotes de montage, **à confirmer à blanc avec les moteurs et accouplements réels avant de couper**. Ébavurer les extrémités.

Pour la visserie, prévoir des assortiments M3 (10, 12, 16 et 20 mm), M4 (10 à tête fraisée, 12, 16, 40, 60 et 65 mm), écrous et rondelles. Les quantités exactes par référence imprimée sont dans la nomenclature ; compter deux vis par éclisse, quatre par retenue. Certaines vis se vissent dans des avant-trous imprimés, d'autres exigent des écrous. Ne pas les confondre.

Les filetages imprimés ne sont pas des inserts métalliques. Si un avant-trou se détériore au montage, le remplacer par un insert ou un boulon traversant et adapter le logement. Ce changement impose de contrôler les dégagements.

## 12. Réception du prototype

- Aucun jeu ne doit empêcher l'alignement de la palette dans l'ouverture arrière (3 mm de jeu nominal par côté).
- Chaque axe doit coulisser à la main sans point dur avec l'entraînement désaccouplé.
- La tige de poussée et ses vis doivent traverser l'ouverture sans accrocher.
- Le poussoir doit revenir derrière Y=100 avant le déplacement du portique.
- Une seule boîte factice est placée dans chaque case ; aucun magasin à plusieurs boîtes n'est prévu.
- Tester d'abord les mouvements sans boîte, puis une seule case, puis les neuf positions.
- Contrôler la rigidité du portique, la flèche des tiges et les liaisons du socle sous le poids réel. La validation géométrique ne garantit pas ces points.

Le modèle est destiné à un projet scolaire avec des boîtes factices. Les essais physiques et la motorisation restent à mettre au point.
