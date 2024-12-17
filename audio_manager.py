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

class AudioManager:
    def __init__(self, config):
        self.config = config
        self.p = pyaudio.PyAudio()
        self.recording_stream = None
        self.desktop_stream = None
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
            
            test_stream = self.p.open(
                format=self.p.get_format_from_width(self.config.AUDIO_FORMAT // 8),
                channels=self.config.CHANNELS,
                rate=self.config.SAMPLE_RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.config.CHUNK_SIZE,
                start=True
            )
            
            # Try to read a single chunk
            data = test_stream.read(self.config.CHUNK_SIZE, exception_on_overflow=False)
            test_stream.close()
            
            if data:
                logging.info("Microphone test successful")
                return True
            else:
                logging.error("No data received from microphone")
                return False
                
        except Exception as e:
            logging.error(f"Microphone test failed: {e}")
            return False

    def get_input_device(self) -> Optional[int]:
        """Find and verify the input audio device."""
        try:
            # Log all available audio devices first
            logging.info("=== Available Audio Devices ===")
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
            logging.error(f"Error finding input device: {e}")
            raise RuntimeError("Failed to initialize audio input device")

    @contextmanager
    def open_streams(self):
        """Context manager for handling audio streams"""
        try:
            input_device = self.get_input_device()
            self.recording_stream = self.p.open(
                format=self.p.get_format_from_width(self.config.AUDIO_FORMAT // 8),
                channels=self.config.CHANNELS,
                rate=self.config.SAMPLE_RATE,
                input=True,
                input_device_index=input_device,
                frames_per_buffer=self.config.CHUNK_SIZE
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
        retry_count = 0
        
        logging.info("=== Starting Audio Recording ===")
        logging.info(f"Requested duration: {duration} seconds")
        
        while retry_count < max_retries:
            try:
                frames = []
                device_index = self.get_input_device()
                device_info = self.p.get_device_info_by_index(device_index)
                logging.info(f"Using device: {device_info['name']}")
                logging.info(f"Device index: {device_index}")
                
                with self.open_streams() as stream:
                    if not stream.is_active():
                        logging.error("Stream not active after opening")
                        raise RuntimeError("Audio stream not active")
                        
                    logging.info("Stream opened successfully")
                    
                    chunks_to_record = int(self.config.SAMPLE_RATE / self.config.CHUNK_SIZE * duration)
                    logging.info(f"Will record {chunks_to_record} chunks")
                    
                    for chunk in range(chunks_to_record):
                        try:
                            data = stream.read(self.config.CHUNK_SIZE, exception_on_overflow=False)
                            if not data:
                                logging.error(f"No data received for chunk {chunk}")
                                continue
                            frames.append(data)
                            if chunk % 10 == 0:  # Log every 10th chunk
                                logging.debug(f"Recorded chunk {chunk}/{chunks_to_record}")
                        except Exception as e:
                            logging.error(f"Error recording chunk {chunk}: {e}")
                            raise

                if not frames:
                    logging.error("No audio data was recorded")
                    raise RuntimeError("No audio data recorded")
                    
                logging.info(f"Successfully recorded {len(frames)} chunks")
                
                # Create WAV buffer
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, 'wb') as wf:
                    wf.setnchannels(self.config.CHANNELS)
                    wf.setsampwidth(self.p.get_sample_size(
                        self.p.get_format_from_width(self.config.AUDIO_FORMAT // 8)))
                    wf.setframerate(self.config.SAMPLE_RATE)
                    wf.writeframes(b''.join(frames))
                
                logging.info("Successfully created WAV buffer")
                return wav_buffer.getvalue()
                
            except Exception as e:
                retry_count += 1
                logging.error(f"Recording attempt {retry_count} failed: {e}")
                if retry_count >= max_retries:
                    raise RuntimeError(f"Failed to record audio after {max_retries} attempts")
                # Reset PyAudio instance before retry
                self.cleanup()
                self.p = pyaudio.PyAudio()
                time.sleep(1)  # Wait before retry

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
        self.p.terminate()
        pygame.mixer.quit()
