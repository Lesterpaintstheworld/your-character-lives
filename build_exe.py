import PyInstaller.__main__
import os

# Create a list of video files to include
video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
video_files = []
if os.path.exists(video_dir):
    for file in os.listdir(video_dir):
        if file.endswith('.mp4'):
            video_files.append((os.path.join(video_dir, file), 'videos'))

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--noconsole',
    '--name', 'CK3_AI_Assistant',
    '--log-level=DEBUG',
    '--exclude-module', 'PyQt6',
    '--exclude-module', 'matplotlib_inline',
    '--exclude-module', 'IPython',
    '--exclude-module', 'jupyter',
    '--exclude-module', 'nbconvert',
    '--exclude-module', 'nbformat',
    '--exclude-module', 'notebook',
    '--hidden-import=queue',
    '--hidden-import=pyaudio',
    '--hidden-import=pygame',
    '--hidden-import=PIL',
    '--hidden-import=requests',
    '--hidden-import=wave',
    '--hidden-import=numpy',
    '--hidden-import=tkinter',
    '--hidden-import=asyncio',
    '--hidden-import=io',
    '--hidden-import=threading',
    '--hidden-import=logging',
    '--hidden-import=argparse',
    # Add video files to the executable
    *[f'--add-data={src};{dst}' for src, dst in video_files],
    '--clean'
])
