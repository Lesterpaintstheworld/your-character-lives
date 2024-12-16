@echo off
echo Installing build requirements...
pip install --user wheel==0.40.0
pip install --user setuptools==65.5.1
pip install --user pyinstaller==6.3.0

echo Installing project dependencies...
pip install --user -r requirements.txt

echo Building executable...
python build_exe.py

echo Build complete! Executable is in the dist folder.
pause
