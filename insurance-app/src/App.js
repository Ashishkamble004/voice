import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [errorMessage, setErrorMessage] = useState('');
  const [transcript, setTranscript] = useState('');
  const [claimType, setClaimType] = useState('health');
  
  const videoRef = useRef(null);
  const audioContextRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const wsRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Initialize camera and audio
  const startMultimodalCapture = async () => {
    try {
      setErrorMessage('');
      
      // Request camera and audio access
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
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
      setIsRecording(true);
      
      // Connect to WebSocket and start streaming
      connectWebSocket(stream);
      
    } catch (error) {
      console.error('Error accessing media devices:', error);
      setErrorMessage('Failed to access camera or microphone. Please grant permissions.');
    }
  };

  // Connect to WebSocket server
  const connectWebSocket = (stream) => {
    // For development, you can replace with your backend URL
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8080';
    
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
            setTranscript(prev => prev + ' ' + data.text);
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
    
    setIsRecording(false);
    setIsCameraActive(false);
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
          <div className="logo">🛡️ SafeGuard Insurance</div>
          <span className="logo-badge">AI Assistant</span>
        </div>
        <div className="connection-status">
          <span className={`status-indicator ${connectionStatus}`}></span>
          <span className="status-text">{connectionStatus}</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Claim Type Selection */}
        <section className="claim-type-section">
          <h2>Select Claim Type</h2>
          <div className="claim-types">
            <button 
              className={`claim-btn ${claimType === 'health' ? 'active' : ''}`}
              onClick={() => setClaimType('health')}
            >
              <span className="icon">🏥</span>
              <span>Health Insurance</span>
            </button>
            <button 
              className={`claim-btn ${claimType === 'vehicle' ? 'active' : ''}`}
              onClick={() => setClaimType('vehicle')}
            >
              <span className="icon">🚗</span>
              <span>Vehicle Insurance</span>
            </button>
            <button 
              className={`claim-btn ${claimType === 'life' ? 'active' : ''}`}
              onClick={() => setClaimType('life')}
            >
              <span className="icon">💼</span>
              <span>Life Insurance</span>
            </button>
            <button 
              className={`claim-btn ${claimType === 'home' ? 'active' : ''}`}
              onClick={() => setClaimType('home')}
            >
              <span className="icon">🏠</span>
              <span>Home Insurance</span>
            </button>
          </div>
        </section>

        {/* Video and Audio Interface */}
        <section className="media-section">
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
                <p>Camera Preview</p>
              </div>
            )}
          </div>

          <div className="controls-section">
            {!isRecording ? (
              <button 
                className="primary-btn start-btn"
                onClick={startMultimodalCapture}
              >
                <span className="btn-icon">🎙️</span>
                Start Claim Assistant
              </button>
            ) : (
              <button 
                className="danger-btn stop-btn"
                onClick={stopRecording}
              >
                <span className="btn-icon">⏹️</span>
                Stop Recording
              </button>
            )}
          </div>

          {errorMessage && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {errorMessage}
            </div>
          )}
        </section>

        {/* Transcript Section */}
        {transcript && (
          <section className="transcript-section">
            <h3>Conversation Transcript</h3>
            <div className="transcript-box">
              {transcript}
            </div>
          </section>
        )}

        {/* Features Section */}
        <section className="features-section">
          <h2>How It Works</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🎤</div>
              <h3>Voice Input</h3>
              <p>Speak naturally to describe your claim or ask questions</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📸</div>
              <h3>Visual Evidence</h3>
              <p>Show documents or damage through your camera</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI Assistant</h3>
              <p>Get instant responses powered by Gemini AI</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Quick Claims</h3>
              <p>File and track claims in minutes, not hours</p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>© 2024 SafeGuard Insurance. Powered by AI Technology</p>
        <p className="disclaimer">This is a demo application. No actual claims are processed.</p>
      </footer>
    </div>
  );
}

export default App;
