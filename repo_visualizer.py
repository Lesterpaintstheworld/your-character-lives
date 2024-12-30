import os
import asyncio
import subprocess
import logging
from threading import Thread
import tkinter as tk
from PIL import Image, ImageTk
from main import ImageWindow

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
            # Check for Node.js first
            try:
                process = await asyncio.create_subprocess_exec(
                    'node', '--version',
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await process.wait()
            except FileNotFoundError:
                logging.error("Node.js not found! Please install Node.js from https://nodejs.org/")
                if hasattr(self, 'status_callback'):
                    self.status_callback("❌ Node.js not found - please install Node.js")
                return False

            # Check if repo-visualizer is installed
            process = await asyncio.create_subprocess_exec(
                'repo-visualizer', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            # Check if repo-visualizer needs to be built
            repo_visualizer_path = os.path.join(os.getcwd(), 'node_modules', 'repo-visualizer')
            dist_path = os.path.join(repo_visualizer_path, 'dist')
            
            if not os.path.exists(dist_path):
                if hasattr(self, 'status_callback'):
                    self.status_callback("🔨 Building repo-visualizer...")
                logging.info("repo-visualizer needs to be built. Attempting build...")
                try:
                    # Install dependencies
                    process = await asyncio.create_subprocess_exec(
                        'npm', 'install',
                        cwd=repo_visualizer_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await process.communicate()
                    
                    # Run build
                    process = await asyncio.create_subprocess_exec(
                        'npm', 'run', 'build',
                        cwd=repo_visualizer_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await process.communicate()
                except Exception as e:
                    logging.error(f"Failed to build repo-visualizer: {e}")
                    if hasattr(self, 'status_callback'):
                        self.status_callback("❌ Failed to build repo-visualizer")
                    return False

            # Generate visualization
            if hasattr(self, 'status_callback'):
                self.status_callback("🔄 Generating repository visualization...")
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
                # Cleanup SVG file
                try:
                    if os.path.exists('diagram.svg'):
                        os.remove('diagram.svg')
                except Exception as e:
                    logging.warning(f"Could not remove temporary SVG file: {e}")
                
                if hasattr(self, 'status_callback'):
                    self.status_callback("✨ Repository visualization updated")
                return True
            except Exception as e:
                logging.error(f"Failed to convert SVG to PNG: {e}")
                if hasattr(self, 'status_callback'):
                    self.status_callback("❌ Failed to convert visualization")
                return False
                
        except FileNotFoundError:
            msg = "repo-visualizer not found. Install with: npm install -g repo-visualizer"
            logging.error(msg)
            if hasattr(self, 'status_callback'):
                self.status_callback(f"❌ {msg}")
            return False
        except Exception as e:
            logging.error(f"Failed to generate visualization: {e}")
            if hasattr(self, 'status_callback'):
                self.status_callback("❌ Failed to generate visualization")
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
        """Stop the visualization loop and cleanup"""
        self.running = False
        if self.current_process:
            try:
                self.current_process.terminate()
            except:
                pass
        try:
            if os.path.exists('diagram.svg'):
                os.remove('diagram.svg')
        except:
            pass

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
