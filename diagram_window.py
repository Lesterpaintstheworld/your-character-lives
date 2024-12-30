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
        self.window.overrideredirect(True)
        
        # Set window size and background
        self.window.geometry('800x800')
        self.window.configure(bg='#0d1117')
        
        # Create canvas instead of label for better image handling
        self.canvas = tk.Canvas(
            self.window, 
            width=800, 
            height=800,
            bg='#0d1117',
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Initialize drag variables
        self.x = 0
        self.y = 0
        
        # Bind events
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.drag)
        self.window.bind('<Double-Button-1>', self.close)
        
        # Load and display the diagram
        try:
            # Get current working directory
            work_dir = os.getcwd()
            svg_path = os.path.join(work_dir, 'diagram.svg')
            
            logging.info(f"Looking for SVG at: {svg_path}")
            
            if not os.path.exists(svg_path):
                raise FileNotFoundError(f"SVG file not found at {svg_path}")
                
            # Convert SVG to PNG
            with open(svg_path, 'rb') as svg_file:
                png_data = io.BytesIO()
                svg2png(file_obj=svg_file, write_to=png_data, output_width=800, output_height=800)
                png_data.seek(0)
                
                # Create PhotoImage
                image = Image.open(png_data)
                self.photo = ImageTk.PhotoImage(image)
                
                # Display on canvas
                self.canvas.create_image(
                    400, 400,  # Center of canvas
                    image=self.photo,
                    anchor='center'
                )
                
                logging.info("Successfully loaded and displayed diagram")
                
        except Exception as e:
            logging.error(f"Error loading diagram: {e}")
            # Display error message on canvas
            self.canvas.create_text(
                400, 400,
                text=f"Error loading diagram:\n{str(e)}",
                fill='white',
                anchor='center'
            )
        
        # Center window on screen
        self.center_window()

    def center_window(self):
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

    def close(self, event):
        self.window.destroy()
