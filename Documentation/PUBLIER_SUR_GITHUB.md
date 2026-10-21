# Mettre ce projet sur GitHub

## Présentation proposée

- **Nom** : `armoire-robotisee-a1-mini`
- **Description** : Prototype étudiant d’armoire de stockage robotisée : 9 cases, 3 axes, pièces imprimables sur A1 mini, CAO STEP et CadQuery.
- **Topics** : `robotics`, `3d-printing`, `cadquery`, `mechatronics`, `fusion360`, `student-project`

Avant publication, relire les fichiers, ajouter les auteurs avec leur accord et choisir une licence avec l’équipe. Le README décrit volontairement une conception non validée physiquement.

## Option 1 — interface GitHub

1. Décompresser l’archive. Ouvrir le dossier `armoire-robotisee-a1-mini`.
2. Sur GitHub, créer un dépôt vide portant le nom proposé, public ou privé selon votre choix. Ne pas générer de README, de licence ou de fichier gitignore supplémentaires.
3. Choisir **Add file → Upload files**, puis déposer le contenu du dossier décompressé. Le README doit être à la racine du dépôt, pas dans un dossier supplémentaire.
4. Vérifier que les dossiers `STL`, `CAO`, `Documentation`, `tools` et `.github` sont inclus. Les dossiers commençant par un point peuvent être masqués dans l’explorateur : afficher les fichiers cachés ou utiliser l’option Git ci-dessous.
5. Enregistrer avec un message tel que `Ajout du prototype mécanique V0.2`.
6. Dans l’onglet Actions, vérifier le résultat de **Vérifier les fichiers imprimables**.

Ne pas téléverser uniquement le ZIP : le README, les sources et les fichiers individuels doivent pouvoir être consultés. L’archive peut être ajoutée ensuite comme pièce jointe d’une release.

## Option 2 — Git depuis votre ordinateur

Installer Git et configurer votre propre identité Git. Dans un terminal ouvert à la racine du dossier décompressé :

```sh
git init -b main
git add .
git commit -m "Ajout du prototype mécanique V0.2"
git remote add origin https://github.com/VOTRE_IDENTIFIANT/armoire-robotisee-a1-mini.git
git push -u origin main
```

Remplacer `VOTRE_IDENTIFIANT` par votre compte. Le dépôt distant doit avoir été créé vide. Utiliser le mécanisme d’authentification proposé par GitHub ; ne jamais mettre un jeton dans les fichiers du projet.

## Première release facultative

Après vérification des fichiers sur GitHub, créer une release `v0.2-prototype`, la marquer comme préversion et reprendre le texte de `Documentation/RELEASE_v0.2.md`. Ne pas présenter cette release comme un robot testé.

## Références officielles

- [Ajouter du code local à GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [Ajouter des fichiers à un dépôt](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)
- [Licences d’un dépôt](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
