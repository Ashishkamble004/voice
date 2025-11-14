# Voice - AI-Powered Voice Assistant

A real-time, streaming multimodal voice assistant powered by Google's Agent Development Kit (ADK) and Vertex AI Live API with Gemini 2.5 Flash Live model.

## 🎯 Overview

This repository contains a complete implementation of an intelligent voice assistant that can:

- 🎤 Process real-time audio input from microphone
- 🎥 Analyze video input from webcam or screen sharing
- 🔊 Stream responses as audio and text
- 🛠️ Execute function calls and tool integrations
- 🌐 Support multilingual conversations (Hindi, Marathi, Gujarati, English)
- 🏦 Demonstrate customer service capabilities (e.g., Cymbal Bank virtual representative)

## ✨ Key Features

- **Bidirectional Audio Streaming**: Real-time voice conversation with the Gemini model
- **Video Analysis**: Process webcam or screen sharing video frames
- **WebSocket Communication**: Low-latency bidirectional communication
- **Function Calling**: ADK tool integration with mock service APIs
- **Full ADK Integration**: Uses ADK's `LiveRequestQueue` and `Runner` for Gemini communication
- **Multilingual Support**: Authentic Indian accent support with Hindi, Marathi, and Gujarati
- **Interruption Handling**: Smart interruption detection and audio playback management

## 📁 Repository Structure

```
voice/
├── README.md                          # This file
├── live-api/                          # Main application directory
│   ├── README.md                      # Detailed documentation
│   ├── adk_audio_to_audio.py         # Standalone ADK audio assistant
│   └── app/                           # Web application
│       ├── client/                    # Frontend web client
│       │   ├── audio-client.js       # Audio WebSocket client base class
│       │   ├── multimodal-client.js  # Extended client with video
│       │   └── multimodal.html       # Web UI interface
│       └── server/                    # Backend server
│           ├── common.py             # Shared utilities and functions
│           ├── multimodal_server_adk.py  # ADK + WebSocket integration
│           ├── requirements.txt      # Python dependencies
│           └── start_servers.sh      # Server startup script
└── venv/                              # Python virtual environment (not committed)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Google Cloud Project with API access
- Vertex AI API enabled
- PyAudio for audio processing
- Node.js (optional, for client development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ashishkamble004/voice.git
   cd voice
   ```

2. **Set up Python virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd live-api/app/server
   pip install -r requirements.txt
   ```

4. **Configure Google Cloud credentials**
   
   Create a `.env` file in the `live-api` directory with your Google Cloud settings:
   ```
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

   Set up authentication:
   ```bash
   gcloud auth application-default login
   ```

### Running the Application

#### Option 1: Standalone Audio Assistant

Run the standalone audio-to-audio assistant:

```bash
cd live-api
python adk_audio_to_audio.py
```

This will start a voice assistant that listens to your microphone and responds with audio.

#### Option 2: Web-Based Multimodal Assistant

1. **Start the WebSocket server**
   ```bash
   cd live-api/app/server
   ./start_servers.sh
   ```

2. **Open the client**
   
   Open `live-api/app/client/multimodal.html` in your web browser.

3. **Start conversing**
   
   Click "Start Recording" to begin your conversation with the AI assistant.

## 🎓 How It Works

### Technology Stack

1. **Google ADK**: Agent Development Kit for building AI agents with tool integration
2. **Vertex AI Live API**: Real-time streaming API for Gemini 2.5 Flash Live model
3. **WebSockets**: Bidirectional communication between client and server
4. **PyAudio**: Audio capture and playback in Python
5. **Async/Await**: Python's asyncio for concurrent task management

### Architecture

```
┌─────────────┐         WebSocket         ┌─────────────┐
│   Browser   │ ◄────────────────────────► │   Server    │
│   Client    │   Audio/Video/Control      │  (Python)   │
└─────────────┘                            └─────────────┘
                                                  │
                                                  │ ADK API
                                                  ▼
                                            ┌─────────────┐
                                            │  Vertex AI  │
                                            │  Live API   │
                                            │  (Gemini)   │
                                            └─────────────┘
```

### Key Components

- **LiveRequestQueue**: ADK component for streaming audio and video to Gemini
- **Runner**: Manages the agent lifecycle and communication
- **AudioManager**: Handles audio capture, playback, and interruption
- **WebSocket Server**: Manages client connections and message routing

## 🛠️ Configuration

### Audio Settings

- Input sample rate: 16,000 Hz
- Output sample rate: 24,000 Hz
- Audio format: PCM (16-bit)
- Channels: Mono

### Model Configuration

- Server model: `gemini-live-2.5-flash-preview-native-audio-09-2025` (Web application)
- Standalone model: `gemini-2.0-flash-live-preview-04-09` (CLI application)
- Voice: Puck (server) / Aoede (standalone) - configurable
- Response modalities: Audio
- Streaming mode: Bidirectional

## 📚 Use Cases

1. **Customer Service Assistant**: Cymbal Bank virtual representative demo
2. **Service Request Status**: Check status of service requests via voice
3. **Multilingual Support**: Conversations in multiple Indian languages
4. **Interactive Voice Response**: Build IVR systems with AI
5. **Voice-Enabled Applications**: Add voice capabilities to any application

## 🔒 Security & Compliance

- Never stores or logs sensitive user data (PII)
- Cannot access user account information
- Uses secure Google Cloud authentication
- All communication over encrypted WebSocket connections

## 📖 Documentation

For detailed documentation, see:
- [Live API Documentation](live-api/README.md)
- [Deployment Guide](live-api/app/server/DEPLOYMENT.md) (if available)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [Google Agent Development Kit (ADK)](https://github.com/google/adk)
- Powered by [Vertex AI](https://cloud.google.com/vertex-ai)
- Uses [Gemini 2.5 Flash Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini)

## 📞 Support

For issues or questions:
- Open an issue in this repository
- Check the [ADK documentation](https://github.com/google/adk)
- Review Vertex AI [documentation](https://cloud.google.com/vertex-ai/docs)

---

**Note**: This is a demonstration project. For production use, ensure proper error handling, security measures, and compliance with data protection regulations.
