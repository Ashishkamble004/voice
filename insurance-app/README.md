# SafeGuard Insurance - AI Assistant

A React-based mobile web application for insurance claims processing with multimodal (camera + audio) input capabilities, powered by Google Gemini Live API.

## 🎯 Overview

This is an insurance-focused web application inspired by modern Indian insurance companies like Acko. It provides an AI-powered assistant that can:

- 📱 Access camera for document/damage verification
- 🎤 Process voice input for natural conversations
- 🤖 Real-time AI responses using Gemini Live API
- 🏥 Handle multiple insurance types (Health, Vehicle, Life, Home)
- 📄 Analyze documents and images shown via camera
- 🌐 Mobile-first responsive design

## 🏗️ Architecture

```
insurance-app/
├── src/                    # React frontend
│   ├── App.js             # Main application component
│   ├── App.css            # Styling (insurance-themed)
│   └── index.js           # Entry point
├── backend/               # Python WebSocket server
│   ├── server.py          # Main server with Gemini integration
│   └── requirements.txt   # Python dependencies
└── public/                # Static assets
```

## 🚀 Getting Started

### Prerequisites

- Node.js 14+ and npm
- Python 3.9+
- Google Cloud Project with Vertex AI enabled
- Camera and microphone permissions on device

### Installation

#### 1. Frontend Setup

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Update .env with your WebSocket URL
# REACT_APP_WS_URL=ws://your-server-url:8080
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Google Cloud credentials
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1

# Authenticate with Google Cloud
gcloud auth application-default login
```

### Running the Application

#### Start Backend Server

```bash
cd backend
source venv/bin/activate
python server.py
```

The WebSocket server will start on `ws://localhost:8080`

#### Start Frontend

```bash
# In the main insurance-app directory
npm start
```

The React app will open at `http://localhost:3000`

## 📱 Usage

1. **Open the app** in your mobile browser (or desktop for testing)
2. **Select claim type** (Health, Vehicle, Life, or Home)
3. **Click "Start Claim Assistant"** to begin
4. **Grant permissions** for camera and microphone when prompted
5. **Interact with AI**:
   - Speak to describe your claim
   - Show documents or damage via camera
   - Get instant AI-powered responses

## 🎨 Features

### Frontend (React)
- Mobile-first responsive design
- Insurance-themed UI with Acko-inspired styling
- Real-time camera preview
- WebSocket communication for audio/video streaming
- Conversation transcript display
- Multiple insurance type selection

### Backend (Python)
- WebSocket server for real-time communication
- Integration with Google Gemini Live API
- Audio and video processing
- Multimodal input handling
- Insurance-specific system instructions

## 🔧 Configuration

### Environment Variables

**Frontend (.env)**:
```
REACT_APP_WS_URL=ws://your-backend-url:8080
```

**Backend (environment variables)**:
```
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GEMINI_MODEL=gemini-2.0-flash-live-preview-04-09
WEBSOCKET_PORT=8080
```

### Audio Settings
- Input sample rate: 16,000 Hz
- Output sample rate: 24,000 Hz
- Audio format: PCM 16-bit
- Channels: Mono

### Video Settings
- Frame capture: 1 frame per second
- Resolution: 640x480
- Format: JPEG with 70% quality
- Thumbnail size: 512x512 (sent to API)

## 🔒 Security & Privacy

- Camera and audio access requires explicit user permission
- No data is stored permanently
- All communication over WebSocket connections
- Follows Google Cloud security best practices

## 🌐 Browser Compatibility

- Chrome/Edge 90+ (recommended)
- Firefox 88+
- Safari 14+ (iOS/macOS)
- Mobile browsers with WebRTC support

## 📚 Technology Stack

### Frontend
- **React 19** - UI framework
- **WebRTC APIs** - Camera and microphone access
- **WebSocket** - Real-time communication
- **CSS3** - Responsive styling

### Backend
- **Python 3.9+** - Server runtime
- **websockets** - WebSocket server
- **google-generativeai** - Gemini AI SDK
- **PyAudio** - Audio processing
- **Pillow** - Image processing

## 🤝 Development

### Project Structure

```
src/
├── App.js              # Main React component
│   ├── Camera/Audio access
│   ├── WebSocket client
│   ├── Stream management
│   └── UI components
└── App.css             # Comprehensive styling

backend/
└── server.py           # WebSocket server
    ├── InsuranceAssistantSession
    ├── AudioManager
    └── WebSocket handlers
```

### Key Components

**Frontend**:
- `startMultimodalCapture()` - Initialize camera and audio
- `connectWebSocket()` - Establish server connection
- `startStreaming()` - Stream audio and video to backend

**Backend**:
- `InsuranceAssistantSession` - Manages client session
- `AudioManager` - Handles audio playback
- `handle_client()` - WebSocket connection handler

## 📄 License

This project is provided as-is for demonstration purposes.

## 🙏 Acknowledgments

- Built with [Google Gemini Live API](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
- Inspired by [Acko Insurance](https://www.acko.com/) UI/UX
- Based on [gen-ai-livestream](https://github.com/SaschaHeyer/gen-ai-livestream) reference implementation

## 📞 Support

For issues or questions:
- Check the console for error messages
- Verify camera/microphone permissions
- Ensure backend server is running
- Check Google Cloud credentials

---

**Note**: This is a demonstration application. For production use, implement proper error handling, security measures, and compliance with data protection regulations.
