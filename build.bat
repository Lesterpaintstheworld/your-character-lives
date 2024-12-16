@echo off
echo Installing build requirements...
python -m pip install --user wheel==0.37.1
python -m pip install --user setuptools==57.5.0
python -m pip install --user pyinstaller==5.13.2

echo Installing project dependencies...
python -m pip install --user -r requirements.txt

echo Building executable...
python build_exe.py

echo Build complete! Executable is in the dist folder.
pause
