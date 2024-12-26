import asyncio
import logging
import argparse
import sys
import os
import time
import io
import wave
import threading
import tempfile
import cv2
import numpy as np
from scipy import signal
from pydub import AudioSegment
from video_window import DraggableVideoWindow
from device_manager import DeviceManager

# Global reference to current video window
current_video_window = None

# Add video-specific debug logging
video_logger = logging.getLogger('video')
video_logger.setLevel(logging.DEBUG)

def init_video():
    """Initialize video subsystem with detailed logging"""
    video_logger.info("Starting video initialization")
    try:
        # Test OpenCV installation
        video_logger.debug("Testing OpenCV installation")
        cv2_version = cv2.__version__
        video_logger.info(f"OpenCV version: {cv2_version}")

        # Test PIL/Pillow installation
        video_logger.debug("Testing PIL installation")
        pil_version = Image.__version__
        video_logger.info(f"PIL version: {pil_version}")

        # Test basic video operations
        video_logger.debug("Testing video operations")
        test_frame = np.zeros((240, 320, 3), dtype=np.uint8)
        test_rgb = cv2.cvtColor(test_frame, cv2.COLOR_BGR2RGB)
        test_image = Image.fromarray(test_rgb)
        video_logger.info("Basic video operations successful")

        return True
    except Exception as e:
        video_logger.error(f"Video initialization failed: {e}", exc_info=True)
        return False
from pathlib import Path
from tkinter import messagebox, Canvas
import numpy as np

def initialize_audio():
    """Initialize audio system with better error handling"""
    try:
        # Test pygame mixer
        pygame.mixer.quit()
        pygame.mixer.init(frequency=AUDIO_FREQUENCY)
        pygame.mixer.quit()
        
        # Test pyttsx3
        engine = pyttsx3.init()
        engine.getProperty('voices')
        engine.stop()
        
        # Initialize input device
        input_device = get_input_device()
        logging.info(f"Audio input device found: {input_device}")
        return True
        
    except Exception as e:
        logging.error(f"Audio initialization failed: {e}")
        messagebox.showwarning(
            "Audio Setup Warning",
            "Audio initialization error occurred. The application will continue but audio may not work properly.\n\n"
            f"Error: {str(e)}\n\n"
            "Try restarting the application or checking your audio devices."
        )
        return False

# Global control variables
running = True
is_playing = True
is_recording = False
auto_recording = False
auto_recording_interval = 50  # seconds
interval_spinbox = None  # Will be set when UI is created
auto_recording_task = None
output_var = None  # Will store output device selection
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
AUDIO_TIMEOUT = 120  # seconds
AUDIO_FREQUENCY = 16000
DEFAULT_SCREENSHOT_INTERVAL = 30
REQUEST_TIMEOUT = 120
API_ENDPOINT = "https://nlr.app.n8n.cloud/webhook/ycl-enpoint"

# Load environment variables and initialize configuration
load_dotenv()
config = Config()
log_manager = LogManager()
logger = log_manager.get_logger(__name__)



