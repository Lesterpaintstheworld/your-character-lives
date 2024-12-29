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
        'argparse'
    ]
    options.extend([f'--hidden-import={imp}' for imp in hidden_imports])

    # Add video files
    # Add videos directory to the executable
    options.extend([
        '--add-data', f'videos{os.pathsep}videos',  # This copies the entire videos folder
    ])
    # Add individual video files if found
    options.extend([f'--add-data={src};{dst}' for src, dst in video_files])

    # Add final options
    options.extend([
        '--clean',
        '--runtime-tmpdir=.'
    ])

    # Run PyInstaller
    PyInstaller.__main__.run(options)

if __name__ == '__main__':
    main()
