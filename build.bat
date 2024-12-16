@echo off
echo Installing build requirements...
pip install wheel==0.40.0
pip install setuptools==65.5.1
pip install pyinstaller==6.3.0

echo Installing project dependencies...
pip install -r requirements.txt

echo Building executable...
python build_exe.py

echo Build complete! Executable is in the dist folder.
pause
