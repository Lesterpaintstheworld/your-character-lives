import asyncio
import logging
import argparse
import sys
import os
import io
import wave
import threading
from pathlib import Path

# Global control variable
running = True
import tkinter as tk
from tkinter import scrolledtext, messagebox
from PIL import Image
import pyautogui
import requests
import pyaudio
import pygame
import pyttsx3
from dotenv import load_dotenv

from config import Config
from audio_manager import AudioManager
from log_manager import LogManager
from event_manager import EventManager
from thread_manager import ThreadManager
from constants import AudioConstants, NetworkConstants, UIConstants

# Audio constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000
DEFAULT_SCREENSHOT_INTERVAL = 30
REQUEST_TIMEOUT = 120
API_ENDPOINT = "https://nlr.app.n8n.cloud/webhook/ycl-enpoint"

# Load environment variables and initialize configuration
load_dotenv()
config = Config()
log_manager = LogManager()
logger = log_manager.get_logger(__name__)



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

async def process_audio_chunk(audio_data: bytes):
    """Process and play audio data."""
    try:
        # Save and play audio
        temp_file = 'temp_audio.mp3'
        with open(temp_file, 'wb') as f:
            f.write(audio_data)
        
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
            
        pygame.mixer.music.unload()
        os.remove(temp_file)
        
    except Exception as e:
        logging.error(f"Error playing audio: {e}")

def update_status(message):
    """Update status in UI"""
    root.after(0, lambda: text_widget.insert(tk.END, f"\n{message}\n"))
    root.after(0, text_widget.see, tk.END)

def mix_audio(mic_data, desktop_data):
    """Mix microphone and desktop audio data."""
    import numpy as np
    mic_array = np.frombuffer(mic_data, dtype=np.int16)
    desktop_array = np.frombuffer(desktop_data, dtype=np.int16)
    
    # Mix the two sources (70% mic, 30% desktop)
    mixed = (mic_array * 0.7 + desktop_array * 0.3).astype(np.int16)
    return mixed.tobytes()

def get_input_device():
    """Find and verify the input audio device."""
    p = pyaudio.PyAudio()
    input_device = None
    
    try:
        # Liste tous les périphériques audio
        logging.info("Scanning audio devices...")
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            logging.info(f"Device {i}: {device_info['name']}, inputs: {device_info['maxInputChannels']}")
            
            # Cherche un périphérique d'entrée valide
            if device_info['maxInputChannels'] > 0:
                input_device = i
                logging.info(f"Selected input device: {device_info['name']}")
                break
                
        if input_device is None:
            logging.error("No input device found!")
            raise Exception("No microphone or input device detected")
            
        return input_device
        
    finally:
        p.terminate()

