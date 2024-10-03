# Realtime API Beta

The Realtime API enables you to build low-latency, multi-modal conversational experiences. It currently supports text and audio as both input and output, as well as function calling.

## Notable Benefits

- Native speech-to-speech: No text intermediary means low latency, nuanced output.
- Natural, steerable voices: The models have a natural inflection and can laugh, whisper, and adhere to tone direction.
- Simultaneous multimodal output: Text is useful for moderation, faster-than-realtime audio ensures stable playback.

## Quickstart

The Realtime API is a WebSocket interface designed to run on the server. A console demo application is available to help visualize and inspect the flow of events in a Realtime integration.

### Get Started with the Realtime Console

Download and configure the Realtime console demo to get started quickly.

## Overview

The Realtime API is a stateful, event-based API that communicates over a WebSocket. The WebSocket connection requires the following parameters:

- URL: `wss://api.openai.com/v1/realtime`
- Query Parameters: `?model=gpt-4o-realtime-preview-2024-10-01`
- Headers:
  - `Authorization: Bearer YOUR_API_KEY`
  - `OpenAI-Beta: realtime=v1`

### Example Connection (Node.js)

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
    console.log("Connected to server.");
    ws.send(JSON.stringify({
        type: "response.create",
        response: {
            modalities: ["text"],
            instructions: "Please assist the user.",
        }
    }));
});

ws.on("message", function incoming(message) {
    console.log(JSON.parse(message.toString()));
});
```

## API Reference

For a complete listing of client and server events in the Realtime API, refer to the API reference documentation.

## Concepts

The Realtime API is stateful, maintaining the state of interactions throughout the lifetime of a session. Clients connect via WebSockets and exchange JSON-formatted events.

### State Components

1. Session
2. Input Audio Buffer
3. Conversations (list of Items)
4. Responses (generate a list of Items)

### Session

A session represents a single WebSocket connection between a client and the server. It contains default configuration that can be updated at any time.

### Conversation

A realtime Conversation consists of a list of Items. By default, there is only one Conversation created at the beginning of the Session.

### Items

A realtime Item can be of three types: message, function_call, or function_call_output. Messages can contain text or audio.

### Input Audio Buffer

The server maintains an Input Audio Buffer containing client-provided audio that has not yet been committed to the conversation state.

### Responses

The server's response timing depends on the turn_detection configuration.

## Integration Guide

### Audio Formats

The realtime API supports two formats:
1. Raw 16 bit PCM audio at 24kHz, 1 channel, little-endian
2. G.711 at 8kHz (both u-law and a-law)

### Instructions

You can control the content of the server's response by setting instructions on the session or per-response.

### Handling Events

To send events to the API, send a JSON string containing your event payload data. To receive events, listen for the WebSocket message event and parse the result as JSON.

### Handling Interruptions

The server can be interrupted during audio response, either by detecting input speech or by an explicit client message.

### Handling Tool Calls

The client can set default functions for the server, and the server will respond with function_call items when appropriate.

### Moderation

It's recommended to include guardrails in your instructions and inspect the model's output for robust usage.

### Handling Errors

All errors are passed from the server to the client with an error event.

### Adding History and Continuing Conversations

The Realtime API allows clients to populate a conversation history and continue conversations across sessions.

### Handling Long Conversations

The Realtime API automatically truncates conversations that exceed the model's input context limit.

## Events

There are 9 client events you can send and 28 server events you can listen to. Refer to the API reference for the full specification.

For the simplest implementation, it's recommended to look at the API reference client source: conversation.js, which handles 13 of the server events.
