@echo off
echo Checking Python version...
python -c "import sys; ver = sys.version_info; exit(1 if ver.major == 3 and ver.minor > 11 else 0)" 2>nul
if %errorlevel% == 1 (
    echo Error: Python version 3.12+ detected. Please use Python 3.11 or lower.
    echo You can download Python 3.11 from: https://www.python.org/downloads/release/python-3116/
    pause
    exit /b 1
)

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
