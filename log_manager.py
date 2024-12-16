import os
import sys
import logging
from typing import Optional

class LogManager:
    """Manages logging configuration and operations"""
    
    def __init__(self) -> None:
        self.log_path = self._setup_logging()
    
    def _setup_logging(self) -> Optional[str]:
        """Configure logging with executable directory as primary location"""
        
        # Determine executable directory
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.getcwd()
        
        # List of possible locations, with exe directory first
        possible_locations = [
            os.path.join(exe_dir, 'CK3_AI_Assistant.log'),
            os.path.join(os.path.expanduser('~'), 'CK3_AI_Assistant.log'),
            os.path.join(os.path.expanduser('~'), 'Desktop', 'CK3_AI_Assistant.log'),
            os.path.join(os.environ.get('TEMP', ''), 'CK3_AI_Assistant.log'),
        ]

        for log_path in possible_locations:
            try:
                logging.basicConfig(
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_path),
                        logging.StreamHandler()
                    ]
                )
                logging.info(f"Log file created at: {log_path}")
                return log_path
            except Exception:
                continue

        # Fallback to console-only logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        logging.warning("Running with console logging only - could not create log file")
        return None

    def get_logger(self, name: str) -> logging.Logger:
        """Get a named logger instance"""
        return logging.getLogger(name)