def record_audio(duration):
    """Record audio with improved error handling."""
    update_status("🎤 Initializing audio...")
    
    try:
        # Vérifier le périphérique d'entrée
        input_device = get_input_device()
        
        p = pyaudio.PyAudio()
        
        # Ouvrir le flux audio avec le périphérique sélectionné
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       input_device_index=input_device,
                       frames_per_buffer=CHUNK)

        # Find loopback device index
        loopback_index = None
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if 'Stereo Mix' in device_info['name'] or 'Loopback' in device_info['name']:
                loopback_index = i
                break
        
        # Open desktop audio stream if available
        if loopback_index is not None:
            desktop_stream = p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  input_device_index=loopback_index,
                                  frames_per_buffer=CHUNK)
            logging.info("Desktop audio capture enabled")
        else:
            logging.warning("Loopback device not found. Recording microphone only.")
            desktop_stream = None

        logging.info(f"Recording for {duration} seconds...")
        frames = []

        update_status("🎤 Recording...")
        frames = []
        
        for i in range(0, int(RATE / CHUNK * duration)):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except Exception as e:
                logging.error(f"Error during recording: {e}")
                update_status("❌ Recording error")
                raise
        
        # Créer le buffer WAV
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        update_status("✅ Recording complete")
        return wav_buffer.getvalue()
        
    except Exception as e:
        logging.error(f"Failed to record audio: {e}")
        update_status(f"❌ Audio recording failed: {str(e)}")
        # Retourner un fichier audio vide plutôt que de planter
        empty_buffer = io.BytesIO()
        with wave.open(empty_buffer, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(RATE)
            wf.writeframes(b'\x00' * RATE)  # 1 seconde de silence
        return empty_buffer.getvalue()
        
    finally:
        try:
            stream.stop_stream()
            stream.close()
        except:
            pass
        try:
            p.terminate()
        except:
            pass

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
    sys.exit(0)


async def api_client(interval):
    global running
    
    while running:
        try:
            update_status("Starting new recording cycle...")
            
            # Capture d'écran
            logging.info("Capture d'écran en cours")
            screenshot_data = take_screenshot()
            logging.info("Capture d'écran terminée")
            
            # Enregistrement audio
            logging.info("Starting 15-second recording...")
            update_status("Recording audio...")
            audio_data = record_audio(15)
            logging.info("Recording completed")

            # Préparation des données pour n8n
            files = {
                'data': ('screenshot.jpg', screenshot_data, 'image/jpeg'),
                'audio': ('audio.wav', audio_data, 'audio/wav')
            }

            # Envoi à n8n
            logging.info("Envoi des données à n8n")
            response = requests.post(
                "https://nlr.app.n8n.cloud/webhook/ycl-enpoint",
                files=files,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            # Traiter la réponse audio
            await process_audio_chunk(response.content)
            logging.info("Audio response played")

            # Attendre l'intervalle configuré
            await asyncio.sleep(interval)
            
        except Exception as e:
            logging.error(f"Une erreur est survenue: {e}")
            root.after(0, lambda e=e: text_widget.insert(tk.END, f"\nERROR: {str(e)}\n"))
            await asyncio.sleep(5)  # Attente avant nouvelle tentative

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CK3 AI Character with OpenAI Real-Time API",
        epilog="Before running, ensure you have:\n"
               "1. Installed dependencies: pip install -r requirements.txt"
    )
    parser.add_argument("--interval", type=int, default=DEFAULT_SCREENSHOT_INTERVAL,
                        help=f"Screenshot interval in seconds (default: {DEFAULT_SCREENSHOT_INTERVAL})")
    args = parser.parse_args()
    
    # Vérifier l'audio au démarrage
    try:
        input_device = get_input_device()
        logging.info(f"Audio input device found: {input_device}")
    except Exception as e:
        logging.error(f"Audio initialization failed: {e}")
        import tkinter.messagebox as messagebox
        messagebox.showwarning(
            "Audio Setup Warning",
            "No microphone detected. Please connect a microphone and restart the application."
        )
        sys.exit(1)
    
    # Add startup logging
    logging.info("Starting CK3 AI Assistant...")
    
    # Initialize UI first
    try:
        logging.info("Initializing UI...")
        # Configurer la gestion de la fermeture
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Add initial status message to UI
        text_widget.insert(tk.END, "Initializing CK3 AI Assistant...\n")
        root.update()
        
        logging.info("Starting API client thread...")
        # Lancer le client WebSocket dans un thread séparé
        api_thread = threading.Thread(target=lambda: asyncio.run(api_client(args.interval)))
        api_thread.daemon = True  # Marquer le thread comme daemon
        api_thread.start()
        
        logging.info("Starting main UI loop...")
        text_widget.insert(tk.END, "Ready! Waiting for game interaction...\n")
        root.update()
        
        # Lancer la boucle principale Tkinter
        root.mainloop()
    except Exception as e:
        logging.error(f"Startup error: {str(e)}")
        # Show error in a simple messagebox since UI might not be ready
        import tkinter.messagebox as messagebox
        messagebox.showerror("Error", f"Failed to start: {str(e)}\nCheck the logs for details.")
        sys.exit(1)
    except KeyboardInterrupt:
        logging.info("Program terminated by user")
        on_closing()
    finally:
        if running:
            on_closing()

print("Pour exécuter ce script, utilisez la commande : python main.py")
