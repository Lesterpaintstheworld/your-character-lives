"""Screenshot capture and management"""
import time
import logging
from typing import Optional
from main import take_screenshot

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
                
            screenshot = take_screenshot()
            if screenshot:
                self.last_screenshot = screenshot
                return screenshot
            else:
                self.last_error_time = current_time
                return self.last_screenshot
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")
            self.last_error_time = time.time()
            return self.last_screenshot
