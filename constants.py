"""Constants used throughout the application"""

class ThemeColors:
    BG_DARK = "#1a1a2e"  # Dark blue background
    BG_LIGHT = "#16213e"  # Slightly lighter blue for contrast
    ACCENT = "#0f3460"    # Medium blue for buttons/controls
    HIGHLIGHT = "#533483" # Purple highlight
    TEXT = "#e94560"      # Accent text color
    TEXT_LIGHT = "#ffffff"# Light text
    TEXT_GRAY = "#a2a2a2" # Secondary text

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
