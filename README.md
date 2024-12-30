# Multi-Domain AI Assistant

An intelligent assistant system featuring two complementary AI personalities - Emily (Creative Intelligence) and Daemon (Technical Implementation) - working together to provide comprehensive solutions across gaming, music production, content creation, web development, and financial analysis.

## Quick Start

### Important Note About Working Directory
The AI Assistant needs to be run from the folder containing your relevant text documents. For example:

```bash
# Navigate to your documents folder
cd C:\Users\YourUser\KinOS_missions\synthetic-souls

# Run the AI Assistant from there
python "C:\Users\YourUser\your-character-lives\main.py"
```

This ensures the assistant can access and process all relevant text files in your working directory.

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



## System Requirements

- Python 3.10 or higher
- Active internet connection
- Working microphone and speakers/headphones
- Minimum 4GB RAM
- 500MB free disk space
- Graphics card supporting OpenCV

## REST API

The AI Assistant exposes a REST API for external integration. All endpoints require authentication using a Bearer token.

### Authentication

Include the API token in the Authorization header:
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" http://localhost:5000/api/memory
```

### Endpoints

#### Memory Management
- GET /api/memory - List all memories
- GET /api/memory/<id> - Get specific memory
- POST /api/memory - Create new memory
- DELETE /api/memory/<id> - Delete memory

#### Performance Metrics
- GET /api/performance - Get current performance metrics

#### Configuration
- GET /api/config - Get current configuration
- PUT /api/config - Update configuration

### Example Usage

List all memories:
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" http://localhost:5000/api/memory
```

Create new memory:
```bash
curl -X POST -H "Authorization: Bearer YOUR_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"id":"123","content":"Test memory","timestamp":"2024-12-30T12:00:00Z","type":"conversation"}' \
     http://localhost:5000/api/memory
```

Get performance metrics:
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" http://localhost:5000/api/performance
```

## Audio Device Management

- Automatic detection of input/output devices
- Real-time VU meter for audio monitoring
- Support for device hot-swapping
- Configurable audio settings:
  - Sample rate (16kHz-48kHz)
  - Buffer size
  - Channels (mono/stereo)

## Video Avatar System

- Borderless draggable video windows
- Smooth transitions between idle/talking states
- Independent control of multiple avatars
- Configurable window transparency
- Resizable with maintained aspect ratio

## Performance Optimization

- Efficient frame buffering
- Automatic resource cleanup
- Memory usage optimization
- Thread-safe operations
- Configurable quality settings

## Error Recovery

- Automatic device reconnection
- Graceful failure handling
- Detailed error logging
- Fallback mechanisms for:
  - Audio devices
  - Video playback
  - Network connectivity

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
ck3-ai-assistant/
├── main.py              # Main application entry
├── audio_manager.py     # Audio recording/playback
├── device_manager.py    # Hardware device management  
├── video_window.py      # Video avatar system
├── thread_manager.py    # Thread management
├── log_manager.py       # Logging utilities
├── constants.py         # Global constants
├── build_exe.py        # Executable builder
├── requirements.txt     # Dependencies
├── videos/             # Video assets
└── documentation/      # Documentation
    ├── api_reference.md     # API documentation
    ├── development.md       # Developer guide
    ├── technical_specs.md   # Technical details
    ├── user_guide.md        # User manual
    └── specifications.md    # Project specs
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


## Documentation

Our comprehensive documentation is available in the `docs` directory:

- [Installation Guide](docs/installation.md) - Get started with setup
- [Usage Guide](docs/usage.md) - Learn how to use the assistant
- [API Reference](docs/api_reference.md) - Detailed API documentation
- [Configuration Guide](docs/configuration.md) - Configure the assistant
- [Plugin Development](docs/plugins.md) - Create custom plugins
- [Contributing Guidelines](docs/contributing.md) - Help improve the project
- [Changelog](docs/changelog.md) - Track project changes

To generate the documentation website locally:
```bash
python generate_docs.py
```

## Support

For help:
- Open an issue on GitHub
- Check the documentation linked above
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
