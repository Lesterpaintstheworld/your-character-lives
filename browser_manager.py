"""Browser automation and web interaction management"""
import asyncio
import logging
import os
import base64
from typing import Any, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page
import aiohttp
import json
from constants import BrowserConstants

class BrowserManager:
    def __init__(self, config):
        self.config = config
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.logger = logging.getLogger(__name__)
        self.endpoint = BrowserConstants.KINKONG_ENDPOINT
        self.is_running = False
        self.browser_loop_task = None
        
    async def start_browser(self, browser_type: str = "chrome") -> None:
        """Initialize and start browser instance"""
        from constants import BrowserConstants
        
        self.logger.info(f"Starting {browser_type} browser with headless={BrowserConstants.HEADLESS_MODE}")
        self.logger.debug(f"Browser config: {vars(self.config)}")

        try:
            self.logger.info("Initializing playwright...")
            playwright = await async_playwright().start()
            self.logger.info("Playwright started successfully")

            # Create user data directory for persistence
            user_data_dir = os.path.join(os.path.expanduser('~'), '.browser_automation')
            os.makedirs(user_data_dir, exist_ok=True)
            self.logger.info(f"Using user data directory: {user_data_dir}")
            
            if browser_type == "chrome":
                self.logger.info("Launching chromium browser...")
                try:
                    # First check if chromium is installed
                    try:
                        import subprocess
                        result = subprocess.run(["playwright", "install", "chromium"], capture_output=True, text=True)
                        self.logger.info("Chromium installation verified")
                    except Exception as e:
                        self.logger.warning(f"Could not verify chromium installation: {e}")

                    # Launch browser first
                    self.browser = await playwright.chromium.launch(
                        headless=BrowserConstants.HEADLESS_MODE,
                        args=[
                            '--disable-dev-shm-usage',
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-gpu',
                            '--disable-software-rasterizer',
                            '--disable-background-timer-throttling',
                            '--disable-backgrounding-occluded-windows',
                            '--disable-renderer-backgrounding'
                        ]
                    )
                    self.logger.info("Browser launched successfully")

                    # Then create context
                    self.context = await self.browser.new_context(
                        viewport={'width': 1280, 'height': 720},
                        permissions=['geolocation']
                    )
                    self.logger.info("Browser context created")

                    # Create new page
                    self.page = await self.context.new_page()
                    self.logger.info("Page created successfully")
                    
                    # Get browser version info
                    try:
                        # Get version info through browser context
                        version_info = await self.browser.version
                        if isinstance(version_info, str):
                            self.logger.info(f"Browser version: {version_info}")
                        else:
                            version_info = await self.context.evaluate('navigator.userAgent')
                            self.logger.info(f"Browser user agent: {version_info}")
                    except Exception as e:
                        self.logger.warning(f"Could not get browser version: {e}")
                        # Continue anyway since this is not critical
                    
                except Exception as e:
                    self.logger.error(f"Failed to launch browser: {e}", exc_info=True)
                    raise
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}", exc_info=True)
            raise

    async def navigate(self, url: str) -> bool:
        """Navigate to specified URL"""
        self.logger.info(f"Navigating to: {url}")
        self.logger.debug(f"Current page: {self.page.url if self.page else 'No page'}")
        try:
            await self.page.goto(url)
            await self.page.wait_for_load_state("networkidle")
            self.logger.info(f"Successfully loaded {url}")
            self.logger.debug(f"Page title: {await self.page.title()}")
            return True
        except Exception as e:
            self.logger.error(f"Navigation failed for {url}: {e}", exc_info=True)
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
        self.logger.info(f"Processing page: {self.page.url}")
        try:
            # Navigate to the endpoint first
            await self.navigate(self.endpoint)
            self.logger.info(f"Navigated to endpoint: {self.endpoint}")
            
            # Wait for any dynamic content to load
            await self.page.wait_for_load_state("networkidle")
            
            # Get page data
            title = await self.page.title()
            content = await self.page.content()
            screenshot = await self.take_screenshot()
            
            self.logger.debug(f"Page title: {title}")
            self.logger.debug(f"Content length: {len(content)} bytes")
            self.logger.debug(f"Screenshot size: {len(screenshot)} bytes")
            
            # Prepare data for endpoint
            data = {
                "title": title,
                "url": self.page.url,
                "content": content,
                "screenshot": base64.b64encode(screenshot).decode() if screenshot else None
            }
            
            # Use requests instead of aiohttp
            import requests
            response = requests.post(
                self.endpoint,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info("Successfully processed page and sent to endpoint")
                return result
            else:
                error_text = response.text
                self.logger.error(f"Endpoint returned status {response.status_code}: {error_text}")
                return None
            
        except Exception as e:
            self.logger.error(f"Page processing failed: {e}", exc_info=True)
            return None

    def toggle_browser(self) -> bool:
        """Toggle browser automation on/off"""
        self.is_running = not self.is_running
        state = "started" if self.is_running else "stopped"
        self.logger.info(f"Browser automation {state}")
        return self.is_running

    async def browser_loop(self):
        """Main browser automation loop"""
        try:
            # Verify playwright installation before starting
            try:
                import subprocess
                self.logger.info("Checking playwright installation...")
                result = subprocess.run(["playwright", "install", "chromium"], capture_output=True, text=True)
                self.logger.info(f"Playwright installation check result: {result.stdout}")
            except Exception as e:
                self.logger.error(f"Failed to verify playwright installation: {e}")
                self.logger.info("Attempting to install playwright...")
                try:
                    subprocess.run(["pip", "install", "playwright"], check=True)
                    subprocess.run(["playwright", "install"], check=True)
                    self.logger.info("Playwright installed successfully")
                except Exception as install_e:
                    self.logger.error(f"Failed to install playwright: {install_e}")
                    raise

            self.logger.info("Initializing browser...")
            await self.start_browser()
            
            # Add state check
            if not self.browser or not self.page:
                raise RuntimeError("Browser or page not initialized")
                
            self.logger.info("Browser initialized successfully, entering main loop")
            
            while self.is_running:
                try:
                    if not self.browser or not self.page:
                        self.logger.error("Browser or page became invalid")
                        raise RuntimeError("Browser or page not initialized")
                        
                    self.logger.info(f"Processing page at endpoint: {self.endpoint}")
                    result = await self.process_page()
                    
                    if result:
                        self.logger.info("Page processed successfully")
                        self.logger.debug(f"Processing result: {result}")
                    else:
                        self.logger.warning("Page processing returned no result")
                    
                    self.logger.debug(f"Waiting {BrowserConstants.BROWSER_INTERVAL} seconds before next iteration")
                    await asyncio.sleep(BrowserConstants.BROWSER_INTERVAL)
                    
                except Exception as e:
                    self.logger.error(f"Error in browser loop iteration: {e}", exc_info=True)
                    self.logger.info(f"Retrying in {BrowserConstants.RETRY_DELAY} seconds")
                    await asyncio.sleep(BrowserConstants.RETRY_DELAY)
                    
        except Exception as e:
            self.logger.error(f"Browser loop failed: {e}", exc_info=True)
        finally:
            self.logger.info("Browser loop ending, cleaning up resources")
            await self.cleanup()

    async def start_browser_automation(self):
        """Start browser automation loop"""
        self.logger.info("Starting browser automation")
        if not self.browser_loop_task:
            self.is_running = True
            # Create and store the task
            self.browser_loop_task = asyncio.create_task(self.browser_loop())
            self.logger.debug("Browser loop task created")
            # Wait for the task to complete
            await self.browser_loop_task

    async def stop_browser_automation(self):
        """Stop browser automation loop"""
        self.logger.info("Stopping browser automation")
        self.is_running = False
        if self.browser_loop_task:
            # Wait for the task to complete
            await self.browser_loop_task
            self.browser_loop_task = None
            self.logger.debug("Browser loop task completed")

    async def cleanup(self) -> None:
        """Clean up browser resources"""
        self.logger.info("Starting browser cleanup")
        try:
            if hasattr(self, 'context') and self.context:
                # Save storage state before closing
                await self.context.storage_state(
                    path=os.path.join(os.path.expanduser('~'), '.browser_automation', 'storage_state.json')
                )
            if self.page:
                self.logger.debug("Closing page")
                await self.page.close()
            if self.browser:
                self.logger.debug("Closing browser")
                await self.browser.close()
            self.logger.info("Browser resources cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}", exc_info=True)
