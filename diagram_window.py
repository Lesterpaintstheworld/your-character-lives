import os
import tkinter as tk
from PIL import Image, ImageTk
from cairosvg import svg2png
import io
import logging

class DiagramWindow:
    def __init__(self):
        # Create main window
        self.window = tk.Tk()
        self.window.title("Repository Diagram")
        
        # Create canvas that fills the window
        self.canvas = tk.Canvas(self.window, bg='#0d1117')  # Dark background
        self.canvas.pack(fill='both', expand=True)
        
        # Initialize image references
        self.image = None
        self.photo = None
        self.canvas_image = None
        
        # Bind resize event with delay
        self.resize_after_id = None
        self.window.bind('<Configure>', self.on_resize)
        
        # Initial load
        self.load_diagram()
        
        # Center window on screen
        self.window.geometry('800x800')
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 800) // 2
        self.window.geometry(f'+{x}+{y}')

    def load_diagram(self):
        """Load and display the SVG diagram"""
        try:
            # Convert SVG to PNG
            with open('diagram.svg', 'rb') as svg_file:
                png_data = io.BytesIO()
                svg2png(file_obj=svg_file, write_to=png_data)
                png_data.seek(0)
                
                # Load the base image
                self.image = Image.open(png_data)
                
                # Create initial PhotoImage
                self.update_display()
                
        except Exception as e:
            logging.error(f"Error loading diagram: {e}")

    def update_display(self):
        """Update the displayed image with current window dimensions"""
        if not self.image:
            return
            
        # Get current window dimensions
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        if width <= 1 or height <= 1:  # Skip invalid dimensions
            return
            
        # Calculate new dimensions maintaining aspect ratio
        img_ratio = self.image.width / self.image.height
        win_ratio = width / height
        
        if win_ratio > img_ratio:
            # Window is wider than image
            new_height = height
            new_width = int(height * img_ratio)
        else:
            # Window is taller than image
            new_width = width
            new_height = int(width / img_ratio)
        
        # Resize image
        resized = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Update PhotoImage
        self.photo = ImageTk.PhotoImage(resized)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas_image = self.canvas.create_image(
            width//2, height//2,
            image=self.photo,
            anchor='center'
        )

    def on_resize(self, event):
        """Handle window resize with debouncing"""
        if event.widget == self.window:
            # Cancel previous resize timer
            if self.resize_after_id:
                self.window.after_cancel(self.resize_after_id)
            
            # Set new timer for resize
            self.resize_after_id = self.window.after(100, self.update_display)