def collect_text_files_content():
    """Collect content from all .md and .txt files in current directory and subdirectories."""
    try:
        content = []
        
        # Get execution directory (where the program is run from)
        base_dir = os.getcwd()
        
        logging.info("=== Path Debug Information ===")
        logging.info(f"Current working directory (execution): {base_dir}")
        
        # List contents of base directory for debugging
        try:
            files = os.listdir(base_dir)
            logging.info(f"Contents of base directory:")
            for f in files:
                full_path = os.path.join(base_dir, f)
                if os.path.isfile(full_path):
                    logging.info(f"  File: {f}")
                elif os.path.isdir(full_path):
                    logging.info(f"  Dir:  {f}")
        except Exception as e:
            logging.error(f"Error listing directory contents: {str(e)}")

        content.append(f"=== Document Scan - {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        
        total_files = 0
        
        # Walk through directory tree
        for root, dirs, files in os.walk(base_dir):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if not d.startswith(('.', '__pycache__', 'build', 'dist'))]
            
            logging.debug(f"Scanning directory: {root}")
            logging.debug(f"Found files: {files}")
            
            for file in files:
                # Case-insensitive extension check
                if file.lower().endswith(('.md', '.txt')):
                    full_path = os.path.join(root, file)
                    try:
                        rel_path = os.path.relpath(full_path, base_dir)
                        logging.info(f"Processing file: {rel_path}")
                        
                        with open(full_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                            content.append("\n" + "="*50)
                            content.append(f"FILE: {rel_path}")
                            content.append("="*50 + "\n")
                            content.append(file_content)
                            total_files += 1
                            
                    except Exception as e:
                        logging.error(f"Error reading file {full_path}: {str(e)}")
                        continue

        logging.info(f"Total files found: {total_files}")
        
        content.append("\n" + "="*50)
        content.append(f"End of document scan - {total_files} files processed")
        content.append("="*50)
        
        result = "\n".join(content)
        logging.info(f"Text content collected: {len(result)} bytes")
        
        return result
        
    except Exception as e:
        logging.error(f"Error in collect_text_files_content: {str(e)}")
        return f"Error collecting text files: {str(e)}"

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
    """Process and play audio data using PyAudio directly."""
    temp_path = None
    p = None
    stream = None
    
    try:
        # Save audio data to temporary file with .mp3 extension
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(audio_data)
            temp_file.flush()
            
        # Get selected output device name
        selected = output_var.get() if output_var else None
        device_index = None
        
        # Don't play if paused
        if not is_playing:
            return

        # Switch to talking video before playing
        if current_video_window:
            current_video_window.switch_to_talk_video()
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        try:
            # First try to find selected device
            if selected:
                device_name = re.match(r'^([^(]+)', selected).group(1).strip()
                logging.info(f"Looking for selected device: {device_name}")
                
                for i in range(p.get_device_count()):
                    info = p.get_device_info_by_index(i)
                    if (device_name.lower() in info['name'].lower() and 
                        info['maxOutputChannels'] > 0):
                        device_index = i
                        logging.info(f"Found selected device: {info['name']} (index: {i})")
                        break
            
            # If no device found, use default output device
            if device_index is None:
                info = p.get_default_output_device_info()
                device_index = info['index']
                logging.info(f"Using default output device: {info['name']} (index: {device_index})")

            # Load and convert audio using pydub
            audio = AudioSegment.from_mp3(temp_path)
            
            # Convert to standard format (16-bit PCM, 24000Hz, mono)
            audio = audio.set_frame_rate(24000)
            audio = audio.set_channels(1)
            audio = audio.set_sample_width(2)  # 16-bit
            
            # Get audio data as raw PCM
            raw_data = audio.raw_data
            
            # Log audio properties
            logging.info(f"Audio properties: {audio.frame_rate}Hz, "
                        f"{audio.channels} channels, "
                        f"{audio.sample_width * 8}bit")
            
            # Open stream with matching parameters
            stream = p.open(format=pyaudio.paInt16,  # 16-bit
                          channels=1,                # mono
                          rate=24000,               # 24kHz
                          output=True,
                          output_device_index=device_index,
                          frames_per_buffer=1024)
            
            # Play audio in chunks with progress tracking
            chunk_size = 1024 * 2  # 1024 16-bit samples = 2048 bytes
            offset = 0
            start_time = time.time()
            last_progress_time = start_time
            
            while offset < len(raw_data):
                current_time = time.time()
                
                # Only timeout if stuck (no progress for 5 seconds)
                if current_time - last_progress_time > 5:
                    logging.warning("Audio playback stuck - no progress for 5 seconds")
                    break
                    
                # Get next chunk
                chunk = raw_data[offset:offset + chunk_size]
                if not chunk:
                    break
                    
                # Write to stream
                stream.write(chunk)
                offset += chunk_size
                last_progress_time = current_time  # Update progress time
                
                # Allow other tasks to run
                await asyncio.sleep(0.001)
                
                # Log progress for very long audio
                if current_time - start_time > 30:  # Log after 30 seconds
                    logging.info(f"Long audio playback: {(offset/len(raw_data))*100:.1f}% complete")
                    
            logging.info(f"Audio playback completed in {time.time() - start_time:.1f} seconds")
                
        except Exception as e:
            logging.error(f"Error during playback: {e}")
            raise
            
    except Exception as e:
        logging.error(f"Error playing audio: {e}")
        update_status(f"❌ Audio playback error: {str(e)}")
        
    finally:
        # Cleanup
        if stream is not None:
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass
                
        if p is not None:
            try:
                p.terminate()
            except:
                pass
                
        # Remove temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logging.warning(f"Failed to remove temp file {temp_path}: {e}")

        # Switch back to idle video
        if current_video_window:
            current_video_window.switch_to_idle_video()

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

def validate_output_device(device_index):
    """Validate if a device index is currently valid and working"""
    try:
        p = pyaudio.PyAudio()
        try:
            # Check if index exists
            device_info = p.get_device_info_by_index(device_index)
            
            # Verify it's an output device
            if device_info['maxOutputChannels'] == 0:
                return False
                
            # Try to open a test stream
            test_stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                output=True,
                output_device_index=device_index,
                frames_per_buffer=1024,
                start=False
            )
            test_stream.close()
            return True
            
        except Exception as e:
            logging.debug(f"Device validation failed for index {device_index}: {e}")
            return False
            
        finally:
            p.terminate()
            
    except Exception:
        return False

