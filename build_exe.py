import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--noconsole',
    '--name', 'CK3_AI_Assistant',
    '--add-data', 'prompts/*;prompts',
    '--add-data', 'documentation/*;documentation',
    '--add-data', '.env;.',  # Add .env file
    '--log-level=DEBUG',
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
    '--hidden-import=asyncio',
    '--hidden-import=io',
    '--hidden-import=threading',
    '--hidden-import=logging',
    '--hidden-import=argparse',
    '--icon', 'icon.ico'  # Optional: add icon if you have one
])
