"""Configuration settings for CK3 AI Assistant"""

import os
from dataclasses import dataclass

@dataclass
class Config:
    # Screenshot settings
    SCREENSHOT_INTERVAL = 30  # seconds
    SCREENSHOT_MAX_SIZE = (1024, 576)
    SCREENSHOT_QUALITY = 85

    # Audio settings
    CHUNK_SIZE = 1024
    AUDIO_FORMAT = 16  # bits
    CHANNELS = 1
    SAMPLE_RATE = 24000
    RECORD_DURATION = 15  # seconds

    # Network settings
    REQUEST_TIMEOUT = 120
    N8N_ENDPOINT = "https://nlr.app.n8n.cloud/webhook/ycl-enpoint"
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    def validate(self):
        """Validate configuration settings"""
        if not isinstance(self.SCREENSHOT_INTERVAL, int) or self.SCREENSHOT_INTERVAL <= 0:
            raise ValueError("Invalid screenshot interval")
        if not isinstance(self.AUDIO_FORMAT, int):
            raise ValueError("Invalid audio format")
        if not isinstance(self.CHANNELS, int) or self.CHANNELS <= 0:
            raise ValueError("Invalid number of channels")
        if not isinstance(self.SAMPLE_RATE, int) or self.SAMPLE_RATE <= 0:
            raise ValueError("Invalid sample rate")
        if not self.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found in environment")
        if not self.OPENAI_API_KEY.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format")
