@echo off
setlocal enabledelayedexpansion

echo Adding temporary antivirus exclusions...
powershell -Command "Add-MpPreference -ExclusionPath '%CD%\dist'" 2>nul
powershell -Command "Add-MpPreference -ExclusionPath '%CD%\build'" 2>nul

echo Cleaning build directories...
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"
if exist "*.spec" del /f /q *.spec

echo Cleaning up previous installations...
python -m pip uninstall -y wheel setuptools pyinstaller pkg_resources

echo Installing build requirements...
python -m pip install --user --upgrade pip
python -m pip install --user --upgrade setuptools>=69.0.3
python -m pip install --user --upgrade wheel>=0.42.0
python -m pip install --user --upgrade pyinstaller>=6.3.0

echo Installing project dependencies...
python -m pip install --user -r requirements.txt

echo Building executable...
python build_exe.py

echo Build complete! Executable is in the dist folder.

echo Removing temporary antivirus exclusions...
powershell -Command "Remove-MpPreference -ExclusionPath '%CD%\dist'" 2>nul
powershell -Command "Remove-MpPreference -ExclusionPath '%CD%\build'" 2>nul

echo.
echo If the build failed due to antivirus, try these steps:
echo 1. Temporarily disable your antivirus
echo 2. Run this script again
echo 3. Re-enable your antivirus after building
echo.

pause
