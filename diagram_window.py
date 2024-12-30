import tkinter as tk
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
        
        # Initialize drag variables
        self.x = 0
        self.y = 0
        
        # Bind events
        self.window.bind('<Button-1>', self.start_drag)
        self.window.bind('<B1-Motion>', self.drag)
        self.window.bind('<Double-Button-1>', self.close)
        
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
