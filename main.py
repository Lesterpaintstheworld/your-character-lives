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

# Load environment variables
load_dotenv()

# Configuration
DEFAULT_SCREENSHOT_INTERVAL = 30  # seconds
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBSOCKET_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"

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

async def handle_server_event(event):
    """Handle server events."""
    event_type = event.get('type')
    if event_type == 'text.content':
        logging.info(f"Received text content: {event.get('text', '')}")
    elif event_type == 'audio.content':
        await process_audio_chunk(base64.b64decode(event.get('audio', '')))
    elif event_type == 'error':
        logging.error(f"Received error: {event.get('message', '')}")
    # Add more event handlers as needed

async def websocket_client(interval):
    while True:
        try:
            async with websockets.connect(
                WEBSOCKET_URL,
                extra_headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "OpenAI-Beta": "realtime=v1"
                }
            ) as websocket:
                logging.info(f"Connected to WebSocket. Starting CK3 AI Character with {interval} second interval")
                
                # Initialize the session
                await websocket.send(json.dumps({
                    "type": "session.create",
                    "session": {
                        "default_response": {
                            "modalities": ["text", "audio"],
                            "instructions": "You are an AI character in Crusader Kings 3. Analyze the game screenshot and provide commentary or advice based on what you see."
                        }
                    }
                }))
                
                while True:
                    logging.info("Taking screenshot")
                    screenshot_base64 = take_screenshot()
                    
                    # Send the screenshot
                    await websocket.send(json.dumps({
                        "type": "conversation.append",
                        "conversation": {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "image",
                                            "image": screenshot_base64
                                        }
                                    ]
                                }
                            ]
                        }
                    }))
                    
                    # Create a new response
                    await websocket.send(json.dumps({
                        "type": "response.create",
                        "response": {
                            "modalities": ["text", "audio"]
                        }
                    }))
                    
                    # Process server events
                    while True:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                            event = json.loads(message)
                            await handle_server_event(event)
                            if event.get('type') == 'response.end':
                                break
                        except asyncio.TimeoutError:
                            break
                    
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
        asyncio.run(websocket_client(args.interval))
    except KeyboardInterrupt:
        logging.info("Program terminated by user")

print("Pour exécuter ce script, utilisez la commande : python main.py")
