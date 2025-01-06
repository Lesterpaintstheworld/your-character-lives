# Multi-Domain AI Assistant API Reference

## Audio Manager API

### Class: AudioManager
```python
class AudioManager:
    def __init__(self, config)
    def record_audio(self, duration: int) -> bytes
    def play_audio(self, audio_data: bytes)
    def get_devices() -> Dict[str, List[Dict]]
    def cleanup()
```

### Class: DeviceManager
```python
class DeviceManager:
    def __init__()
    def refresh_devices()
    def get_input_device() -> Optional[int]
    def get_output_device() -> Optional[int]
    def cleanup()
```

## Video System API

### Class: DraggableVideoWindow
```python
class DraggableVideoWindow:
    def __init__(self, video_path: str)
    def switch_to_talk_video()
    def switch_to_idle_video()
    def cleanup()
```

## Thread Management API

### Class: ThreadManager
```python
class ThreadManager:
    def __init__()
    def start_thread(self, target: Callable, *args, **kwargs)
    def stop_all()
    @property
    def running() -> bool
```

## Logging API

### Class: LogManager
```python
class LogManager:
    def __init__()
    def get_logger(self, name: str) -> logging.Logger
```

## Constants

### Audio Constants
```python
CHUNK_SIZE = 1024
FORMAT = 16  # bits
CHANNELS = 1
SAMPLE_RATE = 24000
```

### Network Constants
```python
REQUEST_TIMEOUT = 120
RECONNECT_DELAY = 5
MAX_RETRIES = 3
```

### UI Constants
```python
WINDOW_WIDTH = 80
WINDOW_HEIGHT = 20
UPDATE_INTERVAL = 100  # ms
```

## Event Handling

### Functions
```python
def on_closing()
def toggle_play_pause()
def toggle_auto_recording()
def update_status(message: str)
```

## Browser Automation API

### Class: BrowserManager
```python
class BrowserManager:
    def __init__(self, config)
    def start_browser(self, browser_type: str = "chrome") -> None
    def navigate(self, url: str) -> bool
    def execute_script(self, script: str) -> Any
    def take_screenshot(self) -> bytes
    def fill_form(self, form_data: Dict[str, str]) -> bool
    def get_page_content(self) -> str
    def cleanup() -> None
```

### Browser Constants
```python
BROWSER_TIMEOUT = 30
SCREENSHOT_QUALITY = 90
DEFAULT_BROWSER = "chrome"
HEADLESS_MODE = False
```

## Error Handling

### Exceptions
```python
class AudioDeviceError(Exception)
class VideoPlaybackError(Exception)
class NetworkError(Exception)
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API authentication
- `N8N_ENDPOINT`: n8n webhook URL
- `LOG_LEVEL`: Logging verbosity

### Config File
```python
class Config:
    AUDIO_FORMAT: int
    CHANNELS: int
    SAMPLE_RATE: int
    CHUNK_SIZE: int
```
