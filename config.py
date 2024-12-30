"""Configuration settings for CK3 AI Assistant"""

import os
import secrets
from pathlib import Path
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

    # API settings
    API_PORT = 5000
    API_DEBUG = False
    API_TOKEN = os.getenv("API_TOKEN", secrets.token_urlsafe(32))
    
    # Visualization settings
    VISUALIZATION_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output", "visualizations")
    DEFAULT_PLOT_STYLE = "seaborn-darkgrid"
    CHART_DPI = 300
    CHART_FIGSIZE = (10, 6)
    
    def validate(self):
        """Validate configuration settings"""
        if not isinstance(self.SCREENSHOT_INTERVAL, int) or self.SCREENSHOT_INTERVAL <= 0:
            raise ValueError("Invalid screenshot interval")
        
        # Create visualization output directory if it doesn't exist
        os.makedirs(self.VISUALIZATION_OUTPUT_DIR, exist_ok=True)
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
        if not isinstance(self.API_PORT, int) or not (1024 <= self.API_PORT <= 65535):
            raise ValueError("Invalid API port number")
        if not isinstance(self.API_TOKEN, str) or len(self.API_TOKEN) < 32:
            raise ValueError("Invalid API token")
