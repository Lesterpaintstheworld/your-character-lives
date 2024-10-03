# CK3 AI Character Project Todolist

## Completed Tasks
- [x] Update project specifications to use OpenAI Real-Time Voice API instead of n8n REST
- [x] Implement WebSocket communication in main script
- [x] Implement real-time audio processing and playback
- [x] Update project structure to use environment variables for API keys and URLs
- [x] Implement proper Real-Time API integration
- [x] Implement error handling and reconnection logic for WebSocket connection
- [x] Add support for handling interruptions in audio responses

## Pending Tasks
- [ ] Update WebSocket URL and headers to match new Real-Time API specifications
- [ ] Implement complete server event handling, especially for audio processing
- [ ] Optimize screenshot capture and processing for better performance
- [ ] Implement audio buffering for smoother playback
- [ ] Add support for customizing AI character voice using OpenAI API options
- [ ] Implement function calling feature (tool calls) as described in the Real-Time API documentation
- [ ] Improve conversation history management for long-running sessions
- [ ] Implement automatic truncation of long conversations
- [ ] Add moderation checks on model output for safer usage
- [ ] Create a user-friendly interface for configuring the AI character
- [ ] Implement logging and telemetry for debugging and performance monitoring
- [ ] Write comprehensive documentation for setup and usage
- [ ] Create unit tests for core functionalities
- [ ] Optimize code for better resource usage and responsiveness
- [ ] Implement full support for both text and audio modalities in input and output
- [ ] Improve handling of interruptions during audio responses
- [ ] Implement turn detection configuration for more natural conversation flow
- [ ] Add support for G.711 audio format (8kHz, u-law and a-law)
- [ ] Implement robust error handling for all possible server events
- [ ] Add support for continuing conversations across sessions
- [ ] Create a system for managing and updating session-wide instructions
- [ ] Update system and character prompts to better match new capabilities

## Future Enhancements
- [ ] Explore deeper integration with Crusader Kings 3 game mechanics
- [ ] Implement multi-language support for international users
- [ ] Develop a plugin system for extending AI character capabilities
- [ ] Create a web-based dashboard for managing AI characters and viewing analytics
- [ ] Implement a caching system for frequently accessed game state data
- [ ] Optimize the SavefileManager for handling larger save files
- [ ] Add support for parallel processing of game state changes
- [ ] Implement a more robust error handling and logging system for SavefileManager
- [ ] Create a configuration file for easily adjusting SavefileManager parameters
- [ ] Develop unit tests for SavefileManager functions
- [ ] Implement a feature to automatically backup save files before modifications
- [ ] Add support for compressing large save files to save storage space

Remember to update this list as tasks are completed or new requirements arise.
