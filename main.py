import asyncio
import websockets
import pyautogui
import io
import pygame
import logging
import argparse
from PIL import Image
import base64
import json
import os
from dotenv import load_dotenv
import pyaudio
import wave
import xata
import difflib
from datetime import datetime
import threading
# Load environment variables
load_dotenv()

# Audio recording constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000  # 24kHz as required by the API

# Xata client initialization
XATA_API_KEY = os.getenv("XATA_API_KEY")
XATA_DATABASE_URL = os.getenv("XATA_DATABASE_URL")
xata_client = xata.XataClient(api_key=XATA_API_KEY, db_url=XATA_DATABASE_URL)

# Game state cache
game_state_cache = {}

# Read system prompts
def read_prompt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

SYSTEM_PROMPT = read_prompt('prompts/system.md')
CHARACTER_PROMPT = read_prompt('prompts/character.md')

# Configuration
DEFAULT_SCREENSHOT_INTERVAL = 30  # seconds
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBSOCKET_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Vérification de la clé API
if not OPENAI_API_KEY:
    logging.error("La clé API OpenAI n'est pas définie. Veuillez la configurer dans le fichier .env")
    exit(1)

# Affichage des premiers et derniers caractères de la clé API pour vérification
logging.info(f"Clé API chargée : sk-...{OPENAI_API_KEY[-4:]}")

# Vérification supplémentaire de la clé API
if not OPENAI_API_KEY.startswith("sk-"):
    logging.error("La clé API OpenAI semble invalide. Assurez-vous qu'elle commence par 'sk-'")
    exit(1)

def parse_ck3_save(save_file_path):
    """Parse the CK3 save file and return relevant game state data."""
    # This is a placeholder function. Implement the actual parsing logic here.
    # You'll need to read the save file and extract the relevant information.
    with open(save_file_path, 'r') as file:
        # Implement parsing logic here
        game_state = {}  # Populate this dictionary with parsed data
    return game_state

def detect_game_state_changes(old_state, new_state):
    """Detect changes between two game states."""
    changes = {}
    for key in set(old_state.keys()) | set(new_state.keys()):
        if key not in old_state:
            changes[key] = f"Added: {new_state[key]}"
        elif key not in new_state:
            changes[key] = "Removed"
        elif old_state[key] != new_state[key]:
            changes[key] = f"Changed: {old_state[key]} -> {new_state[key]}"
    return changes

def update_game_state_cache(new_state):
    """Update the game state cache and store changes in Xata."""
    global game_state_cache
    changes = detect_game_state_changes(game_state_cache, new_state)
    game_state_cache = new_state
    
    # Store changes in Xata
    xata_client.create_record("game_state_changes", {
        "timestamp": datetime.now().isoformat(),
        "changes": json.dumps(changes)
    })

def take_screenshot():
    """Capture a screenshot, resize it, and return it as base64 string."""
    screenshot = pyautogui.screenshot()
    
    # Resize the image to reduce file size (adjust dimensions as needed)
    max_size = (1024, 576)  # Reduced size for faster processing
    screenshot.thumbnail(max_size, Image.LANCZOS)
    
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='JPEG', quality=85, optimize=True)  # Use JPEG for smaller file size
    return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

async def process_audio_chunk(chunk):
    """Process and play an audio chunk."""
    try:
        pygame.mixer.init()
        sound = pygame.mixer.Sound(buffer=chunk)
        sound.play()
        await asyncio.sleep(sound.get_length())
    except pygame.error as e:
        logging.error(f"Failed to play audio chunk: {e}")

def record_audio(duration):
    """Record audio from the microphone for a specified duration."""
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    logging.info(f"Recording for {duration} seconds...")
    frames = []

    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    logging.info("Recording finished")

    stream.stop_stream()
    stream.close()
    p.terminate()

    return b''.join(frames)

import tkinter as tk
from tkinter import scrolledtext

# Créer une fenêtre Tkinter globale
root = tk.Tk()
root.title("CK3 AI Character Response")
text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
text_widget.pack(expand=True, fill='both')