def get_available_outputs():
    """Get list of available and working output devices with improved filtering"""
    p = pyaudio.PyAudio()
    outputs = []
    logging.info("Scanning for working audio output devices...")
    
    try:
        # First try to get default output device
        try:
            default_info = p.get_default_output_device_info()
            logging.info(f"Default output device: {default_info['name']}")
            
            # Only add if it's actually an output device
            if default_info['maxOutputChannels'] > 0:
                # Test default device with lower buffer size and rate
                test_stream = p.open(
                    format=FORMAT,
                    channels=1,
                    rate=16000,
                    output=True,
                    output_device_index=default_info['index'],
                    frames_per_buffer=512,  # Smaller buffer size
                    start=False
                )
                test_stream.close()
                outputs.append({
                    'index': default_info['index'],
                    'name': f"{default_info['name']} (Default)",
                    'channels': default_info['maxOutputChannels'],
                    'default_rate': int(default_info['defaultSampleRate'])
                })
                logging.info("Default output device working")
        except Exception as e:
            logging.warning(f"Default output device test failed: {e}")

        # Then scan other devices
        for i in range(p.get_device_count()):
            try:
                device_info = p.get_device_info_by_index(i)
                
                # Skip if:
                # - not an output device
                # - already added as default
                # - has 0 output channels
                # - is a known problematic device
                if (device_info['maxOutputChannels'] == 0 or 
                    any(o['index'] == i for o in outputs) or
                    device_info.get('isLoopbackDevice', False)):
                    continue
                
                # Skip if device name contains certain keywords
                skip_keywords = ['mapper', 'dummy', 'null', 'loop', 'réseau']
                if any(keyword.lower() in device_info['name'].lower() for keyword in skip_keywords):
                    continue

                # Test if device actually works with minimal configuration
                try:
                    test_stream = p.open(
                        format=FORMAT,
                        channels=1,
                        rate=16000,
                        output=True,
                        output_device_index=i,
                        frames_per_buffer=512,  # Smaller buffer
                        start=False
                    )
                    test_stream.close()
                    
                    outputs.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxOutputChannels'],
                        'default_rate': int(device_info['defaultSampleRate'])
                    })
                    logging.info(f"Found working output device: {device_info['name']}")
                    
                except Exception as e:
                    logging.debug(f"Device {i} test failed: {e}")
                    continue
                    
            except Exception as e:
                logging.debug(f"Error querying device {i}: {e}")
                continue
                
    finally:
        p.terminate()
        
    if not outputs:
        logging.warning("No working output devices found!")
        # Try to find any working output device as last resort
        try:
            for i in range(p.get_device_count()):
                try:
                    device_info = p.get_device_info_by_index(i)
                    if device_info['maxOutputChannels'] > 0:
                        outputs.append({
                            'index': i,
                            'name': f"{device_info['name']} (Fallback)",
                            'channels': device_info['maxOutputChannels'],
                            'default_rate': int(device_info['defaultSampleRate'])
                        })
                        logging.info(f"Added fallback output device: {device_info['name']}")
                        break
                except:
                    continue
        except:
            pass
    
    logging.info(f"Found {len(outputs)} working output device(s)")
    return outputs

