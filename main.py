import asyncio
import logging
import argparse
import sys
import os
import time
import io
import wave
import threading
from pathlib import Path
from tkinter import messagebox, Canvas
import numpy as np

def initialize_audio():
    """Test audio setup and return True if successful"""
    try:
        input_device = get_input_device()
        logging.info(f"Audio input device found: {input_device}")
        return True
    except Exception as e:
        logging.error(f"Audio initialization failed: {e}")
        messagebox.showwarning(
            "Audio Setup Warning",
            "No microphone detected or audio error occurred. The application will continue but audio recording may not work.\n\n"
            f"Error: {str(e)}"
        )
        return False

# Global control variable
running = True
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import re
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
RATE = 16000  # Standard sample rate that's widely supported
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

def get_available_microphones():
    """Get list of available microphone devices"""
    p = pyaudio.PyAudio()
    mics = []
    try:
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:  # Only input devices
                mics.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'default_rate': int(device_info['defaultSampleRate'])
                })
    finally:
        p.terminate()
    return mics

def get_input_device():
    """Find and verify the input audio device with improved detection."""
    p = pyaudio.PyAudio()
    input_device = None
    
    try:
        # Log system default input device
        try:
            default_device_info = p.get_default_input_device_info()
            logging.info(f"System default input device: {default_device_info['name']} (index: {default_device_info['index']})")
        except Exception as e:
            logging.warning(f"Could not get default input device: {e}")

        # List all audio devices
        logging.info("\n=== Available Audio Devices ===")
        devices_info = []
        for i in range(p.get_device_count()):
            try:
                device_info = p.get_device_info_by_index(i)
                device_str = (f"Device {i}: {device_info['name']}\n"
                            f"  Max Input Channels: {device_info['maxInputChannels']}\n"
                            f"  Default Sample Rate: {device_info['defaultSampleRate']}\n"
                            f"  Is Default Input: {device_info.get('isDefaultInput', False)}")
                devices_info.append(device_str)
                logging.info(device_str)
                
                # Try to use this device if it has input channels
                if device_info['maxInputChannels'] > 0:
                    try:
                        # Test device with lower sample rate and smaller buffer
                        test_stream = p.open(
                            format=FORMAT,
                            channels=1,  # Try mono
                            rate=16000,  # Try lower sample rate
                            input=True,
                            input_device_index=i,
                            frames_per_buffer=512,  # Smaller buffer
                            start=False
                        )
                        test_stream.close()
                        input_device = i
                        logging.info(f"Successfully tested device {i}: {device_info['name']}")
                        
                        # If this is the default input device, prefer it
                        if device_info.get('isDefaultInput', False):
                            logging.info(f"Selected default input device: {device_info['name']}")
                            break
                            
                    except Exception as e:
                        logging.warning(f"Device {i} test failed: {e}")
                        continue
            except Exception as e:
                logging.warning(f"Error querying device {i}: {e}")
                continue
        
        if input_device is None:
            # Try to fall back to default input device
            try:
                default_index = p.get_default_input_device_info()['index']
                test_stream = p.open(
                    format=FORMAT,
                    channels=1,
                    rate=16000,
                    input=True,
                    input_device_index=default_index,
                    frames_per_buffer=512,
                    start=False
                )
                test_stream.close()
                input_device = default_index
                logging.info(f"Fallback to default input device successful")
            except Exception as e:
                logging.error(f"Fallback to default device failed: {e}")
                
        if input_device is None:
            logging.error("\nNo working microphone found. Available devices:\n" + "\n".join(devices_info))
            raise Exception("No working microphone or input device detected. Check your system audio settings and ensure a microphone is connected and enabled.")
            
        return input_device
        
    finally:
        p.terminate()

