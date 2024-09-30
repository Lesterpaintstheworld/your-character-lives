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
API_ENDPOINT = "https://nlr.app.n8n.cloud/webhook-test/ycl-enpoint"

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
    """Send the screenshot to the API and return the response."""
    files = {'image': ('screenshot.png', screenshot_bytes, 'image/png')}
    try:
        response = requests.post(API_ENDPOINT, files=files, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None

def play_audio(audio_url):
    """Play the audio file from the given URL."""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(audio_url)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except pygame.error as e:
        logging.error(f"Failed to play audio: {e}")

def main(interval):
    logging.info(f"Starting CK3 AI Character POC with {interval} second interval")
    while True:
        try:
            logging.info("Taking screenshot")
            screenshot_bytes = take_screenshot()
            
            logging.info("Sending screenshot to API")
            api_response = send_screenshot_to_api(screenshot_bytes)
            
            if api_response and 'audio_url' in api_response:
                logging.info("Playing audio response")
                play_audio(api_response['audio_url'])
            else:
                logging.warning("No valid audio URL received from API")
            
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
