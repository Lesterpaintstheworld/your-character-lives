@echo off
echo Installing build requirements...
python -m pip install --user --upgrade pip
python -m pip install --user wheel==0.42.0
python -m pip install --user setuptools==69.0.2
python -m pip install --user pyinstaller==6.3.0

echo Installing project dependencies...
python -m pip install --user -r requirements.txt

echo Building executable...
python build_exe.py

echo Build complete! Executable is in the dist folder.
pause
