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
        self.window.overrideredirect(True)  # Remove window decorations
        
        # Create label for image
        self.label = tk.Label(self.window, bg='#0d1117')
        self.label.pack()
        
        # Initialize drag variables
        self.x = 0
        self.y = 0
        
        # Bind events
        self.label.bind('<Button-1>', self.start_drag)
        self.label.bind('<B1-Motion>', self.drag)
        self.window.bind('<Double-Button-1>', self.close)
        
        # Load initial image
        self.load_diagram()
        
        # Center window on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 800) // 2
        self.window.geometry(f'800x800+{x}+{y}')

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
        self.window.destroy()

    def load_diagram(self):
        """Load and display the SVG diagram at fixed 800x800 size"""
        try:
            # Convert SVG to PNG
            with open('diagram.svg', 'rb') as svg_file:
                png_data = io.BytesIO()
                svg2png(file_obj=svg_file, write_to=png_data)
                png_data.seek(0)
                
                # Load and resize image
                image = Image.open(png_data)
                image = image.resize((800, 800), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage and keep reference
                self.photo = ImageTk.PhotoImage(image)
                
                # Update label
                self.label.configure(image=self.photo)
                
        except Exception as e:
            logging.error(f"Error loading diagram: {e}")
