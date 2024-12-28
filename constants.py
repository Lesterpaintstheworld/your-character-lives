"""Constants used throughout the application"""

class AudioConstants:
    CHUNK_SIZE = 1024
    FORMAT = 16  # bits
    CHANNELS = 1
    SAMPLE_RATE = 24000
    RECORD_DURATION = 15  # seconds

class NetworkConstants:
    REQUEST_TIMEOUT = 120
    RECONNECT_DELAY = 5
    MAX_RETRIES = 3
    DEFAULT_SCREENSHOT_INTERVAL = 30  # seconds
    DEFAULT_ENDPOINT_EMILY = "https://nlr.app.n8n.cloud/webhook/ai-assistant-emily"
    DEFAULT_ENDPOINT_DAEMON = "https://nlr.app.n8n.cloud/webhook/ai-assistant-daemon"

class UIConstants:
    WINDOW_WIDTH = 80
    WINDOW_HEIGHT = 20
    UPDATE_INTERVAL = 100  # ms
