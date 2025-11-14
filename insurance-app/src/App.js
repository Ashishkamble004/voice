import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [errorMessage, setErrorMessage] = useState('');
  const [showAssistant, setShowAssistant] = useState(false);
  const [messages, setMessages] = useState([]);
  
  const videoRef = useRef(null);
  const audioContextRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const wsRef = useRef(null);

  // Initialize camera and audio
  const startMultimodalCapture = async () => {
    try {
      setErrorMessage('');
      
      // Request camera and audio access - back camera for car inspection
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: { ideal: 'environment' }  // Use back camera on mobile
        },
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        }
      });

      mediaStreamRef.current = stream;
      
      // Set video element
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      setIsCameraActive(true);
      setShowAssistant(true);
      
      // Add initial greeting message
      setMessages([{
        type: 'assistant',
        text: 'Hello! I\'m your Cymbal Auto Insurance AI assistant. Please show me the damaged area of your vehicle and describe what happened.',
        timestamp: new Date()
      }]);
      
      // Connect to WebSocket and start streaming
      connectWebSocket(stream);
      
    } catch (error) {
      console.error('Error accessing media devices:', error);
      setErrorMessage('Failed to access camera or microphone. Please grant permissions and try again.');
    }
  };

  // Connect to WebSocket server
  const connectWebSocket = (stream) => {
    // For development, you can replace with your backend URL
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8765';
    
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
        startStreaming(stream);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'transcript') {
            // Add to messages
            setMessages(prev => [...prev, {
              type: 'assistant',
              text: data.text,
              timestamp: new Date()
            }]);
          } else if (data.type === 'audio') {
            // Play received audio
            playAudio(data.audio);
          }
        } catch (error) {
          console.error('Error processing message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
        setErrorMessage('Connection error. Please try again.');
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
        setConnectionStatus('disconnected');
      };
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      setErrorMessage('Failed to connect to server.');
    }
  };

  // Start streaming audio and video
  const startStreaming = async (stream) => {
    try {
      // Set up audio context
      const audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 16000
      });
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(512, 1, 1);

      source.connect(processor);
      processor.connect(audioContext.destination);

      // Send audio chunks via WebSocket
      processor.onaudioprocess = (e) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          const audioData = e.inputBuffer.getChannelData(0);
          const audioBuffer = new Int16Array(audioData.length);
          
          for (let i = 0; i < audioData.length; i++) {
            audioBuffer[i] = Math.max(-1, Math.min(1, audioData[i])) * 0x7FFF;
          }
          
          wsRef.current.send(JSON.stringify({
            type: 'audio',
            data: Array.from(audioBuffer)
          }));
        }
      };

      // Capture and send video frames periodically
      const captureVideoFrame = () => {
        if (!videoRef.current || !isCameraActive) return;
        
        const canvas = document.createElement('canvas');
        canvas.width = 640;
        canvas.height = 480;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob((blob) => {
          if (blob && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            const reader = new FileReader();
            reader.onloadend = () => {
              wsRef.current.send(JSON.stringify({
                type: 'video',
                data: reader.result.split(',')[1] // Base64 data
              }));
            };
            reader.readAsDataURL(blob);
          }
        }, 'image/jpeg', 0.7);
      };

      // Send video frames every second
      const videoInterval = setInterval(captureVideoFrame, 1000);
      
      // Store interval ID for cleanup
      return () => clearInterval(videoInterval);
      
    } catch (error) {
      console.error('Error starting streaming:', error);
      setErrorMessage('Failed to start streaming.');
    }
  };

  // Play received audio
  const playAudio = async (base64Audio) => {
    try {
      const audioData = atob(base64Audio);
      const arrayBuffer = new ArrayBuffer(audioData.length);
      const view = new Uint8Array(arrayBuffer);
      
      for (let i = 0; i < audioData.length; i++) {
        view[i] = audioData.charCodeAt(i);
      }
      
      const audioContext = audioContextRef.current || new AudioContext();
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.destination);
      source.start(0);
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsCameraActive(false);
    setShowAssistant(false);
    setConnectionStatus('disconnected');
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopRecording();
    };
  }, []);

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="logo-section">
          <div className="logo">🚗 Cymbal Auto Insurance</div>
          <span className="logo-badge">Vehicle Claims</span>
        </div>
        {showAssistant && (
          <div className="connection-status">
            <span className={`status-indicator ${connectionStatus}`}></span>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="main-content">
        {!showAssistant ? (
          <>
            {/* Hero Section */}
            <section className="hero-section">
              <div className="hero-content">
                <h1>Vehicle Damage Claims Made Easy</h1>
                <p className="hero-subtitle">
                  Get instant claim assistance with our AI-powered virtual agent
                </p>
                <div className="hero-features">
                  <div className="hero-feature">
                    <span className="feature-icon-small">📸</span>
                    <span>Show damage via camera</span>
                  </div>
                  <div className="hero-feature">
                    <span className="feature-icon-small">🤖</span>
                    <span>AI damage assessment</span>
                  </div>
                  <div className="hero-feature">
                    <span className="feature-icon-small">⚡</span>
                    <span>Instant claim processing</span>
                  </div>
                </div>
              </div>
              
              <div className="hero-image">
                <div className="car-illustration">
                  🚙
                </div>
              </div>
            </section>

            {/* Quick Actions */}
            <section className="quick-actions">
              <h2>File a Claim</h2>
              <div className="action-cards">
                <div className="action-card highlight">
                  <div className="card-icon">🔧</div>
                  <h3>Accident Damage</h3>
                  <p>Report collision or accident damage</p>
                </div>
                <div className="action-card">
                  <div className="card-icon">🌧️</div>
                  <h3>Weather Damage</h3>
                  <p>Hail, flood, or storm damage</p>
                </div>
                <div className="action-card">
                  <div className="card-icon">💥</div>
                  <h3>Vandalism</h3>
                  <p>Theft or vandalism claims</p>
                </div>
              </div>
            </section>

            {/* How It Works */}
            <section className="how-it-works">
              <h2>How It Works</h2>
              <div className="steps">
                <div className="step">
                  <div className="step-number">1</div>
                  <h3>Start Virtual Agent</h3>
                  <p>Click the chat button to connect</p>
                </div>
                <div className="step">
                  <div className="step-number">2</div>
                  <h3>Show Damage</h3>
                  <p>Point camera at damaged areas</p>
                </div>
                <div className="step">
                  <div className="step-number">3</div>
                  <h3>Get Assessment</h3>
                  <p>AI analyzes and processes claim</p>
                </div>
              </div>
            </section>

            {errorMessage && (
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                {errorMessage}
              </div>
            )}
          </>
        ) : (
          <>
            {/* Assistant Interface */}
            <section className="assistant-interface">
              <div className="assistant-header">
                <h2>🤖 AI Claims Assistant</h2>
                <button className="close-assistant" onClick={stopRecording}>
                  ✕
                </button>
              </div>
              
              {/* Video Feed */}
              <div className="video-container">
                <video 
                  ref={videoRef}
                  autoPlay 
                  playsInline 
                  muted
                  className="video-preview"
                />
                {!isCameraActive && (
                  <div className="video-placeholder">
                    <div className="placeholder-icon">📹</div>
                    <p>Initializing camera...</p>
                  </div>
                )}
                <div className="video-overlay">
                  <div className="recording-indicator">
                    <span className="rec-dot"></span>
                    <span>LIVE</span>
                  </div>
                  <div className="video-hint">
                    Point camera at damaged area
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="messages-container">
                {messages.map((msg, index) => (
                  <div key={index} className={`message ${msg.type}`}>
                    <div className="message-icon">
                      {msg.type === 'assistant' ? '🤖' : '👤'}
                    </div>
                    <div className="message-content">
                      <p>{msg.text}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Controls */}
              <div className="assistant-controls">
                <div className="control-hint">
                  🎤 Speak or show damage to continue
                </div>
              </div>
            </section>
          </>
        )}
      </main>

      {/* Floating Chat Button */}
      {!showAssistant && (
        <button 
          className="floating-chat-btn"
          onClick={startMultimodalCapture}
          aria-label="Start virtual agent"
        >
          <span className="chat-icon">💬</span>
          <span className="chat-text">Start Claim</span>
        </button>
      )}

      {/* Footer */}
      <footer className="app-footer">
        <p>© 2024 Cymbal Auto Insurance. Powered by AI Technology</p>
        <p className="disclaimer">Demo application for vehicle damage claims</p>
      </footer>
    </div>
  );
}

export default App;