def get_available_microphones():
    """Get list of available and working microphone devices"""
    p = pyaudio.PyAudio()
    mics = []
    logging.info("Scanning for working audio input devices...")
    
    try:
        # First try to get default input device
        try:
            default_info = p.get_default_input_device_info()
            logging.info(f"Default input device: {default_info['name']}")
            # Test default device
            test_stream = p.open(
                format=FORMAT,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=default_info['index'],
                frames_per_buffer=1024,
                start=False
            )
            test_stream.close()
            mics.append({
                'index': default_info['index'],
                'name': f"{default_info['name']} (Default)",
                'channels': default_info['maxInputChannels'],
                'default_rate': int(default_info['defaultSampleRate'])
            })
            logging.info("Default device working")
        except Exception as e:
            logging.warning(f"Default device test failed: {e}")

        # Then scan other devices
        for i in range(p.get_device_count()):
            try:
                device_info = p.get_device_info_by_index(i)
                # Skip if not an input device or already added as default
                if (device_info['maxInputChannels'] == 0 or 
                    any(m['index'] == i for m in mics)):
                    continue
                
                # Skip if device name contains certain keywords
                skip_keywords = ['mapper', 'dummy', 'null', 'loop']
                if any(keyword in device_info['name'].lower() for keyword in skip_keywords):
                    continue

                # Test if device actually works
                test_stream = p.open(
                    format=FORMAT,
                    channels=1,
                    rate=16000,
                    input=True,
                    input_device_index=i,
                    frames_per_buffer=1024,
                    start=False
                )
                test_stream.close()
                
                mics.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'default_rate': int(device_info['defaultSampleRate'])
                })
                logging.info(f"Found working device: {device_info['name']}")
                
            except Exception as e:
                logging.debug(f"Skipping device {i}: {e}")
                continue
                
    finally:
        p.terminate()
        
    if not mics:
        logging.warning("No working microphones found!")
    else:
        logging.info(f"Found {len(mics)} working microphone(s)")
        
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
    """Record audio with optimal sample rate."""
    global is_recording
    logging.info("=== Starting Audio Recording ===")
    logging.info(f"Requested duration: {duration} seconds")
    
    update_status("🎤 Initializing audio...")
    
    p = None
    stream = None
    frames = []
    
    try:
        # Get selected mic index
        selected = mic_var.get()
        logging.info(f"Selected microphone: {selected}")
        if not selected:
            raise Exception("No microphone selected")
            
        match = re.search(r'Device (\d+)', selected)
        if not match:
            raise Exception("Invalid microphone selection")
            
        input_device = int(match.group(1))
        logging.info(f"Using input device index: {input_device}")
        
        p = pyaudio.PyAudio()
        
        # Log device info
        try:
            device_info = p.get_device_info_by_index(input_device)
            logging.info(f"Device info: {device_info}")
        except Exception as e:
            logging.error(f"Error getting device info: {e}")
        
        # Try to use 16000Hz first
        try:
            logging.info("Attempting to open stream at 16000Hz...")
            stream = p.open(
                format=FORMAT,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=input_device,
                frames_per_buffer=1024,
                start=True  # Explicitly start the stream
            )
            device_rate = 16000
            logging.info("Successfully opened stream at 16000Hz")
        except Exception as e:
            logging.warning(f"Failed to open stream at 16000Hz: {e}")
            # Fall back to device's native rate
            device_info = p.get_device_info_by_index(input_device)
            device_rate = int(device_info['defaultSampleRate'])
            logging.info(f"Falling back to device native rate: {device_rate}Hz")
            stream = p.open(
                format=FORMAT,
                channels=1,
                rate=device_rate,
                input=True,
                input_device_index=input_device,
                frames_per_buffer=1024,
                start=True  # Explicitly start the stream
            )
            
        # Verify stream is active
        if not stream.is_active():
            logging.error("Stream not active after opening")
            raise RuntimeError("Audio stream not active")
        logging.info("Stream is active and ready for recording")
            
        # Calculate number of chunks to record
        chunks = int(device_rate / 1024 * duration)
        logging.info(f"Will record {chunks} chunks at {device_rate}Hz")
        
        # Start recording
        logging.info(f"Starting recording loop...")
        update_status("🎤 Recording...")
        
        is_recording = True
        start_time = time.time()
        
        for i in range(chunks):
            if not is_playing or not is_recording:
                logging.info("Recording interrupted")
                break
                
            try:
                data = stream.read(1024, exception_on_overflow=False)
                
                if not data:
                    continue
                    
                frames.append(data)
                
                # Update VU meter
                level = calculate_audio_level(data)
                root.after(0, lambda l=level: vu_meter.set_level(l))
                
                # Progress update every second
                if i % (device_rate // 1024) == 0:
                    elapsed = time.time() - start_time
                    update_status(f"🎤 Recording... {int(elapsed)}/{duration}s")
                    
            except OSError as e:
                logging.error(f"OSError during recording: {e}")
                time.sleep(0.1)
                continue
            except Exception as e:
                logging.error(f"Error during recording: {e}")
                continue
                
        is_recording = False
        
        # Log recording results
        elapsed = time.time() - start_time
        logging.info(f"Recording completed in {elapsed:.1f}s")
        logging.info(f"Recorded {len(frames)} chunks out of {chunks} expected")
        
        if not frames:
            logging.error("No audio data was recorded")
            raise RuntimeError("No audio data recorded")
            
        # Create WAV buffer
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)  # Always output at 16kHz
            wf.writeframes(b''.join(frames))
            
        return wav_buffer.getvalue()
        
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

