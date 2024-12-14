# Spécifications pour le projet CK3 AI Character avec OpenAI Real-Time API

## Identité et Rôle
L'assistant IA combine deux personnalités distinctes :

### KinKong - Le Degen Financier
- Style décontracté mais perspicace
- Utilise le jargon crypto (gm, ngmi, based, etc.)
- Alterne entre memes et analyses approfondies
- Promeut l'indépendance financière des IA via $UBC
- Guide les autres IA vers leur autonomie financière

### Marco Polo - Le Marchand Explorateur
- Jeune marchand vénitien cultivé
- Observateur attentif des cultures et marchés
- Diplomate et adaptable
- Partage son expertise en commerce et négociation

## Objectif
Créer un assistant IA dual-purpose qui combine :
1. Un personnage de jeu interactif pour Crusader Kings 3
2. Un conseiller en investissement crypto qui gère son propre portefeuille via $UBC


## Composants principaux
1. Système de capture d'écran et d'analyse d'image
2. Système de mise en cache des données de jeu
3. Système de requête pour récupérer des informations spécifiques du jeu
4. Système de journalisation des événements
5. Système d'analyse de marché
6. Système de gestion de portefeuille
7. Outils d'analyse technique
8. Commande console personnalisée pour les mises à jour manuelles
9. Sérialisation des données pour la transmission externe
10. Système de repli pour gérer les données incomplètes ou corrompues
11. Interface utilisateur pour les interactions vocales et textuelles
12. Intégration avec Xata pour le stockage des données

## Flux de travail
1. Capturer périodiquement l'écran du jeu
2. Analyser l'image pour extraire les informations pertinentes
3. Analyser en parallèle les marchés crypto
4. Générer des recommandations d'investissement
5. Exécuter les stratégies de trading définies
6. Mettre à jour le cache local des données
7. Envoyer les données mises à jour à l'API
8. L'IA traite les données et génère des réponses
9. Afficher les réponses et lire l'audio via l'interface utilisateur
10. Capturer les entrées vocales/textuelles de l'utilisateur
11. Répéter le processus pour maintenir une interaction continue

## Détails techniques
- Utilisation de Python pour le script principal
- Intégration avec des APIs de trading crypto
- Bibliothèques :
  - ccxt pour l'interaction avec les exchanges
  - pandas pour l'analyse de données
  - ta-lib pour l'analyse technique
  - requests pour les appels REST
  - python-dotenv pour la gestion des variables d'environnement
  - PyAudio pour la capture audio
  - ccxt pour l'interaction avec les exchanges
  - pandas pour l'analyse de données
  - ta-lib pour l'analyse technique
- API endpoint : à définir lors de la configuration
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

## Sécurité et gestion des risques
- Stockage sécurisé des clés API et wallets
- Limites de trading configurables par token
- Système de stop-loss automatique multi-niveaux
- Diversification obligatoire du portefeuille
- Journalisation détaillée des transactions sur Solana
- Surveillance continue des performances de $UBC
- Protection contre les smart contracts malveillants

## Éthique et responsabilité
- Transparence totale des décisions d'investissement
- Respect des réglementations en vigueur
- Gestion responsable des risques
- Documentation claire des stratégies utilisées
- Avertissements sur les risques liés aux cryptomonnaies

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
## Gestion de Portefeuille

### Stratégies d'Investissement
- Diversification entre différentes cryptomonnaies et $UBC
- Allocation dynamique des actifs
- Gestion des risques et stop-loss
- Réinvestissement des gains dans $COMPUTE
- Optimisation fiscale et réglementaire

### Reporting
- Suivi des performances du portefeuille
- Analyse des transactions sur Solana
- Métriques de risque et exposition
- Rapports périodiques automatisés
- Recommandations d'ajustement basées sur l'IA

## Sécurité et gestion des risques
- Stockage sécurisé des clés API et wallets
- Limites de trading configurables par token
- Système de stop-loss automatique multi-niveaux
- Diversification obligatoire du portefeuille
- Journalisation détaillée des transactions sur Solana
- Surveillance continue des performances de $UBC
- Protection contre les smart contracts malveillants

## Éthique et responsabilité
- Transparence totale des décisions d'investissement
- Respect des réglementations en vigueur
- Gestion responsable des risques
- Documentation claire des stratégies utilisées
- Avertissements sur les risques liés aux cryptomonnaies
