"""Constants used throughout the application"""

class ThemeColors:
    # Main backgrounds
    BG_DARK = "#0d1117"      # Darker navy blue for main background
    BG_LIGHT = "#161b22"     # Slightly lighter navy for controls
    BG_HOVER = "#21262d"     # Hover state for interactive elements
    
    # Accents
    ACCENT_PRIMARY = "#2ea043"    # Green for primary actions
    ACCENT_SECONDARY = "#1f6feb"  # Blue for secondary actions
    ACCENT_WARNING = "#d29922"    # Orange for warnings/important elements
    
    # Text colors
    TEXT_PRIMARY = "#c9d1d9"      # Main text color (light gray)
    TEXT_SECONDARY = "#8b949e"    # Secondary text (darker gray)
    TEXT_BRIGHT = "#ffffff"       # Bright text for emphasis
    
    # VU Meter
    VU_LOW = "#238636"        # Green for low levels
    VU_MID = "#1f6feb"        # Blue for mid levels
    VU_HIGH = "#da3633"       # Red for high levels
    
    # Borders
    BORDER = "#30363d"        # Subtle border color

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
    DEFAULT_SCREENSHOT_INTERVAL = 15  # Changed to 15 seconds
    DEFAULT_ENDPOINT_EMILY = "https://nlr.app.n8n.cloud/webhook/kinos-emily"
    DEFAULT_ENDPOINT_DAEMON = "https://nlr.app.n8n.cloud/webhook/kinos-daemon"
    EDITOR_ENDPOINT = "https://nlr.app.n8n.cloud/webhook/kinos-claude"

class UIConstants:
    WINDOW_WIDTH = 80
    WINDOW_HEIGHT = 20
    UPDATE_INTERVAL = 100  # ms
