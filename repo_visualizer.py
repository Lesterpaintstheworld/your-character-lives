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
        self.image_queue = queue.Queue()
        self.root = None
        self.image_window = None

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
        
    async def ensure_npm_dependencies(self):
        """Install npm dependencies if needed"""
        try:
            npm_path = await self.find_npm()
            if not npm_path:
                logging.error("npm not found")
                return False
                
            process = await asyncio.create_subprocess_exec(
                npm_path, 'install',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logging.info("Successfully installed npm dependencies")
                return True
            else:
                logging.error(f"Failed to install dependencies: {stderr.decode()}")
                return False
                
        except Exception as e:
            logging.error(f"Error installing npm dependencies: {e}")
            return False

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

    async def generate_visualization(self):
        """Generate repository visualization"""
        try:
            # Get the current working directory at start
            working_dir = os.getcwd()
            logging.info(f"Working directory: {working_dir}")

            # Get path to local repo-visualizer installation
            if getattr(sys, 'frozen', False):
                install_dir = os.path.dirname(sys.executable)
            else:
                install_dir = os.path.dirname(os.path.abspath(__file__))
                
            repo_viz_path = os.path.join(install_dir, "repo-visualizer", "index.js")
            logging.info(f"Using repo-visualizer at: {repo_viz_path}")

            # Build command with the working node flags
            cmd = [
                'node',
                '--force-node-api-uncaught-exceptions-policy=true',
                repo_viz_path,
                '--output', 'diagram.svg',
                '--exclude', (
                    '.git,.aider,__pycache__,build,dist,'
                    '*.log,*.pyc,*.pyo,*.pyd,*.so,*.dll,*.dylib,'  # Compiled/binary files
                    '*.egg-info,*.egg,*.whl,'  # Python package files
                    '*.coverage,htmlcov/,'  # Test coverage files
                    'node_modules,.env,.venv,venv,env,'  # Environment and dependency dirs
                    '.DS_Store,Thumbs.db,'  # System files
                    '*.bak,*.swp,*.swo,*~,'  # Backup and temp files
                    '*.png,*.jpg,*.jpeg,*.gif,*.ico,'  # Image files
                    '*.mp3,*.wav,*.mp4,*.avi,*.mov,'  # Media files
                    '*.zip,*.tar,*.gz,*.rar,'  # Archive files
                    '*.sqlite,*.db'  # Database files
                )
            ]
            logging.info(f"Executing command: {' '.join(cmd)}")

            # Run the command
            self.current_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )
            
            stdout, stderr = await self.current_process.communicate()
            
            # Log ALL output regardless of return code
            if stdout:
                logging.info(f"Command stdout:\n{stdout.decode()}")
            if stderr:
                logging.info(f"Command stderr:\n{stderr.decode()}")
                
            # Check if SVG was created successfully, regardless of return code
            svg_path = os.path.join(working_dir, 'diagram.svg')
            if os.path.exists(svg_path):
                logging.info(f"SVG file found at: {svg_path}")
                logging.info(f"SVG file size: {os.path.getsize(svg_path)} bytes")
                    
                # Protect SVG file from cleanup
                if os.name == 'nt':
                    import stat
                    os.chmod(svg_path, stat.S_IWRITE)
                logging.info("Protected diagram.svg from cleanup")
                
                # Convert SVG to PNG using cairosvg
                try:
                    from cairosvg import svg2png
                    
                    # Convert without resizing
                    with open(svg_path, 'rb') as svg_file:
                        svg2png(
                            file_obj=svg_file,
                            write_to='diagram.png'
                        )
                    
                    # Verify the output file exists
                    if os.path.exists('diagram.png'):
                        logging.info("Generated PNG successfully")
                        
                        # Protect PNG file from cleanup
                        png_path = os.path.join(working_dir, 'diagram.png')
                        if os.name == 'nt':
                            import stat
                            os.chmod(png_path, stat.S_IWRITE)
                        logging.info("Protected diagram.png from cleanup")
                    
                    # After successful PNG conversion, queue the update
                    try:
                        self.image_queue.put('diagram.png')
                        logging.info("Queued diagram update")
                        if hasattr(self, 'status_callback'):
                            self.status_callback("✨ Repository visualization updated and displayed")
                        return True
                        
                    except Exception as e:
                        logging.error(f"Failed to display diagram: {e}")
                        if hasattr(self, 'status_callback'):
                            self.status_callback("⚠️ Diagram created but display failed")
                        return True  # Return True since visualization was created successfully
                    
                except Exception as e:
                    logging.error(f"Failed to convert SVG to PNG: {e}")
                    if hasattr(self, 'status_callback'):
                        self.status_callback("⚠️ SVG created but PNG conversion failed")
                    # Return True since SVG was created successfully
                    return True
                    
            else:
                logging.error("SVG file not found - visualization failed")
                if hasattr(self, 'status_callback'):
                    self.status_callback("❌ Failed to generate visualization")
                return False

        except Exception as e:
            logging.error(f"Failed to generate visualization: {e}")
            if hasattr(self, 'status_callback'):
                self.status_callback("❌ Failed to generate visualization")
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

    def initialize_window(self):
        """Initialize the visualization window using existing root"""
        try:
            if not self.root:
                logging.error("No root window provided")
                return False
                
            if not self.image_window:
                from image_window import ImageWindow
                self.image_window = ImageWindow(self.root, 'diagram.png')
                logging.info("Created visualization window")
                
            # Start checking the image queue
            self.check_image_queue()
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize visualization window: {e}")
            return False

    def check_image_queue(self):
        """Check for new images to display"""
        try:
            while not self.image_queue.empty():
                image_path = self.image_queue.get_nowait()
                if self.image_window:
                    self.image_window.update_image(image_path)
        except Exception as e:
            logging.error(f"Error processing image queue: {e}")
        finally:
            # Schedule next check
            if self.root and self.running:
                self.root.after(100, self.check_image_queue)

    def stop(self):
        """Stop the visualization loop and cleanup"""
        self.running = False
        if self.current_process:
            try:
                self.current_process.terminate()
            except:
                pass
        if self.image_window:
            try:
                self.image_window.window.destroy()
            except:
                pass
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
        logging.info("Visualization stopped")

def start_visualization(root_window):
    """Start the repository visualization system"""
    try:
        # Create visualizer with root window
        visualizer = RepoVisualizer(root=root_window, interval=10)
        
        # Schedule window initialization
        root_window.after(1000, visualizer.initialize_window)
        
        # Start visualization thread
        def run_visualization():
            asyncio.run(visualizer.visualization_loop())
        
        visualization_thread = Thread(target=run_visualization, daemon=True)
        visualization_thread.start()
        
        logging.info("Visualization system started")
        return visualizer
        
    except Exception as e:
        logging.error(f"Failed to start visualization: {e}")
        return None
