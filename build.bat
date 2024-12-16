@echo off
echo Installing build requirements...
pip install wheel
pip install --upgrade setuptools
pip install pyinstaller

echo Installing project dependencies...
pip install -r requirements.txt

echo Building executable...
python build_exe.py

echo Build complete! Executable is in the dist folder.
pause
