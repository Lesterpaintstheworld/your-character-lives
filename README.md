# CK3 AI Character with $UBC Integration

A dual-purpose AI assistant that combines Crusader Kings III game interaction with autonomous cryptocurrency portfolio management using $UBC (Universal Basic Compute).

## Quick Start (Investment Features)

### Option 1: Using the Executable (Windows)
1. Download the latest release from GitHub
2. Create a `.env` file in the same folder as the executable with:
```env
OPENAI_API_KEY=your_openai_api_key
SOLANA_WALLET_KEY=your_solana_wallet_key
```
3. Double-click CK3_AI_Assistant.exe to run

### Option 2: Running from Source
1. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment**
Create a `.env` file with:
```env
OPENAI_API_KEY=your_openai_api_key
SOLANA_WALLET_KEY=your_solana_wallet_key
```

3. **Start the AI Assistant**
```bash
python main.py
```

## Investment Features

- Autonomous portfolio management with $UBC
- Real-time market analysis
- Risk management and stop-loss automation
- Investment recommendations
- Performance tracking and reporting
- Integration with Solana blockchain
- Multi-token portfolio diversification

## Security Features

- Secure API key and wallet storage
- Configurable trading limits
- Multi-level stop-loss system
- Malicious smart contract protection
- Detailed transaction logging
- Continuous $UBC performance monitoring

## Game Integration Installation (Optional)

If you want to also use the CK3 game integration features:

1. **Install CK3 Mod**
- Copy the `mod` folder contents to:
  - Windows: `Documents/Paradox Interactive/Crusader Kings III/mod/`
  - Linux: `~/.local/share/Paradox Interactive/Crusader Kings III/mod/`
- Activate the mod in the CK3 launcher

2. **Configure Additional Settings**
Add to your `.env` file:
```env
XATA_API_KEY=your_xata_api_key
XATA_DATABASE_URL=your_xata_database_url
```

3. **Start with Game Integration**
```bash
python main.py --with-game
```

## System Requirements

- Python 3.10 or higher
- Active internet connection
- Solana wallet
- OpenAI API access
- For game features: Crusader Kings III

## Configuration Options

```bash
python main.py --help
```

Available options:
- `--interval`: Screenshot interval in seconds (default: 30)
- `--with-game`: Enable CK3 game integration
- `--risk-level`: Set investment risk level (1-5)
- `--max-allocation`: Maximum allocation per token (%)

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

2. **Trading Issues**
- Verify sufficient $UBC balance
- Check trading limits configuration
- Ensure stop-loss settings are proper

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
