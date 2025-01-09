"""Fixed recording cycle management"""
import asyncio
import logging
from typing import Optional
from constants import AudioConstants, NetworkConstants

class FixedRecordingManager:
    def __init__(self, audio_manager, screenshot_manager):
        self.audio_manager = audio_manager
        self.screenshot_manager = screenshot_manager
        self.is_active = False
        self.current_cycle = 0
        self.logger = logging.getLogger(__name__)

    async def start_cycle(self, emily_endpoint: str, daemon_endpoint: str, 
                         session_id: str, update_status_callback) -> None:
        """Start a fixed recording cycle"""
        self.is_active = True
        self.current_cycle += 1
        cycle_num = self.current_cycle
        
        try:
            # Record with counter
            update_status_callback(f"🎤 Cycle {cycle_num} - Starting...")
            audio_data = await self._record_with_counter(update_status_callback)
            
            if not audio_data:
                raise ValueError("No audio data recorded")

            # Capture contextual data
            screenshot = await self.screenshot_manager.capture()
            if not screenshot:
                raise ValueError("Screenshot capture failed")

            # Send to Emily
            await self._send_to_endpoint(
                emily_endpoint, 
                audio_data, 
                screenshot, 
                session_id,
                False,  # is_daemon
                update_status_callback
            )

            # Send to Daemon
            await self._send_to_endpoint(
                daemon_endpoint, 
                audio_data, 
                screenshot, 
                session_id,
                True,  # is_daemon
                update_status_callback
            )

            update_status_callback(f"✅ Cycle {cycle_num} completed")

        except Exception as e:
            self.logger.error(f"Error in cycle {cycle_num}: {e}")
            update_status_callback(f"❌ Error in cycle {cycle_num}: {str(e)}")
            raise
        finally:
            self.is_active = False

    async def _record_with_counter(self, update_status_callback) -> Optional[bytes]:
        """Record with counter display"""
        for i in range(AudioConstants.FIXED_RECORDING_DURATION):
            if not self.is_active:
                return None
            update_status_callback(f"🎤 Recording... {i+1}/{AudioConstants.FIXED_RECORDING_DURATION}s")
            if i == 0:
                return self.audio_manager.record_audio(
                    AudioConstants.FIXED_RECORDING_DURATION,
                    AudioConstants.FIXED_SAMPLE_RATE,
                    AudioConstants.FIXED_BUFFER_SIZE
                )
            await asyncio.sleep(1)

    async def _send_to_endpoint(self, endpoint: str, audio_data: bytes, 
                              screenshot: bytes, session_id: str,
                              is_daemon: bool, update_status_callback) -> None:
        """Send data to specific endpoint"""
        agent = "Daemon" if is_daemon else "Emily"
        try:
            update_status_callback(f"📤 Sending to {agent}...")
            
            files = {
                'audio': ('audio.wav', audio_data, 'audio/wav'),
                'screenshot': ('screenshot.jpg', screenshot, 'image/jpeg')
            }
            
            data = {
                'text': collect_text_files_content(),
                'session': session_id
            }

            response = await self._make_request(endpoint, files, data)
            
            if response.status_code == 200:
                update_status_callback(f"✅ Playing {agent}'s response...")
                await process_audio_chunk(response.content, is_daemon=is_daemon)
            else:
                raise ValueError(f"API error {agent}: {response.status_code}")

        except Exception as e:
            self.logger.error(f"Error sending to {agent}: {e}")
            raise

    async def _make_request(self, endpoint, files, data):
        """Make request with retry"""
        for attempt in range(NetworkConstants.MAX_RETRIES):
            try:
                return requests.post(
                    endpoint,
                    data=data,
                    files=files,
                    timeout=NetworkConstants.REQUEST_TIMEOUT
                )
            except Exception as e:
                if attempt == NetworkConstants.MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(NetworkConstants.RECONNECT_DELAY)
