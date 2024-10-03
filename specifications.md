# Spécifications pour le projet CK3 AI Character avec OpenAI Real-Time Voice API

## Objectif
Créer un personnage AI pour le jeu Crusader Kings 3 qui peut réagir en temps réel aux événements du jeu en utilisant la vision par ordinateur et la synthèse vocale, en utilisant l'API voix en temps réel d'OpenAI.

## Composants principaux
1. Capture d'écran
2. Analyse d'image (via OpenAI API)
3. Génération de réponse vocale en temps réel (via OpenAI API)
4. Communication WebSocket
5. Lecture audio en streaming

## Flux de travail
1. Établir une connexion WebSocket avec l'API OpenAI
2. Capturer périodiquement des captures d'écran du jeu
3. Envoyer la capture d'écran à l'API OpenAI pour analyse
4. Recevoir et lire en streaming la réponse audio de l'API
5. Maintenir la connexion WebSocket pour une communication continue

## Détails techniques
- Utilisation de Python pour le script principal
- Bibliothèques : 
  - pyautogui pour la capture d'écran
  - websockets pour la communication WebSocket
  - pygame ou pydub pour la lecture audio en streaming
  - openai pour l'intégration avec l'API OpenAI
- API endpoint : À déterminer (endpoint WebSocket d'OpenAI)

## Fonctionnalités futures
- Amélioration de la précision de l'analyse d'image
- Personnalisation de la voix du personnage AI via les options de l'API OpenAI
- Intégration plus profonde avec le jeu (si possible)
- Gestion des interruptions et reprises de la parole

## Considérations de performance
- Optimisation de la taille et de la fréquence des captures d'écran
- Gestion efficace de la connexion WebSocket
- Mise en mémoire tampon audio pour une lecture fluide
