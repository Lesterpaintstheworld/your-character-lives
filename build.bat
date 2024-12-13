@echo off
pip install -r requirements.txt
python build_exe.py
echo Build complete! Executable is in the dist folder.
pause
