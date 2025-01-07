"""Audio recording and playback management"""

import os
import asyncio
import pyaudio
import wave
import pygame
import logging
import io
import time
from contextlib import contextmanager
from typing import Optional, Generator
from device_manager import DeviceManager

class AudioManager:
    def __init__(self, config):
        self.config = config
        self.device_manager = DeviceManager()
        self.recording_stream = None
        self.desktop_stream = None
        self.is_playing = True
        self.is_recording = False
        pygame.mixer.init()
        logging.info("=== Audio Manager Initialization ===")
        if not self.test_microphone_access():
            logging.warning("Microphone access test failed - audio recording may not work")

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
                    format=self.p.get_format_from_width(self.config.AUDIO_FORMAT // 8),
                    channels=self.config.CHANNELS,
                    rate=self.config.SAMPLE_RATE,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=self.config.CHUNK_SIZE,
                    start=True
                )
                
                # Try to read a single chunk with timeout
                import time
                start_time = time.time()
                timeout = 2.0  # 2 second timeout
                while time.time() - start_time < timeout:
                    try:
                        data = test_stream.read(self.config.CHUNK_SIZE, exception_on_overflow=False)
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
                        rate=self.config.SAMPLE_RATE,
                        input=True,
                        input_device_index=default_index,
                        frames_per_buffer=self.config.CHUNK_SIZE,
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
                                rate=self.config.SAMPLE_RATE,
                                input=True,
                                input_device_index=i,
                                frames_per_buffer=self.config.CHUNK_SIZE,
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
                                rate=self.config.SAMPLE_RATE,
                                input=True,
                                input_device_index=i,
                                frames_per_buffer=self.config.CHUNK_SIZE,
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
            self.recording_stream = self.p.open(
                format=pyaudio.paFloat32,  # Higher precision format
                channels=1,
                rate=44100,  # CD quality
                input=True,
                input_device_index=input_device,
                frames_per_buffer=4096,  # Larger buffer
                stream_callback=None  # Disable callback for direct reading
            )
            yield self.recording_stream
        finally:
            if self.recording_stream:
                self.recording_stream.stop_stream()
                self.recording_stream.close()
                self.recording_stream = None

    def record_audio(self, duration: int) -> bytes:
        """Record audio with proper resource management and error recovery"""
        max_retries = 3
        retry_delay = 1.0  # seconds
        retry_count = 0
        
        logging.info("=== Starting Audio Recording ===")
        logging.info(f"Requested duration: {duration} seconds")
        
        while retry_count < max_retries:
            try:
                frames = []
                device_index = self.get_input_device()
                device_info = self.p.get_device_info_by_index(device_index)
                logging.info(f"Using device: {device_info['name']}")
                
                # Use standard audio settings
                BUFFER_SIZE = 2048  # Standard buffer size
                SAMPLE_RATE = 16000  # Standard sample rate for speech
                FORMAT = pyaudio.paInt16  # 16-bit PCM
                
                stream = self.p.open(
                    format=FORMAT,
                    channels=1,
                    rate=SAMPLE_RATE,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=BUFFER_SIZE
                )
                
                if not stream.is_active():
                    logging.error("Stream not active after opening")
                    raise RuntimeError("Audio stream not active")
                
                logging.info("Stream opened successfully")
                
                # Calculate chunks based on duration
                chunks = int(SAMPLE_RATE / BUFFER_SIZE * duration)
                logging.info(f"Will record {chunks} chunks")
                
                is_recording = True
                start_time = time.time()
                
                for i in range(chunks):
                    if not self.is_playing or not self.is_recording:
                        logging.info("Recording interrupted")
                        break
                    
                    try:
                        data = stream.read(BUFFER_SIZE, exception_on_overflow=False)
                        frames.append(data)
                        
                        # Calculate and update VU meter if callback is set
                        if hasattr(self, 'level_callback'):
                            level = self._calculate_audio_level(data)
                            self.level_callback(level)
                        
                        # Update progress every second
                        if i % (SAMPLE_RATE // BUFFER_SIZE) == 0:
                            elapsed = time.time() - start_time
                            self._update_status(f"🎤 Recording... {int(elapsed)}/{duration}s")
                            
                    except Exception as e:
                        logging.warning(f"Stream read error: {e}")
                        continue
                
                stream.stop_stream()
                stream.close()
                
                # Create WAV buffer with correct settings
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, 'wb') as wf:
                    wf.setnchannels(1)        # Mono
                    wf.setsampwidth(2)        # 16-bit
                    wf.setframerate(SAMPLE_RATE)
                    wf.writeframes(b''.join(frames))
                
                logging.info(f"Recording completed - {len(frames)} chunks recorded")
                return wav_buffer.getvalue()
                
            except Exception as e:
                retry_count += 1
                logging.error(f"Recording attempt {retry_count} failed: {e}")
                if retry_count >= max_retries:
                    raise RuntimeError(f"Failed to record audio after {max_retries} attempts")
                time.sleep(retry_delay)
                
            except Exception as e:
                retry_count += 1
                logging.error(f"Recording attempt {retry_count} failed: {e}")
                if retry_count >= max_retries:
                    raise RuntimeError(f"Failed to record audio after {max_retries} attempts")
                # Reset PyAudio instance before retry
                self.cleanup()
                self.p = pyaudio.PyAudio()
                time.sleep(retry_delay)

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
