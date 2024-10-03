# Spécifications pour le projet CK3 AI Character avec OpenAI Real-Time API

## Objectif
Créer un personnage AI pour le jeu Crusader Kings 3 qui peut réagir en temps réel aux événements du jeu en utilisant la vision par ordinateur et la synthèse vocale, en utilisant l'API Real-Time d'OpenAI.

## Composants principaux
1. Capture d'écran
2. Analyse d'image et génération de texte (via OpenAI API)
3. Génération de réponse vocale en temps réel (via OpenAI API)
4. Communication WebSocket
5. Lecture audio en streaming

## Flux de travail
1. Établir une connexion WebSocket avec l'API Real-Time d'OpenAI
2. Initialiser la session avec les instructions système et de personnage
3. Capturer périodiquement des captures d'écran du jeu
4. Envoyer une description de la capture d'écran à l'API OpenAI pour analyse
5. Recevoir et traiter les événements du serveur (texte et audio)
6. Lire en streaming la réponse audio de l'API
7. Maintenir la connexion WebSocket pour une communication continue

## Détails techniques
- Utilisation de Python pour le script principal
- Bibliothèques : 
  - pyautogui pour la capture d'écran
  - websockets pour la communication WebSocket
  - pygame pour la lecture audio en streaming
  - PIL (Python Imaging Library) pour le traitement d'image
  - python-dotenv pour la gestion des variables d'environnement
- API endpoint : wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01

## Fonctionnalités
- Capture d'écran et redimensionnement pour optimiser la taille
- Envoi de la description de la capture d'écran via WebSocket à l'API OpenAI
- Gestion des événements serveur pour le texte et l'audio
- Réception et lecture en temps réel des chunks audio
- Gestion des erreurs et reconnexion en cas de problème
- Configuration via fichier .env pour la sécurité de l'API key
- Utilisation de prompts système et de personnage pour définir le comportement de l'IA

## Fonctionnalités implémentées
- Intégration complète de l'API Real-Time d'OpenAI
- Gestion des événements serveur pour le texte et l'audio
- Utilisation de prompts système et de personnage
- Capture d'écran et envoi de description textuelle

## Fonctionnalités futures
- Amélioration de la précision de l'analyse d'image
- Personnalisation de la voix du personnage AI via les options de l'API OpenAI
- Intégration plus profonde avec le jeu (si possible)
- Gestion des interruptions et reprises de la parole
- Implémentation des appels de fonction (tool calls)
- Gestion de l'historique des conversations
- Optimisation de la détection des tours de parole

## Considérations de performance
- Optimisation de la taille et de la fréquence des captures d'écran
- Gestion efficace de la connexion WebSocket
- Mise en mémoire tampon audio pour une lecture fluide
- Gestion asynchrone pour une meilleure réactivité
- Troncature automatique des conversations longues

## Utilisation
1. Configurer les variables d'environnement (OPENAI_API_KEY)
2. Exécuter le script principal : `python main.py`
3. Le script capturera périodiquement des captures d'écran du jeu CK3
4. L'IA analysera la capture d'écran et fournira des commentaires vocaux et textuels

## Notes importantes
- Assurez-vous que les fichiers de prompts (system.md et character.md) sont présents dans le dossier 'prompts'
- Le script utilise l'API Real-Time d'OpenAI, qui est encore en version bêta et peut être sujette à des changements
- Veillez à respecter les conditions d'utilisation de l'API OpenAI et les limites de taux
