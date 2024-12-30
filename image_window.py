import tkinter as tk
from PIL import Image, ImageTk
import logging
import os

class ImageWindow:
    def __init__(self, root, image_path):
        """Initialize image window using provided root"""
        try:
            self.root = root
            # Create a Toplevel window instead of new Tk
            self.window = tk.Toplevel(root)
            self.window.overrideredirect(True)
            self.window.attributes('-alpha', 0.9)
            
            # Load initial image
            self.load_image(image_path)
            
            # Create label to display image
            self.label = tk.Label(self.window, image=self.photo)
            self.label.pack()
            
            # Store path and setup monitoring
            self.image_path = image_path
            self.last_modified = os.path.getmtime(image_path)
            
            # Start update checker
            self.check_file_changes = self.window.after(10000, self.check_for_updates)
            
            # Setup window dragging
            self._setup_dragging()
            
            # Center window
            self._center_window()
            
            # Keep reference to prevent garbage collection
            self.window.image = self.photo
            
            logging.info("Image window created successfully")
            
        except Exception as e:
            logging.error(f"Failed to create image window: {e}")
            raise

    def update_image(self, image_path):
        """Thread-safe image update"""
        try:
            def do_update():
                try:
                    self.load_image(image_path)
                    self.label.configure(image=self.photo)
                    self.window.image = self.photo  # Keep reference
                    self.last_modified = os.path.getmtime(image_path)
                    logging.info("Image updated successfully")
                except Exception as e:
                    logging.error(f"Error in image update: {e}")
            
            # Schedule update on main thread
            self.window.after(0, do_update)
        except Exception as e:
            logging.error(f"Failed to schedule image update: {e}")

    def _setup_dragging(self):
        """Setup window drag functionality"""
        self.x = 0
        self.y = 0
        self.label.bind('<Button-1>', self.start_drag)
        self.label.bind('<B1-Motion>', self.drag)
        self.window.bind('<Double-Button-1>', self.close)

    def _center_window(self):
        """Center window on screen"""
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
