import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--noconsole',
    '--name', 'CK3_AI_Assistant',
    '--log-level=DEBUG',
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
    '--icon', 'icon.ico'  # Optional: add icon if you have one
])
