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
# Load environment variables
load_dotenv()

# Audio recording constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000  # 24kHz as required by the API

# Read system prompts
def read_prompt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

SYSTEM_PROMPT = read_prompt('prompts/system.md')
CHARACTER_PROMPT = read_prompt('prompts/character.md')

# Configuration
DEFAULT_SCREENSHOT_INTERVAL = 30  # seconds
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBSOCKET_URL = "wss://api.openai.com/v1/realtime"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Vérification de la clé API
if not OPENAI_API_KEY:
    logging.error("La clé API OpenAI n'est pas définie. Veuillez la configurer dans le fichier .env")
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

async def handle_server_event(event):
    """Handle server events."""
    event_type = event.get('type')
    if event_type == 'response.text.delta':
        logging.info(f"Received text delta: {event.get('delta', '')}")
    elif event_type == 'response.audio.delta':
        await process_audio_chunk(base64.b64decode(event.get('delta', '')))
    elif event_type == 'error':
        logging.error(f"Received error: {event.get('error', {})}")
    elif event_type == 'response.done':
        logging.info("Response completed")
    elif event_type == 'response.created':
        logging.info("Response started")
    elif event_type == 'response.function_call_arguments.delta':
        logging.info(f"Function call arguments delta: {event.get('delta', {})}")
    else:
        logging.info(f"Received event: {event_type}")

async def websocket_client(interval):
    while True:
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            }
            async with websockets.connect(
                f"{WEBSOCKET_URL}?model=gpt-4o-realtime-preview-2024-10-01",
                extra_headers=headers
            ) as websocket:
                logging.info(f"Connected to WebSocket. Starting CK3 AI Character with {interval} second interval")
    
                # Initialize the session
                await websocket.send(json.dumps({
                    "type": "session.create",
                    "session": {
                        "instructions": SYSTEM_PROMPT + "\n" + CHARACTER_PROMPT,
                        "modalities": ["text", "audio"],
                        "voice": "alloy"
                    }
                }))
                
                while True:
                    logging.info("Taking screenshot")
                    screenshot_base64 = take_screenshot()
                    
                    # Record audio
                    audio_data = record_audio(5)  # Record for 5 seconds
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    
                    # Send the screenshot description and audio
                    await websocket.send(json.stringify({
                        "type": "conversation.item.create",
                        "item": {
                            "type": "message",
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": "Describe the current game state based on this screenshot and respond to my audio input."
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
                    }))
    
                    # Request a response from the model
                    await websocket.send(json.stringify({
                        "type": "response.create",
                        "response": {
                            "modalities": ["text", "audio"]
                        }
                    }))
                    
                    # Process server events
                    async for message in websocket:
                        event = json.loads(message)
                        await handle_server_event(event)
                        if event.get('type') == 'done':
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
