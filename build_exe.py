import PyInstaller.__main__
import os
import sys

def collect_video_files():
    """Collect video files with proper path handling for both source and frozen contexts"""
    if getattr(sys, 'frozen', False):
        # Running from executable
        base_path = sys._MEIPASS
    else:
        # Running from source
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    video_dir = os.path.join(base_path, 'videos')
    video_files = []
    
    if os.path.exists(video_dir):
        for file in os.listdir(video_dir):
            if file.endswith('.mp4'):
                # Use proper path joining for both source and frozen contexts
                src = os.path.join(video_dir, file)
                video_files.append((src, 'videos'))
                
    return video_files

def ensure_directories():
    """Ensure required directories exist"""
    directories = ['videos', 'visualizations']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def main():
    video_files = collect_video_files()
    
    # Base options
    options = [
        'main.py',
        '--onefile',
        '--noconsole',
        '--name', 'AI_Assistant',
        '--log-level=DEBUG',
        '--noupx',  # Avoid UPX compression which triggers some antiviruses
        '--disable-windowed-traceback',
        
        # Exclude problematic/unnecessary packages
        '--exclude-module', 'PyQt6',
        '--exclude-module', 'matplotlib_inline',
        '--exclude-module', 'IPython',
        '--exclude-module', 'jupyter',
        '--exclude-module', 'nbconvert', 
        '--exclude-module', 'nbformat',
        '--exclude-module', 'notebook',
        '--exclude-module', 'torch',
        '--exclude-module', 'torchaudio',
        '--exclude-module', 'timm',
        '--exclude-module', 'nltk',
    ]

    # Add hidden imports for core functionality only
    hidden_imports = [
        'queue', 
        'pyaudio', 
        'pygame', 
        'PIL', 
        'requests', 
        'wave',
        'numpy', 
        'tkinter', 
        'asyncio', 
        'io', 
        'threading', 
        'logging', 
        'argparse',
        'matplotlib',
        'seaborn',
        'pandas',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_svg',
        'cairosvg'
    ]
    options.extend([f'--hidden-import={imp}' for imp in hidden_imports])

    # Add video files
    options.extend([
        '--add-data', f'videos{os.pathsep}videos',  # This copies the entire videos folder
    ])
    options.extend([f'--add-data={src};{dst}' for src, dst in video_files])

    # Add visualization output directory
    options.extend([
        '--add-data', f'visualizations{os.pathsep}visualizations',
    ])

    # Add matplotlib data files
    import matplotlib
    matplotlib_data = os.path.join(matplotlib.__path__[0], 'mpl-data')
    options.extend([
        '--add-data', f'{matplotlib_data}{os.pathsep}mpl-data'
    ])

    # Add final options
    options.extend([
        '--clean',
        '--runtime-tmpdir=.'
    ])

    # Run PyInstaller
    PyInstaller.__main__.run(options)

if __name__ == '__main__':
    ensure_directories()
    main()