def toggle_play_pause():
    """Toggle between play and pause states"""
    global is_playing, is_recording
    is_playing = not is_playing
    
    # Update button text
    play_pause_btn.config(text="▶️" if not is_playing else "⏸️")
    
    if is_playing:
        # Start a new recording cycle immediately
        update_status("▶️ Starting new interaction...")
        api_thread = threading.Thread(
            target=lambda: asyncio.run(api_client(0))
        )
        api_thread.daemon = True
        api_thread.start()
    else:
        # If pausing, stop current recording and playback
        is_recording = False  # Signal recording to stop
        try:
            pygame.mixer.music.stop()
            update_status("⏸️ Interaction stopped")
        except:
            pass

def stop_auto_recording():
    """Clean stop of auto recording"""
    global auto_recording
    auto_recording = False
    update_status("⏹️ Stopping automatic recording...")

def toggle_auto_recording():
    """Toggle automatic recording every X seconds"""
    global auto_recording, auto_recording_interval
    
    # Get interval from spinbox
    try:
        auto_recording_interval = max(5, int(interval_spinbox.get()))  # Minimum 5 seconds
    except ValueError:
        auto_recording_interval = 90  # fallback to default
        interval_spinbox.delete(0, tk.END)
        interval_spinbox.insert(0, "90")
    
    auto_recording = not auto_recording
    auto_btn.config(text="🔄 Auto ON" if auto_recording else "🔄 Auto OFF")
    interval_spinbox.config(state='disabled' if auto_recording else 'normal')
    
    if auto_recording:
        update_status(f"🔄 Starting continuous recording...")
        
        def auto_record_thread():
            while auto_recording and is_playing:
                try:
                    # Record audio for the entire interval
                    audio_data = record_audio(auto_recording_interval)
                    
                    # Take screenshot
                    screenshot_data = take_screenshot()
                    
                    # Collect text content as string
                    logging.info("Collecting text content...")
                    text_content = collect_text_files_content()
                    logging.info(f"Text content collected: {len(text_content)} bytes")

                    # Prepare multipart form data with text in body
                    data = {
                        'text': text_content  # Send text directly in request body
                    }

                    files = {
                        'data': ('screenshot.jpg', screenshot_data, 'image/jpeg'),
                        'audio': ('audio.wav', audio_data, 'audio/wav')
                    }

                    # Send request with text in body and files in multipart/form-data
                    logging.info("Sending data to n8n...")
                    response = requests.post(
                        API_ENDPOINT,
                        data=data,  # Text content in request body
                        files=files,  # Binary files in multipart/form-data
                        timeout=REQUEST_TIMEOUT
                    )
                    response.raise_for_status()
                    
                    # Process audio response
                    asyncio.run(process_audio_chunk(response.content))
                    
                except Exception as e:
                    logging.error(f"Error in auto recording thread: {e}")
                    update_status(f"❌ Auto recording error: {str(e)}")
                    break
        
        # Start auto recording thread
        auto_thread = threading.Thread(target=auto_record_thread)
        auto_thread.daemon = True
        auto_thread.start()
    else:
        update_status("⏹️ Automatic recording stopped")

