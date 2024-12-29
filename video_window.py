"""Draggable borderless video window implementation"""
import threading
import cv2
# Global lock for video operations
video_lock = threading.Lock()
from PIL import Image, ImageTk
import tkinter as tk
import logging
import os
import numpy as np
import gc
import time
import sys
import threading

# Global lock for video operations
video_lock = threading.Lock()

class DraggableVideoWindow:
    window_count = 0  # Track number of windows
    
    def __init__(self, idle_video_path):
        """Initialize with path to idle/default video"""
        DraggableVideoWindow.window_count += 1
        self.window_number = DraggableVideoWindow.window_count
        self.logger = logging.getLogger(f"{__name__}_{self.window_number}")
        self.logger.info(f"Initializing DraggableVideoWindow #{self.window_number}")
        self.is_switching = False  # Flag for video switching state
        
        # Get proper video directory path
        if getattr(sys, 'frozen', False):
            # Running from executable
            base_path = sys._MEIPASS
        else:
            # Running from source
            base_path = os.path.dirname(os.path.abspath(__file__))
        videos_dir = os.path.join(base_path, "videos")
        
        # Initialize drag and resize data
        self.drag_data = {'x': 0, 'y': 0}
        self.resize_data = {'x': 0, 'y': 0}
        self.is_transparent = False
        
        # Use proper path construction
        self.idle_video_path = os.path.join(videos_dir, os.path.basename(idle_video_path))
        base_name = os.path.splitext(os.path.basename(idle_video_path))[0]
        if base_name.endswith('2'):
            self.talk_video_path = os.path.join(videos_dir, "talk2.mp4")
        else:
            self.talk_video_path = os.path.join(videos_dir, "talk.mp4")
            
        self.logger.info(f"Idle video path: {self.idle_video_path}")
        self.logger.info(f"Talk video path: {self.talk_video_path}")
        
        self.current_video_path = idle_video_path
        self.transition_requested = False
        self.fade_frames = 15
        self.fade_counter = 0
        self.last_frame = None
        self.frame_buffer = []
        self.buffer_size = 30

        # Verify video files exist
        if not os.path.exists(self.idle_video_path):
            self.logger.error(f"Idle video not found: {self.idle_video_path}")
            raise FileNotFoundError(f"Idle video not found: {self.idle_video_path}")
        if not os.path.exists(self.talk_video_path):
            self.logger.error(f"Talk video not found: {self.talk_video_path}")
            raise FileNotFoundError(f"Talk video not found: {self.talk_video_path}")

        # Initialize video capture with error checking
        try:
            self.cap = cv2.VideoCapture(self.current_video_path)
            if not self.cap.isOpened():
                raise ValueError(f"Failed to open video: {self.current_video_path}")
            
            # Set video properties
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
            if sys.platform == 'win32':
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            
            # Get and verify FPS
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            if self.fps <= 0:
                self.fps = 30  # Default to 30fps if invalid
            self.logger.info(f"Video FPS: {self.fps}")
            
            # Preload frames
            self.preload_frames()
            
            # Try to disable audio if the property exists
            try:
                if hasattr(cv2, 'CAP_PROP_AUDIO_ENABLE'):
                    self.cap.set(cv2.CAP_PROP_AUDIO_ENABLE, 0)
                else:
                    self.logger.info("Audio disable property not available in this OpenCV version")
            except Exception as e:
                self.logger.warning(f"Could not disable audio: {e}")
                
            # Get video properties and reduce by 15%
            original_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.width = int(original_width * 0.85)  # Reduce by 15%
            self.height = int(original_height * 0.85)  # Reduce by 15%
            self.logger.info(f"Video dimensions: {self.width}x{self.height}")
            
            # Create window
            self.logger.info("Creating Tkinter window")
            self.window = tk.Toplevel()
            self.window.withdraw()  # Hide window initially
            
            # Configure window
            self.window.overrideredirect(True)
            self.window.attributes('-topmost', True)
            self.window.attributes('-alpha', 1.0)
            self.window.attributes('-transparentcolor', 'black')
            
            # Set window size with new minimum dimensions
            self.width = max(272, self.width // 2)  # 320 * 0.85 ≈ 272
            self.height = max(204, self.height // 2)  # 240 * 0.85 ≈ 204
            self.window.geometry(f"{self.width}x{self.height}+100+100")
            
            # Create video display label with transparent background
            self.label = tk.Label(self.window, bg='black')
            self.label.pack(fill='both', expand=True)
            
            # Initialize storage
            self.photo = None
            self.image = None
            
            # Bind events
            self._bind_events()
            
            # Test frame display
            self.logger.info("Testing frame display")
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.logger.error("Failed to read first frame")
                raise ValueError("Failed to read first frame")
                
            # Try to display first frame
            try:
                self.display_frame(frame)
            except Exception as e:
                self.logger.error(f"Failed to display first frame: {e}")
                raise
                
            # Show window
            self.window.deiconify()
            self.logger.info("Window initialization complete")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize video window: {e}")
            self.cleanup()
            raise
        
        # Start video loop
        self.update_frame()
        
    def start_drag(self, event):
        """Begin drag of window"""
        self.drag_data['x'] = event.x_root - self.window.winfo_x()
        self.drag_data['y'] = event.y_root - self.window.winfo_y()
        
    def drag(self, event):
        """Handle window dragging"""
        x = event.x_root - self.drag_data['x']
        y = event.y_root - self.drag_data['y']
        self.window.geometry(f"+{x}+{y}")
        
    def start_resize(self, event):
        """Begin resize of window"""
        self.resize_data['x'] = event.x
        self.resize_data['y'] = event.y
        self.resize_data['width'] = self.window.winfo_width()    # Store initial window size
        self.resize_data['height'] = self.window.winfo_height()
        
    def resize(self, event):
        """Handle window resizing"""
        try:
            # Calculate change in position
            dx = event.x - self.resize_data['x']
            dy = event.y - self.resize_data['y']
            
            # Calculate new dimensions
            new_width = max(272, self.resize_data['width'] + dx)   # Minimum width 272
            new_height = max(204, self.resize_data['height'] + dy) # Minimum height 204
            
            # Update window size
            self.window.geometry(f"{int(new_width)}x{int(new_height)}")
            
            # Log resize operation
            self.logger.debug(f"Resizing window to {new_width}x{new_height}")
            
        except Exception as e:
            self.logger.error(f"Error during resize: {e}")
        
    def close_window(self, event):
        """Close the window and cleanup resources"""
        self.cleanup()
        self.window.destroy()
        
    def toggle_transparency(self, event):
        """Toggle window transparency on middle click"""
        self.is_transparent = not self.is_transparent
        self.window.attributes('-alpha', 0.5 if self.is_transparent else 1.0)
        
    def preload_frames(self):
        """Preload frames into buffer to smooth playback"""
        try:
            self.frame_buffer.clear()
            ret = True
            while ret and len(self.frame_buffer) < self.buffer_size:
                ret, frame = self.cap.read()
                if ret:
                    self.frame_buffer.append(frame)
                else:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.cap.read()
                    if ret:
                        self.frame_buffer.append(frame)
        except Exception as e:
            self.logger.error(f"Error preloading frames: {e}")

    def cleanup_buffer(self):
        """Clean up frame buffer to free memory"""
        try:
            # Clear buffer with thread safety
            with threading.Lock():
                self.frame_buffer.clear()
                gc.collect()
        except Exception as e:
            self.logger.error(f"Error cleaning buffer: {e}")

    def _bind_events(self):
        """Bind all window events"""
        try:
            self.label.bind('<Button-1>', self.start_drag)
            self.label.bind('<B1-Motion>', self.drag)
            self.window.bind('<Button-3>', self.start_resize)  # Bind to window instead of label
            self.window.bind('<B3-Motion>', self.resize)       # Bind to window instead of label
            self.label.bind('<Double-Button-1>', self.close_window)
            self.label.bind('<Button-2>', self.toggle_transparency)
            self.logger.info("Events bound successfully")
        except Exception as e:
            self.logger.error(f"Failed to bind events: {e}")
            raise

    def display_frame(self, frame):
        """Convert and display a frame with better error handling."""
        try:
            if frame is None:
                self.logger.error("Received None frame")
                return

            # Check if we're falling behind
            current_time = time.time()
            if hasattr(self, 'last_frame_time'):
                try:
                    frame_delta = current_time - self.last_frame_time
                    target_delta = 1.0 / max(0.1, self.cap.get(cv2.CAP_PROP_FPS))  # Prevent division by zero
                    
                    # Skip frame if we're more than half a frame behind
                    if frame_delta < target_delta * 0.5:
                        return
                except Exception as e:
                    self.logger.warning(f"Frame timing calculation error: {e}")
                    # Continue with frame display even if timing fails
                    
            self.last_frame_time = current_time

            # Handle transition if requested
            if self.transition_requested and self.last_frame is not None:
                try:
                    # Calculate transition alpha
                    alpha = self.fade_counter / max(1, self.fade_frames)  # Prevent division by zero
                    # Blend frames
                    frame = cv2.addWeighted(self.last_frame, 1-alpha, frame, alpha, 0)
                    self.fade_counter -= 1
                    if self.fade_counter <= 0:
                        self.transition_requested = False
                        self.last_frame = None
                except Exception as e:
                    self.logger.warning(f"Frame transition error: {e}")
                    # Continue with normal frame display if transition fails

            # Store frame for next transition
            if self.transition_requested and self.last_frame is None:
                self.last_frame = frame.copy()

            # Convert frame from BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get current window dimensions with error protection
            try:
                current_width = max(1, self.window.winfo_width())  # Ensure non-zero
                current_height = max(1, self.window.winfo_height()) # Ensure non-zero
            except Exception as e:
                self.logger.error(f"Failed to get window dimensions: {e}")
                current_width = max(1, self.width)
                current_height = max(1, self.height)
                
            # Resize frame with dimension validation
            if current_width > 0 and current_height > 0:
                resized = cv2.resize(rgb_frame, (current_width, current_height))
            else:
                self.logger.error("Invalid dimensions for resize")
                return
            
            # Convert to PIL Image
            image = Image.fromarray(resized)
            
            # Create rounded corner mask
            mask = Image.new('L', (current_width, current_height), 0)
            radius = min(30, current_width//10, current_height//10)  # Adaptive radius
            
            # Draw the rounded rectangle mask
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([(0, 0), (current_width-1, current_height-1)], 
                                 radius=radius, fill=255)
            
            # Apply mask
            image.putalpha(mask)
            
            # Convert to PhotoImage
            self.image = image  # Store reference
            self.photo = ImageTk.PhotoImage(image=image)
            
            # Update label
            if hasattr(self, 'label') and self.label.winfo_exists():
                self.label.configure(image=self.photo)
                self.label.image = self.photo  # Keep a reference
            else:
                self.logger.error("Label does not exist")
                
        except Exception as e:
            self.logger.error(f"Error in display_frame: {e}")
            raise

    def update_frame(self):
        """Update video frame with buffering and FPS protection"""
        if not hasattr(self, 'window') or not self.window.winfo_exists():
            return
            
        if getattr(self, 'is_switching', False):
            # Skip frame update during video switch
            if hasattr(self, 'window') and self.window.winfo_exists():
                self.window.after(int(1000/30), self.update_frame)  # Try again in ~33ms
            return
            
        try:
            # Get frame from buffer with protection
            if self.frame_buffer:
                frame = self.frame_buffer.pop(0)
                
                # Validate frame before processing
                if frame is None or frame.size == 0:
                    self.logger.warning("Invalid frame detected, skipping")
                    return
                    
                # Replenish buffer with protection
                try:
                    if self.cap is None or not self.cap.isOpened():
                        self.logger.error("Video capture is not open")
                        self.reopen_video()
                        return
                        
                    ret, new_frame = self.cap.read()
                    if not ret:
                        self.logger.info("Reached end of video, resetting position")
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, new_frame = self.cap.read()
                    
                    if ret and new_frame is not None:
                        self.frame_buffer.append(new_frame)
                    
                except Exception as e:
                    self.logger.error(f"Error replenishing buffer: {e}")
                    self.reopen_video()
                    
                if frame is not None:
                    self.last_valid_frame = frame.copy()
                    try:
                        self.display_frame(frame)
                    except Exception as e:
                        self.logger.error(f"Error displaying frame: {e}")
                        if self.last_valid_frame is not None:
                            self.display_frame(self.last_valid_frame)
                    
        except Exception as e:
            self.logger.error(f"Error updating video frame: {e}")
            
        finally:
            if hasattr(self, 'window') and self.window.winfo_exists():
                # Get FPS with protection against zero
                try:
                    if self.cap is None or not self.cap.isOpened():
                        fps = 30  # Default fallback
                    else:
                        fps = self.cap.get(cv2.CAP_PROP_FPS)
                        if fps <= 0 or not fps:
                            fps = 30  # Default to 30fps if invalid
                    delay = max(1, int(1000 / fps))  # Ensure delay is at least 1ms
                except:
                    delay = 33  # ~30fps as fallback
                self.window.after(delay, self.update_frame)
            
    def run(self):
        """Start the video window"""
        try:
            # Instead of running mainloop, just start the frame updates
            self.update_frame()
        except Exception as e:
            self.logger.error(f"Error in video window run: {e}")
            self.cleanup()
        
    def switch_to_talk_video(self):
        """Switch to talking video with global lock and improved thread safety"""
        global video_lock
        
        with video_lock:  # Global lock for video operations
            try:
                if self.current_video_path != self.talk_video_path:
                    self.logger.info(f"Switching to talk video: {self.talk_video_path}")
                    
                    # Verify talk video exists
                    if not os.path.exists(self.talk_video_path):
                        self.logger.error(f"Talk video not found: {self.talk_video_path}")
                        return
                        
                    # Stop current video processing
                    self.is_switching = True
                    time.sleep(0.1)  # Allow current frame processing to complete
                    
                    # Clear buffer and request transition
                    self.cleanup_buffer()
                    self.transition_requested = True
                    self.fade_counter = self.fade_frames
                    
                    # Create new capture with retry mechanism
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            # Create new capture
                            new_cap = cv2.VideoCapture(self.talk_video_path)
                            if not new_cap.isOpened():
                                raise ValueError(f"Failed to open talk video: {self.talk_video_path}")
                            
                            # Configure new capture
                            new_cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
                            if sys.platform == 'win32':
                                new_cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                            
                            # Test new capture
                            ret, test_frame = new_cap.read()
                            if not ret or test_frame is None:
                                raise ValueError("Failed to read first frame")
                            new_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            
                            # Switch captures with proper cleanup
                            if self.cap is not None:
                                old_cap = self.cap
                                self.cap = None  # Clear reference first
                                try:
                                    old_cap.release()
                                    del old_cap  # Explicitly delete
                                except Exception as e:
                                    self.logger.warning(f"Error releasing old capture: {e}")
                            
                            # Assign new capture and update path
                            self.cap = new_cap
                            self.current_video_path = self.talk_video_path
                            
                            # Force garbage collection
                            gc.collect()
                            
                            # Wait for resources to be properly released
                            time.sleep(0.2)
                            
                            # Preload frames
                            self.preload_frames()
                            
                            self.logger.info("Successfully switched to talk video")
                            break
                            
                        except Exception as e:
                            if attempt < max_retries - 1:
                                self.logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying...")
                                time.sleep(0.5)  # Wait before retry
                                continue
                            raise
                            
            except Exception as e:
                self.logger.error(f"Failed to switch to talk video: {e}")
                self.reopen_video()
                
            finally:
                self.is_switching = False

    def switch_to_idle_video(self):
        """Switch to idle video with improved thread synchronization"""
        try:
            if self.current_video_path != self.idle_video_path:
                self.logger.info(f"Switching to idle video: {self.idle_video_path}")
                
                # Set switching flag
                self.is_switching = True
                
                # Add small delay for thread sync
                time.sleep(0.1)
                
                # Verify idle video exists
                if not os.path.exists(self.idle_video_path):
                    self.logger.error(f"Idle video not found: {self.idle_video_path}")
                    return
                    
                with video_lock:  # Use global video lock
                    # Release current capture with protection
                    if self.cap is not None:
                        try:
                            self.cap.release()
                            self.cap = None  # Clear reference
                            time.sleep(0.1)  # Allow time for release
                        except Exception as e:
                            self.logger.warning(f"Error releasing capture: {e}")
                    
                    # Clear buffer before switching
                    self.cleanup_buffer()
                    self.transition_requested = True
                    self.fade_counter = self.fade_frames
                    
                    # Create new capture with retry mechanism
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            # Create new capture
                            self.cap = cv2.VideoCapture(self.idle_video_path)
                            if not self.cap.isOpened():
                                raise ValueError(f"Failed to open idle video: {self.idle_video_path}")
                            
                            # Configure capture
                            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
                            if sys.platform == 'win32':
                                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                            
                            # Test capture
                            ret, test_frame = self.cap.read()
                            if not ret or test_frame is None:
                                raise ValueError("Failed to read first frame")
                                
                            # Reset position
                            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            
                            # Update current path
                            self.current_video_path = self.idle_video_path
                            
                            # Force garbage collection
                            gc.collect()
                            
                            # Preload frames
                            self.preload_frames()
                            
                            self.logger.info("Successfully switched to idle video")
                            break
                            
                        except Exception as e:
                            if attempt < max_retries - 1:
                                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                                time.sleep(0.5)  # Wait before retry
                                if self.cap is not None:
                                    self.cap.release()
                                    self.cap = None
                                continue
                            raise
                            
        except Exception as e:
            self.logger.error(f"Failed to switch to idle video: {e}")
            self.reopen_video()
            
        finally:
            self.is_switching = False

    def cleanup(self):
        """Release resources"""
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
    def reopen_video(self):
        """Reopen current video with improved thread synchronization"""
        with video_lock:  # Use global video lock
            try:
                # Release existing capture if any
                if self.cap is not None:
                    try:
                        self.cap.release()
                        self.cap = None
                        time.sleep(0.1)  # Allow time for release
                    except Exception as e:
                        self.logger.warning(f"Error releasing existing capture: {e}")
                
                # Create new capture
                self.cap = cv2.VideoCapture(self.current_video_path)
                if not self.cap.isOpened():
                    raise ValueError(f"Failed to open video: {self.current_video_path}")
                
                # Configure capture
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
                if sys.platform == 'win32':
                    self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                
                # Test capture
                ret, test_frame = self.cap.read()
                if not ret or test_frame is None:
                    raise ValueError("Failed to read first frame")
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                
                # Force garbage collection
                gc.collect()
                
                # Wait for resources to be properly released
                time.sleep(0.1)
                
                # Preload frames
                self.preload_frames()
                
                self.logger.info(f"Successfully reopened video: {self.current_video_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to reopen video: {e}")
                if self.cap is not None:
                    try:
                        self.cap.release()
                    except:
                        pass
                    self.cap = None
                raise
