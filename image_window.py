import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import logging

class ImageWindow:
    def __init__(self, image_path):
        self.image_path = image_path  # Store the path
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)  # Remove window decorations
        self.window.configure(bg='white')
        
        # Add file monitoring
        self.last_modified = os.path.getmtime(image_path)
        
        # Load and display image
        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image)
        self.label = tk.Label(self.window, image=self.photo, bg='white')
        self.label.pack(padx=2, pady=2)

        # Create and start update checker
        self.check_file_changes()
        
        # Bind events
        self.label.bind('<Button-1>', self.start_drag)
        self.label.bind('<B1-Motion>', self.drag)
        self.window.bind('<Double-Button-1>', self.close)
        self.window.bind('<Configure>', self.on_resize)
        
        # Add resize grip
        self.grip = ttk.Sizegrip(self.window)
        self.grip.place(relx=1.0, rely=1.0, anchor='se')
        
        # Initialize drag variables
        self.x = 0
        self.y = 0
        
        # Center window on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - self.image.width) // 2
        y = (screen_height - self.image.height) // 2
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
        
    def close(self, event):
        # Cancel the update checker before destroying
        self.window.after_cancel(self.check_file_changes)
        self.window.destroy()
        
    def check_file_changes(self):
        """Check if image file has been modified"""
        try:
            current_modified = os.path.getmtime(self.image_path)
            if current_modified != self.last_modified:
                # Reload image
                new_image = Image.open(self.image_path)
                
                # Keep current window size
                current_width = self.window.winfo_width()
                current_height = self.window.winfo_height()
                
                # Update image maintaining current window size
                self.image = new_image
                ratio = min(current_width / self.image.width, 
                          current_height / self.image.height)
                new_width = int(self.image.width * ratio)
                new_height = int(self.image.height * ratio)
                
                resized = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(resized)
                self.label.configure(image=self.photo)
                
                self.last_modified = current_modified
                logging.info(f"Updated image from {self.image_path}")
                
        except Exception as e:
            logging.error(f"Error checking/updating image: {e}")
            
        finally:
            # Schedule next check in 1 second
            self.window.after(1000, self.check_file_changes)
        
    def on_resize(self, event):
        # Only resize if the window size has actually changed
        if hasattr(self, 'last_width') and hasattr(self, 'last_height'):
            if event.width == self.last_width and event.height == self.last_height:
                return
                
        self.last_width = event.width
        self.last_height = event.height
        
        # Get original image dimensions
        orig_width = self.image.width
        orig_height = self.image.height
        
        # Calculate maximum dimensions while maintaining aspect ratio
        max_width = min(event.width - 4, 1920)  # Subtract padding, add max limit
        max_height = min(event.height - 4, 1080)  # Subtract padding, add max limit
        
        # Calculate scaling ratio while maintaining aspect ratio
        ratio = min(max_width / orig_width, max_height / orig_height)
        
        # Calculate new dimensions
        new_width = int(orig_width * ratio)
        new_height = int(orig_height * ratio)
        
        # Resize image
        resized = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized)
        self.label.configure(image=self.photo)
