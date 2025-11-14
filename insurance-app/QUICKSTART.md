# Quick Start Guide - Cymbal Auto Insurance Demo

This guide will help you quickly set up and run the vehicle damage claims demo on your phone.

## Prerequisites

✅ Python 3.9+ installed  
✅ Node.js 14+ and npm installed  
✅ Google Cloud account with Vertex AI enabled  
✅ Mobile device with camera and browser  

## Step 1: Backend Setup (5 minutes)

```bash
# Navigate to backend directory
cd insurance-app/backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up Google Cloud authentication
gcloud auth application-default login

# Start the server
python server.py
```

The server will start on `ws://0.0.0.0:8765`

**Note your computer's IP address** (e.g., `192.168.1.100`) - you'll need this for mobile access.

## Step 2: Frontend Setup (3 minutes)

```bash
# Open new terminal and navigate to app directory
cd insurance-app

# Install dependencies (first time only)
npm install

# Create .env file
echo "REACT_APP_WS_URL=ws://YOUR_COMPUTER_IP:8765" > .env
# Replace YOUR_COMPUTER_IP with your actual IP address
# Example: REACT_APP_WS_URL=ws://192.168.1.100:8765

# Start development server
npm start
```

The app will be available at `http://localhost:3000`

## Step 3: Mobile Access

### Option A: Same Network (Recommended)
1. Ensure your phone is on the same WiFi network as your computer
2. On your phone, open browser and navigate to:
   ```
   http://YOUR_COMPUTER_IP:3000
   ```
   (Example: `http://192.168.1.100:3000`)

### Option B: USB Debugging (Android)
1. Enable USB debugging on your Android phone
2. Connect phone to computer via USB
3. Use Chrome Remote Debugging or port forwarding
4. Navigate to `http://localhost:3000`

## Step 4: Run Demo

1. **Open the app** on your phone
2. **Click "Start Claim"** button (floating blue button)
3. **Grant permissions** for camera and microphone
4. **Show vehicle damage**:
   - Point camera at a damaged car (or show a picture of damage on screen)
   - Speak to describe what happened: "I hit a pole and damaged my front bumper"
5. **Watch AI analyze** the damage and provide assessment
6. **Continue conversation** with voice or show different angles

## Troubleshooting

### Backend Issues

**Error: "FATAL: Google GenAI Client is not available"**
- Run `gcloud auth application-default login`
- Verify project ID is set: `export GOOGLE_CLOUD_PROJECT=general-ak`

**Error: "Address already in use"**
- Change port in backend/server.py: `WEBSOCKET_PORT = 8081`
- Update frontend .env accordingly

### Frontend Issues

**Error: "Failed to connect to server"**
- Verify backend is running
- Check firewall settings allow port 8765
- Confirm IP address in .env is correct
- Try accessing from browser: `ws://YOUR_IP:8765`

**Error: "Camera/Microphone permission denied"**
- Browser settings → Site permissions → Allow camera/microphone
- On iOS Safari: Settings → Safari → Camera/Microphone → Allow
- Try HTTPS instead of HTTP for production

### Network Issues

**Can't access from phone**
- Verify both devices on same WiFi network
- Check firewall isn't blocking connections
- Try accessing `http://YOUR_IP:3000` from phone browser
- On Mac: System Preferences → Sharing → ensure nothing blocks port

**WebSocket connection fails**
- Check backend logs for errors
- Verify WebSocket server is actually running on correct port
- Try telnet: `telnet YOUR_IP 8080` to test connectivity

## Finding Your Computer's IP Address

### macOS
```bash
ipconfig getifaddr en0  # WiFi
ipconfig getifaddr en1  # Ethernet
```

### Linux
```bash
hostname -I
# or
ip addr show
```

### Windows
```bash
ipconfig
# Look for "IPv4 Address" under your active network adapter
```

## Demo Tips

### Best Practices
✅ Use good lighting for camera  
✅ Speak clearly and naturally  
✅ Show damage from multiple angles  
✅ Describe incident context ("hit a pole", "hail damage", etc.)  
✅ Wait for AI response before continuing  

### Example Conversations

**Accident Damage:**
> "Hi, I need to file a claim. I was backing out and hit a pole. Let me show you the damage to my rear bumper."

**Hail Damage:**
> "My car was damaged in a hailstorm yesterday. You can see the dents on the hood and roof here."

**Scratches:**
> "Someone scratched my car door in the parking lot. Here's the damage along the side."

## Performance Notes

- **Initial connection**: May take 2-3 seconds
- **Video streaming**: 1 frame per second (optimized for bandwidth)
- **Audio response**: Near real-time (< 1 second latency)
- **Model processing**: 2-5 seconds for complex damage analysis

## Production Deployment

For production use:
1. Use HTTPS for frontend (required for camera on iOS)
2. Use WSS (WebSocket Secure) for backend
3. Deploy backend to Cloud Run or similar
4. Configure proper CORS and security headers
5. Implement authentication and rate limiting
6. Add error tracking and monitoring

## Support

If you encounter issues:
1. Check browser console (F12) for errors
2. Check backend terminal for server logs
3. Verify all prerequisites are met
4. Try a different browser or device
5. Restart both frontend and backend servers

## Next Steps

Once the demo is running:
- Experiment with different damage scenarios
- Test voice commands in different languages (Hindi supported)
- Try showing documents (policy papers, license)
- Observe how AI analyzes different types of damage

---

**Enjoy your demo! 🚗💬🤖**
