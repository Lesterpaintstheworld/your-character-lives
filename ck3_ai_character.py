import time
import requests
import pyautogui
import io
import pygame
import logging
import argparse
from PIL import Image
import tempfile
import os
import subprocess

# Configuration
# Chemin vers FFmpeg (à ajuster selon votre installation)
FFMPEG_PATH = r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"
# Chemin vers opusdec (à ajuster selon votre installation)
OPUSDEC_PATH = r"C:\Program Files\opus-tools\opusdec.exe"
DEFAULT_SCREENSHOT_INTERVAL = 30  # seconds
API_ENDPOINT = "https://nlr.app.n8n.cloud/webhook/ycl-enpoint"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def take_screenshot():
    """Capture a screenshot, resize it, and return it as bytes."""
    screenshot = pyautogui.screenshot()
    
    # Resize the image to reduce file size (adjust dimensions as needed)
    max_size = (1280, 882)
    screenshot.thumbnail(max_size, Image.LANCZOS)
    
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='PNG', optimize=True)
    return img_byte_arr.getvalue()

def send_screenshot_to_api(screenshot_bytes):
    """Send the screenshot to the API and return the audio data."""
    files = {'image': ('screenshot.png', screenshot_bytes, 'image/png')}
    try:
        response = requests.post(API_ENDPOINT, files=files, timeout=30)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')
        logging.info(f"API response content type: {content_type}")
        logging.info(f"API response size: {len(response.content)} bytes")
        
        # Vérifier si le contenu est un fichier audio OPUS
        if content_type == 'audio/opus':
            return response.content
        else:
            logging.error(f"Unexpected content type: {content_type}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None

def play_audio(data):
    """Play the audio from binary OPUS data."""
    try:
        logging.info(f"Received audio data of size: {len(data)} bytes")
        if len(data) < 1000:
            logging.warning("Audio data seems too small, might be invalid")
            return

        # Créer un fichier temporaire pour stocker l'audio OPUS
        with tempfile.NamedTemporaryFile(delete=False, suffix='.opus') as temp_opus:
            temp_opus.write(data)
            temp_opus_path = temp_opus.name

        # Convertir OPUS en WAV en utilisant opusdec
        temp_wav_path = temp_opus_path.replace('.opus', '.wav')
        opusdec_command = f'"{OPUSDEC_PATH}" "{temp_opus_path}" "{temp_wav_path}"'
        
        try:
            subprocess.run(opusdec_command, check=True, shell=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logging.error(f"Opus decoding failed: {e.stderr.decode()}")
            return

        # Jouer le fichier WAV
        pygame.mixer.init()
        try:
            sound = pygame.mixer.Sound(temp_wav_path)
            duration = sound.get_length()
            
            if duration < 0.5:
                logging.warning(f"Audio duration ({duration} seconds) seems too short, might be invalid")
                return

            logging.info(f"Playing audio of duration: {duration} seconds")
            sound.play()
            pygame.time.wait(int(duration * 1000))
        except pygame.error as pe:
            logging.error(f"Failed to load or play audio: {pe}")
        finally:
            # Nettoyer les fichiers temporaires
            os.remove(temp_opus_path)
            os.remove(temp_wav_path)

    except Exception as e:
        logging.error(f"Unexpected error while processing or playing audio: {e}")

def main(interval):
    logging.info(f"Starting CK3 AI Character POC with {interval} second interval")
    while True:
        try:
            logging.info("Taking screenshot")
            screenshot_bytes = take_screenshot()
            
            logging.info("Sending screenshot to API")
            api_response = send_screenshot_to_api(screenshot_bytes)
            
            if api_response:
                logging.info("Playing audio response")
                play_audio(api_response)
            else:
                logging.warning("No audio data received from API")
            
            time.sleep(interval)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CK3 AI Character POC")
    parser.add_argument("--interval", type=int, default=DEFAULT_SCREENSHOT_INTERVAL,
                        help=f"Screenshot interval in seconds (default: {DEFAULT_SCREENSHOT_INTERVAL})")
    args = parser.parse_args()
    
    try:
        main(args.interval)
    except KeyboardInterrupt:
        logging.info("Program terminated by user")

# Ajout d'un message pour indiquer comment exécuter le script
print("Pour exécuter ce script, utilisez la commande : python ck3_ai_character.py")
