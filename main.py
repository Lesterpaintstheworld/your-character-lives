import asyncio
import logging
import argparse
import sys
import os
import aiohttp
from threading import Thread
from audio_buffer import AudioBufferManager
from voice_activity import VoiceActivityDetector
from screenshot_manager import ScreenshotManager
from repo_visualizer import start_visualization
import time
import io
import wave
import threading
from PIL import Image, ImageTk
import tempfile
import cv2
import numpy as np
from scipy import signal
import json
from pydub import AudioSegment
from video_window import DraggableVideoWindow
from device_manager import DeviceManager

# Global references to video windows
current_video_window = None
second_video_window = None

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
import subprocess

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
current_speaker = "emily"  # Alternates between "emily" and "daemon"
last_audio_time = 0
audio_buffer = []
output_var = None  # Will store output device selection
emily_endpoint_var = None  # Will store Emily endpoint
daemon_endpoint_var = None  # Will store Daemon endpoint
ui_elements_created = False  # Track UI element creation
browser_button = None  # Will store browser control button
recording_status = None  # Will store recording status label
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import re
from PIL import Image
from constants import ThemeColors
import pyautogui
import requests
import pyaudio
import pygame
import asyncio
import pyperclip
import pyttsx3
from dotenv import load_dotenv

from config import Config
from audio_manager import AudioManager
from log_manager import LogManager
from event_manager import EventManager
from thread_manager import ThreadManager
from browser_manager import BrowserManager
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
    """Collect content from relevant text files in current directory and subdirectories."""
    try:
        content = []
        
        # Get execution directory (where the program is run from)
        base_dir = os.getcwd()
        
        logging.info("=== Path Debug Information ===")
        logging.info(f"Current working directory (execution): {base_dir}")

        # Define exclusion patterns
        excluded_dirs = {
            'node_modules',
            'dist',
            'build',
            '__pycache__',
            'venv',
            '.git',
            '.github',
            '.idea',
            '.vscode',
            '.aider',
            'temp',
            'tmp',
            '_MEI*'  # Exclude PyInstaller temp directories
        }

        excluded_file_prefixes = {
            '.',
            '_',
            'flycheck_'
        }

        excluded_file_extensions = {
            '.pyc',
            '.pyo',
            '.pyd',
            '.so',
            '.dll',
            '.dylib',
            '.exe',
            '.bin',
            '.pkl',
            '.log',
            '.cache'
        }

        content.append(f"=== Document Scan - {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        
        total_files = 0
        
        # Walk through directory tree
        for root, dirs, files in os.walk(base_dir):
            # Remove excluded directories in-place
            dirs[:] = [d for d in dirs if not any(
                pattern.endswith('*') and d.startswith(pattern[:-1]) or d == pattern 
                for pattern in excluded_dirs
            )]
            
            # Skip if current directory starts with excluded prefix
            current_dir = os.path.basename(root)
            if any(current_dir.startswith(prefix) for prefix in excluded_file_prefixes):
                continue

            logging.debug(f"Scanning directory: {root}")
            
            for file in files:
                # Skip files with excluded prefixes or extensions
                if (any(file.startswith(prefix) for prefix in excluded_file_prefixes) or
                    any(file.endswith(ext) for ext in excluded_file_extensions)):
                    continue

                # Only include relevant text and code files
                if file.lower().endswith(('.md', '.txt', '.py', '.js', '.java', '.cpp', '.c', '.h', 
                                        '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.ts',
                                        '.html', '.css', '.sql', '.r', '.m', '.scala', '.pl', '.sh',
                                        '.bat', '.json', '.yaml', '.yml', '.toml', '.ini')):
                    full_path = os.path.join(root, file)
                    try:
                        rel_path = os.path.relpath(full_path, base_dir)
                        logging.info(f"Processing file: {rel_path}")
                        
                        # Try different encodings
                        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                        file_content = None
                        
                        for encoding in encodings:
                            try:
                                with open(full_path, 'r', encoding=encoding) as f:
                                    file_content = f.read()
                                logging.debug(f"Successfully read file with {encoding} encoding")
                                break
                            except UnicodeDecodeError:
                                continue
                            except Exception as e:
                                logging.error(f"Error reading file with {encoding}: {str(e)}")
                                continue
                        
                        if file_content is not None:
                            content.append("\n" + "="*50)
                            content.append(f"FILE: {rel_path}")
                            content.append("="*50 + "\n")
                            content.append(file_content)
                            total_files += 1
                        else:
                            logging.error(f"Failed to read file {rel_path} with any encoding")
                            
                    except Exception as e:
                        logging.error(f"Error processing file {full_path}: {str(e)}")
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


import queue

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speech rate (default is 200)
engine.setProperty('volume', 1.0)  # Volume between 0 and 1.0

def safe_remove_file(filepath: str, max_retries: int = 3, delay: float = 0.5) -> bool:
    """Safely remove a file with retries and proper cleanup."""
    import gc
    for attempt in range(max_retries):
        try:
            # Force garbage collection to release file handles
            gc.collect()
            
            # Try to close any remaining handles (Windows specific)
            if os.name == 'nt':
                import ctypes
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                handle = kernel32.CreateFileW(
                    filepath, 
                    0x80000000, # GENERIC_READ
                    0,          # No sharing
                    None,       # No security
                    3,          # OPEN_EXISTING
                    0x80,       # FILE_ATTRIBUTE_NORMAL
                    None        # No template
                )
                if handle != -1:  # INVALID_HANDLE_VALUE
                    kernel32.CloseHandle(handle)
            
            # Remove the file
            if os.path.exists(filepath):
                os.remove(filepath)
                logging.info(f"Successfully removed temp file: {filepath}")
                return True
                
        except Exception as e:
            logging.warning(f"Failed to remove temp file (attempt {attempt + 1}): {e}")
            time.sleep(delay)
            continue
            
    return False

def validate_and_fix_audio_data(audio_data: bytes) -> bytes:
    """Simple validation of audio data."""
    try:
        if not audio_data:
            raise ValueError("Empty audio data received")
            
        # Just verify we have some data and return it
        logging.info(f"Received raw audio data: {len(audio_data)} bytes")
        return audio_data
        
    except Exception as e:
        logging.error(f"Error validating audio data: {e}")
        raise

async def process_audio_chunk(audio_data: bytes, is_daemon=False):
    """Process and play raw binary audio data using PyAudio directly."""
    temp_path = None
    p = None
    stream = None
    
    try:
        if not audio_data:
            raise ValueError("Empty audio data received")
            
        # Switch videos sequentially, not simultaneously
        logging.info(f"Attempting to switch to talk video (is_daemon={is_daemon})...")
        if not is_daemon:  # Emily (first speaker) uses loop2/talk2
            if current_video_window:
                logging.info("Switching Emily to talk2 video...")
                current_video_window.switch_to_talk_video()  # This will use talk2.mp4
                await asyncio.sleep(0.2)  # Give time for video switch
            else:
                logging.error("First video window (Emily) not initialized")
        else:  # Daemon uses loop/talk
            if second_video_window:
                logging.info("Switching Daemon to talk video...")
                second_video_window.switch_to_talk_video()  # This will use talk.mp4
                await asyncio.sleep(0.2)  # Give time for video switch
            else:
                logging.error("Second video window (Daemon) not initialized")
            
        # Get user-specific temp directory with proper permissions
        temp_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp', 'AI_Assistant')
        
        # Create temp directory if it doesn't exist
        try:
            os.makedirs(temp_dir, exist_ok=True)
            # Explicitly set directory permissions
            os.chmod(temp_dir, 0o700)  # User read/write/execute only
        except Exception as e:
            logging.error(f"Failed to create/set permissions on temp directory: {e}")
            # Fallback to system temp directory
            temp_dir = tempfile.gettempdir()

        # Create temp file with proper permissions
        try:
            temp_fd, temp_path = tempfile.mkstemp(suffix='.mp3', dir=temp_dir)
            os.close(temp_fd)  # Close file descriptor immediately
            # Set file permissions
            os.chmod(temp_path, 0o600)  # User read/write only
            logging.info(f"Created temp file with permissions: {temp_path}")
        except Exception as e:
            logging.error(f"Failed to create temp file: {e}")
            # Fallback to system temp directory
            temp_fd, temp_path = tempfile.mkstemp(suffix='.mp3')
            os.close(temp_fd)

        # Switch videos sequentially, not simultaneously
        logging.info(f"Attempting to switch to talk video (is_daemon={is_daemon})...")
        if not is_daemon:  # Emily (first speaker) uses loop2/talk2
            if current_video_window:
                logging.info("Switching Emily to talk2 video...")
                current_video_window.switch_to_talk_video()  # This will use talk2.mp4
                await asyncio.sleep(0.2)  # Give time for video switch
            else:
                logging.error("First video window (Emily) not initialized")
        else:  # Daemon uses loop/talk
            if second_video_window:
                logging.info("Switching Daemon to talk video...")
                second_video_window.switch_to_talk_video()  # This will use talk.mp4
                await asyncio.sleep(0.2)  # Give time for video switch
            else:
                logging.error("Second video window (Daemon) not initialized")

        # Play audio
        try:
            # Create temp file with unique name in user temp directory
            temp_fd, temp_path = tempfile.mkstemp(suffix='.mp3')
            os.close(temp_fd)  # Close file descriptor immediately
            
            logging.info(f"Created temp file: {temp_path}")
            
            # Write audio data to temp file
            with open(temp_path, 'wb') as f:
                f.write(audio_data)

            # Get selected output device
            selected = output_var.get() if output_var else None
            device_index = None
            
            p = pyaudio.PyAudio()
            
            # Find selected device
            if selected:
                device_name = re.match(r'^([^(]+)', selected).group(1).strip()
                for i in range(p.get_device_count()):
                    info = p.get_device_info_by_index(i)
                    if device_name.lower() in info['name'].lower():
                        if validate_output_device(i):
                            device_index = i
                            break

            # Process and play audio
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            if len(audio) == 0:
                raise ValueError("Audio file is empty")
            
            # Force specific format
            audio = audio.set_frame_rate(24000)
            audio = audio.set_channels(1)
            audio = audio.set_sample_width(2)
            
            raw_data = audio.raw_data
            if not raw_data:
                raise ValueError("No raw audio data available")

            # Open and configure audio stream
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                output=True,
                output_device_index=device_index,
                frames_per_buffer=1024,
                start=False
            )
            
            stream.start_stream()
            
            # Play audio in smaller chunks with yields to prevent blocking
            chunk_size = 1024
            total_bytes = len(raw_data)
            total_chunks = (total_bytes + chunk_size - 1) // chunk_size

            for i in range(total_chunks):
                if not is_playing:
                    break
                    
                start = i * chunk_size
                end = min(start + chunk_size, total_bytes)
                chunk = raw_data[start:end]
                
                if chunk:
                    stream.write(chunk)
                    await asyncio.sleep(0.001)  # Yield to other tasks

        finally:
            # Cleanup audio resources
            if stream:
                stream.stop_stream()
                stream.close()
            if p:
                p.terminate()

    except Exception as e:
        logging.error(f"Error in process_audio_chunk: {e}")
        raise

    finally:
        # Clean up temp file with elevated permissions if needed
        if temp_path and os.path.exists(temp_path):
            for attempt in range(3):
                try:
                    # Ensure we have write permission to delete
                    current_perms = os.stat(temp_path).st_mode
                    if not current_perms & 0o200:  # Check write permission
                        os.chmod(temp_path, 0o600)  # Set user read/write
                        
                    os.remove(temp_path)
                    logging.info(f"Successfully removed temp file: {temp_path}")
                    break
                except PermissionError as e:
                    logging.warning(f"Permission error removing file (attempt {attempt+1}): {e}")
                    # Try to force close any open handles on Windows
                    if os.name == 'nt':
                        try:
                            import win32file
                            win32file.CloseHandle(win32file._get_osfhandle(temp_fd))
                        except:
                            pass
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logging.warning(f"Failed to remove temp file (attempt {attempt+1}): {e}")
                    await asyncio.sleep(0.1)
                
        # Switch back to idle videos sequentially
        logging.info("Switching back to idle videos...")
        if not is_daemon:  # Emily back to loop2
            if current_video_window:
                current_video_window.switch_to_idle_video()  # This will use loop2.mp4
                await asyncio.sleep(0.2)  # Give time for video switch
        else:  # Daemon back to loop
            if second_video_window:
                second_video_window.switch_to_idle_video()  # This will use loop.mp4
                await asyncio.sleep(0.2)  # Give time for video switch

