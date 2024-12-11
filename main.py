import asyncio
import requests
import pyautogui
import io
import pyttsx3
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
import tkinter as tk
from tkinter import scrolledtext

running = True  # Global control variable

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speech rate (default is 200)
engine.setProperty('volume', 1.0)  # Volume between 0 and 1.0
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
REQUEST_TIMEOUT = 120  # Timeout in seconds for API requests
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
    """Capture a screenshot, resize it, and return it as binary data."""
    screenshot = pyautogui.screenshot()
    
    # Resize the image to reduce file size
    max_size = (1024, 576)  # Reduced size for faster processing
    screenshot.thumbnail(max_size, Image.LANCZOS)
    
    # Save as binary data
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
    return img_byte_arr.getvalue()  # Return binary data directly

import queue

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speech rate (default is 200)
engine.setProperty('volume', 1.0)  # Volume between 0 and 1.0

async def process_audio_chunk(response_data):
    """Process and play text using text-to-speech."""
    try:
        # Vérifier si response_data est déjà un dict ou doit être parsé
        if isinstance(response_data, bytes):
            response_json = json.loads(response_data.decode('utf-8'))
        elif isinstance(response_data, str):
            response_json = json.loads(response_data)
        else:
            response_json = response_data

        # Extraire le texte de différentes structures JSON possibles
        text = None
        if 'text' in response_json:
            text = response_json['text']
        elif 'choices' in response_json and len(response_json['choices']) > 0:
            text = response_json['choices'][0].get('text', '')
        elif isinstance(response_json, str):
            text = response_json

        if text:
            # Afficher le texte dans l'UI
            root.after(0, lambda: text_widget.insert(tk.END, f"\nAI: {text}\n"))
            # Synthèse vocale
            engine.say(text)
            engine.runAndWait()
        else:
            logging.error("Aucun texte trouvé dans la réponse")
            
    except Exception as e:
        logging.error(f"Erreur lors du traitement de la réponse: {e}")
        logging.error(f"Contenu de la réponse: {response_data}")

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


async def api_client(interval):
    global running
    while running:
        try:
            # Capture d'écran
            logging.info("Capture d'écran en cours")
            screenshot_data = take_screenshot()
            logging.info("Capture d'écran terminée")
            
            # Enregistrement audio
            logging.info("Enregistrement audio en cours")
            audio_data = record_audio(5)  # 5 secondes d'enregistrement
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            logging.info("Enregistrement audio terminé")
            
            # Préparation des données pour l'API
            files = {
                'data': ('screenshot.jpg', screenshot_data, 'image/jpeg'),
                'audio': ('audio.wav', audio_data, 'audio/wav'),
            }

            # Ajouter les instructions comme données de formulaire
            data = {
                'instructions': INVESTMENT_PROMPT
            }

            # Envoi de la requête à n8n
            logging.info("Envoi des données à n8n")
            
            try:
                response = requests.post(
                    N8N_ENDPOINT,
                    files=files,
                    data=data,
                    headers={'User-Agent': 'CK3-AI-Character/1.0'},
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()
                
                # Process the response as JSON containing text
                await process_audio_chunk(response.content)
                logging.info("Response processed successfully")
                
            except requests.exceptions.RequestException as e:
                logging.error(f"Erreur de requête: {e}")
                root.after(0, lambda e=e: text_widget.insert(tk.END, f"\nERROR: {str(e)}\n"))
            
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
