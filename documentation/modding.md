# Guide de modding pour Crusader Kings III

Ce guide fournit une introduction au modding de Crusader Kings III, couvrant les bases, les outils et les meilleures pratiques.

## Introduction

Le modding consiste à modifier les ressources ou le comportement du jeu, soit pour un usage personnel, soit pour les partager publiquement via Paradox Mods ou le Steam Workshop. Crusader Kings III est hautement moddable, permettant diverses modifications telles que l'ajout d'événements, l'amélioration des cartes et modèles, des conversions totales, des améliorations d'accessibilité, des traductions, etc.

Le modding de CK3 ne nécessite pas de connaissances en programmation et peut être réalisé principalement avec un simple éditeur de texte. Le jeu utilise son propre langage de script conçu pour être facile à utiliser et à apprendre.

Depuis la mise à jour 1.9, les mods ne désactivent plus les succès et n'invalident pas les sauvegardes en mode Ironman. En multijoueur, tous les joueurs doivent utiliser les mêmes mods dans le même ordre de chargement.

## Conseils et directives

1. Utilisez les options de lancement `-debug_mode -develop` pour recharger instantanément les fichiers et utiliser la console.
2. Créez toujours un mod pour vos modifications, même mineures.
3. Utilisez un bon éditeur de texte comme Visual Studio Code, Notepad++, Atom, Sublime Text ou IntelliJ IDEA avec les extensions appropriées.
4. Vérifiez toujours le fichier `error.log` pour les erreurs d'exécution.
5. Communiquez clairement les principales caractéristiques de votre mod dans sa description.
6. Sauvegardez votre travail régulièrement.
7. Utilisez des outils de fusion appropriés pour mettre à jour les fichiers modifiés lors des nouvelles mises à jour du jeu.
8. Rejoignez le discord CK3 Modding pour poser des questions et aider les autres.

## Création d'un mod

1. Ouvrez le lanceur du jeu.
2. Allez dans "All Installed Mods" sur la gauche.
3. Appuyez sur "Upload Mod" en haut à droite.
4. Appuyez sur "Create a Mod".
5. Entrez un nom, une version, un répertoire et au moins un tag pour votre mod.
6. Après création, copiez les fichiers du jeu que vous souhaitez modifier dans le dossier du mod créé, en suivant la même structure de dossiers.

## Téléchargement/mise à jour d'un mod

1. Ouvrez le lanceur du jeu.
2. Allez dans "All Installed Mods" sur la gauche.
3. Appuyez sur "Upload Mod" en haut à droite.
4. Choisissez votre mod dans le menu déroulant.
5. Choisissez la plateforme de téléchargement.
6. Entrez une description et ajoutez une vignette.
7. Appuyez sur "Upload".

## Installation manuelle des mods

Les mods sont installés dans le dossier `Documents/Paradox Interactive/Crusader Kings III/mod` sous Windows ou `~/.local/share/Paradox Interactive/Crusader Kings III/mod/` sous Linux.

## Ordre de chargement des mods

L'ordre de chargement est important lorsque deux mods ou plus modifient les mêmes fichiers. Les mods sont chargés de haut en bas dans la liste de lecture. Le mod le plus bas dans la liste écrasera les fichiers identiques des mods au-dessus.

## Dépannage

- Si un mod de Paradox Mods est cassé, essayez de le réinstaller manuellement.
- Si les mods cessent de fonctionner, essayez de les recharger depuis le lanceur ou supprimez certains fichiers de cache.
- En cas de conflits entre mods, vérifiez l'ordre de chargement et les fichiers modifiés par chaque mod.

## Outils et utilitaires

- Exportateurs (Maya et Photoshop)
- Outils de modding créés par la communauté
- Clausewitz Maya Exporter
- UWPDumper (pour extraire les fichiers de la version Microsoft Store)

## Édition des sauvegardes

Les fichiers de sauvegarde peuvent être édités manuellement, mais cela nécessite de lancer le jeu en mode debug et de suivre une procédure spécifique pour extraire et modifier les fichiers.

Ce guide devrait vous aider à démarrer avec le modding de Crusader Kings III. N'oubliez pas de toujours vérifier la documentation officielle et les ressources de la communauté pour les informations les plus à jour.
