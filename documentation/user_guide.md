# Multi-Domain AI Assistant User Guide

## Quick Start

### Installation Options

#### Option 1: Windows Executable
1. Download the latest release from GitHub
2. Double-click AI_Assistant.exe to run

#### Option 2: Running from Source
1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start the AI Assistant:
```bash
python main.py
```

## Basic Usage

### Main Interface
- Click ▶️ to start interaction
- Use 🔄 Auto button for continuous recording
- Adjust recording interval (5-3600 seconds)
- Monitor input levels with VU meter

### Audio Setup
- Select input device (microphone)
- Select output device (speakers/headphones)
- Use refresh button to update device lists
- Test audio devices before starting

### Smart Recording Mode
Smart mode provides a more natural conversation experience by automatically detecting when you've finished speaking and managing the turn-taking between Emily and Daemon.

#### How it works
- Click the "Smart Mode" button to activate
- Speak naturally - the system will listen continuously
- When you pause for 3+ seconds, the system will automatically respond
- Emily and Daemon will take turns responding
- You can interrupt their responses by speaking
- Screenshots are automatically taken every 20 seconds

#### Controls
- Play/Pause: Start or stop the smart conversation mode
- Mode Switch: Toggle between Manual/Auto/Smart modes
- Status Indicator: Shows current state (recording/processing/playing)
- Level Meter: Shows your audio input level

#### Tips
- Speak at a normal volume and pace
- Natural pauses under 3 seconds won't trigger a response
- You can interrupt responses at any time by speaking
- Use Play/Pause to control the conversation flow

### Video Avatars
- Drag avatars to reposition
- Right-click and drag to resize
- Middle-click to adjust transparency
- Double-click to close avatar window

## Troubleshooting

### Audio Issues
- Verify microphone is connected and enabled
- Check Windows/system audio settings
- Try refreshing audio devices
- Restart application if devices not detected

### Video Issues
- Ensure graphics drivers are up to date
- Check if OpenCV is properly installed
- Verify video files exist in correct location
- Try restarting application

### Performance Issues
- Close unnecessary applications
- Check system requirements
- Monitor resource usage
- Reduce recording interval if needed

## Support
- Open an issue on GitHub
- Check detailed documentation
- Join our Discord community

## System Requirements
- Python 3.10 or higher
- Working microphone and speakers
- 4GB RAM minimum
- 500MB free disk space
- Graphics card supporting OpenCV
