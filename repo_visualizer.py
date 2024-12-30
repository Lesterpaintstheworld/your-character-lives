import os
import asyncio
import subprocess
import logging
from threading import Thread
import tkinter as tk
from PIL import Image, ImageTk

class RepoVisualizer:
    def __init__(self, interval=10):
        self.interval = interval
        self.running = True
        self.current_process = None
        
        # Start visualization loop in a separate thread
        self.visualization_thread = Thread(
            target=lambda: asyncio.run(self.visualization_loop()),
            daemon=True
        )
        self.visualization_thread.start()
        
    async def generate_visualization(self):
        """Generate repository visualization"""
        try:
            # Check if repo-visualizer is installed
            process = await asyncio.create_subprocess_exec(
                'repo-visualizer', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            # Generate visualization
            self.current_process = await asyncio.create_subprocess_exec(
                'repo-visualizer',
                '--output', 'diagram.svg',
                '--exclude', '.git,.aider,__pycache__,build,dist',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await self.current_process.communicate()
            
            if self.current_process.returncode != 0:
                logging.error(f"Visualization failed: {stderr.decode()}")
                return False
                
            # Convert SVG to PNG using cairosvg
            try:
                from cairosvg import svg2png
                with open('diagram.svg', 'rb') as svg_file:
                    svg2png(
                        file_obj=svg_file,
                        write_to='diagram.png',
                        output_width=1024,
                        output_height=1024
                    )
                logging.info("Generated new repository visualization")
                return True
            except Exception as e:
                logging.error(f"Failed to convert SVG to PNG: {e}")
                return False
                
        except FileNotFoundError:
            logging.error("repo-visualizer not found. Install with: npm install -g repo-visualizer")
            return False
        except Exception as e:
            logging.error(f"Failed to generate visualization: {e}")
            return False

    async def visualization_loop(self):
        """Run continuous visualization generation"""
        while self.running:
            try:
                success = await self.generate_visualization()
                if success:
                    logging.info(f"Visualization updated successfully")
                await asyncio.sleep(self.interval)
            except Exception as e:
                logging.error(f"Error in visualization loop: {e}")
                await asyncio.sleep(self.interval)

    def stop(self):
        """Stop the visualization loop"""
        self.running = False
        if self.current_process:
            self.current_process.terminate()

def start_visualization():
    """Start the repository visualization system"""
    # Create and start visualizer
    visualizer = RepoVisualizer(interval=10)
    
    # Check for and display diagram
    if os.path.exists('diagram.png'):
        try:
            ImageWindow('diagram.png')
            logging.info("Displaying repository visualization")
        except Exception as e:
            logging.error(f"Error displaying visualization: {e}")
    
    return visualizer
