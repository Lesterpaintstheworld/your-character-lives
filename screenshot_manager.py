"""Screenshot capture and management"""
import time
import logging
from typing import Optional
import pyautogui
from PIL import Image
import io

class ScreenshotManager:
    """Manages screenshot capture and optimization"""
    def __init__(self):
        self.last_screenshot = None
        self.last_error_time = 0
        self.logger = logging.getLogger(__name__)
        
    async def capture(self) -> Optional[bytes]:
        """Capture screenshot with error handling and rate limiting"""
        try:
            # Rate limit on errors
            current_time = time.time()
            if current_time - self.last_error_time < 5:
                return self.last_screenshot
                
            # Take screenshot using pyautogui
            try:
                screenshot = pyautogui.screenshot()
            except Exception as e:
                self.logger.error(f"PyAutoGUI screenshot failed: {e}")
                # Fallback to PIL
                from PIL import ImageGrab
                screenshot = ImageGrab.grab()

            if screenshot:
                # Resize with logging
                max_size = (1024, 576)
                original_size = screenshot.size
                self.logger.debug(f"Original size: {original_size}")
                
                screenshot.thumbnail(max_size, Image.LANCZOS)
                self.logger.debug(f"Resized to: {screenshot.size}")
                
                # Convert to bytes
                img_byte_arr = io.BytesIO()
                screenshot.save(img_byte_arr, format='JPEG', 
                              quality=85, optimize=True)
                
                screenshot_bytes = img_byte_arr.getvalue()
                self.last_screenshot = screenshot_bytes
                return screenshot_bytes
            else:
                self.last_error_time = current_time
                return self.last_screenshot
                
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")
            self.last_error_time = time.time()
            return self.last_screenshot
