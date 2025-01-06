"""Browser automation and web interaction management"""
import asyncio
import logging
from typing import Any, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page
import aiohttp
import json

class BrowserManager:
    def __init__(self, config):
        self.config = config
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.logger = logging.getLogger(__name__)
        self.endpoint = "https://nlr.app.n8n.cloud/webhook/kinos-kinkong"
        
    async def start_browser(self, browser_type: str = "chrome") -> None:
        """Initialize and start browser instance"""
        try:
            playwright = await async_playwright().start()
            if browser_type == "chrome":
                self.browser = await playwright.chromium.launch(
                    headless=self.config.HEADLESS_MODE
                )
            elif browser_type == "firefox":
                self.browser = await playwright.firefox.launch(
                    headless=self.config.HEADLESS_MODE
                )
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
                
            self.page = await self.browser.new_page()
            self.logger.info(f"Started {browser_type} browser")
            
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            raise

    async def navigate(self, url: str) -> bool:
        """Navigate to specified URL"""
        try:
            await self.page.goto(url)
            await self.page.wait_for_load_state("networkidle")
            self.logger.info(f"Navigated to {url}")
            return True
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            return False

    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript code"""
        try:
            result = await self.page.evaluate(script)
            return result
        except Exception as e:
            self.logger.error(f"Script execution failed: {e}")
            return None

    async def take_screenshot(self) -> bytes:
        """Capture screenshot of current page"""
        try:
            screenshot = await self.page.screenshot()
            return screenshot
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return None

    async def send_to_endpoint(self, data: Dict) -> Any:
        """Send data to n8n webhook endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, json=data) as response:
                    return await response.json()
        except Exception as e:
            self.logger.error(f"Failed to send data to endpoint: {e}")
            return None

    async def process_page(self) -> Dict:
        """Process current page and extract relevant data"""
        try:
            title = await self.page.title()
            content = await self.page.content()
            screenshot = await self.take_screenshot()
            
            data = {
                "title": title,
                "url": self.page.url,
                "content": content,
                "screenshot": screenshot.hex() if screenshot else None
            }
            
            return await self.send_to_endpoint(data)
            
        except Exception as e:
            self.logger.error(f"Page processing failed: {e}")
            return None

    async def cleanup(self) -> None:
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            self.logger.info("Browser resources cleaned up")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
