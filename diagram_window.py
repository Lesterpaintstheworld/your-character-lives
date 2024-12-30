import tkinter as tk
from PIL import Image, ImageTk
import cairosvg
import io
import logging
import os

class DiagramWindow:
    def __init__(self):
        # Create window
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)  # Remove window decorations
        self.window.attributes('-topmost', True)  # Keep window on top
        
        # Set fixed size
        self.width = 500
        self.height = 500
        
        # Create canvas for image
        self.canvas = tk.Canvas(
            self.window, 
            width=self.width, 
            height=self.height,
            highlightthickness=0,
            bg='white'
        )
        self.canvas.pack()
        
        # Initialize drag variables
        self.x = 0
        self.y = 0
        
        # Bind events
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.drag)
        self.canvas.bind('<Double-Button-1>', self.close)
        
        # Center window on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.window.geometry(f'{self.width}x{self.height}+{x}+{y}')
        
        # Initial load
        self.load_diagram()
        
        # Set up periodic refresh
        self.check_diagram()
        
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
        self.window.after_cancel(self.check_diagram)
        self.window.destroy()
        
    def load_diagram(self):
        try:
            if os.path.exists('diagram.svg'):
                # Convert SVG to PNG using cairosvg
                png_data = cairosvg.svg2png(
                    url='diagram.svg',
                    output_width=self.width,
                    output_height=self.height
                )
                
                # Convert to PIL Image
                image = Image.open(io.BytesIO(png_data))
                
                # Convert to PhotoImage
                self.photo = ImageTk.PhotoImage(image)
                
                # Update canvas
                self.canvas.delete("all")
                self.canvas.create_image(
                    self.width//2, 
                    self.height//2, 
                    image=self.photo
                )
                
                logging.info("Diagram loaded successfully")
                
        except Exception as e:
            logging.error(f"Error loading diagram: {e}")
            
    def check_diagram(self):
        """Check for diagram updates every second"""
        self.load_diagram()
        self.window.after(1000, self.check_diagram)
