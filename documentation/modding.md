# Guide de modding pour Crusader Kings III

Ce guide fournit une introduction au modding de Crusader Kings III, couvrant les bases, les outils et les meilleures pratiques.

## Introduction

Le modding consiste à modifier les ressources ou le comportement du jeu, soit pour un usage personnel, soit pour les partager publiquement via Paradox Mods ou le Steam Workshop. Crusader Kings III est hautement moddable, permettant diverses modifications telles que l'ajout d'événements, l'amélioration des cartes et modèles, des conversions totales, des améliorations d'accessibilité, des traductions, etc.

Le modding de CK3 ne nécessite pas de connaissances en programmation et peut être réalisé principalement avec un simple éditeur de texte. Le jeu utilise son propre langage de script conçu pour être facile à utiliser et à apprendre.

Depuis la mise à jour 1.9, les mods ne désactivent plus les succès et n'invalident pas les sauvegardes en mode Ironman. En multijoueur, tous les joueurs doivent utiliser les mêmes mods dans le même ordre de chargement.

## Conseils et directives

1. Utilisez les options de lancement `-debug_mode -develop` pour recharger instantanément les fichiers et utiliser la console.
   - Sur Steam : clic droit sur le jeu -> Propriétés -> ajoutez `-debug_mode -develop` dans Options de lancement
   - Windows : Créez un raccourci pour le fichier .exe -> clic droit -> Propriétés -> ajoutez `-debug_mode -develop` à la fin du champ Cible
   - Windows Xbox Game Pass : Ouvrez 'Invite de commandes' et exécutez 'start shell:AppsFolder\ParadoxInteractive.ProjectTitus_zfnrdv2de78ny!App -debug_mode -develop'
2. Créez toujours un mod pour vos modifications, même mineures. Ne modifiez jamais directement les fichiers du jeu.
3. Utilisez un bon éditeur de texte. Options gratuites recommandées :
   - Visual Studio Code avec l'extension CWTools
   - Notepad++ (choisissez Perl comme langage)
   - Atom (choisissez Perl 6 (Raku) comme langage)
   - Sublime Text avec l'extension Sublime Tools
   - IntelliJ IDEA avec le plugin Paradox Language Support
4. Vérifiez toujours le fichier `error.log` pour les erreurs d'exécution (Documents/Paradox Interactive/Crusader Kings III/logs/error.log).
5. Communiquez clairement les caractéristiques de votre mod :
   - Listez les principaux changements en haut de la description
   - Fournissez des liens vers votre mod sur d'autres plateformes
   - Si possible, téléchargez votre mod sur toutes les plateformes
6. Sauvegardez régulièrement votre travail. Utilisez un système de contrôle de version comme Git.
7. Utilisez des outils de fusion (comme WinMerge) pour mettre à jour les fichiers modifiés.
8. Utilisez des expressions régulières pour les remplacements de texte à grande échelle.
9. Utilisez Win+V pour accéder à l'historique du presse-papiers.
10. Rejoignez le discord CK3 Modding pour obtenir de l'aide et aider les autres.
11. Consultez le Modding Git Guide pour des conseils sur l'utilisation de Git et GitHub/GitLab.

## Fichiers de localisation

- Les fichiers *.yml dans le dossier de localisation doivent être enregistrés avec l'encodage UTF-8 + BOM.
- Les noms de fichiers doivent être au format *l_<langue>.yml (par exemple, council_l_english.yml).
- Utilisez l'orthographe américaine "localization" (pas "localisation").
- Pour écraser les valeurs de localisation existantes, placez vos fichiers dans un dossier "replace" dans le dossier de localisation.
- Si un mod n'a que la localisation anglaise, copiez-la pour les autres langues même sans traduction.

## Options de lancement

- -debug_mode : active les info-bulles et interactions de développement
- -develop : active le rechargement à chaud de la plupart des fichiers
- -mapeditor : ouvre l'éditeur de carte
- -debug_controller_camera : ajoute le support pour contrôler la caméra avec une manette
- -nographics : lance le jeu sans créer de fenêtre ni rien rendre et démarre une partie en observateur
- -random_seed=42 : lance le jeu avec une graine RNG fixe (fonctionne uniquement avec -debug_mode)
- -benchmark : exécute un test automatisé pendant 1,5 an
- -continuelastsave : peut être utilisé dans un raccourci vers ck3.exe pour charger automatiquement la dernière sauvegarde

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
