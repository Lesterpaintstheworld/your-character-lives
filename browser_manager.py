"""Browser automation and web interaction management"""
import asyncio
import logging
import os
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
        self.is_running = False
        self.browser_loop_task = None
        
    async def start_browser(self, browser_type: str = "chrome") -> None:
        """Initialize and start browser instance"""
        from constants import BrowserConstants
        
        self.logger.info(f"Starting {browser_type} browser with headless={BrowserConstants.HEADLESS_MODE}")
        self.logger.debug(f"Browser config: {vars(self.config)}")
        
        # First verify playwright is installed
        try:
            from playwright.async_api import async_playwright
            self.logger.info("Playwright module imported successfully")
        except ImportError as e:
            self.logger.error(f"Failed to import playwright: {e}")
            self.logger.info("Attempting to install playwright...")
            try:
                import subprocess
                subprocess.run(["pip", "install", "playwright"], check=True)
                subprocess.run(["playwright", "install"], check=True)
                from playwright.async_api import async_playwright
                self.logger.info("Playwright installed successfully")
            except Exception as e:
                self.logger.error(f"Failed to install playwright: {e}")
                raise

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

                    # Launch browser without user_data_dir
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

                    # Create persistent context with user_data_dir
                    self.context = await self.browser.new_context(
                        viewport={'width': 1280, 'height': 720},
                        user_data_dir=user_data_dir,
                        permissions=['geolocation']
                    )
                    self.logger.info("Browser context created")

                    # Create new page
                    self.logger.info("Creating new page...")
                    self.page = await self.context.new_page()
                    self.logger.info("Page created successfully")
                    
                    # Log browser version
                    version = await self.browser.version()
                    self.logger.info(f"Browser version: {version}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize browser: {e}", exc_info=True)
                    raise
                    
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}", exc_info=True)
            # Re-raise to ensure proper cleanup
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
            title = await self.page.title()
            content = await self.page.content()
            screenshot = await self.take_screenshot()
            
            self.logger.debug(f"Page title: {title}")
            self.logger.debug(f"Content length: {len(content)} bytes")
            self.logger.debug(f"Screenshot size: {len(screenshot)} bytes")
            
            data = {
                "title": title,
                "url": self.page.url,
                "content": content,
                "screenshot": screenshot.hex() if screenshot else None
            }
            
            response = await self.send_to_endpoint(data)
            self.logger.info("Successfully processed page and sent to endpoint")
            return response
            
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
        self.logger.info("Starting browser automation loop")
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
                        
                    self.logger.info(f"Navigating to Kinkong endpoint: {self.endpoint}")
                    await self.navigate(self.endpoint)
                    
                    self.logger.debug("Processing current page")
                    result = await self.process_page()
                    if result:
                        self.logger.info("Page processed successfully")
                        self.logger.debug(f"Processing result: {result}")
                    else:
                        self.logger.warning("Page processing returned no result")
                    
                    self.logger.debug(f"Waiting {self.config.BROWSER_INTERVAL} seconds before next iteration")
                    await asyncio.sleep(self.config.BROWSER_INTERVAL)
                    
                except Exception as e:
                    self.logger.error(f"Error in browser loop iteration: {e}", exc_info=True)
                    self.logger.info(f"Retrying in {self.config.RETRY_DELAY} seconds")
                    await asyncio.sleep(self.config.RETRY_DELAY)
                    
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
