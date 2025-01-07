"""Voice activity detection"""
import time
from constants import AudioConstants

class VoiceActivityDetector:
    """Detects voice activity in audio stream"""
    def __init__(self, 
                 threshold=AudioConstants.SILENCE_THRESHOLD,
                 min_silence=AudioConstants.MIN_SILENCE_DURATION):
        self.threshold = threshold
        self.min_silence = min_silence
        self.silence_start = None
        
    def process(self, audio_level: float) -> bool:
        """Process audio level and return True if silence detected"""
        if audio_level < self.threshold:
            if self.silence_start is None:
                self.silence_start = time.time()
            elif time.time() - self.silence_start >= self.min_silence:
                return True
        else:
            self.silence_start = None
        return False
        
    def reset(self):
        """Reset detector state"""
        self.silence_start = None
