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
        
        # Check if video file exists
        if not os.path.exists(video_path):
            self.logger.error(f"Video file not found: {video_path}")
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        self.logger.info(f"Initializing video window with: {video_path}")
        
        # Initialize video capture first
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            self.logger.error(f"Could not open video file: {video_path}")
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if self.width == 0 or self.height == 0:
            self.logger.error("Invalid video dimensions")
            raise ValueError("Invalid video dimensions")
            
        self.logger.info(f"Video dimensions: {self.width}x{self.height}")
        
        # Create main window
        self.window = tk.Toplevel()  # Use Toplevel instead of Tk
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 1.0)
        
        # Set initial window size to half the video size
        self.width = self.width // 2
        self.height = self.height // 2
        self.window.geometry(f"{self.width}x{self.height}+100+100")
        
        # Create label for video display
        self.label = tk.Label(self.window, bg='black')
        self.label.pack(fill='both', expand=True)
        
        # Initialize PhotoImage storage
        self.photo = None
        self.image = None
        
        # Initialize drag and resize data
        self.drag_data = {'x': 0, 'y': 0}
        self.resize_data = {'x': 0, 'y': 0}
        self.is_transparent = False
        
        # Bind mouse events
        self.label.bind('<Button-1>', self.start_drag)
        self.label.bind('<B1-Motion>', self.drag)
        self.label.bind('<Button-3>', self.start_resize)
        self.label.bind('<B3-Motion>', self.resize)
        self.label.bind('<Double-Button-1>', self.close_window)
        self.label.bind('<Button-2>', self.toggle_transparency)
        
        # Read first frame to initialize display
        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)
            self.logger.info("First frame displayed successfully")
        else:
            self.logger.error("Failed to read first frame")
            raise ValueError("Failed to read first frame")
        
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
        
    def display_frame(self, frame):
        """Convert and display a frame"""
        try:
            # Convert frame from BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize frame to window size
            current_width = self.window.winfo_width()
            current_height = self.window.winfo_height()
            resized = cv2.resize(rgb_frame, (current_width, current_height))
            
            # Convert to PIL Image
            self.image = Image.fromarray(resized)
            
            # Convert to PhotoImage
            self.photo = ImageTk.PhotoImage(image=self.image)
            
            # Update label
            self.label.configure(image=self.photo)
            
        except Exception as e:
            self.logger.error(f"Error displaying frame: {e}")

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
