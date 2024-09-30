import time
import requests
import pyautogui
import io
import pygame
import logging
import argparse
from PIL import Image

# Configuration
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
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None

def play_audio(audio_data):
    """Play the audio from binary data."""
    try:
        logging.info(f"Received audio data of size: {len(audio_data)} bytes")
        if len(audio_data) < 100:  # Ajustez cette valeur selon vos besoins
            logging.warning("Audio data seems too small, might be invalid")
            return

        pygame.mixer.init()
        sound = pygame.mixer.Sound(buffer=audio_data)
        duration = sound.get_length()
        
        if duration < 0.1:  # Ajustez cette valeur selon vos besoins
            logging.warning(f"Audio duration ({duration} seconds) seems too short, might be invalid")
            return

        logging.info(f"Playing audio of duration: {duration} seconds")
        sound.play()
        pygame.time.wait(int(duration * 1000))
    except pygame.error as e:
        logging.error(f"Failed to play audio: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while playing audio: {e}")

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