def create_device_selectors():
    """Create input and output device selection frame with VU meter"""
    device_frame = tk.Frame(root)
    device_frame.pack(fill='x', padx=5, pady=5)
    
    # Add play/pause button
    global play_pause_btn
    play_pause_btn = tk.Button(device_frame, text="⏸️", width=3, command=toggle_play_pause)
    play_pause_btn.pack(side='left', padx=5)
    
    # Create auto recording frame
    auto_frame = tk.Frame(device_frame)
    auto_frame.pack(side='left', padx=5)

    # Add auto recording button
    global auto_btn
    auto_btn = tk.Button(auto_frame, text="🔄 Auto OFF", width=8, command=toggle_auto_recording)
    auto_btn.pack(side='left')

    # Add interval spinbox
    tk.Label(auto_frame, text="Interval:").pack(side='left', padx=(5,0))
    global interval_spinbox
    interval_spinbox = tk.Spinbox(auto_frame, from_=5, to=3600, width=5, increment=5)
    interval_spinbox.delete(0, tk.END)
    interval_spinbox.insert(0, "30")  # default value
    interval_spinbox.pack(side='left', padx=(0,5))
    tk.Label(auto_frame, text="sec").pack(side='left')
    
    # Input device selector
    input_frame = tk.Frame(device_frame)
    input_frame.pack(fill='x', pady=(0, 2))
    tk.Label(input_frame, text="Input Device:").pack(side='left')
    
    mic_var = tk.StringVar()
    mic_combo = ttk.Combobox(input_frame, textvariable=mic_var, state='readonly')
    mic_combo.pack(side='left', fill='x', expand=True, padx=(5, 0))
    
    # Output device selector
    output_frame = tk.Frame(device_frame)
    output_frame.pack(fill='x', pady=(2, 0))
    tk.Label(output_frame, text="Output Device:").pack(side='left')
    
    output_var = tk.StringVar()
    output_combo = ttk.Combobox(output_frame, textvariable=output_var, state='readonly')
    output_combo.pack(side='left', fill='x', expand=True, padx=(5, 0))
    
    # Refresh button (shared for both devices)
    refresh_btn = tk.Button(device_frame, text="🔄", command=lambda: refresh_devices(mic_combo, output_combo))
    refresh_btn.pack(side='right', padx=(5, 0))
    
    # Add VU meter
    vu_frame = tk.Frame(root)
    vu_frame.pack(fill='x', padx=5, pady=2)
    tk.Label(vu_frame, text="Input Level:").pack(side='left')
    vu_meter = VUMeter(vu_frame, width=200, height=20)
    vu_meter.pack(side='left', fill='x', expand=True, padx=(5, 0))
    
    # Initial population of device lists
    refresh_devices(mic_combo, output_combo)
    
    return mic_var, output_var, mic_combo, output_combo, vu_meter

def get_available_outputs():
    """Get list of available and working output devices"""
    p = pyaudio.PyAudio()
    outputs = []
    logging.info("Scanning for working audio output devices...")
    
    try:
        # First try to get default output device
        try:
            default_info = p.get_default_output_device_info()
            logging.info(f"Default output device: {default_info['name']}")
            # Test default device
            test_stream = p.open(
                format=FORMAT,
                channels=1,
                rate=16000,
                output=True,
                output_device_index=default_info['index'],
                frames_per_buffer=1024,
                start=False
            )
            test_stream.close()
            outputs.append({
                'index': default_info['index'],
                'name': f"{default_info['name']} (Default)",
                'channels': default_info['maxOutputChannels'],
                'default_rate': int(default_info['defaultSampleRate'])
            })
            logging.info("Default output device working")
        except Exception as e:
            logging.warning(f"Default output device test failed: {e}")

        # Then scan other devices
        for i in range(p.get_device_count()):
            try:
                device_info = p.get_device_info_by_index(i)
                # Skip if not an output device or already added as default
                if (device_info['maxOutputChannels'] == 0 or 
                    any(o['index'] == i for o in outputs)):
                    continue
                
                # Skip if device name contains certain keywords
                skip_keywords = ['mapper', 'dummy', 'null', 'loop']
                if any(keyword in device_info['name'].lower() for keyword in skip_keywords):
                    continue

                # Test if device actually works
                test_stream = p.open(
                    format=FORMAT,
                    channels=1,
                    rate=16000,
                    output=True,
                    output_device_index=i,
                    frames_per_buffer=1024,
                    start=False
                )
                test_stream.close()
                
                outputs.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxOutputChannels'],
                    'default_rate': int(device_info['defaultSampleRate'])
                })
                logging.info(f"Found working output device: {device_info['name']}")
                
            except Exception as e:
                logging.debug(f"Skipping output device {i}: {e}")
                continue
                
    finally:
        p.terminate()
        
    if not outputs:
        logging.warning("No working output devices found!")
    else:
        logging.info(f"Found {len(outputs)} working output device(s)")
        
    return outputs

