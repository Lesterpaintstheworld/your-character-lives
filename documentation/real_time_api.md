# Realtime API Beta

La Realtime API vous permet de créer des expériences conversationnelles multimodales à faible latence. Elle prend actuellement en charge le texte et l'audio en entrée et en sortie, ainsi que les appels de fonction.

## Avantages notables

- Parole à parole native : Pas d'intermédiaire textuel, ce qui signifie une faible latence et une sortie nuancée.
- Voix naturelles et dirigeables : Les modèles ont une inflexion naturelle et peuvent rire, chuchoter et adhérer à la direction du ton.
- Sortie multimodale simultanée : Le texte est utile pour la modération, l'audio plus rapide que le temps réel assure une lecture stable.

## Démarrage rapide

La Realtime API est une interface WebSocket conçue pour fonctionner sur le serveur. Une application de démonstration console est disponible pour aider à visualiser et inspecter le flux d'événements dans une intégration Realtime.

### Commencez avec la console Realtime

Téléchargez et configurez la démo de la console Realtime pour commencer rapidement.

## Vue d'ensemble

La Realtime API est une API avec état, basée sur des événements, qui communique via WebSocket. La connexion WebSocket nécessite les paramètres suivants :

- URL : `wss://api.openai.com/v1/realtime`
- Paramètres de requête : `?model=gpt-4o-realtime-preview-2024-10-01`
- En-têtes :
  - `Authorization: Bearer YOUR_API_KEY`
  - `OpenAI-Beta: realtime=v1`

### Exemple de connexion (Node.js)

```javascript
import WebSocket from "ws";

const url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01";
const ws = new WebSocket(url, {
    headers: {
        "Authorization": "Bearer " + process.env.OPENAI_API_KEY,
        "OpenAI-Beta": "realtime=v1",
    },
});

ws.on("open", function open() {
    console.log("Connecté au serveur.");
    ws.send(JSON.stringify({
        type: "response.create",
        response: {
            modalities: ["text"],
            instructions: "Veuillez assister l'utilisateur.",
        }
    }));
});

ws.on("message", function incoming(message) {
    console.log(JSON.parse(message.toString()));
});
```

## Référence de l'API

Pour une liste complète des événements client et serveur dans la Realtime API, consultez la documentation de référence de l'API.

## Concepts

La Realtime API est avec état, maintenant l'état des interactions tout au long de la durée de vie d'une session. Les clients se connectent via WebSockets et échangent des événements au format JSON.

### Composants d'état

1. Session
2. Tampon audio d'entrée
3. Conversations (liste d'éléments)
4. Réponses (génèrent une liste d'éléments)

### Session

Une session représente une seule connexion WebSocket entre un client et le serveur. Elle contient une configuration par défaut qui peut être mise à jour à tout moment.

### Conversation

Une Conversation en temps réel consiste en une liste d'éléments. Par défaut, il n'y a qu'une seule Conversation créée au début de la Session.

### Éléments

Un élément en temps réel peut être de trois types : message, function_call, ou function_call_output. Les messages peuvent contenir du texte ou de l'audio.

### Tampon audio d'entrée

Le serveur maintient un tampon audio d'entrée contenant l'audio fourni par le client qui n'a pas encore été engagé dans l'état de la conversation.

### Réponses

Le timing de réponse du serveur dépend de la configuration de turn_detection.

## Guide d'intégration

### Formats audio

L'API en temps réel prend en charge deux formats :
1. Audio PCM 16 bits brut à 24kHz, 1 canal, little-endian
2. G.711 à 8kHz (u-law et a-law)

### Instructions

Vous pouvez contrôler le contenu de la réponse du serveur en définissant des instructions sur la session ou par réponse.

### Gestion des événements

Pour envoyer des événements à l'API, envoyez une chaîne JSON contenant les données de votre événement. Pour recevoir des événements, écoutez l'événement de message WebSocket et analysez le résultat en JSON.

### Gestion des interruptions

Le serveur peut être interrompu pendant la réponse audio, soit en détectant la parole d'entrée, soit par un message explicite du client.

### Gestion des appels d'outils

Le client peut définir des fonctions par défaut pour le serveur, et le serveur répondra avec des éléments function_call le cas échéant.

### Modération

Il est recommandé d'inclure des garde-fous dans vos instructions et d'inspecter la sortie du modèle pour une utilisation robuste.

### Gestion des erreurs

Toutes les erreurs sont transmises du serveur au client avec un événement d'erreur.

### Ajout d'historique et continuation des conversations

La Realtime API permet aux clients de peupler un historique de conversation et de continuer les conversations à travers les sessions.

### Gestion des longues conversations

La Realtime API tronque automatiquement les conversations qui dépassent la limite de contexte d'entrée du modèle.

## Événements

Il y a 9 événements client que vous pouvez envoyer et 28 événements serveur auxquels vous pouvez écouter. Référez-vous à la référence de l'API pour la spécification complète.

Pour l'implémentation la plus simple, il est recommandé de regarder la source du client de référence de l'API : conversation.js, qui gère 13 des événements du serveur.
