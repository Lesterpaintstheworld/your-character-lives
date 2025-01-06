"""Thread management utilities"""
import threading
from typing import Callable, List
import logging

class ThreadManager:
    def __init__(self):
        self.threads: List[threading.Thread] = []
        self.logger = logging.getLogger(__name__)
        self._running = True

    def start_thread(self, target: Callable, *args, **kwargs) -> None:
        """Start a new managed thread.
        
        Args:
            target: Function to run in thread
            *args: Positional arguments for target
            **kwargs: Keyword arguments for target
        """
        thread = threading.Thread(target=target, args=args, kwargs=kwargs)
        thread.daemon = True
        self.threads.append(thread)
        thread.start()
        self.logger.debug(f"Started thread: {thread.name}")

    def stop_all(self) -> None:
        """Stop all managed threads."""
        self._running = False
        for thread in self.threads:
            if thread.is_alive():
                thread.join()
        self.logger.info("All threads stopped")

    @property
    def running(self) -> bool:
        """Check if thread manager is running."""
        return self._running
        
    async def start_browser_task(self, target: Callable, *args, **kwargs) -> None:
        """Start an async browser task.
        
        Args:
            target: Async function to run
            *args: Positional arguments for target
            **kwargs: Keyword arguments for target
        """
        try:
            task = asyncio.create_task(target(*args, **kwargs))
            self.tasks.append(task)
            await task
        except Exception as e:
            self.logger.error(f"Browser task error: {e}")
