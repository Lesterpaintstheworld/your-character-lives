import PyInstaller.__main__
import os
import sys

def collect_video_files():
    video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
    video_files = []
    if os.path.exists(video_dir):
        for file in os.listdir(video_dir):
            if file.endswith('.mp4'):
                video_files.append((os.path.join(video_dir, file), 'videos'))
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
        '--exclude-module', 'PyQt6',
        '--exclude-module', 'matplotlib_inline',
        '--exclude-module', 'IPython',
        '--exclude-module', 'jupyter',
        '--exclude-module', 'nbconvert', 
        '--exclude-module', 'nbformat',
        '--exclude-module', 'notebook',
    ]

    # Add hidden imports
    hidden_imports = [
        'queue', 'pyaudio', 'pygame', 'PIL', 'requests', 'wave',
        'numpy', 'tkinter', 'asyncio', 'io', 'threading', 
        'logging', 'argparse'
    ]
    options.extend([f'--hidden-import={imp}' for imp in hidden_imports])

    # Add video files
    options.extend([f'--add-data={src};{dst}' for src, dst in video_files])

    # Add final options
    options.extend([
        '--clean',
        '--runtime-tmpdir=.',
        '--key=random_key_123'  # Add encryption key to help avoid detection
    ])

    # Run PyInstaller
    PyInstaller.__main__.run(options)

if __name__ == '__main__':
    main()
