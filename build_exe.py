import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=CK3_AI_Assistant',
    '--add-data=prompts/*;prompts',
    '--icon=assets/icon.ico',  # You'll need to create/add an icon file
    '--hidden-import=queue',
    '--hidden-import=pyttsx3.drivers',
    '--hidden-import=pyttsx3.drivers.sapi5',
])