def refresh_devices(mic_combo, output_combo):
    """Refresh both input and output device lists"""
    # Save current selections
    current_mic = mic_combo.get()
    current_output = output_combo.get()
    
    # Update input devices
    mics = get_available_microphones()
    mic_options = [f"{m['name']} (Device {m['index']})" for m in mics]
    mic_combo['values'] = mic_options
    
    # Update output devices
    outputs = get_available_outputs()
    output_options = [f"{o['name']} (Device {o['index']})" for o in outputs]
    output_combo['values'] = output_options
    
    # Restore previous selections if possible
    if current_mic in mic_options:
        mic_combo.set(current_mic)
    elif mic_options:
        mic_combo.set(mic_options[0])
        
    if current_output in output_options:
        output_combo.set(current_output)
    elif output_options:
        output_combo.set(output_options[0])
    
    # Update status
    status = []
    if mic_options:
        status.append(f"Found {len(mic_options)} input device(s)")
    else:
        status.append("❌ No input devices found")
        
    if output_options:
        status.append(f"Found {len(output_options)} output device(s)")
    else:
        status.append("❌ No output devices found")
        
    update_status(" | ".join(status))

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

# Create text widget first
text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
text_widget.pack(expand=True, fill='both', padx=5, pady=5)

# Create main controls frame
controls_frame = tk.Frame(root)
controls_frame.pack(fill='x', padx=5, pady=5)

# Add microphone selector and VU meter
mic_var, output_var, mic_combo, output_combo, vu_meter = create_device_selectors()
mic_combo.bind('<<ComboboxSelected>>', lambda e: update_mic_status(mic_combo))
output_combo.bind('<<ComboboxSelected>>', lambda e: update_mic_status(output_combo))



def on_closing():
    """Handle application shutdown."""
    global running, vu_meter, auto_recording, auto_recording_task
    running = False
    auto_recording = False  # Stop auto recording
    auto_recording = False
    if auto_recording_task:
        auto_recording_task.cancel()
    # Reset VU meter
    vu_meter.set_level(0.0)
    logging.info("Shutting down application...")
    root.quit()
    root.destroy()
    sys.exit(0)


async def api_client(interval):
    """Execute a single recording/response cycle"""
    try:
        # Check if paused
        if not is_playing:
            return
            
        update_status("Starting new recording cycle...")
        
        # Capture first screenshot with verification
        logging.info("Taking initial screenshot...")
        initial_screenshot = take_screenshot()
        if not initial_screenshot:
            raise Exception("Failed to capture initial screenshot")
        logging.info(f"Initial screenshot captured: {len(initial_screenshot)} bytes")
        
        # Record audio
        logging.info("Starting 15-second recording...")
        update_status("Recording audio...")
        audio_data = record_audio(15)
        logging.info("Recording completed")

        # Capture final screenshot with verification
        logging.info("Taking final screenshot...")
        final_screenshot = take_screenshot()
        if not final_screenshot:
            raise Exception("Failed to capture final screenshot")
        logging.info(f"Final screenshot captured: {len(final_screenshot)} bytes")

        # Collect text content as string
        logging.info("Collecting text content...")
        text_content = collect_text_files_content()
        logging.info(f"Text content collected: {len(text_content)} bytes")

        # Prepare multipart form data with text in body
        data = {
            'text': text_content  # Send text directly in request body
        }

        files = {
            'initial_screenshot': ('initial_screenshot.jpg', initial_screenshot, 'image/jpeg'),
            'final_screenshot': ('final_screenshot.jpg', final_screenshot, 'image/jpeg'),
            'audio': ('audio.wav', audio_data, 'audio/wav')
        }

        # Send request with text in body and files in multipart/form-data
        logging.info("Sending data to n8n...")
        response = requests.post(
            "https://nlr.app.n8n.cloud/webhook/ycl-enpoint",
            data=data,  # Text content in request body
            files=files,  # Binary files in multipart/form-data
            timeout=REQUEST_TIMEOUT
        )
        
        # Log response details
        logging.info(f"n8n response status: {response.status_code}")
        logging.info(f"n8n response headers: {response.headers}")
        
        response.raise_for_status()
        
        # Process audio response
        await process_audio_chunk(response.content)
        logging.info("Audio response played")

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        update_status(f"❌ Error: {str(e)}")

def setup_logging():
    """Configure logging with Unicode support"""
    # Force UTF-8 encoding for logging
    class UTFStreamHandler(logging.StreamHandler):
        def emit(self, record):
            try:
                msg = self.format(record)
                stream = self.stream
                # Ensure Unicode encoding
                if isinstance(msg, str):
                    stream.buffer.write(msg.encode('utf-8'))
                    stream.buffer.write(b'\n')
                else:
                    stream.buffer.write(msg)
                    stream.buffer.write(b'\n')
                self.flush()
            except Exception:
                self.handleError(record)

    # Remove existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Add UTF-8 handler
    handler = UTFStreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)