def safe_remove_file(filepath: str, max_retries: int = 3, delay: float = 0.5) -> bool:
    """Safely remove a file with retries and proper cleanup."""
    import gc
    for attempt in range(max_retries):
        try:
            # Force garbage collection to release file handles
            gc.collect()
            
            # Try to close any remaining handles (Windows specific)
            if os.name == 'nt':
                import ctypes
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                handle = kernel32.CreateFileW(
                    filepath, 
                    0x80000000, # GENERIC_READ
                    0,          # No sharing
                    None,       # No security
                    3,          # OPEN_EXISTING
                    0x80,       # FILE_ATTRIBUTE_NORMAL
                    None        # No template
                )
                if handle != -1:  # INVALID_HANDLE_VALUE
                    kernel32.CloseHandle(handle)
            
            # Remove the file
            if os.path.exists(filepath):
                os.remove(filepath)
                logging.info(f"Successfully removed temp file: {filepath}")
                return True
                
        except Exception as e:
            logging.warning(f"Failed to remove temp file (attempt {attempt + 1}): {e}")
            time.sleep(delay)
            continue
            
    return False

def update_status(message):
    """Update status in UI with more detail for errors"""
    if "❌" in message:
        logging.error(message)
        # Make errors more visible in UI
        message = f"\n{message}\n"
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
    """Record audio with ALC compensation"""
    global is_recording
    logging.info("=== Starting Audio Recording ===")
    logging.info(f"Requested duration: {duration} seconds")
    
    # First get a noise floor sample
    noise_floor = None
    try:
        p = pyaudio.PyAudio()
        device_index = get_input_device()
        stream = p.open(
            format=FORMAT,
            channels=1,
            rate=48000,  # Match Jabra's native rate
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024
        )
        
        # Sample noise for 100ms
        noise_data = []
        for _ in range(5):  # ~100ms at 48kHz
            data = stream.read(1024, exception_on_overflow=False)
            noise_data.append(np.frombuffer(data, dtype=np.int16))
            
        noise_floor = np.mean([np.sqrt(np.mean(np.square(chunk))) for chunk in noise_data])
        logging.info(f"Measured noise floor RMS: {noise_floor}")
        
    except Exception as e:
        logging.error(f"Error measuring noise floor: {e}")
    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        if p:
            p.terminate()

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
                
                # Calculate level with noise floor compensation
                if noise_floor is not None:
                    audio_array = np.frombuffer(data, dtype=np.int16)
                    rms = np.sqrt(np.mean(np.square(audio_array)))
                    level = max(0, (rms - noise_floor) / (32768 - noise_floor))
                    root.after(0, lambda l=level: vu_meter.set_level(l))
                else:
                    # Fallback to original calculation if no noise floor
                    level = calculate_audio_level(data)
                    root.after(0, lambda l=level: vu_meter.set_level(l))
                
                # Progress update every second
                if i % (48000 // 1024) == 0:  # Update every second at 48kHz
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
                logging.warning(f"Error closing stream: {e}")
        if p:
            try:
                p.terminate()
            except Exception as e:
                logging.warning(f"Error terminating PyAudio: {e}")

import tkinter as tk
from tkinter import scrolledtext

class VUMeter(Canvas):
    def __init__(self, master, width=200, height=20, bg=ThemeColors.BG_LIGHT,
                 low_color=ThemeColors.VU_LOW, 
                 mid_color=ThemeColors.VU_MID,
                 high_color=ThemeColors.VU_HIGH, **kwargs):
        super().__init__(master, width=width, height=height, bg=bg,
                        highlightthickness=0,
                        **kwargs)
        self.width = width
        self.height = height
        self.segments = 30
        self.low_color = low_color
        self.mid_color = mid_color
        self.high_color = high_color
        
        # Calculate silence threshold position (matching calculate_audio_level)
        MIN_DB = -30  # Match the new values from calculate_audio_level
        MAX_DB = -3
        THRESHOLD_DB = -25  # Set visible threshold
        self.threshold_position = (THRESHOLD_DB - MIN_DB) / (MAX_DB - MIN_DB) * self.segments
        
        # Bind to resize events
        self.bind('<Configure>', self.on_resize)
        self.create_segments()
        self.level = 0

    def on_resize(self, event):
        """Handle resize events"""
        self.width = event.width
        self.height = event.height
        self.create_segments()
        self.set_level(self.level)  # Redraw with current level

    def create_segments(self):
        """Create segments with smooth color transition and threshold marker"""
        # Clear existing segments
        self.delete('all')
        self.segments_ids = []
        
        # Calculate segment width based on actual widget width
        actual_width = self.winfo_width()
        self.segment_width = actual_width / self.segments
        
        for i in range(self.segments):
            x1 = i * self.segment_width
            y1 = 0
            x2 = (i + 1) * self.segment_width
            y2 = self.winfo_height()
            
            # Smooth color gradient
            if i < self.segments * 0.4:  # First 40% - green
                ratio = i / (self.segments * 0.4)
                color = self.blend_colors(self.low_color, self.mid_color, ratio)
            elif i < self.segments * 0.8:  # Next 40% - blue to orange
                ratio = (i - self.segments * 0.4) / (self.segments * 0.4)
                color = self.blend_colors(self.mid_color, self.high_color, ratio)
            else:  # Last 20% - red
                color = self.high_color
                
            segment = self.create_rectangle(
                x1, y1, x2, y2,
                fill=ThemeColors.BG_DARK,
                outline='',
                width=0
            )
            self.segments_ids.append((segment, color))
            
        # Add threshold marker line
        threshold_x = self.threshold_position * self.segment_width
        self.create_line(
            threshold_x, 0, 
            threshold_x, self.winfo_height(),
            fill='white',
            width=2,
            dash=(2, 2)  # Create dashed line
        )

    def blend_colors(self, color1, color2, ratio):
        """Blend two hex colors"""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        return f'#{r:02x}{g:02x}{b:02x}'

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
    """Calculate audio level with detailed diagnostics"""
    if isinstance(audio_data, bytes):
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
    else:
        audio_array = audio_data
        
    # Add diagnostic info
    logging.debug(f"Audio data type: {type(audio_data)}")
    logging.debug(f"Audio array type: {audio_array.dtype}")
    logging.debug(f"Audio array range: [{np.min(audio_array)}, {np.max(audio_array)}]")
    logging.debug(f"Audio array mean: {np.mean(audio_array)}")
    
    # Calculate RMS with more precision
    rms = np.sqrt(np.mean(np.square(audio_array.astype(np.float64))))
    logging.debug(f"Raw RMS value: {rms}")
    
    # Convert to decibels and normalize
    if rms > 0:
        db = 20 * np.log10(rms / 32768.0)  # Full scale reference
        logging.debug(f"Decibel value: {db} dB")
        
        # More conservative ranges
        MIN_DB = -60
        MAX_DB = -24  # Lower max to reduce sensitivity
        NOISE_GATE = -45  # Higher noise gate to filter more background
        
        if db < NOISE_GATE:
            logging.debug("Below noise gate threshold")
            return 0.0
            
        normalized = (db - MIN_DB) / (MAX_DB - MIN_DB)
        normalized = np.power(normalized, 0.5)  # Less aggressive compression
        normalized *= 0.9  # Scale down slightly
        
        result = max(0.0, min(1.0, normalized))
        logging.debug(f"Normalized value: {result}")
        return result
        
    return 0.0

def toggle_play_pause():
    """Toggle between play and pause states"""
    global is_playing, is_recording
    is_playing = not is_playing
    
    # Update button text
    play_pause_btn.config(text="▶️" if not is_playing else "⏸️")
    
    if is_playing:
        # Start smart recording
        update_status("▶️ Starting interaction...")
        smart_thread = threading.Thread(
            target=lambda: asyncio.run(start_smart_recording()),
            daemon=True
        )
        smart_thread.start()
    else:
        # Stop current recording and playback
        is_recording = False
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

async def editor_loop():
    """Run the editor loop that processes code changes"""
    try:
        screenshot_manager = ScreenshotManager()
        while is_playing and editor_active:
            try:
                # Take screenshots before and after collecting text content
                update_status("Taking screenshots...")
                pre_screenshot = await screenshot_manager.capture()
                if pre_screenshot is None:
                    raise ValueError("Failed to capture pre-screenshot")

                # Collect text content and file paths
                update_status("Collecting text content...")
                text_content = collect_text_files_content()
                update_status(f"Text content collected: {len(text_content)} bytes")

                post_screenshot = await screenshot_manager.capture()
                if post_screenshot is None:
                    raise ValueError("Failed to capture post-screenshot")

                # Get list of text file paths
                base_dir = os.getcwd()
                file_paths = []
                for root, _, files in os.walk(base_dir):
                    for file in files:
                        if file.lower().endswith(('.md', '.txt', '.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.ts', '.html', '.css', '.sql', '.r', '.m', '.scala', '.pl', '.sh', '.bat')):
                            rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                            file_paths.append(rel_path)

                # Prepare request data with session ID and screenshots
                data = {
                    'text': text_content,
                    'session': session_id
                }

                files = {
                    'pre_screenshot': ('pre_screenshot.jpg', pre_screenshot, 'image/jpeg'),
                    'post_screenshot': ('post_screenshot.jpg', post_screenshot, 'image/jpeg')
                }

                # Call the Claude endpoint
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: requests.post(
                        NetworkConstants.EDITOR_ENDPOINT,
                        data=data,
                        files=files,
                        timeout=NetworkConstants.REQUEST_TIMEOUT
                    )
                )
                response.raise_for_status()
                
                # Extract output from JSON response
                output = response.json().get('output')
                if not output:
                    msg = "No output received from editor endpoint"
                    logging.warning(msg)
                    update_status(msg)
                    continue
                
                # Log and display the Claude response
                response_msg = "\n=== Claude Response ===\n" + output + "\n====================="
                logging.info(response_msg)
                update_status(response_msg)
                    
                # Build and display aider command
                cmd = ['aider', '--yes-always']
                for file_path in file_paths:
                    cmd.extend(['--file', file_path])
                cmd.extend(['--message', output])

                cmd_msg = "\n=== Aider Command ===\n" + ' '.join(cmd) + "\n===================="
                logging.info(cmd_msg)
                update_status(cmd_msg)

                # Run aider with the output and file paths
                update_status(f"Starting aider session with files: {file_paths}")
                # Create startupinfo to hide console window on Windows
                startupinfo = None
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE

                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    startupinfo=startupinfo
                )
                
                # Stream stdout and stderr in real-time to both logs and UI
                while True:
                    stdout_line = await process.stdout.readline()
                    stderr_line = await process.stderr.readline()
                    
                    if not stdout_line and not stderr_line:
                        break
                        
                    if stdout_line:
                        raw_line = stdout_line.decode().strip()
                        
                        # Format different types of aider output
                        if raw_line.startswith("Applied edit to"):
                            formatted_line = f"✅ {raw_line}"
                        elif raw_line.startswith("Commit"):
                            formatted_line = f"\n🔒 {raw_line}\n"
                        elif raw_line.startswith("pip install"):
                            formatted_line = f"\n📦 {raw_line}\n"
                        elif raw_line.startswith("mkdir"):
                            formatted_line = f"\n📁 {raw_line}\n"
                        elif raw_line.startswith("python"):
                            formatted_line = f"\n🐍 {raw_line}\n"
                        else:
                            formatted_line = f"   {raw_line}"
                        
                        # Log original line but show formatted in UI
                        logging.info(f"[aider stdout] {raw_line}")
                        update_status(formatted_line)
                        
                    if stderr_line:
                        raw_line = stderr_line.decode().strip()
                        # Format error messages
                        formatted_line = f"❌ {raw_line}"
                        logging.error(f"[aider stderr] {raw_line}")
                        update_status(formatted_line)
                
                await process.wait()
                
                if process.returncode != 0:
                    error_msg = f"Aider process failed with return code {process.returncode}"
                    logging.error(error_msg)
                    update_status(error_msg)
                else:
                    success_msg = "Aider session completed successfully"
                    logging.info(success_msg)
                    update_status(success_msg)
                    
                    # Attempt git push
                    try:
                        logging.info("Attempting git push...")
                        update_status("🔄 Pushing changes to remote...")
                        
                        push_process = await asyncio.create_subprocess_exec(
                            'git', 'push',
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        
                        # Get output
                        stdout, stderr = await push_process.communicate()
                        
                        if push_process.returncode == 0:
                            logging.info("Git push successful")
                            update_status("✅ Changes pushed to remote")
                        else:
                            error_output = stderr.decode().strip() if stderr else "Unknown error"
                            logging.warning(f"Git push failed but continuing: {error_output}")
                            update_status("⚠️ Git push failed - continuing anyway")
                    except Exception as e:
                        logging.warning(f"Git push failed but continuing: {e}")
                        update_status("⚠️ Git push failed - continuing anyway")
                    
                # Small delay before next iteration
                await asyncio.sleep(1)
                
            except Exception as e:
                error_msg = f"Error in editor loop: {e}"
                logging.error(error_msg)
                update_status(error_msg)
                await asyncio.sleep(5)  # Longer delay on error
                
    except Exception as e:
        error_msg = f"Editor loop crashed: {e}"
        logging.error(error_msg)
        update_status(error_msg)
    finally:
        logging.info("Editor loop stopped")
        update_status("Editor loop stopped")

def toggle_browser():
    """Toggle browser automation"""
    if not hasattr(toggle_browser, 'browser_manager'):
        # Initialize browser manager on first use
        toggle_browser.browser_manager = BrowserManager(config)
        
    if toggle_browser.browser_manager.toggle_browser():
        browser_button.configure(text="⏸️ Browser")
        # Start browser loop in a new thread to handle asyncio
        browser_thread = threading.Thread(
            target=lambda: asyncio.run(toggle_browser.browser_manager.start_browser_automation()),
            daemon=True
        )
        browser_thread.start()
        update_status("▶️ Browser automation started")
    else:
        browser_button.configure(text="▶️ Browser")
        # Stop browser automation
        asyncio.run(toggle_browser.browser_manager.stop_browser_automation())
        update_status("⏸️ Browser automation stopped")

def toggle_editor():
    """Toggle the editor loop on/off"""
    global editor_active
    editor_active = not editor_active
    
    editor_play_pause_btn.config(text="⏸️ Editor" if editor_active else "▶️ Editor")
    
    if editor_active:
        # Start editor loop in a new thread to handle asyncio
        editor_thread = threading.Thread(
            target=lambda: asyncio.run(editor_loop()),
            daemon=True
        )
        editor_thread.start()
        update_status("▶️ Editor loop started")
    else:
        update_status("⏸️ Editor loop stopped")

# Global control variables
auto_recording_task = None  # To store the auto recording thread


async def process_buffer(buffer_manager: AudioBufferManager, screenshot: bytes):
    """Process recorded audio buffer"""
    global current_speaker
    
    try:
        # Convert buffer to WAV
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(RATE)
            wf.writeframes(buffer_manager.get_data())
        
        # Prepare request
        endpoint = emily_endpoint_var.get() if current_speaker == "emily" else daemon_endpoint_var.get()
        
        files = {
            'audio': ('audio.wav', wav_buffer.getvalue(), 'audio/wav'),
            'screenshot': ('screenshot.jpg', screenshot, 'image/jpeg')
        }
        
        # Send request with timeout and retry
        for attempt in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(endpoint, data=files, timeout=30) as response:
                        if response.status == 200:
                            response_data = await response.read()
                            # Play response with interrupt support
                            await process_audio_chunk(response_data, is_daemon=(current_speaker=="daemon"))
                            # Switch speakers
                            current_speaker = "daemon" if current_speaker == "emily" else "emily"
                            update_speaker_indicator()
                            break
            except Exception as e:
                if attempt == 2:
                    raise
                await asyncio.sleep(1)
                
    except Exception as e:
        logging.error(f"Buffer processing error: {e}")
        update_status(f"❌ Processing error: {str(e)}")

def cleanup_recording(stream: pyaudio.Stream, p: pyaudio.PyAudio):
    """Clean up recording resources"""
    if stream:
        try:
            stream.stop_stream()
            stream.close()
        except:
            pass
    if p:
        try:
            p.terminate()
        except:
            pass

async def start_smart_recording():
    """Handle continuous recording in smart mode with improved management"""
    global current_speaker
    
    buffer_manager = AudioBufferManager()
    vad = VoiceActivityDetector()
    screenshot_manager = ScreenshotManager()
    
    global smart_mode
    smart_mode = True
    try:
        p = pyaudio.PyAudio()
        input_device = get_input_device()
        
        stream = p.open(
            format=FORMAT,
            channels=1,
            rate=RATE,
            input=True,
            input_device_index=input_device,
            frames_per_buffer=AudioConstants.SMART_BUFFER_SIZE,
            start=True
        )
        
        last_screenshot_time = time.time()
        current_screenshot = None
        update_recording_status("Recording")
        
        while smart_mode and is_playing:
            try:
                # Handle screenshot timing
                current_time = time.time()
                if current_time - last_screenshot_time >= AudioConstants.SMART_SCREENSHOT_INTERVAL:
                    current_screenshot = await screenshot_manager.capture()
                    last_screenshot_time = current_time
                
                # Read and process audio
                data = stream.read(AudioConstants.SMART_BUFFER_SIZE, exception_on_overflow=False)
                if not buffer_manager.add(data):
                    logging.warning("Buffer full - processing now")
                    update_recording_status("Processing")
                    await process_buffer(buffer_manager, current_screenshot)
                    buffer_manager.clear()
                    update_recording_status("Recording")
                
                # Calculate and display audio level
                level = calculate_audio_level(data)
                root.after(0, lambda l=level: vu_meter.set_level(l))
                
                # Check for silence/speech end
                if vad.process(level):
                    if buffer_manager.current_size > 0:
                        update_recording_status("Processing")
                        await process_buffer(buffer_manager, current_screenshot)
                        buffer_manager.clear()
                        update_recording_status("Recording")
                    vad.reset()
                
            except OSError as e:
                logging.error(f"Stream read error: {e}")
                await asyncio.sleep(0.1)
                continue
            
            await asyncio.sleep(0.001)
            
    except Exception as e:
        logging.error(f"Smart recording error: {e}")
        update_status(f"❌ Smart recording error: {str(e)}")
    finally:
        update_recording_status("Idle")
        cleanup_recording(stream, p)



def create_status_indicators():
    """Create status indicators"""
    global recording_status, speaker_indicator
    
    status_frame = ttk.Frame(main_frame, style='Modern.TFrame')
    status_frame.pack(fill='x', pady=5)
    
    # Speaker indicator
    speaker_label = tk.Label(status_frame, text="Current Speaker:",
        bg=ThemeColors.BG_DARK,
        fg=ThemeColors.TEXT_PRIMARY)
    speaker_label.pack(side='left')
    
    speaker_indicator = tk.Label(status_frame, text="Emily",
        bg=ThemeColors.ACCENT_PRIMARY,
        fg=ThemeColors.TEXT_BRIGHT,
        padx=5)
    speaker_indicator.pack(side='left', padx=5)
    
    # Recording status
    recording_status = tk.Label(status_frame, text="Idle",
        bg=ThemeColors.BG_LIGHT,
        fg=ThemeColors.TEXT_SECONDARY)
    recording_status.pack(side='right')

def update_speaker_indicator():
    """Update the speaker indicator"""
    speaker_indicator.config(
        text="Emily" if current_speaker == "emily" else "Daemon",
        bg=ThemeColors.ACCENT_PRIMARY if current_speaker == "emily" 
           else ThemeColors.ACCENT_SECONDARY
    )

def update_recording_status(status: str):
    """Update recording status indicator"""
    global recording_status
    if recording_status and recording_status.winfo_exists():
        recording_status.config(text=status)
    else:
        logging.warning(f"Attempted to update recording status to '{status}' but label not ready")

def create_device_selectors():
    """Create modern-styled input and output device selection frame"""
    global ui_elements_created, editor_play_pause_btn, editor_active, browser_button
    
    # Check if UI elements have already been created
    if ui_elements_created:
        logging.warning("UI elements already created - skipping creation")
        return None, None, None, None, None, None, None
        
    logging.info("Creating UI elements for first time")
    ui_elements_created = True
    
    # Configure root window style
    root.configure(bg=ThemeColors.BG_DARK)
    
    # Configure ttk styles
    style = ttk.Style()
    style.configure('Modern.TCombobox',
        background=ThemeColors.BG_LIGHT,
        fieldbackground=ThemeColors.BG_LIGHT,
        foreground=ThemeColors.TEXT_PRIMARY,
        arrowcolor=ThemeColors.TEXT_PRIMARY)
    
    style.configure('Modern.TFrame', 
        background=ThemeColors.BG_DARK)

    # Create a SINGLE main frame to contain all controls
    main_frame = ttk.Frame(root, style='Modern.TFrame')
    main_frame.pack(fill='x', padx=10, pady=5)

    # Create status indicators right after main frame
    create_status_indicators()

    # Controls row (play/pause only)
    controls_frame = ttk.Frame(main_frame, style='Modern.TFrame')
    controls_frame.pack(fill='x', pady=(0, 5))

    # Play/Pause button 
    global play_pause_btn
    play_pause_btn = tk.Button(controls_frame, text="⏸️", width=3,
        command=toggle_play_pause,
        bg=ThemeColors.ACCENT_PRIMARY,
        fg=ThemeColors.TEXT_BRIGHT,
        relief='flat',
        activebackground=ThemeColors.BG_HOVER,
        activeforeground=ThemeColors.TEXT_BRIGHT,
        borderwidth=0,
        padx=10,
        pady=5)
    play_pause_btn.pack(side='left', padx=5)

    # Editor controls
    editor_frame = ttk.Frame(controls_frame, style='Modern.TFrame')
    editor_frame.pack(side='left', padx=5)

    editor_active = False
    editor_play_pause_btn = tk.Button(editor_frame, text="▶️ Editor",
        command=toggle_editor,
        bg=ThemeColors.ACCENT_SECONDARY,
        fg=ThemeColors.TEXT_BRIGHT,
        relief='flat',
        activebackground=ThemeColors.BG_HOVER,
        activeforeground=ThemeColors.TEXT_BRIGHT,
        borderwidth=0,
        padx=10,
        pady=5)
    editor_play_pause_btn.pack(side='left')

    # Browser controls
    browser_frame = ttk.Frame(controls_frame, style='Modern.TFrame')
    browser_frame.pack(side='left', padx=5)

    global browser_button
    browser_button = tk.Button(browser_frame, text="▶️ Browser",
        command=toggle_browser,
        bg=ThemeColors.ACCENT_SECONDARY,
        fg=ThemeColors.TEXT_BRIGHT,
        relief='flat',
        activebackground=ThemeColors.BG_HOVER,
        activeforeground=ThemeColors.TEXT_BRIGHT,
        borderwidth=0,
        padx=10,
        pady=5)
    browser_button.pack(side='left')


    # Device selection frame
    devices_frame = ttk.Frame(main_frame, style='Modern.TFrame')
    devices_frame.pack(fill='x', pady=5)

    # Input device
    input_frame = ttk.Frame(devices_frame, style='Modern.TFrame')
    input_frame.pack(fill='x', pady=2)
    tk.Label(input_frame, text="Input Device:",
        bg=ThemeColors.BG_DARK,
        fg=ThemeColors.TEXT_PRIMARY).pack(side='left')
    
    global mic_var
    mic_var = tk.StringVar()
    mic_combo = ttk.Combobox(input_frame, textvariable=mic_var, state='readonly', style='Modern.TCombobox')
    mic_combo.pack(side='left', fill='x', expand=True, padx=(5, 0))

    # Output device
    output_frame = ttk.Frame(devices_frame, style='Modern.TFrame')
    output_frame.pack(fill='x', pady=2)
    tk.Label(output_frame, text="Output Device:",
        bg=ThemeColors.BG_DARK,
        fg=ThemeColors.TEXT_PRIMARY).pack(side='left')
    
    global output_var
    output_var = tk.StringVar()
    output_combo = ttk.Combobox(output_frame, textvariable=output_var, state='readonly', style='Modern.TCombobox')
    output_combo.pack(side='left', fill='x', expand=True, padx=(5, 0))

    # Refresh button
    refresh_btn = tk.Button(devices_frame, text="🔄",
        command=lambda: refresh_devices(mic_combo, output_combo),
        bg=ThemeColors.ACCENT_SECONDARY,
        fg=ThemeColors.TEXT_BRIGHT,
        relief='flat',
        activebackground=ThemeColors.BG_HOVER,
        activeforeground=ThemeColors.TEXT_BRIGHT,
        borderwidth=0)
    refresh_btn.pack(side='right', padx=(5, 0))

    # VU meter
    vu_frame = ttk.Frame(main_frame, style='Modern.TFrame')
    vu_frame.pack(fill='x', pady=5)
    tk.Label(vu_frame, text="Input Level:",
        bg=ThemeColors.BG_DARK,
        fg=ThemeColors.TEXT_PRIMARY).pack(side='left')
    vu_meter = VUMeter(vu_frame, width=200, height=20)
    vu_meter.pack(side='left', fill='x', expand=True, padx=(5, 0))  # Added expand=True

    # Endpoints frame
    endpoints_frame = ttk.Frame(main_frame, style='Modern.TFrame')
    endpoints_frame.pack(fill='x', pady=5)

    # Emily endpoint
    emily_frame = ttk.Frame(endpoints_frame, style='Modern.TFrame')
    emily_frame.pack(fill='x', pady=2)
    tk.Label(emily_frame, text="Emily Endpoint:",
        bg=ThemeColors.BG_DARK,
        fg=ThemeColors.TEXT_PRIMARY).pack(side='left')
    emily_endpoint_var = tk.StringVar(value=NetworkConstants.DEFAULT_ENDPOINT_EMILY)
    emily_entry = tk.Entry(emily_frame, textvariable=emily_endpoint_var,
        bg=ThemeColors.BG_LIGHT,
        fg=ThemeColors.TEXT_PRIMARY,
        insertbackground=ThemeColors.TEXT_PRIMARY,
        relief='flat',
        highlightthickness=1,
        highlightbackground=ThemeColors.BORDER,
        highlightcolor=ThemeColors.ACCENT_SECONDARY)
    emily_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))

    # Daemon endpoint
    daemon_frame = ttk.Frame(endpoints_frame, style='Modern.TFrame')
    daemon_frame.pack(fill='x', pady=2)
    tk.Label(daemon_frame, text="Daemon Endpoint:",
        bg=ThemeColors.BG_DARK,
        fg=ThemeColors.TEXT_PRIMARY).pack(side='left')
    daemon_endpoint_var = tk.StringVar(value=NetworkConstants.DEFAULT_ENDPOINT_DAEMON)
    daemon_entry = tk.Entry(daemon_frame, textvariable=daemon_endpoint_var,
        bg=ThemeColors.BG_LIGHT,
        fg=ThemeColors.TEXT_PRIMARY,
        insertbackground=ThemeColors.TEXT_PRIMARY,
        relief='flat',
        highlightthickness=1,
        highlightbackground=ThemeColors.BORDER,
        highlightcolor=ThemeColors.ACCENT_SECONDARY)
    daemon_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))

    # Initial population of device lists
    refresh_devices(mic_combo, output_combo)

    return mic_var, output_var, mic_combo, output_combo, vu_meter, emily_endpoint_var, daemon_endpoint_var

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
root.title("AI Assistant")

