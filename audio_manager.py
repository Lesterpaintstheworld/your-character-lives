"""Audio recording and playback management"""

import pyaudio
import wave
import pygame
import logging
import io
from contextlib import contextmanager
from typing import Optional, Generator

class AudioManager:
    def __init__(self, config):
        self.config = config
        self.p = pyaudio.PyAudio()
        self.recording_stream = None
        self.desktop_stream = None
        pygame.mixer.init()

    def get_input_device(self) -> Optional[int]:
        """Find and verify the input audio device."""
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                logging.info(f"Selected input device: {device_info['name']}")
                return i
        raise RuntimeError("No microphone or input device detected")

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
        """Record audio with proper resource management"""
        frames = []
        
        with self.open_streams() as stream:
            for _ in range(0, int(self.config.SAMPLE_RATE / self.config.CHUNK_SIZE * duration)):
                try:
                    data = stream.read(self.config.CHUNK_SIZE, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    logging.error(f"Error during recording: {e}")
                    raise

        # Create WAV buffer
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(self.config.CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(
                self.p.get_format_from_width(self.config.AUDIO_FORMAT // 8)))
            wf.setframerate(self.config.SAMPLE_RATE)
            wf.writeframes(b''.join(frames))
        
        return wav_buffer.getvalue()

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
