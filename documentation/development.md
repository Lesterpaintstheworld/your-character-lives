# CK3 AI Assistant Development Guide

## Development Environment

### Prerequisites
1. Python 3.10 or higher
2. Git for version control
3. Visual Studio Code (recommended)
4. Required build tools:
   - Windows: Visual C++ build tools
   - Linux: gcc and required headers

### Setup
1. Clone repository:
```bash
git clone https://github.com/yourusername/ck3-ai-assistant.git
cd ck3-ai-assistant
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

### Core Modules
- `audio_manager.py`: Audio device and recording management
- `video_window.py`: Video playback and window management
- `device_manager.py`: Hardware device detection/configuration
- `log_manager.py`: Logging and diagnostics
- `thread_manager.py`: Thread and process management

### Support Files
- `constants.py`: Global constants and configuration
- `main.py`: Application entry point
- `build_exe.py`: Executable build script
- `requirements.txt`: Python dependencies

## Development Workflow

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Document all public functions/methods
- Keep functions focused and concise

### Testing
1. Run unit tests:
```bash
python -m unittest discover tests
```

2. Test executable build:
```bash
python build_exe.py
```

### Debugging
- Use logging for diagnostics
- Check log files in user directory
- Enable debug mode with --debug flag
- Use VS Code debugger for step-through

## Contributing

### Pull Requests
1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

### Code Review
- All changes require review
- Address review comments
- Ensure tests pass
- Update documentation

## Building

### Windows Executable
1. Install build requirements:
```bash
pip install --upgrade wheel setuptools pyinstaller
```

2. Run build script:
```bash
python build_exe.py
```

### Troubleshooting
- Check build logs
- Verify dependencies
- Test in clean environment
- Use --clean flag for fresh build