def record_audio(duration):
    """Record audio with VU meter updates"""
    update_status("🎤 Initializing audio...")
    
    p = None
    stream = None
    frames = []
    
    try:
        # Get selected mic index from combo box
        selected = mic_var.get()
        if not selected:
            raise Exception("No microphone selected")
            
        match = re.search(r'Device (\d+)', selected)
        if not match:
            raise Exception("Invalid microphone selection")
            
        input_device = int(match.group(1))
        p = pyaudio.PyAudio()
        
        try:
            # Create non-callback stream for recording
            # Before opening the stream, verify the device supports our sample rate
            device_info = p.get_device_info_by_index(input_device)
            supported_rate = int(device_info['defaultSampleRate'])
            if supported_rate != 16000:
                logging.warning(f"Device default sample rate ({supported_rate}) differs from requested rate (16000)")
                # Optionally adjust rate to match device
                # RATE = supported_rate
            
            try:
                stream = p.open(
                    format=FORMAT,
                    channels=1,
                    rate=16000,  # Make sure this matches the RATE constant
                    input=True,
                    input_device_index=input_device,
                    frames_per_buffer=1024
                )
            except ValueError as e:
                logging.error(f"Sample rate error: {e}")
                update_status(f"❌ Sample rate error: {e}")
                raise
            
            logging.info(f"Recording for {duration} seconds...")
            update_status("🎤 Recording...")
            
            # Calculate number of chunks to record
            chunks = int(16000 / 1024 * duration)
            
            for i in range(chunks):
                try:
                    data = stream.read(1024, exception_on_overflow=False)
                    frames.append(data)
                    
                    # Calculate and update VU meter
                    level = calculate_audio_level(data)
                    root.after(0, lambda l=level: vu_meter.set_level(l))
                    
                    # Update progress every second
                    if i % (16000 // 1024) == 0:
                        seconds = i // (16000 // 1024)
                        update_status(f"🎤 Recording... {seconds}/{duration}s")
                        
                except OSError as e:
                    logging.error(f"OSError during recording: {e}")
                    # Try to recover
                    time.sleep(0.1)
                    continue
                    
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    logging.error(f"Error closing stream: {e}")
            if p:
                try:
                    p.terminate()
                except Exception as e:
                    logging.error(f"Error terminating PyAudio: {e}")
                    
        update_status("✅ Recording complete")
        
        # Create WAV buffer
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(16000)
            wf.writeframes(b''.join(frames))
        
        return wav_buffer.getvalue()
        
    except Exception as e:
        logging.error(f"Failed to record audio: {e}")
        update_status(f"❌ Audio recording failed: {str(e)}")
        # Return empty audio rather than crashing
        empty_buffer = io.BytesIO()
        with wave.open(empty_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b'\x00' * 16000)  # 1 second of silence
        return empty_buffer.getvalue()

import tkinter as tk
from tkinter import scrolledtext

class VUMeter(Canvas):
    def __init__(self, master, width=200, height=20, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)
        self.configure(bg='black')
        self.width = width
        self.height = height
        self.segments = 20
        self.segment_width = (width - 4) / self.segments
        self.create_segments()
        self.level = 0

    def create_segments(self):
        """Create the meter segments"""
        self.segments_ids = []
        for i in range(self.segments):
            x1 = 2 + i * self.segment_width
            y1 = 2
            x2 = x1 + self.segment_width - 1
            y2 = self.height - 2
            
            # Color gradient from green to yellow to red
            if i < self.segments * 0.6:  # First 60% green
                color = '#00ff00'
            elif i < self.segments * 0.8:  # Next 20% yellow
                color = '#ffff00'
            else:  # Last 20% red
                color = '#ff0000'
                
            segment = self.create_rectangle(
                x1, y1, x2, y2,
                fill='dark gray', outline='black'
            )
            self.segments_ids.append((segment, color))

    def set_level(self, level):
        """Update the meter level (0.0 to 1.0)"""
        self.level = min(max(level, 0.0), 1.0)
        active_segments = int(self.level * self.segments)
        
        for i, (segment_id, color) in enumerate(self.segments_ids):
            if i < active_segments:
                self.itemconfig(segment_id, fill=color)
            else:
                self.itemconfig(segment_id, fill='dark gray')

def calculate_audio_level(audio_data):
    """Calculate audio level from raw audio data"""
    if isinstance(audio_data, bytes):
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
    else:
        audio_array = audio_data
        
    # Calculate RMS value
    rms = np.sqrt(np.mean(np.square(audio_array, dtype=np.float64)))
    
    # Convert to decibels and normalize
    if rms > 0:
        db = 20 * np.log10(rms / 32768.0)  # Normalize to 16-bit range
        # Normalize decibels to 0-1 range (-60dB to 0dB)
        normalized = (db + 60) / 60
        return max(0.0, min(1.0, normalized))
    return 0.0

def create_mic_selector():
    """Create microphone selection frame with VU meter"""
    mic_frame = tk.Frame(root)
    mic_frame.pack(fill='x', padx=5, pady=5)
    
    tk.Label(mic_frame, text="Select Microphone:").pack(side='left')
    
    # Create combobox for mic selection
    mic_var = tk.StringVar()
    mic_combo = ttk.Combobox(mic_frame, textvariable=mic_var, state='readonly')
    mic_combo.pack(side='left', fill='x', expand=True, padx=(5, 0))
    
    # Populate mic list
    mics = get_available_microphones()
    mic_options = [f"{m['name']} (Device {m['index']})" for m in mics]
    mic_combo['values'] = mic_options
    
    # Select default mic if available
    if mic_options:
        mic_combo.set(mic_options[0])
    
    # Add refresh button
    refresh_btn = tk.Button(mic_frame, text="🔄", command=lambda: refresh_mics(mic_combo))
    refresh_btn.pack(side='left', padx=(5, 0))
    
    # Add VU meter
    vu_frame = tk.Frame(root)
    vu_frame.pack(fill='x', padx=5, pady=2)
    tk.Label(vu_frame, text="Input Level:").pack(side='left')
    vu_meter = VUMeter(vu_frame, width=200, height=20)
    vu_meter.pack(side='left', fill='x', expand=True, padx=(5, 0))
    
    return mic_var, mic_combo, vu_meter

def refresh_mics(combo):
    """Refresh the microphone list"""
    current = combo.get()
    mics = get_available_microphones()
    mic_options = [f"{m['name']} (Device {m['index']})" for m in mics]
    combo['values'] = mic_options
    
    # Try to keep the same selection if possible
    if current in mic_options:
        combo.set(current)
    elif mic_options:
        combo.set(mic_options[0])

def update_mic_status(combo):
    """Update status text based on selected microphone"""
    selected = combo.get()
    if selected:
        try:
            match = re.search(r'Device (\d+)', selected)
            if match:
                index = int(match.group(1))
                p = pyaudio.PyAudio()
                device_info = p.get_device_info_by_index(index)
                p.terminate()
                update_status(f"Selected microphone: {device_info['name']}")
        except Exception as e:
            update_status(f"Error checking microphone: {str(e)}")
    else:
        update_status("No microphone selected")

# Create main window
root = tk.Tk()
root.title("CK3 AI Character Response")

# Create main controls frame
controls_frame = tk.Frame(root)
controls_frame.pack(fill='x', padx=5, pady=5)

# Add microphone selector and VU meter
mic_var, mic_combo, vu_meter = create_mic_selector()
mic_combo.bind('<<ComboboxSelected>>', lambda e: update_mic_status(mic_combo))

# Create text widget
text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
text_widget.pack(expand=True, fill='both', padx=5, pady=5)


def on_closing():
    """Handle application shutdown."""
    global running, vu_meter
    running = False
    # Reset VU meter
    vu_meter.set_level(0.0)
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
    
    # Initialize logging first
    logging.info("Starting CK3 AI Assistant...")
    
    # Initialize UI
    try:
        logging.info("Initializing UI...")
        root.protocol("WM_DELETE_WINDOW", on_closing)
        text_widget.insert(tk.END, "Initializing CK3 AI Assistant...\n")
        root.update()
        
        # Test audio but don't exit if it fails
        audio_ok = initialize_audio()
        if audio_ok:
            text_widget.insert(tk.END, "Audio initialization successful\n")
        else:
            text_widget.insert(tk.END, "Audio initialization failed - continuing without audio\n")
        root.update()
        
        logging.info("Starting API client thread...")
        api_thread = threading.Thread(target=lambda: asyncio.run(api_client(args.interval)))
        api_thread.daemon = True
        api_thread.start()
        
        logging.info("Starting main UI loop...")
        text_widget.insert(tk.END, "Ready! Waiting for game interaction...\n")
        root.update()
        
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
