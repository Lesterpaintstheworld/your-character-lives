"""Constants used throughout the application"""

class AudioConstants:
    CHUNK_SIZE = 1024  # Smaller chunks
    FORMAT = 'int16'
    CHANNELS = 1       # Mono only
    SAMPLE_RATE = 16000  # Lower sample rate
    BITS_PER_SAMPLE = 16
    SILENCE_THRESHOLD = -60
    MIN_SILENCE_DURATION = 3.0
    SMART_SCREENSHOT_INTERVAL = 20
    FIXED_RECORDING_DURATION = 20  # Fixed duration in seconds
    FIXED_BUFFER_SIZE = 2048      # Optimized buffer size
    FIXED_SAMPLE_RATE = 16000     # Fixed sample rate
    SMART_BUFFER_SIZE = 1024  # Match chunk size
    MAX_RECORDING_SIZE = 500 * 1024 * 1024

class NetworkConstants:
    REQUEST_TIMEOUT = 120
    RECONNECT_DELAY = 5
    MAX_RETRIES = 3
    DEFAULT_ENDPOINT_EMILY = "https://nlr.app.n8n.cloud/webhook/kinos-emily"
    DEFAULT_ENDPOINT_DAEMON = "https://nlr.app.n8n.cloud/webhook/kinos-daemon"

    @staticmethod
    def generate_session_id():
        """Generate a unique session ID"""
        import uuid
        return str(uuid.uuid4())

class ThemeColors:
    # Main backgrounds
    BG_DARK = "#0d1117"      # Darker navy blue for main background
    BG_LIGHT = "#161b22"     # Slightly lighter navy for controls
    BG_HOVER = "#21262d"     # Hover state for interactive elements
    
    # Accents
    ACCENT_PRIMARY = "#2ea043"    # Green for primary actions
    ACCENT_SECONDARY = "#1f6feb"  # Blue for secondary actions
    ACCENT_WARNING = "#d29922"    # Orange for warnings
    
    # Text colors
    TEXT_PRIMARY = "#c9d1d9"      # Main text color
    TEXT_SECONDARY = "#8b949e"    # Secondary text
    TEXT_BRIGHT = "#ffffff"       # Bright text for emphasis
    
    # VU Meter
    VU_LOW = "#238636"        # Green for low levels
    VU_MID = "#1f6feb"        # Blue for mid levels
    VU_HIGH = "#da3633"       # Red for high levels
    
    # Borders
    BORDER = "#30363d"        # Subtle border color

class UIConstants:
    WINDOW_WIDTH = 80
    WINDOW_HEIGHT = 20
    UPDATE_INTERVAL = 100  # ms

class BrowserConstants:
    HEADLESS_MODE = False
    BROWSER_INTERVAL = 30  # seconds between browser actions
    RETRY_DELAY = 5  # seconds between retries
    KINKONG_ENDPOINT = "https://nlr.app.n8n.cloud/webhook/kinkong"
    
    @staticmethod
    def generate_session_id():
        """Generate a unique session ID"""
        import uuid
        return str(uuid.uuid4())
