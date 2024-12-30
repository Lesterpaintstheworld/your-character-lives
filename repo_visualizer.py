import os
import asyncio
import subprocess
import logging
from threading import Thread
import tkinter as tk
from PIL import Image, ImageTk
from image_window import ImageWindow

class RepoVisualizer:
    def __init__(self, interval=10):
        """Initialize the repo visualizer"""
        self.interval = interval
        self.running = True
        self.current_process = None

    async def find_npm(self):
        """Find npm executable with detailed logging"""
        logging.info("Searching for npm installation...")
        
        # Possible npm locations
        npm_cmd = 'npm.cmd' if os.name == 'nt' else 'npm'  # Use npm.cmd on Windows
        possible_paths = [
            # Windows-specific paths
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            os.path.join(os.environ.get('APPDATA', ''), 'npm', 'npm.cmd'),
            os.path.join(os.environ.get('ProgramFiles', ''), 'nodejs', 'npm.cmd'),
            # Unix-like paths
            "/usr/local/bin/npm",
            "/usr/bin/npm",
            # Look in PATH
            npm_cmd
        ]

        # Log PATH for debugging
        logging.info(f"Current PATH: {os.environ.get('PATH', '')}")
        
        for path in possible_paths:
            try:
                logging.info(f"Trying npm at: {path}")
                process = await asyncio.create_subprocess_exec(
                    path, '--version',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    version = stdout.decode().strip()
                    logging.info(f"Found npm version {version} at {path}")
                    return path
                    
            except Exception as e:
                logging.debug(f"Failed to execute {path}: {e}")
                continue
                
        return None

    async def diagnose_npm(self):
        """Run npm installation diagnostics"""
        logging.info("=== Running npm diagnostics ===")
        
        # Check Node.js installation
        try:
            node_process = await asyncio.create_subprocess_exec(
                'node', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await node_process.communicate()
            if node_process.returncode == 0:
                logging.info(f"Node.js version: {stdout.decode().strip()}")
            else:
                logging.error("Node.js not found")
        except Exception as e:
            logging.error(f"Error checking Node.js: {e}")

        # Check PATH
        logging.info("Checking PATH environment variable...")
        path_entries = os.environ.get('PATH', '').split(os.pathsep)
        for entry in path_entries:
            logging.info(f"PATH entry: {entry}")
            if 'node' in entry.lower() or 'npm' in entry.lower():
                logging.info(f"Potential Node.js/npm path found: {entry}")
                
        # Try where/which command
        try:
            if os.name == 'nt':  # Windows
                where_process = await asyncio.create_subprocess_exec(
                    'where', 'npm',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            else:  # Unix-like
                where_process = await asyncio.create_subprocess_exec(
                    'which', 'npm',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            stdout, stderr = await where_process.communicate()
            if where_process.returncode == 0:
                logging.info(f"npm found at: {stdout.decode().strip()}")
            else:
                logging.error("npm not found in PATH")
        except Exception as e:
            logging.error(f"Error running where/which: {e}")

        logging.info("=== End npm diagnostics ===")
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

            # Check if repo-visualizer is installed globally
            try:
                process = await asyncio.create_subprocess_exec(
                    'repo-visualizer', '--version',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
            except FileNotFoundError:
                # Find npm first
                npm_path = await find_npm()
                if not npm_path:
                    await diagnose_npm()  # Run diagnostics
                    error_msg = (
                        "npm not found in system! Please ensure Node.js is installed and in your PATH.\n"
                        "Download from: https://nodejs.org/\n"
                        "After installation, you may need to restart your computer."
                    )
                    logging.error(error_msg)
                    if hasattr(self, 'status_callback'):
                        self.status_callback(f"❌ {error_msg}")
                    return False

                logging.info(f"Using npm at: {npm_path}")

                # Create temp directory for installation
                import tempfile
                temp_dir = tempfile.mkdtemp()
                logging.info(f"Created temp directory: {temp_dir}")
                
                try:
                    # Clone repo-visualizer from GitHub using HTTPS
                    if hasattr(self, 'status_callback'):
                        self.status_callback("🔄 Cloning repo-visualizer...")
                        
                    clone_process = await asyncio.create_subprocess_exec(
                        'git', 'clone', 'https://github.com/githubocto/repo-visualizer.git',
                        temp_dir,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await clone_process.communicate()
                    
                    if clone_process.returncode != 0:
                        raise Exception(f"Failed to clone repo-visualizer: {stderr.decode()}")
                        
                    logging.info("Successfully cloned repo-visualizer")
                    
                    # Change to the cloned directory
                    repo_dir = os.path.join(temp_dir, 'repo-visualizer')
                    if not os.path.exists(repo_dir):
                        raise Exception("repo-visualizer directory not found after clone")
                    
                    # Install dependencies
                    if hasattr(self, 'status_callback'):
                        self.status_callback("📦 Installing dependencies...")
                        
                    install_process = await asyncio.create_subprocess_exec(
                        npm_path, 'install',
                        cwd=repo_dir,  # Use the correct directory
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await install_process.communicate()
                    
                    if install_process.returncode != 0:
                        raise Exception(f"Failed to install dependencies: {stderr.decode()}")
                        
                    logging.info("Successfully installed dependencies")
                    
                    # Install globally
                    if hasattr(self, 'status_callback'):
                        self.status_callback("📦 Installing globally...")
                        
                    global_install_process = await asyncio.create_subprocess_exec(
                        npm_path, 'install', '-g',
                        cwd=repo_dir,  # Use the correct directory
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await global_install_process.communicate()
                    
                    if global_install_process.returncode != 0:
                        raise Exception(f"Failed to install globally: {stderr.decode()}")
                    
                    logging.info("Successfully installed repo-visualizer globally")
                    if hasattr(self, 'status_callback'):
                        self.status_callback("✅ repo-visualizer installed successfully")
                        
                finally:
                    # Cleanup temp directory
                    try:
                        import shutil
                        shutil.rmtree(temp_dir, ignore_errors=True)
                        logging.info("Cleaned up temporary installation files")
                    except Exception as e:
                        logging.warning(f"Failed to cleanup temp directory: {e}")

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
            # Cleanup temporary files
            for file in ['diagram.svg', 'diagram.png']:
                if os.path.exists(file):
                    os.remove(file)
            
            # Optionally cleanup repo-visualizer installation
            if os.path.exists(os.path.join('node_modules', 'repo-visualizer')):
                import shutil
                shutil.rmtree(os.path.join('node_modules', 'repo-visualizer'))
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
