"""Audio recording and playback management"""
import os
import re
import asyncio
import sounddevice as sd
import numpy as np
import wave
import pygame
import logging
import io
import time
import pyaudio
from contextlib import contextmanager
from typing import Optional
from device_manager import DeviceManager

class AudioManager:
    def __init__(self, config):
        self.config = config
        self.p = pyaudio.PyAudio()  # Initialize PyAudio instance
        self.device_manager = DeviceManager()
        self.recording_stream = None
        self.desktop_stream = None
        self.is_playing = True
        self.is_recording = False
        pygame.mixer.init()
        logging.info("=== Audio Manager Initialization ===")
        if not self.test_microphone_access():
            logging.warning("Microphone access test failed - audio recording may not work")

    def __del__(self):
        """Cleanup PyAudio on deletion"""
        if hasattr(self, 'p'):
            self.p.terminate()

    def test_microphone_access(self) -> bool:
        """Test if we can access the microphone."""
        try:
            logging.info("Testing microphone access...")
            device_index = self.get_input_device()
            if device_index is None:
                logging.error("No input device found")
                return False
                
            device_info = self.p.get_device_info_by_index(device_index)
            logging.info(f"Testing device: {device_info['name']}")
            
            # Add timeout for device test
            test_stream = None
            try:
                test_stream = self.p.open(
                    format=pyaudio.paInt16,  # Use direct format instead of config
                    channels=1,              # Use mono for test
                    rate=16000,             # Use lower sample rate for test
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=1024,  # Use smaller buffer for test
                    start=False
                )
                test_stream.start_stream()
                
                # Try to read a single chunk with timeout
                start_time = time.time()
                timeout = 2.0  # 2 second timeout
                while time.time() - start_time < timeout:
                    try:
                        data = test_stream.read(1024, exception_on_overflow=False)
                        if data:
                            logging.info("Microphone test successful")
                            return True
                    except OSError as e:
                        if "Unanticipated host error" in str(e):
                            logging.warning(f"Host error during test: {e}")
                            time.sleep(0.1)
                            continue
                        raise
                
                logging.error("Microphone test timed out")
                return False
                
            finally:
                if test_stream:
                    test_stream.stop_stream()
                    test_stream.close()
                    
        except Exception as e:
            logging.error(f"Microphone test failed: {e}")
            return False

    def get_input_device(self) -> Optional[int]:
        """Find and verify the input audio device."""
        max_retries = 3
        retry_delay = 1.0  # seconds
        
        for attempt in range(max_retries):
            try:
                # Log all available audio devices first
                logging.info(f"=== Available Audio Devices (Attempt {attempt + 1}/{max_retries}) ===")
                for i in range(self.p.get_device_count()):
                    try:
                        device_info = self.p.get_device_info_by_index(i)
                        logging.info(f"Device {i}: {device_info['name']}")
                        logging.info(f"  Max Input Channels: {device_info['maxInputChannels']}")
                        logging.info(f"  Default Sample Rate: {device_info['defaultSampleRate']}")
                        logging.info(f"  Is Default Input: {device_info.get('isDefaultInput', False)}")
                    except Exception as e:
                        logging.error(f"Error getting info for device {i}: {e}")

                # Try to use default input device first
                try:
                    default_device_info = self.p.get_default_input_device_info()
                    logging.info(f"Attempting to use default input device: {default_device_info['name']}")
                    default_index = default_device_info['index']
                    
                    test_stream = self.p.open(
                        format=self.p.get_format_from_width(self.config.AUDIO_FORMAT // 8),
                        channels=self.config.CHANNELS,
                        rate=16000,  # Try lower sample rate
                        input=True,
                        input_device_index=default_index,
                        frames_per_buffer=1024,  # Smaller buffer
                        start=False
                    )
                    test_stream.close()
                    logging.info(f"Successfully initialized default input device")
                    return default_index
                except Exception as e:
                    logging.warning(f"Default input device failed: {e}")

                # First try to find a working microphone device
                for i in range(self.p.get_device_count()):
                    device_info = self.p.get_device_info_by_index(i)
                    if (device_info['maxInputChannels'] > 0 and 
                        'Microphone' in device_info['name']):
                        try:
                            test_stream = self.p.open(
                                format=self.p.get_format_from_width(self.config.AUDIO_FORMAT // 8),
                                channels=self.config.CHANNELS,
                                rate=16000,  # Try lower sample rate
                                input=True,
                                input_device_index=i,
                                frames_per_buffer=1024,  # Smaller buffer
                                start=False
                            )
                            test_stream.close()
                            logging.info(f"Selected working input device: {device_info['name']}")
                            return i
                        except Exception as e:
                            logging.warning(f"Device {device_info['name']} test failed: {e}")
                            continue

                # If no microphone found, try any input device
                for i in range(self.p.get_device_count()):
                    device_info = self.p.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        try:
                            test_stream = self.p.open(
                                format=self.p.get_format_from_width(self.config.AUDIO_FORMAT // 8),
                                channels=self.config.CHANNELS,
                                rate=16000,  # Try lower sample rate
                                input=True,
                                input_device_index=i,
                                frames_per_buffer=1024,  # Smaller buffer
                                start=False
                            )
                            test_stream.close()
                            logging.info(f"Selected fallback input device: {device_info['name']}")
                            return i
                        except Exception as e:
                            logging.warning(f"Fallback device {device_info['name']} test failed: {e}")
                            continue

                raise RuntimeError("No working input device found")
            except Exception as e:
                if attempt < max_retries - 1:
                    logging.error(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(retry_delay)
                    continue
                logging.error(f"Error finding input device: {e}")
                raise RuntimeError("Failed to initialize audio input device")

    @contextmanager
    def open_streams(self):
        """Context manager for handling audio streams"""
        try:
            input_device = self.get_input_device()
            self.recording_stream = sd.InputStream(
                device=input_device,
                channels=1,
                samplerate=44100,  # CD quality
                blocksize=4096,  # Larger buffer
                dtype=np.float32  # Higher precision format
            )
            yield self.recording_stream
        finally:
            if self.recording_stream:
                self.recording_stream.stop_stream()
                self.recording_stream.close()
                self.recording_stream = None

    def record_audio(self, duration: int, mic_var) -> bytes:
        """Record audio with detailed diagnostics"""
        max_retries = 3
        retry_delay = 1.0
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logging.info("\n=== Starting Audio Recording with Diagnostics ===")
                logging.info(f"Requested duration: {duration} seconds")

                p = None
                stream = None
                frames = []
                
                try:
                    # Get selected mic index with validation
                    selected = mic_var.get()
                    if not selected:
                        raise Exception("No microphone selected")
                        
                    match = re.search(r'Device (\d+)', selected)
                    if not match:
                        raise Exception("Invalid microphone selection")
                        
                    device_index = int(match.group(1))
                    logging.info(f"Using input device index: {device_index}")

                    # Initialize PyAudio
                    p = pyaudio.PyAudio()
                    device_info = p.get_device_info_by_index(device_index)
                    logging.info(f"Device name: {device_info['name']}")
                    logging.info(f"Max input channels: {device_info['maxInputChannels']}")
                    logging.info(f"Default sample rate: {device_info['defaultSampleRate']}")
                    
                    # Configure for more stable recording
                    CHUNK = 1024  # Smaller chunks
                    FORMAT = pyaudio.paInt16  # 16-bit
                    CHANNELS = device_info['maxInputChannels']  # Use device's max input channels
                    RATE = int(device_info['defaultSampleRate'])  # Use device's default sample rate
                    
                    logging.info("\n=== Recording Configuration ===")
                    logging.info(f"Format: 16-bit PCM")
                    logging.info(f"Channels: {CHANNELS} (Mono)")
                    logging.info(f"Sample Rate: {RATE} Hz")
                    logging.info(f"Chunk Size: {CHUNK}")

                    # Open stream with explicit settings
                    stream = p.open(
                        format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=CHUNK,
                        start=False  # Don't start yet
                    )

                    # Start stream explicitly
                    stream.start_stream()
                    if not stream.is_active():
                        raise RuntimeError("Failed to start audio stream")

                    # Calculate frames needed
                    total_frames = int(RATE * duration)
                    chunks_needed = total_frames // CHUNK
                    logging.info(f"\nWill record {chunks_needed} chunks ({total_frames} frames)")

                    # Record with timing and monitoring
                    start_time = time.time()
                    bytes_recorded = 0
                    
                    for i in range(chunks_needed):
                        if not self.is_playing:
                            logging.info("Recording stopped by user")
                            break
                            
                        try:
                            data = stream.read(CHUNK, exception_on_overflow=False)
                            frames.append(data)
                            bytes_recorded += len(data)
                            
                            # Monitor progress every second
                            elapsed = time.time() - start_time
                            if i % (RATE // CHUNK) == 0:  # Once per second
                                logging.info(f"Progress: {int(elapsed)}s / {duration}s")
                                
                            # Update VU meter less frequently
                            if i % 4 == 0:
                                level = np.max(np.frombuffer(data, dtype=np.int16)) / 32768.0
                                if hasattr(self, 'level_callback'):
                                    self.level_callback(level)
                                    
                        except Exception as e:
                            logging.error(f"Error reading chunk {i}: {e}")
                            continue

                    # Calculate final statistics
                    end_time = time.time()
                    total_time = end_time - start_time
                    total_bytes = sum(len(f) for f in frames)

                    logging.info("\n=== Recording Complete ===")
                    logging.info(f"Total bytes: {total_bytes}")
                    logging.info(f"Total time: {total_time:.2f} seconds")
                    
                    # Create WAV with explicit format
                    wav_buffer = io.BytesIO()
                    with wave.open(wav_buffer, 'wb') as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(2)  # 16-bit
                        wf.setframerate(RATE)
                        wf.writeframes(b''.join(frames))
                        
                    wav_size = wav_buffer.tell()
                    logging.info(f"WAV file size: {wav_size} bytes")
                    
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

            except Exception as e:
                retry_count += 1
                logging.error(f"Recording attempt {retry_count} failed: {e}")
                if retry_count >= max_retries:
                    raise RuntimeError(f"Failed to record audio after {max_retries} attempts")
                # Reset sounddevice before retry
                self.cleanup()
                sd.default.reset()
                time.sleep(retry_delay)
                
        raise RuntimeError(f"Failed to record audio after {max_retries} attempts")

    async def play_audio(self, audio_data: bytes):
        """Play audio data with proper cleanup"""
        temp_file = 'temp_audio.mp3'
        try:
            with open(temp_file, 'wb') as f:
                f.write(audio_data if isinstance(audio_data, bytes) else audio_data.encode())
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
        finally:
            pygame.mixer.music.unload()
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def cleanup(self):
        """Clean up audio resources"""
        if self.recording_stream:
            self.recording_stream.stop_stream()
            self.recording_stream.close()
        if self.desktop_stream:
            self.desktop_stream.stop_stream()
            self.desktop_stream.close()
        self.device_manager.cleanup()
        pygame.mixer.quit()
    def _calculate_audio_level(self, audio_data):
        """Calculate audio level from raw audio data"""
        import numpy as np
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

    def _update_status(self, message):
        """Update status if callback is set"""
        if hasattr(self, 'status_callback'):
            self.status_callback(message)

    def set_callbacks(self, level_callback=None, status_callback=None):
        """Set callbacks for level meter and status updates"""
        if level_callback:
            self.level_callback = level_callback
        if status_callback:
            self.status_callback = status_callback
