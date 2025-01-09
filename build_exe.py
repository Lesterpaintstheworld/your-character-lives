import PyInstaller.__main__
import os
import sys

def collect_video_files():
    """Collect video files with proper path handling"""
    base_path = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else sys._MEIPASS
    video_dir = os.path.join(base_path, 'videos')
    video_files = []
    
    if os.path.exists(video_dir):
        for file in os.listdir(video_dir):
            if file.endswith('.mp4'):
                src = os.path.join(video_dir, file)
                video_files.append((src, 'videos'))
                
    return video_files

def ensure_directories():
    """Ensure required directories exist"""
    directories = ['videos', 'visualizations']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def main():
    video_files = collect_video_files()
    
    options = [
        'main.py',
        '--onefile',
        '--noconsole',
        '--name', 'AI_Assistant',
        '--log-level=DEBUG',
        '--noupx',
        '--disable-windowed-traceback',
        
        # Exclude problematic packages
        '--exclude-module', 'PyQt6',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'matplotlib_inline',
        '--exclude-module', 'IPython',
        '--exclude-module', 'jupyter_client',
        '--exclude-module', 'jupyter_core',
        '--exclude-module', 'ipykernel',
        '--exclude-module', 'debugpy',
        '--exclude-module', 'tornado',
        '--exclude-module', 'jedi',
        '--exclude-module', 'parso',
        '--exclude-module', 'prompt_toolkit',
        
        # Core hidden imports
        '--hidden-import=queue',
        '--hidden-import=pyaudio',
        '--hidden-import=pygame',
        '--hidden-import=PIL',
        '--hidden-import=numpy',
        '--hidden-import=tkinter',
        '--hidden-import=asyncio',
        '--hidden-import=threading',
        '--hidden-import=logging',
        
        # Add data files
        '--add-data', f'videos{os.pathsep}videos',
        '--add-data', f'visualizations{os.pathsep}visualizations',
    ]

    # Add video files
    options.extend([f'--add-data={src};{dst}' for src, dst in video_files])

    # Run PyInstaller
    PyInstaller.__main__.run(options)

if __name__ == '__main__':
    ensure_directories()
    main()