# Create main frame to contain all controls
main_frame = ttk.Frame(root, style='Modern.TFrame')
main_frame.pack(fill='x', padx=10, pady=5)

# Create text widget first
text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20,
    bg=ThemeColors.BG_LIGHT,
    fg=ThemeColors.TEXT_PRIMARY,
    insertbackground=ThemeColors.TEXT_PRIMARY,
    relief='flat',
    padx=10,
    pady=5,
    font=('Segoe UI', 10),
    highlightthickness=1,
    highlightbackground=ThemeColors.BORDER,
    highlightcolor=ThemeColors.ACCENT_SECONDARY)
text_widget.pack(expand=True, fill='both', padx=10, pady=5)

# Create main controls frame
controls_frame = tk.Frame(root)
controls_frame.pack(fill='x', padx=5, pady=5)

# Add microphone selector and VU meter
mic_var, output_var, mic_combo, output_combo, vu_meter, emily_endpoint_var, daemon_endpoint_var = create_device_selectors()
mic_combo.bind('<<ComboboxSelected>>', lambda e: update_mic_status(mic_combo))
output_combo.bind('<<ComboboxSelected>>', lambda e: update_mic_status(output_combo))



def on_closing():
    """Handle application shutdown"""
    global running, vu_meter, is_recording, current_video_window, second_video_window
    
    logging.info("Starting application shutdown...")
    
    try:
        # Stop all processes
        running = False
        is_playing = False
        is_recording = False
        
        # Reset VU meter
        if vu_meter:
            try:
                vu_meter.set_level(0.0)
            except Exception as e:
                logging.error(f"Error resetting VU meter: {e}")

        # Clean up video windows
        if current_video_window:
            try:
                current_video_window.cleanup()
            except Exception as e:
                logging.error(f"Error cleaning up first video window: {e}")
        
        if second_video_window:
            try:
                second_video_window.cleanup()
            except Exception as e:
                logging.error(f"Error cleaning up second video window: {e}")

        # Stop pygame mixer
        try:
            pygame.mixer.quit()
        except Exception as e:
            logging.error(f"Error stopping pygame mixer: {e}")

        logging.info("Shutting down application...")
        
        # Force destroy after brief delay if normal shutdown fails
        root.after(100, force_quit)
        
        # Attempt normal shutdown
        root.quit()
        root.destroy()
        
    except Exception as e:
        logging.error(f"Error during shutdown: {e}")
        force_quit()

