# AI Assistant Technical Specifications

## Core Components

### Audio System
- Sample Rate: 24kHz
- Format: 16-bit PCM
- Channels: Mono
- Buffer Size: 1024 samples
- Device hot-plugging support
- Real-time VU meter monitoring

### Smart Conversation Mode
- Continuous audio monitoring
  - Real-time audio level analysis
  - Silence detection threshold: -60dB
  - Minimum silence duration: 3 seconds
  - Buffer management for continuous recording

- Turn Management
  - Voice activity detection (VAD)
  - Silence-based turn completion
  - Interrupt handling during playback
  - Turn alternation between Emily and Daemon

- Performance Requirements
  - Maximum latency: 100ms
  - Memory usage: < 100MB for audio buffer
  - CPU usage: < 10% during monitoring

- Configuration Parameters
  - SILENCE_THRESHOLD: -60dB
  - MIN_SILENCE_DURATION: 3 seconds
  - SCREENSHOT_INTERVAL: 20 seconds
  - BUFFER_SIZE: 1024
  - MAX_RECORDING_SIZE: 500MB

### Video System
- Format: MP4 (H.264)
- Resolution: 320x240 minimum
- FPS: 30
- Alpha channel support
- Hardware acceleration when available
- Borderless window support
- Smooth video transitions
- Multiple avatar support

### Network Communication
- REST API integration
- Request/response handling
- Error recovery
- Data validation
- Timeout: 120 seconds
- Retry mechanism: 3 attempts

## Performance Requirements
- CPU: < 15% average usage
- Memory: < 750MB working set
- Disk: < 2GB total space
- Network: < 2MB/s bandwidth
- Frame rate: 30 FPS minimum
- Audio latency: < 100ms
- Response time: < 2s average

## Security Considerations
- No persistent storage of audio
- Temporary files cleaned up
- Network encryption (HTTPS)
- API key protection

## Error Handling
- Graceful degradation
- Automatic recovery
- Detailed logging
- User notifications

2. Video System
   - Borderless window management
   - Real-time video playback
   - Smooth transitions
   - Resource optimization

3. Network Communication
   - REST API integration
   - Request/response handling
   - Error recovery
   - Data validation

4. User Interface
   - Tkinter-based controls
   - Event handling
   - Status updates
   - Configuration management

5. Browser Automation
   - Selenium/Playwright integration
   - DOM manipulation
   - JavaScript execution
   - Network monitoring
   - State management
   - Screenshot capture

### Browser System
- Engine: Selenium/Playwright
- Supported browsers: Chrome, Firefox, Edge
- Headless mode support
- Proxy configuration
- Custom user agent support
- JavaScript injection
- Network request interception
- Cookie management
- Screenshot capabilities
- PDF generation

### Data Flow
1. Input Processing
   - Audio capture
   - Device management
   - Format conversion
   - Buffer management

2. Network Operations
   - API requests
   - Response handling
   - Error recovery
   - Data validation

3. Output Generation
   - Audio playback
   - Video transitions
   - UI updates
   - Status logging

## Technical Requirements

### Audio System
- Sample Rate: 24kHz
- Format: 16-bit PCM
- Channels: Mono
- Buffer Size: 1024 samples
- Device hot-plugging support
- Automatic device detection and testing
- Real-time VU meter monitoring
- Multiple device selection support
- Fallback device handling
- Audio format conversion

### Smart Recording Mode
- Continuous audio monitoring
  - Real-time audio level analysis
  - Configurable silence detection threshold (default: -60dB)
  - Minimum silence duration: 3 seconds
  - Buffer management for continuous recording

- Automatic Turn Detection
  - Voice activity detection (VAD)
  - Silence-based turn completion
  - Interrupt handling during playback
  - Turn alternation between Emily and Daemon

- Performance Requirements
  - Maximum latency: 100ms
  - Memory usage: < 100MB for audio buffer
  - CPU usage: < 10% during monitoring
  - Disk I/O: Minimal (in-memory processing)

- Configuration Parameters
  - SILENCE_THRESHOLD: -60dB
  - MIN_SILENCE_DURATION: 3 seconds
  - SCREENSHOT_INTERVAL: 20 seconds
  - BUFFER_SIZE: 1024 samples
  - MAX_RECORDING_SIZE: 500MB

- State Management
  - RECORDING: Continuous audio capture
  - PROCESSING: Sending request to API
  - PLAYING: Response playback
  - INTERRUPTED: Playback stopped by user
  - PAUSED: System paused

- UI Elements
  - Play/Pause toggle button
  - Current speaker indicator (Emily/Daemon)
  - Audio level visualization
  - Recording status indicator
  - Mode selector (Manual/Auto/Smart)

### Video System
- Format: MP4 (H.264)
- Resolution: 320x240 minimum
- FPS: 30
- Alpha channel support
- Hardware acceleration when available
- Borderless window support
- Draggable/resizable windows
- Transparency control
- Smooth video transitions
- Multiple avatar support
- Resource cleanup on exit

### Network
- REST API endpoints
- Timeout: 120 seconds
- Retry mechanism: 3 attempts
- Request interval: 5-3600 seconds

### Context Distribution System
- Unified content collection
  - Project directory scanning
  - File content extraction
  - Screenshot capture
  - Audio recording
  - Web page content

- Content Filtering
  - Intelligent file type detection
  - Directory exclusion patterns
  - Binary file filtering
  - Encoding detection and handling

- Agent Communication
  - Synchronized context delivery
  - Multi-format data packaging
  - Real-time updates
  - Session management
  - Context versioning

- Performance Optimization
  - Efficient content caching
  - Incremental updates
  - Resource sharing
  - Memory management

### Performance
- CPU: < 15% average usage
- Memory: < 750MB working set
- Disk: < 2GB total space
- Network: < 2MB/s bandwidth
- Frame rate: 30 FPS minimum
- Audio latency: < 100ms
- Response time: < 2s average

### Phantom Wallet Integration

#### Connection Management
- Automatic wallet detection
- Connection state tracking
- Multiple network support
- Connection recovery
- Session management

#### Transaction Support
- Transaction Types:
  - Native SOL transfers
  - SPL token transfers
  - Program interactions
  - Memo support
- Transaction Formatting:
  - Automatic fee calculation
  - Blockhash management
  - Signature verification
  - Transaction confirmation tracking

#### Security Features
- Popup Management:
  - Connection approval handling
  - Transaction approval handling
  - Timeout management
  - Retry mechanisms
- Network Validation:
  - RPC endpoint verification
  - Network status monitoring
  - Version compatibility checks
  - Connection security validation

#### Performance
- Connection Timeout: 30 seconds
- Transaction Timeout: 30 seconds
- Max Retries: 3
- Network Polling Interval: 5 seconds
- Maximum Concurrent Transactions: 1

#### Error Handling
- Connection Failures
- Transaction Rejections
- Network Issues
- Insufficient Funds
- Invalid Instructions
- Timeout Recovery

## Security Considerations

### Data Protection
- No persistent storage of audio
- Temporary files cleaned up
- Network encryption (HTTPS)
- API key protection

### Error Handling
- Graceful degradation
- Automatic recovery
- Detailed logging
- User notifications

## Development Guidelines

### Code Structure
- Modular design
- Clear separation of concerns
- Consistent error handling
- Comprehensive logging

### Testing
- Unit tests for core components
- Integration testing
- Performance profiling
- Error scenario validation

### Documentation
- Inline code documentation
- API documentation
- User guides
- Technical specifications
