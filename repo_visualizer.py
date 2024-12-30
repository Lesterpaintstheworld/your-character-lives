import os
import sys
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

        # Remove PATH logging and just try each location
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
        
        # Start visualization loop in a separate thread
        self.visualization_thread = Thread(
            target=lambda: asyncio.run(self.visualization_loop()),
            daemon=True
        )
        self.visualization_thread.start()
        
    async def verify_repo_integrity(self):
        """Verify repo-visualizer installation is intact"""
        if getattr(sys, 'frozen', False):
            install_dir = os.path.dirname(sys.executable)
        else:
            install_dir = os.path.dirname(os.path.abspath(__file__))
            
        repo_dir = os.path.join(install_dir, "repo-visualizer")
        
        # Check if essential files exist
        essential_files = ['package.json', 'src', 'bin']
        
        if not os.path.exists(repo_dir):
            return False
            
        for file in essential_files:
            if not os.path.exists(os.path.join(repo_dir, file)):
                return False
                
        return True

    async def generate_visualization(self):
        """Generate repository visualization"""
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
        except Exception as e:
            logging.error(f"Error checking Node.js: {e}")
            return False

        # Get the installation directory
        try:
            if getattr(sys, 'frozen', False):
                install_dir = os.path.dirname(sys.executable)
            else:
                install_dir = os.path.dirname(os.path.abspath(__file__))
                
            # Path to repo-visualizer in install directory
            repo_dir = os.path.join(install_dir, "repo-visualizer")
            logging.info(f"Looking for repo-visualizer at: {repo_dir}")

            # If repo directory is missing or damaged, clone it
            if not os.path.exists(repo_dir) or not await self.verify_repo_integrity():
                logging.info("Cloning repo-visualizer repository...")
                if os.path.exists(repo_dir):
                    logging.info("Removing damaged repo directory...")
                    import shutil
                    shutil.rmtree(repo_dir)
                    
                # Clone the repository
                process = await asyncio.create_subprocess_exec(
                    'git', 'clone', 'https://github.com/githubocto/repo-visualizer.git',
                    repo_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    logging.info("Successfully cloned repo-visualizer")
                    
                    # Install dependencies
                    npm_process = await asyncio.create_subprocess_exec(
                        'npm', 'install',
                        cwd=repo_dir,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await npm_process.communicate()
                    
                    if npm_process.returncode == 0:
                        logging.info("Successfully installed dependencies")
                    else:
                        error_msg = f"Failed to install dependencies: {stderr.decode()}"
                        logging.error(error_msg)
                        return False
                else:
                    error_msg = f"Failed to clone repository: {stderr.decode()}"
                    logging.error(error_msg)
                    return False

            # Use npx to run the local version
            if hasattr(self, 'status_callback'):
                self.status_callback("🔄 Generating repository visualization...")

            self.current_process = await asyncio.create_subprocess_exec(
                'npx', '--prefix', repo_dir, 'repo-visualizer',
                '--output', 'diagram.svg',
                '--exclude', '.git,.aider,__pycache__,build,dist',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await self.current_process.communicate()
            
            if stdout:
                logging.info(f"Command stdout: {stdout.decode()}")
            if stderr:
                logging.error(f"Command stderr: {stderr.decode()}")
                
            if self.current_process.returncode == 0:
                logging.info("Generated visualization successfully")
            else:
                logging.error(f"Visualization failed with return code {self.current_process.returncode}")
                logging.error(f"Error output: {stderr.decode()}")
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
                if hasattr(self, 'status_callback'):
                    self.status_callback("✨ Repository visualization updated")
                return True
            except Exception as e:
                logging.error(f"Failed to convert SVG to PNG: {e}")
                if hasattr(self, 'status_callback'):
                    self.status_callback("❌ Failed to convert visualization")
                return False

        except FileNotFoundError as e:
            msg = f"File not found error: {e}"
            logging.error(msg)
            if hasattr(self, 'status_callback'):
                self.status_callback(f"❌ {msg}")
            return False
        except Exception as e:
            logging.error(f"Failed to generate visualization: {e}")
            if hasattr(self, 'status_callback'):
                self.status_callback("❌ Failed to generate visualization")
            return False
                except Exception as e:
                    logging.error(f"Failed to clone repo-visualizer: {e}")
                    if hasattr(self, 'status_callback'):
                        self.status_callback("❌ Failed to clone repo-visualizer")
                    return False
                if hasattr(self, 'status_callback'):
                    self.status_callback("🔄 Generating repository visualization...")
                # Use npx to run the local version
                self.current_process = await asyncio.create_subprocess_exec(
                    'npx', '--prefix', repo_dir, 'repo-visualizer',
                    '--output', 'diagram.svg',
                    '--exclude', '.git,.aider,__pycache__,build,dist',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await self.current_process.communicate()
                
                # Log command output
                if stdout:
                    logging.info(f"Command stdout: {stdout.decode()}")
                if stderr:
                    logging.error(f"Command stderr: {stderr.decode()}")
                    
                if self.current_process.returncode == 0:
                    logging.info("Generated visualization successfully")
                else:
                    logging.error(f"Visualization failed with return code {self.current_process.returncode}")
                    logging.error(f"Error output: {stderr.decode()}")
                    return False
            except Exception as e:
                logging.error(f"Error generating visualization: {e}")
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
        finally:
            pass

    async def visualization_loop(self):
        """Run continuous visualization generation"""
        while self.running:
            try:
                # Verify repo integrity first
                if not await self.verify_repo_integrity():
                    logging.warning("repo-visualizer installation appears damaged, attempting repair...")
                    success = await self.generate_visualization()  # This will trigger a fresh clone
                    if not success:
                        logging.error("Failed to repair repo-visualizer")
                        await asyncio.sleep(self.interval)
                        continue
                
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
            # Only cleanup temporary files
            for file in ['diagram.svg', 'diagram.png']:
                if os.path.exists(file):
                    os.remove(file)
        except:
            pass

def start_visualization():
    """Start the repository visualization system"""
    # Create visualizer with shorter initial interval
    visualizer = RepoVisualizer(interval=10)
    
    # Generate initial visualization immediately
    try:
        asyncio.run(visualizer.generate_visualization())
        logging.info("Initial visualization generated")
    except Exception as e:
        logging.error(f"Initial visualization failed: {e}")
    
    # Check for and display diagram
    if os.path.exists('diagram.png'):
        try:
            ImageWindow('diagram.png')
            logging.info("Displaying repository visualization")
        except Exception as e:
            logging.error(f"Error displaying visualization: {e}")
    
    return visualizer