def force_quit():
    """Force quit the application if normal shutdown fails."""
    try:
        import os
        import signal
        logging.info("Forcing application quit...")
        if hasattr(signal, 'SIGKILL'):
            os.kill(os.getpid(), signal.SIGKILL)
        else:
            sys.exit(1)
    except Exception as e:
        logging.error(f"Error during force quit: {e}")
        sys.exit(1)


async def api_client(interval):
    """Execute recording/response cycles for both characters sequentially"""
    try:
        screenshot_manager = ScreenshotManager()
        if not is_playing:
            return
            
        # First character (Emily)
        update_status("Starting Emily's recording cycle...")
        
        # Take screenshots and ensure they're not None
        logging.info("Taking pre-recording screenshot for Emily...")
        pre_screenshot_emily = await screenshot_manager.capture()
        if pre_screenshot_emily is None:
            raise ValueError("Failed to capture pre-recording screenshot")
            
        # Record audio for Emily
        audio_data = record_audio(15)
        if audio_data is None:
            raise ValueError("Failed to record audio")
            
        post_screenshot_emily = await screenshot_manager.capture()
        if post_screenshot_emily is None:
            raise ValueError("Failed to capture post-recording screenshot")
        
        # Collect text content
        text_content = collect_text_files_content()

        # Prepare multipart form data with session ID
        files = {
            'pre_screenshot': ('pre_screenshot.jpg', pre_screenshot_emily, 'image/jpeg'),
            'post_screenshot': ('post_screenshot.jpg', post_screenshot_emily, 'image/jpeg'),
            'audio': ('audio.wav', audio_data, 'audio/wav')
        }

        # Add text content and session ID to form data
        data = {
            'text': text_content,
            'session': session_id
        }

        # Get endpoints from UI
        emily_endpoint = emily_endpoint_var.get()
        daemon_endpoint = daemon_endpoint_var.get()

        # Log request details
        logging.info(f"Sending request to Emily endpoint: {emily_endpoint}")
        logging.info(f"Files being sent: {[k for k in files.keys()]}")
        logging.info(f"Screenshot sizes - Pre: {len(pre_screenshot_emily)}, Post: {len(post_screenshot_emily)}")

        # Send request with explicit content types
        response = requests.post(
            emily_endpoint,
            data=data,
            files=files,
            timeout=NetworkConstants.REQUEST_TIMEOUT,
            headers={'Accept': 'application/octet-stream'}
        )

        # Log response details
        logging.info(f"Response status: {response.status_code}")
        logging.info(f"Response headers: {response.headers}")
        logging.info(f"Response content type: {response.headers.get('content-type')}")
        
        # Process Emily's response and wait for completion
        if response.status_code == 200:
            try:
                logging.info("Playing Emily's response...")
                await process_audio_chunk(response.content, is_daemon=False)
                logging.info("Emily's response completed")
            except Exception as e:
                logging.error(f"Error processing Emily's response: {e}")
                update_status(f"❌ Error playing response: {str(e)}")
                # Continue execution even if playback fails
            
        # Wait 1 second after Emily's response finishes
        logging.info("Waiting 1 second before Daemon's turn...")
        await asyncio.sleep(1)
        
        # Second character (Daemon)
        if not is_playing:  # Check if still playing after wait
            return
            
        update_status("Starting Daemon's recording cycle...")
        
        # Take pre-recording screenshot for Daemon
        logging.info("Taking pre-recording screenshot for Daemon...")
        pre_screenshot_daemon = await screenshot_manager.capture()
        
        # Record audio for Daemon
        logging.info("Starting 15-second recording for Daemon...")
        audio_data = record_audio(15)
        
        # Take post-recording screenshot for Daemon
        logging.info("Taking post-recording screenshot for Daemon...")
        post_screenshot_daemon = await screenshot_manager.capture()
        
        text_content = collect_text_files_content()

        data = {'text': text_content}
        files = {
            'pre_screenshot': ('pre_screenshot.jpg', pre_screenshot_daemon, 'image/jpeg'),
            'post_screenshot': ('post_screenshot.jpg', post_screenshot_daemon, 'image/jpeg'),
            'audio': ('audio.wav', audio_data, 'audio/wav')
        }

        # Send request for Daemon
        logging.info("Sending data to Daemon endpoint...")
        response = requests.post(
            daemon_endpoint,
            data=data,
            files=files,
            timeout=NetworkConstants.REQUEST_TIMEOUT
        )
        
        # Process Daemon's response and wait for completion
        if response.status_code == 200:
            logging.info("Playing Daemon's response...")
            # Only process audio once for Daemon
            await process_audio_chunk(response.content, is_daemon=True)
            logging.info("Daemon's response completed")
            
        # Log response details for debugging
        logging.info(f"Response status: {response.status_code}")
        logging.info(f"Response headers: {response.headers}")
        logging.info(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
                    
        # Inspect the raw binary content
        binary_data = response.content
        logging.info(f"Raw binary length: {len(binary_data)} bytes")
        
        # Basic validation of response
        if response.status_code != 200:
            logging.error(f"Error response from n8n: {response.status_code}")
            logging.error(f"Response content: {response.text[:1000]}")
            response.raise_for_status()
            
        if len(binary_data) < 1000:  # Arbitrary minimum size for valid audio
            logging.warning(f"Audio data suspiciously small: {len(binary_data)} bytes")
            raise ValueError("Audio data too small to be valid")

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

    # Add UTF-8 handler with DEBUG level
    handler = UTFStreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.DEBUG)