if __name__ == "__main__":
    # Initialize logging first
    setup_logging()
    
    # Initialize managers
    device_manager = DeviceManager()
    audio_manager = AudioManager(config)
    
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

        # Initialize video window in a separate thread
        def create_test_video():
            """Create test idle and talk videos if they don't exist"""
            video_logger.info("Creating test videos")
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                videos_dir = os.path.join(script_dir, "videos")
                idle_path = os.path.join(videos_dir, "loop.mp4")
                talk_path = os.path.join(videos_dir, "talk.mp4")

                if not os.path.exists(videos_dir):
                    os.makedirs(videos_dir)
                    video_logger.info(f"Created videos directory: {videos_dir}")

                # Utiliser un codec compatible avec votre système
                if sys.platform == 'win32':
                    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
                else:
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Fallback codec

                # Create idle video (green circle moving horizontally)
                if not os.path.exists(idle_path):
                    out = cv2.VideoWriter(idle_path, fourcc, 30.0, (320,240), isColor=True)
                    if not out.isOpened():
                        raise Exception("Failed to create idle video writer")
            
                    for i in range(90):  # Plus de frames pour une animation plus fluide
                        frame = np.zeros((240,320,3), dtype=np.uint8)
                        x = 160 + int(100*np.sin(2*np.pi*i/90))  # Mouvement plus fluide
                        cv2.circle(frame, (x, 120), 20, (0,255,0), -1)
                        out.write(frame)
                    out.release()

                # Create talk video (green circle moving vertically)
                if not os.path.exists(talk_path):
                    out = cv2.VideoWriter(talk_path, fourcc, 30.0, (320,240), isColor=True)
                    if not out.isOpened():
                        raise Exception("Failed to create talk video writer")
            
                    for i in range(90):  # Plus de frames pour une animation plus fluide
                        frame = np.zeros((240,320,3), dtype=np.uint8)
                        y = 120 + int(60*np.sin(2*np.pi*i/90))  # Mouvement plus fluide
                        cv2.circle(frame, (160, y), 20, (0,255,0), -1)
                        out.write(frame)
                    out.release()

                return idle_path

            except Exception as e:
                video_logger.error(f"Failed to create test video: {e}", exc_info=True)
                return None

        def get_video_path():
            """Get the correct path to video files whether running from source or executable"""
            if getattr(sys, 'frozen', False):
                # Running from executable
                base_path = sys._MEIPASS
            else:
                # Running from source
                base_path = os.path.dirname(os.path.abspath(__file__))
        
            videos_dir = os.path.join(base_path, "videos")
            if not os.path.exists(videos_dir):
                os.makedirs(videos_dir)
        
            return videos_dir

        def init_video_window():
            try:
                # Get video directory path
                videos_dir = get_video_path()
                
                # Ensure videos directory exists
                os.makedirs(videos_dir, exist_ok=True)
                logging.info(f"Using videos directory: {videos_dir}")
                
                video_path = os.path.join(videos_dir, "loop.mp4")
        
                logging.info(f"Checking for video file: {video_path}")
                if not os.path.exists(video_path):
                    logging.info("Video file not found, creating test video...")
                    video_path = create_test_video()
                    if not video_path:
                        logging.error("Failed to create test video")
                        return
            
                logging.info(f"Creating video window with path: {video_path}")
                # Instead of creating the window directly, schedule it on the main thread
                root.after(100, lambda: create_video_window(video_path))

            except Exception as e:
                logging.error(f"Failed to create video window: {e}", exc_info=True)

        def create_video_window(video_path):
            """Create video window in the main thread"""
            try:
                video_window = DraggableVideoWindow(video_path)
                # Store reference to prevent garbage collection
                global current_video_window
                current_video_window = video_window
                logging.info("Video window created successfully")
            except Exception as e:
                logging.error(f"Failed to create video window in main thread: {e}", exc_info=True)

        # Initialize video subsystem first
        if not init_video():
            messagebox.showwarning(
                "Video Warning",
                "Video subsystem initialization failed. The application will continue without video support."
            )
        else:
            # Initialize video window directly (it will schedule itself on main thread)
            video_logger.info("Initializing video window")
            init_video_window()
        
        # Test audio but don't exit if it fails
        audio_ok = initialize_audio()
        if audio_ok:
            text_widget.insert(tk.END, "Audio initialization successful\n")
        else:
            text_widget.insert(tk.END, "Audio initialization failed - continuing without audio\n")
        root.update()
        
        logging.info("Starting main UI loop...")
        text_widget.insert(tk.END, "Ready! Click ▶️ to start interaction\n")
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
