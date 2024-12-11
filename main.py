import asyncio
import requests
import pyautogui
import io
import pyttsx3
import pygame
import os
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
    """Process and play audio data."""
    try:
        # Sauvegarder temporairement l'audio
        temp_file = 'temp_audio.mp3'
        with open(temp_file, 'wb') as f:
            if isinstance(response_data, bytes):
                f.write(response_data)
            else:
                f.write(response_data.encode())
        
        # Initialiser pygame pour la lecture audio
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        # Attendre la fin de la lecture
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        
        # Nettoyer
        pygame.mixer.music.unload()
        os.remove(temp_file)
            
    except Exception as e:
        logging.error(f"Erreur lors du traitement de l'audio: {e}")
        if isinstance(response_data, bytes):
            logging.error(f"Taille des données reçues: {len(response_data)} bytes")
        else:
            logging.error(f"Type de données reçues: {type(response_data)}")

def update_status(message):
    """Update status in UI"""
    root.after(0, lambda: text_widget.insert(tk.END, f"\n{message}\n"))
    root.after(0, text_widget.see, tk.END)

def record_audio(duration):
    """Record audio from the microphone for a specified duration and return raw PCM data."""
    update_status("🎤 Enregistrement en cours...")
    p = pyaudio.PyAudio()
    
    # Ouvrir le flux avec les paramètres requis par l'API (24kHz, 16-bit, 1 canal)
    stream = p.open(format=FORMAT,
                   channels=CHANNELS,
                   rate=RATE,
                   input=True,
                   frames_per_buffer=CHUNK)

    logging.info(f"Recording for {duration} seconds...")
    frames = []

    try:
        # Enregistrement
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        
        logging.info("Recording finished")
        
        # Créer un buffer temporaire pour le WAV
        wav_buffer = io.BytesIO()
        
        # Créer un fichier WAV en mémoire avec les bons headers
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        # Récupérer les données WAV complètes
        wav_data = wav_buffer.getvalue()
        
    finally:
        # Nettoyage
        stream.stop_stream()
        stream.close()
        p.terminate()

    update_status("✅ Enregistrement terminé")
    return wav_data

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
    
    # Faire le premier enregistrement audio avant de commencer la boucle
    logging.info("Starting initial 15-second recording...")
    previous_audio = record_audio(15)  # Premier enregistrement de 15 secondes
    logging.info("Initial recording completed")
    
    while running:
        try:
            # Capture d'écran
            logging.info("Capture d'écran en cours")
            screenshot_data = take_screenshot()
            logging.info("Capture d'écran terminée")
            
            # Préparation des données pour l'API
            files = {
                'data': ('screenshot.jpg', screenshot_data, 'image/jpeg'),
                'audio': ('audio.wav', previous_audio, 'audio/wav')  # On aura toujours de l'audio
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
                
                # Jouer l'audio reçu
                await process_audio_chunk(response.content)
                logging.info("Audio response played")
                
                # Enregistrer l'audio pour la prochaine requête
                logging.info("Starting 15-second recording...")
                previous_audio = record_audio(15)  # 15 secondes d'enregistrement
                logging.info("Recording completed")
                
            except requests.exceptions.RequestException as e:
                logging.error(f"Erreur de requête: {e}")
                root.after(0, lambda e=e: text_widget.insert(tk.END, f"\nERROR: {str(e)}\n"))
                await asyncio.sleep(5)  # Courte pause avant de réessayer
                continue
            
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
