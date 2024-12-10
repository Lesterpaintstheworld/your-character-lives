import asyncio
import requests
import pyautogui
running = True  # Global control variable
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
import difflib
from datetime import datetime
import threading
import queue
# Load environment variables
load_dotenv()

# Audio recording constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000  # 24kHz as required by the API


# Read investment prompt
def read_prompt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

INVESTMENT_PROMPT = read_prompt('prompts/investment.md')

# Configuration
DEFAULT_SCREENSHOT_INTERVAL = 30  # seconds
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
N8N_ENDPOINT = "https://nlr.app.n8n.cloud/webhook/ycl-enpoint"

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


def take_screenshot():
    """Capture a screenshot, resize it, and return it as base64 string."""
    screenshot = pyautogui.screenshot()
    
    # Resize the image to reduce file size (adjust dimensions as needed)
    max_size = (1024, 576)  # Reduced size for faster processing
    screenshot.thumbnail(max_size, Image.LANCZOS)
    
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='JPEG', quality=85, optimize=True)  # Use JPEG for smaller file size
    return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

import queue

audio_queue = queue.Queue()
is_playing = False

async def process_audio_chunk(chunk):
    """Process and play an audio chunk."""
    global is_playing
    audio_queue.put(chunk)
    
    if not is_playing:
        is_playing = True
        await play_audio_queue()

async def play_audio_queue():
    """Play audio chunks from the queue."""
    global is_playing
    try:
        pygame.mixer.init()
        while not audio_queue.empty():
            chunk = audio_queue.get()
            sound = pygame.mixer.Sound(buffer=chunk)
            sound.play()
            await asyncio.sleep(sound.get_length())
    except pygame.error as e:
        logging.error(f"Failed to play audio chunk: {e}")
    finally:
        is_playing = False

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

def on_closing():
    """Handle application shutdown."""
    global running
    running = False
    logging.info("Shutting down application...")
    root.quit()
    root.destroy()

async def handle_server_event(event):
    """Handle server events."""
    event_type = event.get('type')
    if event_type == 'response.text.delta':
        delta_text = event.get('delta', '')
        logging.info(f"Received text delta: {delta_text}")
        # Mettre à jour l'interface graphique avec le texte reçu
        root.after(0, lambda: text_widget.insert(tk.END, delta_text))
    elif event_type == 'response.audio.delta':
        audio_chunk = base64.b64decode(event.get('delta', ''))
        # Jouer l'audio immédiatement
        asyncio.create_task(process_audio_chunk(audio_chunk))
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

async def api_client(interval):
    global running
    while running:
        try:
            # Capture d'écran
            logging.info("Capture d'écran en cours")
            screenshot_base64 = take_screenshot()
            logging.info("Capture d'écran terminée")
            
            # Enregistrement audio
            logging.info("Enregistrement audio en cours")
            audio_data = record_audio(5)  # 5 secondes d'enregistrement
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            logging.info("Enregistrement audio terminé")
            
            # Préparation des données pour l'API
            payload = {
                "screenshot": screenshot_base64,
                "audio": audio_base64,
                "instructions": INVESTMENT_PROMPT
            }
            
            # Envoi de la requête à n8n
            logging.info("Envoi des données à n8n")
            response = requests.post(N8N_ENDPOINT, json=payload)
            
            if response.status_code == 200:
                # Traitement de la réponse
                response_data = response.json()
                
                # Mise à jour de l'interface utilisateur avec le texte
                if 'text' in response_data:
                    root.after(0, lambda: text_widget.insert(tk.END, f"\n{response_data['text']}\n"))
                
                # Lecture de l'audio si présent
                if 'audio' in response_data:
                    audio_bytes = base64.b64decode(response_data['audio'])
                    await process_audio_chunk(audio_bytes)
                
                logging.info("Réponse traitée avec succès")
            else:
                error_message = f"Erreur API: {response.status_code} - {response.text}"
                logging.error(error_message)
                root.after(0, lambda: text_widget.insert(tk.END, f"\nERROR: {error_message}\n"))
            
            # Attente avant la prochaine itération
            logging.info(f"Attente de {interval} secondes avant la prochaine itération")
            await asyncio.sleep(interval)
            
        except Exception as e:
            logging.error(f"Une erreur est survenue: {e}")
            root.after(0, lambda e=e: text_widget.insert(tk.END, f"\nERROR: {str(e)}\n"))
            await asyncio.sleep(5)  # Attente avant nouvelle tentative

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CK3 AI Character with OpenAI Real-Time API",
        epilog="Before running, ensure you have:\n"
               "1. Installed dependencies: pip install -r requirements.txt\n"
               "2. Created .env file with OPENAI_API_KEY, XATA_API_KEY, and XATA_DATABASE_URL"
    )
    parser.add_argument("--interval", type=int, default=DEFAULT_SCREENSHOT_INTERVAL,
                        help=f"Screenshot interval in seconds (default: {DEFAULT_SCREENSHOT_INTERVAL})")
    args = parser.parse_args()
    
    try:
        # Configurer la gestion de la fermeture
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Lancer le client WebSocket dans un thread séparé
        api_thread = threading.Thread(target=lambda: asyncio.run(api_client(args.interval)))
        api_thread.daemon = True  # Marquer le thread comme daemon
        api_thread.start()
        
        # Lancer la boucle principale Tkinter
        root.mainloop()
    except KeyboardInterrupt:
        logging.info("Program terminated by user")
        on_closing()
    finally:
        if running:
            on_closing()

print("Pour exécuter ce script, utilisez la commande : python main.py")
