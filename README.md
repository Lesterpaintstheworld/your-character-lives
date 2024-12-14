# CK3 AI Character

An AI assistant that enhances Crusader Kings III gameplay through intelligent character interactions and dynamic responses.

## Quick Start

### Option 1: Using the Executable (Windows)
1. Download the latest release from GitHub
2. Double-click CK3_AI_Assistant.exe to run

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
- For game features: Crusader Kings III

## Configuration Options

```bash
python main.py --help
```

Available options:
- `--interval`: Screenshot interval in seconds (default: 30)
- `--with-game`: Enable CK3 game integration

## Project Structure

```
ck3-ai-character/
├── main.py              # Main script
├── requirements.txt     # Python dependencies
├── prompts/            # System and character prompts
│   ├── system.md       # System instructions
│   └── character.md    # Character definitions
└── documentation/      # Detailed documentation
```

## Troubleshooting

1. **Connection Issues**
- Verify your OpenAI API key
- Check your internet connection
- Ensure Solana wallet is properly configured


3. **Game Integration Issues**
- Verify mod installation
- Check CK3 launcher mod activation
- Ensure correct file permissions

## Security Considerations

- Store API keys securely
- Use hardware wallet when possible
- Enable 2FA on all accounts
- Regularly monitor transactions
- Keep software updated

## Risk Warning

Cryptocurrency investments carry significant risks. Only invest what you can afford to lose. This software is provided as-is with no guarantees of returns or security.

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