def init_screenshot():
    """Initialize screenshot capabilities"""
    logging.info("=== Initializing Screenshot System ===")
    try:
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = False
        
        # Test basic screenshot capability
        test_shot = pyautogui.screenshot()
        logging.info(f"Test screenshot successful: {test_shot.size}")
        
        # Test PIL fallback
        from PIL import ImageGrab
        test_grab = ImageGrab.grab()
        logging.info(f"Test ImageGrab successful: {test_grab.size}")
        
        return True
    except Exception as e:
        logging.error(f"Screenshot initialization failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    # Initialize logging first
    setup_logging()
    
    # Initialize visualization after root window exists
    try:
        logging.info("Starting repository visualization...")
        visualizer = start_visualization(root)
        if visualizer:
            logging.info("Repository visualization started")
        else:
            logging.warning("Failed to start visualization - continuing without it")
    except Exception as e:
        logging.error(f"Failed to start visualization: {e}")
        visualizer = None

    # Initialize screenshot system
    if not init_screenshot():
        messagebox.showwarning(
            "Screenshot Warning",
            "Screenshot system initialization failed.\n"
            "The application may not be able to capture screenshots."
        )
    
    def init_screenshot():
        """Initialize screenshot capabilities"""
        logging.info("=== Initializing Screenshot System ===")
        try:
            # Configure PyAutoGUI
            pyautogui.FAILSAFE = False
            
            # Test basic screenshot capability
            test_shot = pyautogui.screenshot()
            logging.info(f"Test screenshot successful: {test_shot.size}")
            
            # Test PIL fallback
            from PIL import ImageGrab
            test_grab = ImageGrab.grab()
            logging.info(f"Test ImageGrab successful: {test_grab.size}")
            
            return True
        except Exception as e:
            logging.error(f"Screenshot initialization failed: {e}", exc_info=True)
            return False

    # Initialize managers
    device_manager = DeviceManager()
    audio_manager = AudioManager(config)
    
    # Initialize screenshot system
    if not init_screenshot():
        messagebox.showwarning(
            "Screenshot Warning",
            "Screenshot system initialization failed.\n"
            "The application may not be able to capture screenshots."
        )
    
    parser = argparse.ArgumentParser(
        description="CK3 AI Character with OpenAI Real-Time API",
        epilog="Before running, ensure you have:\n"
               "1. Installed dependencies: pip install -r requirements.txt"
    )
    parser.add_argument("--interval", type=int, default=DEFAULT_SCREENSHOT_INTERVAL,
                        help=f"Screenshot interval in seconds (default: {DEFAULT_SCREENSHOT_INTERVAL})")
    args = parser.parse_args()
    
    # Generate session ID and initialize logging
    session_id = NetworkConstants.generate_session_id()
    logging.info(f"Starting CK3 AI Assistant (Session: {session_id})...")
    
    # Initialize UI and get endpoint variables
    try:
        logging.info("Initializing UI...")
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.wm_attributes("-topmost", 0)  # Ensure window isn't stuck on top
        text_widget.insert(tk.END, "Initializing CK3 AI Assistant...\n")
        root.update()
            
        # Create UI elements ONCE
        result = create_device_selectors()
        if result[0] is not None:  # Only assign if creation was successful
            mic_var, output_var, mic_combo, output_combo, vu_meter, emily_endpoint_var, daemon_endpoint_var = result

        # Initialize video window in a separate thread
        def create_test_video():
            """Create test idle and talk videos if they don't exist"""
            video_logger.info("Creating test videos")
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                videos_dir = os.path.join(script_dir, "videos")
                idle_path = os.path.join(videos_dir, "loop.mp4")
                talk_path = os.path.join(videos_dir, "talk.mp4")
                idle_path2 = os.path.join(videos_dir, "loop2.mp4")
                talk_path2 = os.path.join(videos_dir, "talk2.mp4")

                if not os.path.exists(videos_dir):
                    os.makedirs(videos_dir)
                    video_logger.info(f"Created videos directory: {videos_dir}")

                # Utiliser un codec compatible avec votre système
                if sys.platform == 'win32':
                    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
                else:
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Fallback codec

                # Create first set of videos (green circle)
                if not os.path.exists(idle_path):
                    out = cv2.VideoWriter(idle_path, fourcc, 30.0, (320,240), isColor=True)
                    if not out.isOpened():
                        raise Exception("Failed to create idle video writer")
                    for i in range(90):
                        frame = np.zeros((240,320,3), dtype=np.uint8)
                        x = 160 + int(100*np.sin(2*np.pi*i/90))
                        cv2.circle(frame, (x, 120), 20, (0,255,0), -1)
                        out.write(frame)
                    out.release()

                if not os.path.exists(talk_path):
                    out = cv2.VideoWriter(talk_path, fourcc, 30.0, (320,240), isColor=True)
                    if not out.isOpened():
                        raise Exception("Failed to create talk video writer")
                    for i in range(90):
                        frame = np.zeros((240,320,3), dtype=np.uint8)
                        y = 120 + int(60*np.sin(2*np.pi*i/90))
                        cv2.circle(frame, (160, y), 20, (0,255,0), -1)
                        out.write(frame)
                    out.release()

                # Create second set of videos (red circle)
                if not os.path.exists(idle_path2):
                    out = cv2.VideoWriter(idle_path2, fourcc, 30.0, (320,240), isColor=True)
                    if not out.isOpened():
                        raise Exception("Failed to create idle2 video writer")
                    for i in range(90):
                        frame = np.zeros((240,320,3), dtype=np.uint8)
                        x = 160 + int(100*np.sin(2*np.pi*i/90))
                        cv2.circle(frame, (x, 120), 20, (0,0,255), -1)
                        out.write(frame)
                    out.release()

                if not os.path.exists(talk_path2):
                    out = cv2.VideoWriter(talk_path2, fourcc, 30.0, (320,240), isColor=True)
                    if not out.isOpened():
                        raise Exception("Failed to create talk2 video writer")
                    for i in range(90):
                        frame = np.zeros((240,320,3), dtype=np.uint8)
                        y = 120 + int(60*np.sin(2*np.pi*i/90))
                        cv2.circle(frame, (160, y), 20, (0,0,255), -1)
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
        
            logging.info(f"Video directory path: {videos_dir}")
            logging.info(f"Video files present: {os.listdir(videos_dir) if os.path.exists(videos_dir) else 'directory not found'}")
        
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
            """Create video windows in the main thread"""
            try:
                # Create first video window (Emily) with loop2.mp4
                videos_dir = os.path.dirname(video_path)
                video_path2 = os.path.join(videos_dir, "loop2.mp4")
                video_window1 = DraggableVideoWindow(video_path2)  # Emily uses loop2/talk2

                # Create second video window (Daemon) with loop.mp4
                video_window2 = DraggableVideoWindow(video_path)  # Daemon uses loop/talk

                # Store references to prevent garbage collection
                global current_video_window, second_video_window
                current_video_window = video_window1  # Emily's window
                second_video_window = video_window2   # Daemon's window

                # Offset second window position
                second_video_window.window.geometry(f"+{300}+{100}")  # Offset by 300 pixels
        
                logging.info("Video windows created successfully")
            except Exception as e:
                logging.error(f"Failed to create video windows in main thread: {e}", exc_info=True)

        # Initialize video subsystem first
        if not init_video():
            messagebox.showwarning(
                "Video Warning",
                "Video subsystem initialization failed. The application will continue without video support."
            )
        
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
        if 'visualizer' in locals():
            visualizer.stop()

print("Pour exécuter ce script, utilisez la commande : python main.py")
