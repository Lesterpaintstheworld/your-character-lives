@echo off
echo Installing build requirements...
pip install wheel
pip install --upgrade setuptools
pip install pyinstaller

echo Setting up ta-lib...
if not exist "ta-lib-0.4.0-msvc.zip" (
    echo Downloading ta-lib...
    powershell -Command "Invoke-WebRequest -Uri 'http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip' -OutFile 'ta-lib-0.4.0-msvc.zip'"
)

if not exist "C:\ta-lib" (
    echo Extracting ta-lib...
    powershell -Command "Expand-Archive -Path 'ta-lib-0.4.0-msvc.zip' -DestinationPath 'C:\'"
)

echo Installing project dependencies...
pip install -r requirements.txt

echo Building executable...
python build_exe.py
echo Build complete! Executable is in the dist folder.
pause
