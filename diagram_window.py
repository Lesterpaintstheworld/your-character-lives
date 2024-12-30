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
        
        # Bind resize event
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
                
                # Load and display the image
                self.image = Image.open(png_data)
                self.photo = ImageTk.PhotoImage(self.image)
                
                # Update canvas
                self.canvas.delete("all")
                self.canvas.create_image(
                    self.canvas.winfo_width()//2,
                    self.canvas.winfo_height()//2,
                    image=self.photo,
                    anchor='center'
                )
                
        except Exception as e:
            logging.error(f"Error loading diagram: {e}")

    def on_resize(self, event):
        """Handle window resize"""
        # Only resize if window dimensions actually changed
        if event.widget == self.window:
            # Get new dimensions
            width = event.width
            height = event.height
            
            if hasattr(self, 'image'):
                # Resize image to fit window while maintaining aspect ratio
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
                
                # Resize and display
                resized = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(resized)
                
                # Update canvas
                self.canvas.delete("all")
                self.canvas.create_image(
                    width//2, height//2,
                    image=self.photo,
                    anchor='center'
                )
