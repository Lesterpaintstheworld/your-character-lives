"""Draggable borderless video window implementation"""
import cv2
from PIL import Image, ImageTk
import tkinter as tk
import logging
import os

class DraggableVideoWindow:
    def __init__(self, video_path):
        """Initialize video window with given video path"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing DraggableVideoWindow")
        
        if not os.path.exists(video_path):
            self.logger.error(f"Video file not found: {video_path}")
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        try:
            # Initialize video capture
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                self.logger.error("Failed to open video capture")
                raise ValueError("Failed to open video capture")
                
            # Get video properties
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.logger.info(f"Video dimensions: {self.width}x{self.height}")
            
            # Create window
            self.logger.info("Creating Tkinter window")
            self.window = tk.Toplevel()
            self.window.withdraw()  # Hide window initially
            
            # Configure window
            self.window.overrideredirect(True)
            self.window.attributes('-topmost', True)
            self.window.attributes('-alpha', 1.0)
            
            # Set window size
            self.width = max(320, self.width // 2)  # Minimum width of 320
            self.height = max(240, self.height // 2)  # Minimum height of 240
            self.window.geometry(f"{self.width}x{self.height}+100+100")
            
            # Create video display label
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
        
    def resize(self, event):
        """Handle window resizing"""
        dx = event.x - self.resize_data['x']
        dy = event.y - self.resize_data['y']
        width = max(50, self.window.winfo_width() + dx)
        height = max(50, self.window.winfo_height() + dy)
        self.window.geometry(f"{width}x{height}")
        self.resize_data['x'] = event.x
        self.resize_data['y'] = event.y
        
    def close_window(self, event):
        """Close the window on double-click"""
        self.window.quit()
        
    def toggle_transparency(self, event):
        """Toggle window transparency on middle click"""
        self.is_transparent = not self.is_transparent
        self.window.attributes('-alpha', 0.5 if self.is_transparent else 1.0)
        
    def _bind_events(self):
        """Bind all window events"""
        try:
            self.label.bind('<Button-1>', self.start_drag)
            self.label.bind('<B1-Motion>', self.drag)
            self.label.bind('<Button-3>', self.start_resize)
            self.label.bind('<B3-Motion>', self.resize)
            self.label.bind('<Double-Button-1>', self.close_window)
            self.label.bind('<Button-2>', self.toggle_transparency)
            self.logger.info("Events bound successfully")
        except Exception as e:
            self.logger.error(f"Failed to bind events: {e}")
            raise

    def display_frame(self, frame):
        """Convert and display a frame"""
        try:
            if frame is None:
                self.logger.error("Received None frame")
                return
                
            # Convert frame from BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get current window dimensions
            try:
                current_width = self.window.winfo_width()
                current_height = self.window.winfo_height()
            except Exception as e:
                self.logger.error(f"Failed to get window dimensions: {e}")
                current_width = self.width
                current_height = self.height
                
            # Resize frame
            resized = cv2.resize(rgb_frame, (current_width, current_height))
            
            # Convert to PIL Image and PhotoImage
            self.image = Image.fromarray(resized)
            self.photo = ImageTk.PhotoImage(image=self.image)
            
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
        """Update video frame"""
        if not hasattr(self, 'window') or not self.window.winfo_exists():
            return
            
        try:
            ret, frame = self.cap.read()
            if not ret:
                # Reset video to start
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    self.logger.error("Could not read video frame even after reset")
                    self.window.after(33, self.update_frame)
                    return
            
            self.display_frame(frame)
            
        except Exception as e:
            self.logger.error(f"Error updating video frame: {e}")
            
        finally:
            if hasattr(self, 'window') and self.window.winfo_exists():
                self.window.after(33, self.update_frame)
            
    def run(self):
        """Start the video window"""
        try:
            self.window.mainloop()
        except Exception as e:
            self.logger.error(f"Error in video window main loop: {e}")
        finally:
            self.cleanup()
        
    def cleanup(self):
        """Release resources"""
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
