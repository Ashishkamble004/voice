# Cymbal Auto Insurance - AI-Powered Vehicle Claims Assistant

A mobile-first React web application for vehicle damage claims processing with multimodal (camera + audio) capabilities, powered by Google Gemini Live API.

## 🎯 Overview

This application provides an AI-powered virtual agent for Cymbal Auto Insurance that enables customers to file vehicle damage claims using their smartphone camera and voice. The agent can analyze vehicle damage in real-time and guide customers through the claims process.

## ✨ Key Features

- 📱 **Mobile-First Design**: Optimized for smartphone use with responsive layouts
- 🎤 **Voice Input**: Natural language conversation with AI assistant
- 📸 **Camera Access**: Real-time video streaming using device's back camera
- 🤖 **AI Damage Assessment**: Gemini AI analyzes vehicle damage from video feed
- 💬 **Chat Interface**: Floating chat button for easy access to virtual agent
- ⚡ **Real-Time Processing**: Instant feedback and guidance during claims process

## 🏗️ Architecture

### Frontend (React)
- **Framework**: React 19
- **Styling**: Custom CSS with mobile-first responsive design
- **Camera**: WebRTC API with environment-facing camera mode
- **Audio**: Web Audio API for real-time streaming
- **Communication**: WebSocket for bidirectional data flow

### Backend (Python)
- **Server**: WebSocket server using `websockets` library
- **AI Model**: Google Gemini Live API (`gemini-live-2.5-flash-preview-native-audio-09-2025`)
- **Processing**: Audio (16kHz PCM) and Video (JPEG frames at 1fps)
- **Project**: `general-ak` (us-central1)

## 🚀 Getting Started

### Prerequisites

- Node.js 14+ and npm
- Python 3.9+
- Google Cloud Project with Vertex AI enabled
- Camera and microphone permissions on device

### Installation

#### 1. Frontend Setup

```bash
cd insurance-app

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Update .env with your WebSocket server URL
# REACT_APP_WS_URL=ws://your-server-url:8080

# Start development server
npm start
```

The app will be available at `http://localhost:3000`

#### 2. Backend Setup

```bash
cd insurance-app/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_CLOUD_PROJECT=general-ak
export GOOGLE_CLOUD_LOCATION=us-central1

# Authenticate with Google Cloud
gcloud auth application-default login

# Start WebSocket server
python server.py
```

The server will start on `ws://0.0.0.0:8080`

## 📱 Usage

### Desktop/Laptop Testing
1. Open `http://localhost:3000` in your browser
2. Click the "Start Claim" button
3. Grant camera and microphone permissions
4. Interact with the AI assistant

### Mobile Phone (Recommended)
1. Ensure backend server is accessible from your phone's network
2. Update `REACT_APP_WS_URL` in frontend `.env` to your server's IP
3. Open the app on your phone's browser
4. Click "Start Claim" - the back camera will activate automatically
5. Point camera at vehicle damage and describe what happened
6. The AI will analyze the damage and guide you through the claim

## 🎨 Screenshots

### Desktop View
![Desktop View](https://github.com/user-attachments/assets/6bb326fc-d947-4cbe-9910-2209b3742856)

### Mobile View
![Mobile View](https://github.com/user-attachments/assets/70caca52-5265-4d49-9b78-c9d63e6d42e0)

## 🔧 Configuration

### Environment Variables

**Frontend (`.env`)**:
```env
REACT_APP_WS_URL=ws://localhost:8080
```

**Backend (environment variables)**:
```env
GOOGLE_CLOUD_PROJECT=general-ak
GOOGLE_CLOUD_LOCATION=us-central1
GEMINI_MODEL=gemini-live-2.5-flash-preview-native-audio-09-2025
WEBSOCKET_PORT=8080
```

## 🛠️ Technology Stack

### Frontend
- React 19
- WebRTC APIs (getUserMedia)
- Web Audio API
- WebSocket Client
- CSS3 with Flexbox/Grid

### Backend
- Python 3.9+
- websockets
- google-generativeai
- google-cloud-aiplatform
- PyAudio
- Pillow (PIL)

## 📁 Project Structure

```
insurance-app/
├── public/                 # Static assets
├── src/
│   ├── App.js             # Main React component
│   ├── App.css            # Styling
│   └── index.js           # React entry point
├── backend/
│   ├── server.py          # WebSocket server + Gemini integration
│   └── requirements.txt   # Python dependencies
├── .env.example           # Environment variables template
├── package.json           # npm dependencies
└── README.md             # This file
```

## 🌐 Browser Compatibility

- **Recommended**: Chrome/Edge 90+ on Android/iOS
- Firefox 88+
- Safari 14+ (iOS/macOS)
- Requires WebRTC support

## 🔒 Security & Privacy

- Camera/microphone access requires explicit user permission
- All communication over WebSocket connections
- No permanent data storage
- Follows Google Cloud security best practices

## 🚢 Deployment

### Frontend
```bash
cd insurance-app
npm run build
# Deploy build/ directory to your hosting service
```

### Backend
- Deploy to Cloud Run, App Engine, or any Python hosting service
- Ensure WebSocket support is enabled
- Configure appropriate CORS settings

## 📖 How It Works

1. **User Clicks "Start Claim"**: Floating button initiates the session
2. **Camera & Audio Activation**: App requests permissions and activates back camera
3. **WebSocket Connection**: Establishes connection to backend server
4. **Streaming Begins**:
   - Audio: Continuous streaming at 16kHz
   - Video: Frame capture at 1fps, compressed to JPEG
5. **AI Processing**: Gemini analyzes both audio and video streams
6. **Real-Time Response**: AI provides voice and text responses about damage assessment
7. **Session Management**: User can end session anytime via close button

## 🤝 Contributing

This is a demonstration project showcasing multimodal AI capabilities for insurance claims processing.

## 📄 License

This project is provided as-is for demonstration purposes.

## 🙏 Acknowledgments

- Built with [Google Gemini Live API](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
- Based on [gen-ai-livestream](https://github.com/SaschaHeyer/gen-ai-livestream) reference implementation
- Cymbal Auto Insurance is a fictional company for demonstration purposes

## 📞 Support

For issues or questions:
- Check browser console for error messages
- Verify camera/microphone permissions
- Ensure backend server is running and accessible
- Confirm Google Cloud credentials are configured

---

**Note**: This is a demonstration application. For production use, implement proper error handling, security measures, rate limiting, and compliance with data protection regulations.
