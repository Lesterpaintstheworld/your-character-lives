# AI Assistant User Guide

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
- Monitor input levels with VU meter
- Current speaker indicator shows who is speaking (Emily/Daemon)

### Audio Setup
- Select input device (microphone)
- Select output device (speakers/headphones)
- Use refresh button to update device lists
- Test audio devices before starting

### Smart Conversation Mode
The AI Assistant uses smart conversation mode for natural interaction:

- System automatically detects when you've finished speaking
- Emily and Daemon take turns responding
- You can interrupt their responses by speaking
- Screenshots are automatically taken every 20 seconds

#### Controls
- Play/Pause: Start or stop the conversation
- Status Indicator: Shows current state (recording/processing/playing)
- Level Meter: Shows your audio input level

#### Tips
- Speak at a normal volume and pace
- Natural pauses under 3 seconds won't trigger a response
- You can interrupt responses at any time by speaking

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
