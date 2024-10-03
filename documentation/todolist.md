# CK3 AI Mod: Detailed Phase 1 (MVP) To-Do List

## 1. Set Up Development Environment
- [x] Install necessary development tools
  - [x] Choose and install an IDE (e.g., Visual Studio Code)
  - [x] Install Git for version control
  - [x] Set up a Python environment (for n8n scripting)
- [ ] Set up a local CK3 modding environment
  - [ ] Install CK3 modding tools
  - [ ] Set up a test environment for the mod
- [ ] Create a GitHub repository for the project
  - [ ] Initialize the repository with a README
  - [ ] Set up .gitignore file for CK3 modding
  - [ ] Create initial project structure in the repository

## 2. Basic CK3 Mod Structure
- [ ] Create the mod folder structure
  - [ ] Set up main mod folder
  - [ ] Create subfolders for events, interface, localization
- [ ] Write the descriptor.mod file
  - [ ] Define mod name, supported game version, and tags
  - [ ] List required DLCs (if any)
- [ ] Set up basic localization files
  - [ ] Create English localization file
  - [ ] Add placeholder strings for mod UI elements

## 3. OpenAI Real-Time Voice API Integration
- [x] Set up API access to OpenAI Real-Time Voice API
  - [x] Obtain API credentials
  - [x] Test API connection
- [x] Implement WebSocket communication in main script
- [x] Implement real-time audio processing and playback
- [ ] Update WebSocket URL and headers to match new Real-Time API specifications
- [ ] Implement complete server event handling, especially for audio processing
- [ ] Implement function calling feature (tool calls) as described in the Real-Time API documentation
- [ ] Add support for customizing AI character voice using OpenAI API options
- [ ] Implement turn detection configuration for more natural conversation flow
- [ ] Add support for G.711 audio format (8kHz, u-law and a-law)

## 4. Error Handling and Logging
- [x] Implement error handling and reconnection logic for WebSocket connection
- [ ] Implement robust error handling for all possible server events
- [ ] Implement logging and telemetry for debugging and performance monitoring
- [ ] Add moderation checks on model output for safer usage

## 5. Basic Character Personality Modeling
- [ ] Define a simple personality model
  - [ ] Identify key CK3 traits to use
  - [ ] Create a mapping between traits and personality aspects
- [ ] Implement function to generate character personality
  - [ ] Write script to extract character traits from CK3 data
  - [ ] Create personality profile based on traits
- [ ] Create system to incorporate personality into AI prompts
  - [ ] Design template for personality-infused prompts
  - [ ] Implement function to merge personality with base prompt

## 6. Minimal UI
- [ ] Design a basic chat window interface
  - [ ] Sketch UI layout
  - [ ] Create necessary UI script files
- [ ] Implement UI for displaying AI responses
  - [ ] Create text display area in the UI
  - [ ] Implement text updating function
- [ ] Create a simple text input field for player responses
  - [ ] Add input field to UI
  - [ ] Implement input handling function

## 7. Data Management and Performance Optimization
- [x] Update project structure to use environment variables for API keys and URLs
- [ ] Implement conversation history management for long-running sessions
- [ ] Implement automatic truncation of long conversations
- [ ] Add support for continuing conversations across sessions
- [ ] Create a system for managing and updating session-wide instructions
- [ ] Implement a caching system for frequently accessed game state data
- [ ] Optimize screenshot capture and processing for better performance
- [ ] Implement audio buffering for smoother playback
- [ ] Optimize code for better resource usage and responsiveness

## 8. Basic CK3 Integration
- [ ] Implement function to extract relevant game state data
  - [ ] Identify necessary game state variables
  - [ ] Write script to access and format game state data
- [ ] Create event listeners for key game events
  - [ ] Identify important game events to track
  - [ ] Implement event handling scripts
- [ ] Set up system to trigger AI interactions based on game events
  - [ ] Design trigger conditions
  - [ ] Implement triggering mechanism

## 9. AI Interaction and User Interface
- [x] Implement full support for both text and audio modalities in input and output
- [x] Add support for handling interruptions in audio responses
- [ ] Improve handling of interruptions during audio responses
- [ ] Create a user-friendly interface for configuring the AI character
- [ ] Update system and character prompts to better match new capabilities
- [ ] Implement system to display AI responses in the UI
  - [ ] Create function to update UI with new responses
  - [ ] Implement basic animation for text appearance

## 10. Error Handling and Logging
- [ ] Set up basic error handling for all main functions
  - [ ] Implement try-catch blocks in critical areas
  - [ ] Create error messages for common failure points
- [ ] Implement a logging system for debugging
  - [ ] Set up logging library
  - [ ] Add log entries at key points in the code
- [ ] Create user-facing error messages for common issues
  - [ ] Design error message display in UI
  - [ ] Write clear, informative error messages

## 11. Testing
- [ ] Write unit tests for core functions
  - [ ] Set up testing framework
  - [ ] Create test cases for each major function
- [ ] Perform integration testing of CK3 mod with n8n and GPT-4o-mini
  - [ ] Design integration test scenarios
  - [ ] Run and document integration tests
- [ ] Conduct playtesting sessions to identify major issues
  - [ ] Create playtesting scripts/scenarios
  - [ ] Recruit playtesters and gather feedback

## 12. Documentation
- [ ] Write basic installation and setup instructions
  - [ ] Document mod installation process
  - [ ] Create guide for setting up n8n and GPT-4o-mini
- [ ] Create a simple user guide for the MVP features
  - [ ] Describe how to interact with the AI character
  - [ ] Explain basic mod functionality
- [ ] Document known issues and limitations
  - [ ] Compile list of known bugs and limitations
  - [ ] Create FAQ for common user questions

## 13. Prepare for Release
- [ ] Perform final testing and bug fixes
  - [ ] Run full test suite
  - [ ] Address any last-minute issues
- [ ] Create a build script for packaging the mod
  - [ ] Write script to compile mod files
  - [ ] Implement versioning system
- [ ] Write release notes
  - [ ] Summarize features and known issues
  - [ ] Include credits and acknowledgments

## 14. Plan Next Phase
- [ ] Review completed work and lessons learned
  - [ ] Hold team retrospective meeting
  - [ ] Document key insights and challenges
- [ ] Gather initial user feedback
  - [ ] Create feedback form or survey
  - [ ] Analyze and summarize user responses
- [ ] Begin planning for Phase 2 enhancements
  - [ ] Prioritize features for next phase
  - [ ] Create high-level roadmap for Phase 2
