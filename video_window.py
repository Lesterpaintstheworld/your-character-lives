"""Draggable borderless video window implementation"""
import cv2
from PIL import Image, ImageTk
import tkinter as tk
import logging

class DraggableVideoWindow:
    def __init__(self, video_path):
        """Initialize video window with given video path"""
        self.logger = logging.getLogger(__name__)
        
        # Create borderless window
        self.window = tk.Tk()
        self.window.overrideredirect(True)  # Remove window borders/title
        self.window.attributes('-topmost', True)  # Keep window on top
        self.window.attributes('-alpha', 1.0)  # Full opacity
        
        # Create video label
        self.label = tk.Label(self.window)
        self.label.pack()
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            self.logger.error(f"Could not open video file: {video_path}")
            raise ValueError(f"Could not open video file: {video_path}")
            
        # Get video properties
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Set initial window size
        self.window.geometry(f"{self.width}x{self.height}+100+100")
        
        # Bind mouse events for dragging
        self.label.bind('<Button-1>', self.start_drag)
        self.label.bind('<B1-Motion>', self.drag)
        
        # Bind mouse events for resizing
        self.label.bind('<Button-3>', self.start_resize)  # Right click
        self.label.bind('<B3-Motion>', self.resize)
        
        # Bind double-click to close
        self.label.bind('<Double-Button-1>', self.close_window)
        
        # Bind middle click to toggle transparency
        self.label.bind('<Button-2>', self.toggle_transparency)
        
        # Store drag and resize data
        self.drag_data = {'x': 0, 'y': 0, 'item': None}
        self.resize_data = {'x': 0, 'y': 0}
        self.is_transparent = False
        
        # Start video loop
        self.update_frame()
        
    def start_drag(self, event):
        """Begin drag of window"""
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y
        
    def drag(self, event):
        """Handle window dragging"""
        dx = event.x - self.drag_data['x']
        dy = event.y - self.drag_data['y']
        x = self.window.winfo_x() + dx
        y = self.window.winfo_y() + dy
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
        
    def update_frame(self):
        """Update video frame"""
        try:
            ret, frame = self.cap.read()
            if not ret:
                # Reset video to start when it ends
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                
            if ret:
                # Convert frame to proper format
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Resize frame to window size
                current_width = self.window.winfo_width()
                current_height = self.window.winfo_height()
                frame = cv2.resize(frame, (current_width, current_height))
                
                # Convert to PhotoImage
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=image)
                
                # Update label
                self.label.configure(image=photo)
                self.label.image = photo  # Keep a reference!
                
            # Schedule next update
            self.window.after(33, self.update_frame)  # ~30 FPS
            
        except Exception as e:
            self.logger.error(f"Error updating video frame: {e}")
            
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
        if self.cap is not None:
            self.cap.release()
