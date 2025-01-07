"""Audio buffer management"""
from constants import AudioConstants

class AudioBufferManager:
    """Manages circular audio buffer with automatic size limiting"""
    def __init__(self, max_size=AudioConstants.MAX_RECORDING_SIZE):
        self.buffer = []
        self.max_size = max_size
        self.current_size = 0
        
    def add(self, data: bytes) -> bool:
        """Add data to buffer, returns False if buffer is full"""
        data_size = len(data)
        if self.current_size + data_size > self.max_size:
            return False
            
        self.buffer.append(data)
        self.current_size += data_size
        return True
        
    def clear(self):
        """Clear the buffer"""
        self.buffer = []
        self.current_size = 0
        
    def get_data(self) -> bytes:
        """Get all buffered data as bytes"""
        return b''.join(self.buffer)
