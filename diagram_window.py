import tkinter as tk
from PIL import Image, ImageTk
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import io
import logging
import os

class DiagramWindow:
    def __init__(self):
        # Create window with frame
        self.window = tk.Tk()  # Change to Tk instead of Toplevel
        self.window.title("Repository Diagram")
        
        # Set fixed size and theme colors
        self.width = 800
        self.height = 800
        
        # Dark blue theme colors
        self.bg_color = "#0d1117"  # Dark blue background
        self.frame_color = "#161b22"  # Slightly lighter blue for frame
        
        # Configure window
        self.window.configure(bg=self.bg_color)
        
        # Create main frame with padding
        self.main_frame = tk.Frame(
            self.window,
            bg=self.bg_color,
            padx=10,
            pady=10
        )
        self.main_frame.pack(fill='both', expand=True)
        
        # Create canvas with border effect
        self.canvas = tk.Canvas(
            self.main_frame, 
            width=self.width,
            height=self.height,
            bg=self.bg_color,
            highlightthickness=1,
            highlightbackground=self.frame_color
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Initialize drag variables
        self.x = 0
        self.y = 0
        
        # Bind events
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.drag)
        
        # Add window resize binding
        self.window.bind('<Configure>', self.on_resize)
        
        # Center window on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.window.geometry(f'{self.width}x{self.height}+{x}+{y}')
        
        # Set minimum window size
        self.window.minsize(400, 400)
        
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
        """Load and display the SVG diagram with enhanced error handling"""
        try:
            if not os.path.exists('diagram.svg'):
                logging.error("diagram.svg file not found")
                return

            # Log file details
            file_size = os.path.getsize('diagram.svg')
            logging.info(f"Found diagram.svg: {file_size} bytes")

            try:
                # First attempt: Try cairosvg
                from cairosvg import svg2png
                logging.info("Attempting conversion with cairosvg...")
                
                # Create BytesIO object for PNG data
                png_data = io.BytesIO()
                
                with open('diagram.svg', 'rb') as svg_file:
                    svg_content = svg_file.read()
                    logging.info(f"Read SVG content: {len(svg_content)} bytes")
                    
                    svg2png(
                        bytestring=svg_content,
                        write_to=png_data,
                        scale=2.0
                    )
                    
                png_data.seek(0)
                logging.info(f"Generated PNG data: {len(png_data.getvalue())} bytes")

            except (ImportError, Exception) as e:
                logging.warning(f"cairosvg conversion failed: {e}")
                
                try:
                    # Second attempt: Try svglib
                    logging.info("Attempting conversion with svglib...")
                    from svglib.svglib import svg2rlg
                    from reportlab.graphics import renderPM
                    
                    drawing = svg2rlg('diagram.svg')
                    if drawing:
                        png_data = io.BytesIO()
                        renderPM.drawToFile(drawing, png_data, fmt='PNG')
                        png_data.seek(0)
                        logging.info("svglib conversion successful")
                    else:
                        raise ValueError("svg2rlg returned None")

                except Exception as e2:
                    logging.error(f"Both conversion methods failed: {e2}")
                    # Create a simple placeholder image
                    logging.info("Creating placeholder image...")
                    from PIL import Image, ImageDraw
                    
                    img = Image.new('RGB', (400, 300), color='darkgray')
                    draw = ImageDraw.Draw(img)
                    draw.text((10, 10), "Diagram Conversion Failed", fill='white')
                    draw.text((10, 30), f"Error: {str(e2)}", fill='white')
                    
                    png_data = io.BytesIO()
                    img.save(png_data, format='PNG')
                    png_data.seek(0)

            # Convert to PIL Image and display
            try:
                new_image = Image.open(png_data)
                logging.info(f"Created PIL Image: {new_image.size}")
                
                new_photo = ImageTk.PhotoImage(new_image)
                logging.info("Created Tkinter PhotoImage")
                
                # Update display
                if hasattr(self, 'photo'):
                    self._fade_transition(new_photo)
                else:
                    self.photo = new_photo
                    self.canvas.delete("all")
                    self.canvas.create_image(
                        self.width//2, 
                        self.height//2, 
                        image=self.photo,
                        tags="diagram"
                    )
                
                logging.info("Diagram displayed successfully")
                return True

            except Exception as e:
                logging.error(f"Failed to display image: {e}")
                return False

        except Exception as e:
            logging.error(f"Critical error in load_diagram: {e}")
            return False
            
    def check_diagram(self):
        """Check for diagram updates every 10 seconds"""
        self.load_diagram()
        self.window.after(10000, self.check_diagram)  # Changed from 1000 to 10000 milliseconds
        
    def _fade_transition(self, new_photo, steps=10, duration=500):
        """
        Perform a smooth fade transition between diagrams
        
        Args:
            new_photo: The new PhotoImage to transition to
            steps: Number of opacity steps (default 10)
            duration: Total duration of transition in milliseconds (default 500)
        """
        try:
            # Store the new photo as an instance variable to prevent garbage collection
            self.new_photo = new_photo
            
            # Create overlay rectangle if it doesn't exist
            if not hasattr(self, 'overlay'):
                self.overlay = self.canvas.create_rectangle(
                    0, 0, self.width, self.height,
                    fill='white', stipple='gray50',
                    state='hidden'
                )
            
            # Calculate delay between steps
            step_delay = duration // steps
            
            def fade_step(step=0):
                if step <= steps:
                    # Calculate opacity (0 to 1)
                    opacity = step / steps
                    
                    if step == 0:
                        # Start of transition - show old image with overlay
                        self.canvas.itemconfig(self.overlay, state='normal')
                    elif step == steps:
                        # End of transition - update to new image and hide overlay
                        self.photo = self.new_photo
                        self.canvas.delete("diagram")
                        self.canvas.create_image(
                            self.width//2, 
                            self.height//2, 
                            image=self.photo,
                            tags="diagram"
                        )
                        self.canvas.itemconfig(self.overlay, state='hidden')
                    else:
                        # During transition - update overlay opacity
                        stipple = f'gray{int(opacity * 100)}'
                        self.canvas.itemconfig(self.overlay, stipple=stipple)
                    
                    # Schedule next step
                    self.window.after(step_delay, lambda: fade_step(step + 1))
            
            # Start the transition
            fade_step()
            
        except Exception as e:
            logging.error(f"Error during transition: {e}")
            # Fallback to immediate update if transition fails
            self.photo = new_photo
            self.canvas.delete("all")
            self.canvas.create_image(
                self.width//2, 
                self.height//2, 
                image=self.photo
            )
    def on_resize(self, event):
        """Handle window resize events"""
        # Only resize if the window size has actually changed
        if hasattr(self, 'last_width') and hasattr(self, 'last_height'):
            if event.width == self.last_width and event.height == self.last_height:
                return
                
        self.last_width = event.width
        self.last_height = event.height
        
        # Update canvas size
        self.width = event.width - 20  # Account for padding
        self.height = event.height - 20
        
        # Reload diagram at new size
        self.load_diagram()
