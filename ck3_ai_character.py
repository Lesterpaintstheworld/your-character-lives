import sys
import asyncio
import websockets
import pyautogui
import time
import pyttsx3
print("WARNING: This script is deprecated. Please use 'main.py' instead.", file=sys.stderr)
print("Run 'python main.py --help' for usage information.", file=sys.stderr)
sys.exit(1)
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

# Global variables
current_video_window = None
is_playing = True

# Configuration
DEFAULT_SCREENSHOT_INTERVAL = 30  # seconds
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "wss://api.openai.com/v1/audio/speech")  # URL à confirmer avec OpenAI
AUDIO_TIMEOUT = 30  # seconds

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_status(message):
    """Update status in UI"""
    # Since this is a deprecated file, just print to console
    print(message)

def take_screenshot():
    """Capture a screenshot, resize it, and return it as base64 string."""
    screenshot = pyautogui.screenshot()
    
    # Resize the image to reduce file size (adjust dimensions as needed)
    max_size = (1024, 576)  # Reduced size for faster processing
    screenshot.thumbnail(max_size, Image.LANCZOS)
    
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='JPEG', quality=85, optimize=True)  # Use JPEG for smaller file size
    return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

async def process_audio_chunk(audio_data: bytes):
    """Process and play audio data with improved error handling and fallback."""
    temp_file = 'temp_audio.mp3'
    fallback_file = 'fallback_audio.mp3'
    
    try:
        # Switch to talking video before playing
        if current_video_window:
            current_video_window.switch_to_talk_video()

        # Don't play if paused
        if not is_playing:
            return

        # Try primary playback method with pygame
        try:
            pygame.mixer.quit()  # Reset mixer
            pygame.mixer.init(frequency=16000)  # Initialize with correct frequency
            
            with open(temp_file, 'wb') as f:
                f.write(audio_data)
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to complete with timeout
            start_time = time.time()
            timeout = AUDIO_TIMEOUT  # Maximum wait time in seconds
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                if time.time() - start_time > timeout:
                    logging.warning("Audio playback timeout - forcing stop")
                    pygame.mixer.music.stop()
                    break
                
        except Exception as e:
            logging.error(f"Primary playback failed: {e}")
            
            # Fallback to pyttsx3
            try:
                logging.info("Attempting fallback playback with pyttsx3")
                engine = pyttsx3.init()
                engine.save_to_file(audio_data, fallback_file)
                engine.runAndWait()
                
                # Play the saved file
                pygame.mixer.quit()
                pygame.mixer.init()
                pygame.mixer.music.load(fallback_file)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                    
            except Exception as fallback_error:
                logging.error(f"Fallback playback failed: {fallback_error}")
                raise  # Re-raise if both methods fail
                
    except Exception as e:
        logging.error(f"Error playing audio: {e}")
        update_status(f"❌ Audio playback error: {str(e)}")
        
    finally:
        # Cleanup
        try:
            pygame.mixer.music.unload()
        except:
            pass
            
        try:
            pygame.mixer.quit()
        except:
            pass
            
        # Remove temporary files
        for file in [temp_file, fallback_file]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except Exception as e:
                    logging.warning(f"Failed to remove temp file {file}: {e}")

        # Switch back to idle video
        if current_video_window:
            current_video_window.switch_to_idle_video()

async def websocket_client(interval):
    while True:
        try:
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
                    except websockets.exceptions.ConnectionClosed:
                        logging.error("WebSocket connection closed. Attempting to reconnect...")
                        break
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            logging.info("Attempting to reconnect in 5 seconds...")
            await asyncio.sleep(5)

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
print("Pour exécuter ce script, utilisez la commande : python ck3_ai_character.py")
