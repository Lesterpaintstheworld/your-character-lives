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
import openai

# Configuration
DEFAULT_SCREENSHOT_INTERVAL = 30  # seconds
OPENAI_API_KEY = "your_openai_api_key_here"  # Remplacez par votre clé API OpenAI
WEBSOCKET_URL = "wss://api.openai.com/v1/audio/speech"  # URL à confirmer avec OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def take_screenshot():
    """Capture a screenshot, resize it, and return it as base64 string."""
    screenshot = pyautogui.screenshot()
    
    # Resize the image to reduce file size (adjust dimensions as needed)
    max_size = (2048, 768)
    screenshot.thumbnail(max_size, Image.LANCZOS)
    
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='PNG', optimize=True)
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

async def websocket_client(interval):
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        logging.info(f"Connected to WebSocket. Starting CK3 AI Character with {interval} second interval")
        
        while True:
            try:
                logging.info("Taking screenshot")
                screenshot_base64 = take_screenshot()
                
                # Prepare the message to send
                message = {
                    "type": "image",
                    "image": screenshot_base64,
                    "api_key": OPENAI_API_KEY
                }
                
                logging.info("Sending screenshot to API")
                await websocket.send(json.dumps(message))
                
                # Receive and process audio chunks
                while True:
                    try:
                        chunk = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        await process_audio_chunk(chunk)
                    except asyncio.TimeoutError:
                        break  # No more chunks, exit the inner loop
                
                await asyncio.sleep(interval)
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                await asyncio.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CK3 AI Character with OpenAI Real-Time Voice API")
    parser.add_argument("--interval", type=int, default=DEFAULT_SCREENSHOT_INTERVAL,
                        help=f"Screenshot interval in seconds (default: {DEFAULT_SCREENSHOT_INTERVAL})")
    args = parser.parse_args()
    
    try:
        asyncio.run(websocket_client(args.interval))
    except KeyboardInterrupt:
        logging.info("Program terminated by user")

# Ajout d'un message pour indiquer comment exécuter le script
print("Pour exécuter ce script, utilisez la commande : python main.py")