async def handle_server_event(event):
    """Handle server events."""
    event_type = event.get('type')
    if event_type == 'response.text.delta':
        delta_text = event.get('delta', '')
        logging.info(f"Received text delta: {delta_text}")
        # Mettre à jour l'interface graphique avec le texte reçu
        root.after(0, lambda: text_widget.insert(tk.END, delta_text))
    elif event_type == 'response.audio.delta':
        await process_audio_chunk(base64.b64decode(event.get('delta', '')))
    elif event_type == 'error':
        error_message = f"Received error: {event.get('error', {})}"
        logging.error(error_message)
        root.after(0, lambda: text_widget.insert(tk.END, f"\nERROR: {error_message}\n"))
    elif event_type == 'response.done':
        logging.info("Response completed")
        root.after(0, lambda: text_widget.insert(tk.END, "\n--- Response completed ---\n\n"))
    elif event_type == 'response.created':
        logging.info("Response started")
        root.after(0, lambda: text_widget.insert(tk.END, "\n--- New response ---\n"))
    elif event_type == 'response.function_call_arguments.delta':
        func_call_delta = f"Function call arguments delta: {event.get('delta', {})}"
        logging.info(func_call_delta)
        root.after(0, lambda: text_widget.insert(tk.END, f"\n{func_call_delta}\n"))
    else:
        logging.info(f"Received event: {event_type}")
        root.after(0, lambda: text_widget.insert(tk.END, f"\nReceived event: {event_type}\n"))

async def websocket_client(interval):
    while True:
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            }
            logging.info(f"Tentative de connexion à {WEBSOCKET_URL}")
            masked_headers = headers.copy()
            masked_headers["Authorization"] = f"Bearer sk-...{OPENAI_API_KEY[-4:]}"
            logging.info(f"Headers utilisés : {masked_headers}")
            async with websockets.connect(
                WEBSOCKET_URL,
                extra_headers=headers
            ) as websocket:
                logging.info(f"Connecté au WebSocket. Démarrage de CK3 AI Character avec un intervalle de {interval} secondes")
    
                # Initialize the session
                session_init = {
                    "type": "session.create",
                    "session": {
                        "instructions": SYSTEM_PROMPT + "\n" + CHARACTER_PROMPT,
                        "modalities": ["text", "audio"],
                        "voice": "alloy"
                    }
                }
                logging.info(f"Initialisation de la session avec : {session_init}")
                await websocket.send(json.dumps(session_init))
                logging.info("Session initialisée")
                
                while True:
                    logging.info("Analyse du fichier de sauvegarde CK3 en cours")
                    new_game_state = parse_ck3_save("path/to/ck3/save/file.ck3")  # Remplacer par le chemin réel
                    update_game_state_cache(new_game_state)
                    logging.info("Analyse du fichier de sauvegarde terminée")
                    
                    logging.info("Capture d'écran en cours")
                    screenshot_base64 = take_screenshot()
                    logging.info("Capture d'écran terminée")
                    
                    # Record audio
                    logging.info("Enregistrement audio en cours")
                    audio_data = record_audio(5)  # Record for 5 seconds
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    logging.info("Enregistrement audio terminé")
                    
                    # Send the game state, screenshot description and audio
                    conversation_item = {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "message",
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": f"Current game state: {json.dumps(game_state_cache)}. Describe the current game state based on this information and the screenshot, then respond to my audio input."
                                },
                                {
                                    "type": "input_image",
                                    "image": screenshot_base64
                                },
                                {
                                    "type": "input_audio",
                                    "audio": audio_base64
                                }
                            ]
                        }
                    }
                    logging.info("Envoi de l'état du jeu, de la capture d'écran et de l'audio à l'API")
                    await websocket.send(json.dumps(conversation_item))
                    logging.info("Données envoyées avec succès")
    
                    # Request a response from the model
                    response_request = {
                        "type": "response.create",
                        "response": {
                            "modalities": ["text", "audio"]
                        }
                    }
                    logging.info("Demande de réponse au modèle")
                    await websocket.send(json.dumps(response_request))
                    logging.info("Demande de réponse envoyée")
                    
                    # Process server events
                    async for message in websocket:
                        event = json.loads(message)
                        logging.info(f"Événement reçu du serveur : {event.get('type')}")
                        await handle_server_event(event)
                        if event.get('type') == 'done':
                            logging.info("Traitement de la réponse terminé")
                            break
                    
                    logging.info(f"Attente de {interval} secondes avant la prochaine itération")
                    await asyncio.sleep(interval)
                
        except websockets.exceptions.ConnectionClosed:
            logging.error("WebSocket connection closed. Attempting to reconnect...")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            logging.info("Attempting to reconnect in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CK3 AI Character with OpenAI Real-Time API")
    parser.add_argument("--interval", type=int, default=DEFAULT_SCREENSHOT_INTERVAL,
                        help=f"Screenshot interval in seconds (default: {DEFAULT_SCREENSHOT_INTERVAL})")
    args = parser.parse_args()
    
    try:
        # Lancer le client WebSocket dans un thread séparé
        websocket_thread = threading.Thread(target=lambda: asyncio.run(websocket_client(args.interval)))
        websocket_thread.start()
        
        # Lancer la boucle principale Tkinter
        root.mainloop()
    except KeyboardInterrupt:
        logging.info("Program terminated by user")
    finally:
        root.quit()

print("Pour exécuter ce script, utilisez la commande : python main.py")
