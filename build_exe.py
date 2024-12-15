import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--noconsole',  # Changed from --windowed to --noconsole for Windows
    '--name', 'CK3_AI_Assistant',  # Separated name parameter
    '--add-data', 'prompts/*;prompts',
    '--add-data', 'documentation/*;documentation',
    '--icon=assets/icon.ico',
    '--hidden-import=queue',
    '--hidden-import=pyttsx3.drivers',
    '--hidden-import=pyttsx3.drivers.sapi5',
    '--hidden-import=pyaudio',
    '--hidden-import=pygame',
    '--hidden-import=PIL',
    '--hidden-import=requests',
    '--hidden-import=python-dotenv',
    '--hidden-import=wave',
    '--hidden-import=numpy',
    '--hidden-import=tkinter',
])
