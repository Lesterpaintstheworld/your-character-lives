# Multi-Domain AI Assistant

An intelligent assistant system featuring two complementary AI personalities - Emily (Creative Intelligence) and Daemon (Technical Implementation) - working together to provide comprehensive solutions across gaming, music production, content creation, web development, and financial analysis.

## Quick Start

### Option 1: Using the Executable (Windows)
1. Download the latest release from GitHub
2. Double-click AI_Assistant.exe to run

### Option 2: Running from Source
1. **Install Build Tools**
```bash
# Windows
pip install wheel
pip install --upgrade setuptools

# For ta-lib
# Download and install ta-lib: http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip
# Extract to C:\ta-lib
```

2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

3. **Start the AI Assistant**
```bash
python main.py
```


## Game Integration Installation (Optional)

If you want to also use the CK3 game integration features:

1. **Install CK3 Mod**
- Copy the `mod` folder contents to:
  - Windows: `Documents/Paradox Interactive/Crusader Kings III/mod/`
  - Linux: `~/.local/share/Paradox Interactive/Crusader Kings III/mod/`
- Activate the mod in the CK3 launcher

2. **Start with Game Integration**
```bash
python main.py --with-game
```

## System Requirements

- Python 3.10 or higher
- Active internet connection
- Working microphone and speakers/headphones
- Minimum 4GB RAM
- 500MB free disk space
- Graphics card supporting OpenCV

## Configuration Options

```bash
python main.py --help
```

Available options:
- `--domain`: Set primary domain focus
- `--interval`: Response interval in seconds (default: 30)
- `--mode`: Set interaction mode (voice/text/both)

## Project Structure

```
ai-assistant/
├── main.py              # Main application entry
├── requirements.txt     # Python dependencies
├── config/             # Configuration files
│   ├── domains/        # Domain-specific settings
│   └── profiles/       # AI personality profiles
├── modules/            # Domain-specific modules
├── resources/          # Media and assets
│   ├── avatars/        # Visual avatar files
│   └── audio/         # Audio resources
└── documentation/      # Detailed documentation
```

## Troubleshooting

1. **Voice Interaction Issues**
- Verify microphone settings
- Check audio device selection
- Test both AI personalities separately

2. **Visual Avatar Issues**
- Verify graphics drivers
- Check OpenCV installation
- Ensure avatar files are present

3. **Domain Processing Issues**
- Verify domain module installation
- Check API connectivity
- Ensure sufficient system resources

4. **Performance Issues**
- Close unnecessary applications
- Check system requirements
- Monitor resource usage

## Features

- Dual AI Personality System
  - Emily: Creative strategy and pattern recognition
  - Daemon: Technical analysis and implementation

- Multi-Domain Expertise
  - Gaming & Interactive Experiences
  - Music & Audio Production
  - Content Creation & Writing
  - Web Development
  - Financial Analysis

- Real-Time Interaction
  - Voice recognition and synthesis
  - Visual avatar system
  - Context-aware responses
  - Multi-modal input processing

- Technical Capabilities
  - Sequential processing pipeline
  - Cross-domain context integration
  - Real-time data analysis
  - Secure cloud synchronization

## Character Interaction

The system alternates between two AI characters:
1. **Emily**: First character to respond
2. **Daemon**: Responds 30 seconds after Emily

Each character:
- Has their own distinct video avatar
- Processes game context independently
- Provides unique perspectives and responses
- Features individual interaction styles

## Character Interaction

The system alternates between two AI characters:
1. **Emily**: First character to respond
2. **Daemon**: Responds 30 seconds after Emily

Each character:
- Has their own distinct video avatar
- Processes game context independently
- Provides unique perspectives and responses
- Features individual interaction styles

## Support

For help:
- Open an issue on GitHub
- Check detailed documentation in `documentation/`
- Join our Discord (coming soon)

## License

This project is licensed under the MIT License. See `LICENSE` file for details.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## Updates

Check the GitHub repository regularly for updates and security patches.
