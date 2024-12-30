import tkinter as tk
from PIL import Image, ImageTk
import logging
import os

class ImageWindow:
    def __init__(self, image_path):
        # Create root window without decorations
        self.window = tk.Tk()
        self.window.overrideredirect(True)
        self.window.attributes('-alpha', 0.9)  # Slight transparency
        
        # Load and resize image to 800x800
        self.load_image(image_path)
        
        # Create label to display image
        self.label = tk.Label(self.window, image=self.photo)
        self.label.pack()

        # Add file monitoring
        self.image_path = image_path
        self.last_modified = os.path.getmtime(image_path)
        
        # Start checking for file changes every 10 seconds
        self.check_file_changes = self.window.after(10000, self.check_for_updates)
        
        # Initialize drag variables
        self.x = 0
        self.y = 0
        
        # Bind events
        self.label.bind('<Button-1>', self.start_drag)
        self.label.bind('<B1-Motion>', self.drag)
        self.window.bind('<Double-Button-1>', self.close)
        
        # Center window on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 800) // 2
        self.window.geometry(f'+{x}+{y}')
        
    def start_drag(self, event):
        self.x = event.x
        self.y = event.y
        
    def drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f'+{x}+{y}')
        
    def load_image(self, image_path):
        """Thread-safe image loading"""
        try:
            self.image = Image.open(image_path)
            self.image = self.image.resize((800, 800), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.image)
        except Exception as e:
            logging.error(f"Error loading image: {e}")

    def check_for_updates(self):
        """Thread-safe update checker"""
        try:
            current_modified = os.path.getmtime(self.image_path)
            if current_modified > self.last_modified:
                def update_image():
                    self.load_image(self.image_path)
                    self.label.configure(image=self.photo)
                    self.last_modified = current_modified
                
                # Schedule image update on main thread
                self.window.after(0, update_image)
                
        except Exception as e:
            logging.error(f"Error checking for image updates: {e}")
        finally:
            # Schedule next check
            self.check_file_changes = self.window.after(10000, self.check_for_updates)

    def close(self, event):
        try:
            # Cancel the update checker before destroying
            if hasattr(self, 'check_file_changes'):
                self.window.after_cancel(self.check_file_changes)
            self.window.destroy()
        except Exception as e:
            logging.error(f"Error closing window: {e}")
