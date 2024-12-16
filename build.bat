@echo off
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
pause
