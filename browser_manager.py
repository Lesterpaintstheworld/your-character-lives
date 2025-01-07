"""Browser automation and web interaction management"""
import asyncio
import logging
import os
import base64
import time
from typing import Any, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page
import aiohttp
import requests
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

    async def take_screenshot(self, path: str = None) -> Optional[bytes]:
        """Capture screenshot of current page
        
        Args:
            path: Optional path to save screenshot file
            
        Returns:
            Screenshot as bytes if no path provided, otherwise None
        """
        try:
            if path:
                await self.page.screenshot(path=path)
                return None
            else:
                # Return optimized JPEG bytes directly
                return await self.page.screenshot(type='jpeg', quality=85)
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

    async def wait_for_clickable(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to be clickable with better error reporting"""
        try:
            element = await self.page.wait_for_selector(
                selector,
                state='visible',
                timeout=timeout
            )
            if element:
                is_visible = await element.is_visible()
                is_enabled = await element.is_enabled()
                if not is_visible or not is_enabled:
                    self.logger.warning(f"Element {selector} found but not interactable: visible={is_visible}, enabled={is_enabled}")
                    return False
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for {selector}: {e}")
            return False

    async def safe_click(self, selector: str, timeout: int = 10000) -> bool:
        """Safely click an element with retries"""
        try:
            if await self.wait_for_clickable(selector, timeout):
                element = await self.page.query_selector(selector)
                await element.scroll_into_view_if_needed()
                await asyncio.sleep(0.5)  # Stability delay
                await element.click()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Safe click failed for {selector}: {e}")
            return False

    async def process_page(self) -> Dict:
        """Process current page and execute instruction sequences"""
        try:
            # Get current page info if we're on a page
            current_data = {}
            webpage_content = ""  # Initialize webpage content
            
            if self.page and self.page.url != "about:blank":
                # Get basic page info
                current_data = {
                    "current_url": self.page.url,
                    "title": await self.page.title(),
                    "content": await self.page.content()
                }
                
                # Extract readable text content from the page
                webpage_content = await self.page.evaluate("""() => {
                    // Helper function to get visible text
                    function getVisibleText(node) {
                        if (node.nodeType === Node.TEXT_NODE) {
                            return node.textContent.trim();
                        }
                        
                        // Skip hidden elements
                        const style = window.getComputedStyle(node);
                        if (style && (style.display === 'none' || style.visibility === 'hidden')) {
                            return '';
                        }
                        
                        // Recursively get text from child nodes
                        let text = '';
                        for (let child of node.childNodes) {
                            if (child.nodeType === Node.ELEMENT_NODE) {
                                text += ' ' + getVisibleText(child);
                            } else if (child.nodeType === Node.TEXT_NODE) {
                                text += ' ' + child.textContent.trim();
                            }
                        }
                        return text.trim();
                    }
                    
                    // Get main content, prioritizing article/main content areas
                    const mainContent = document.querySelector('article, [role="main"], main, .main-content');
                    if (mainContent) {
                        return getVisibleText(mainContent);
                    }
                    
                    // Fallback to body if no main content area found
                    return getVisibleText(document.body);
                }""")
                
                # Format webpage content for context
                if webpage_content:
                    webpage_content = f"\n=== Current Webpage Content ===\nURL: {self.page.url}\nTitle: {await self.page.title()}\n\n{webpage_content}\n=== End Webpage Content ===\n"
                
                # Take screenshot as binary
                screenshot_bytes = await self.take_screenshot()
                if screenshot_bytes:
                    current_data["screenshot"] = screenshot_bytes
            
            # Get instructions from endpoint
            self.logger.info("Getting navigation instructions from endpoint")
            
            # Prepare multipart form data
            files = {
                'screenshot': ('screenshot.jpg', current_data.pop('screenshot', None), 'image/jpeg')
            }
            
            # Add webpage content to text data if available
            if 'text' in current_data:
                current_data['text'] += webpage_content
            else:
                current_data['text'] = webpage_content
                
            response = requests.post(
                self.endpoint,
                data=current_data,
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'instructions' not in data:
                    self.logger.warning("No instructions in response")
                    return None
                    
                instructions = data['instructions']
                self.logger.info(f"Received instructions: {instructions}")
                
                results = {}
                # Process each instruction in sequence
                for instruction in instructions:
                    try:
                        action = instruction.get('action')
                        max_retries = 3
                        retry_delay = 2  # seconds
                        
                        for attempt in range(max_retries):
                            try:
                                if action == 'navigate':
                                    url = instruction.get('url')
                                    await self.navigate(url)
                                    if 'wait_for' in instruction:
                                        await self.page.wait_for_selector(
                                            instruction['wait_for'],
                                            state='visible',
                                            timeout=10000
                                        )
                                        
                                elif action == 'waitForSelector':
                                    selector = instruction.get('selector')
                                    timeout = instruction.get('timeout', 10000)
                                    await self.page.wait_for_selector(
                                        selector,
                                        state='visible',
                                        timeout=timeout
                                    )
                                    
                                elif action == 'click':
                                    selector = instruction.get('selector')
                                    if await self.safe_click(selector):
                                        break
                                    raise Exception(f"Failed to click {selector}")
                                    
                                elif action == 'type':
                                    selector = instruction.get('selector')
                                    text = instruction.get('text')
                                    await self.page.wait_for_selector(selector, state='visible')
                                    await self.page.fill(selector, text)
                                    
                                elif action == 'press':
                                    key = instruction.get('key')
                                    await self.page.keyboard.press(key)
                                    
                                elif action == 'extract':
                                    selector = instruction.get('selector')
                                    attribute = instruction.get('attribute')
                                    output_key = instruction.get('output')
                                    await self.page.wait_for_selector(selector, state='visible')
                                    elements = await self.page.query_selector_all(selector)
                                    extracted = []
                                    for element in elements:
                                        if attribute == 'innerText':
                                            text = await element.inner_text()
                                            extracted.append(text)
                                    results[output_key] = extracted
                                    
                                elif action == 'screenshot':
                                    path = instruction.get('path')
                                    await self.take_screenshot(path)
                                    
                                elif action == 'close':
                                    await self.page.close()
                                    
                                else:
                                    self.logger.warning(f"Unknown action: {action}")
                                    
                                break  # Action succeeded, exit retry loop
                                
                            except Exception as e:
                                if attempt == max_retries - 1:
                                    self.logger.error(f"Action {action} failed after {max_retries} attempts: {e}")
                                    # Take screenshot on failure
                                    error_screenshot = await self.take_screenshot()
                                    if error_screenshot:
                                        error_path = f"error_{action}_{time.time()}.jpg"
                                        with open(error_path, "wb") as f:
                                            f.write(error_screenshot)  # Write raw bytes
                                        self.logger.info(f"Error screenshot saved to {error_path}")
                                    raise
                                else:
                                    self.logger.warning(f"Attempt {attempt + 1} failed for {action}: {e}. Retrying...")
                                    await asyncio.sleep(retry_delay)
                                    # Refresh page if needed
                                    if 'refresh_on_retry' in instruction and instruction['refresh_on_retry']:
                                        await self.page.reload()
                                    continue
                                    
                    except Exception as e:
                        self.logger.error(f"Failed to execute {action}: {e}")
                        if instruction.get('critical', False):
                            raise  # Re-raise if instruction is marked as critical
                        continue  # Otherwise continue with next instruction
                        
                return results
                    
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
