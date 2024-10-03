# Spécifications pour le projet CK3 AI Character avec OpenAI Real-Time API

## Objectif
Créer un personnage AI pour le jeu Crusader Kings 3 qui peut réagir en temps réel aux événements du jeu en utilisant la vision par ordinateur et la synthèse vocale, en utilisant l'API Real-Time d'OpenAI.

## Composants principaux
1. Parseur de fichier de sauvegarde CK3
2. Système de surveillance périodique des fichiers de sauvegarde
3. Système de différenciation pour détecter les changements entre les versions de sauvegarde
4. Système de mise en cache des données de jeu
5. Système de requête pour récupérer des informations spécifiques du jeu
6. Système de journalisation des événements
7. Commande console personnalisée pour les mises à jour manuelles
8. Sérialisation des données pour la transmission externe
9. Système de repli pour gérer les données incomplètes ou corrompues
10. Intégration avec n8n pour l'orchestration des flux de travail
11. Interface utilisateur pour les interactions vocales et textuelles
12. Intégration avec Xata pour le stockage des données

## Flux de travail
1. Surveiller périodiquement les changements dans le fichier de sauvegarde CK3
2. Parser le fichier de sauvegarde pour extraire les données pertinentes
3. Comparer avec la version précédente pour identifier les changements
4. Mettre à jour le cache local des données de jeu
5. Envoyer les données mises à jour à n8n via des appels REST
6. n8n traite les données et interagit avec le modèle de langage GPT-4o-mini
7. n8n envoie les réponses générées au mod CK3
8. Le mod CK3 affiche les réponses et lit l'audio via l'interface utilisateur
9. Capturer les entrées vocales/textuelles de l'utilisateur et les envoyer au mod CK3
10. Répéter le processus pour maintenir une interaction continue

## Détails techniques
- Utilisation de C++ pour le mod CK3 principal
- Utilisation de Python pour les scripts auxiliaires et l'intégration avec n8n
- Bibliothèques :
  - Boost pour les fonctionnalités C++ avancées
  - nlohmann/json pour le traitement JSON en C++
  - requests pour les appels REST en Python
  - python-dotenv pour la gestion des variables d'environnement
  - PyAudio pour la capture audio
- API endpoint pour n8n : à définir lors de la configuration de n8n
- Intégration avec Xata pour le stockage cloud
- Utilisation de l'API de modding CK3 pour les événements et triggers personnalisés

## Fonctionnalités
- Parseur de fichier de sauvegarde CK3 robuste
- Système de surveillance périodique des fichiers de sauvegarde
- Système de différenciation pour détecter les changements entre les versions de sauvegarde
- Système de mise en cache des données de jeu pour un accès rapide
- Système de requête pour récupérer des informations spécifiques du jeu
- Système de journalisation des événements importants
- Commande console personnalisée pour les mises à jour manuelles de l'état du jeu
- Sérialisation des données pour la transmission à n8n
- Système de repli pour gérer les données incomplètes ou corrompues
- Intégration avec n8n pour l'orchestration des flux de travail
- Interface utilisateur pour les interactions vocales et textuelles
- Intégration avec Xata pour le stockage des données de conversation et de personnage
- Capture audio du microphone de l'utilisateur
- Synthèse vocale pour les réponses de l'IA
- Gestion des erreurs et reconnexion en cas de problème
- Configuration via fichier .env pour la sécurité des clés API
- Utilisation de prompts système et de personnage pour définir le comportement de l'IA

## Fonctionnalités implémentées
- Structure de base du mod CK3
- Intégration avec n8n pour l'orchestration des flux de travail
- Utilisation de prompts système et de personnage
- Capture audio du microphone et envoi à n8n
- Lecture de la réponse audio générée

## Fonctionnalités futures
- Amélioration de la précision du parseur de fichier de sauvegarde
- Optimisation du système de mise en cache des données de jeu
- Personnalisation avancée des voix des personnages IA
- Intégration plus profonde avec les mécaniques de jeu CK3
- Optimisation de la détection des changements d'état de jeu importants
- Implémentation d'un système de prise de décision IA plus avancé
- Gestion avancée de l'historique des conversations et des relations entre personnages
- Support pour la continuation des conversations à travers plusieurs sessions de jeu
- Développement d'une API pour permettre l'extension du mod par des tiers

## Considérations de performance
- Optimisation de la fréquence de lecture et de parsing des fichiers de sauvegarde
- Gestion efficace des appels REST vers n8n
- Optimisation du système de mise en cache des données de jeu
- Gestion asynchrone des tâches pour une meilleure réactivité
- Troncature automatique des conversations longues dans la base de données Xata
- Gestion des limites de taux des API externes (n8n, Xata, etc.)
- Optimisation de l'utilisation de la mémoire pour minimiser l'impact sur les performances du jeu

## Utilisation
1. Installer le mod CK3 AI Character via le Steam Workshop ou manuellement
2. Configurer n8n avec les flux de travail nécessaires
3. Configurer la base de données Xata
4. Configurer les variables d'environnement (clés API pour n8n, Xata, etc.)
5. Lancer Crusader Kings III avec le mod activé
6. Le mod surveillera automatiquement l'état du jeu et interagira avec l'IA via n8n
7. Utiliser l'interface du mod pour les interactions vocales et textuelles avec les personnages IA

## Notes importantes
- Assurez-vous que les fichiers de prompts (system.md et character.md) sont présents dans le dossier du mod
- Le mod nécessite une connexion internet active pour fonctionner avec n8n et Xata
- Veillez à respecter les conditions d'utilisation des différentes API et services utilisés
- Implémentez des garde-fous dans vos instructions et inspectez la sortie du modèle pour une utilisation robuste
- Gérez correctement les erreurs potentielles lors des interactions avec n8n et Xata
- Assurez-vous que votre système répond aux exigences minimales pour exécuter CK3 avec le mod
