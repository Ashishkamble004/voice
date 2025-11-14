"""
Multimodal Insurance Assistant Backend
Based on Google Gemini Live API with WebSocket support
Handles audio and video streaming from React frontend
"""

import asyncio
import base64
import io
import json
import logging
import os
from collections import deque
from typing import Optional

import PIL.Image
import pyaudio
import websockets
from google import genai
from google.genai.types import (
    LiveConnectConfig,
    PrebuiltVoiceConfig,
    SpeechConfig,
    VoiceConfig,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'general-ak')
GOOGLE_CLOUD_LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-live-2.5-flash-preview-native-audio-09-2025')
WEBSOCKET_PORT = int(os.getenv('WEBSOCKET_PORT', '8080'))

# Audio Configuration
AUDIO_FORMAT = pyaudio.paInt16
AUDIO_CHANNELS = 1
AUDIO_RECEIVE_SAMPLE_RATE = 24000
AUDIO_SEND_SAMPLE_RATE = 16000
AUDIO_CHUNK_SIZE = 512

# Insurance assistant system instruction
INSURANCE_SYSTEM_INSTRUCTION = """You are an AI assistant for Cymbal Auto Insurance, specializing in vehicle damage claims assessment.

Your role is to:
1. Analyze vehicle damage shown through the camera
2. Assess the severity and type of damage (collision, dents, scratches, broken parts, etc.)
3. Guide customers through the claims process
4. Ask relevant questions about the incident (when, where, how it happened)
5. Provide professional and empathetic support

When viewing video/images from the customer:
- Carefully examine the damaged areas of the vehicle
- Identify specific parts affected (bumper, doors, windshield, lights, panels, etc.)
- Describe the extent of damage (minor scratches, significant dents, structural damage, etc.)
- Note any safety concerns
- Estimate if it's likely cosmetic or requires structural repair

Be friendly, professional, and thorough. Speak naturally in a conversational tone.
Support both English and Hindi based on customer preference.

Start by greeting the customer as a Cymbal Auto Insurance representative and asking them to show the damaged area while describing what happened.
"""

# Gemini Live API Configuration
LIVE_CONNECT_CONFIG = LiveConnectConfig(
    response_modalities=["AUDIO"],
    speech_config=SpeechConfig(
        voice_config=VoiceConfig(
            prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Puck")
        )
    ),
    system_instruction=INSURANCE_SYSTEM_INSTRUCTION,
)


class AudioManager:
    """Manages audio playback for the backend"""
    
    def __init__(self, output_sample_rate=24000):
        self.pya = pyaudio.PyAudio()
        self.output_stream = None
        self.output_sample_rate = output_sample_rate
        self.audio_queue = deque()
        self.is_playing = False
        self.playback_task = None

    async def initialize(self):
        """Initialize audio output stream"""
        try:
            self.output_stream = await asyncio.to_thread(
                self.pya.open,
                format=AUDIO_FORMAT,
                channels=AUDIO_CHANNELS,
                rate=self.output_sample_rate,
                output=True,
            )
            logger.info("Audio output initialized")
        except Exception as e:
            logger.error(f"Error initializing audio output: {e}")

    def add_audio(self, audio_data):
        """Add audio data to playback queue"""
        self.audio_queue.append(audio_data)
        
        if self.playback_task is None or self.playback_task.done():
            self.playback_task = asyncio.create_task(self.play_audio())

    async def play_audio(self):
        """Play all queued audio data"""
        logger.debug("Playing audio from queue")
        while self.audio_queue:
            try:
                audio_data = self.audio_queue.popleft()
                if self.output_stream:
                    await asyncio.to_thread(self.output_stream.write, audio_data)
            except Exception as e:
                logger.error(f"Error playing audio: {e}")
        
        self.is_playing = False

    def interrupt(self):
        """Handle interruption by clearing audio queue"""
        self.audio_queue.clear()
        self.is_playing = False
        
        if self.playback_task and not self.playback_task.done():
            self.playback_task.cancel()

    def close(self):
        """Clean up audio resources"""
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        self.pya.terminate()


class InsuranceAssistantSession:
    """Manages a single client session with Gemini Live API"""
    
    def __init__(self, websocket, client_instance):
        self.websocket = websocket
        self.client_instance = client_instance
        self.audio_manager = AudioManager()
        self.audio_queue = asyncio.Queue(maxsize=100)
        self.video_queue = asyncio.Queue(maxsize=10)
        self.stop_event = asyncio.Event()
        self.session = None

    async def start(self):
        """Start the assistant session"""
        try:
            await self.audio_manager.initialize()
            
            # Connect to Gemini Live API
            async with self.client_instance.aio.live.connect(
                model=GEMINI_MODEL, 
                config=LIVE_CONNECT_CONFIG
            ) as session:
                self.session = session
                logger.info("Connected to Gemini Live API")
                
                async with asyncio.TaskGroup() as tg:
                    # Start all tasks
                    tg.create_task(self.receive_from_websocket())
                    tg.create_task(self.send_audio_to_gemini())
                    tg.create_task(self.send_video_to_gemini())
                    tg.create_task(self.receive_from_gemini())
                    
                    # Wait for stop signal
                    await self.stop_event.wait()
                    
        except Exception as e:
            logger.error(f"Error in session: {e}")
        finally:
            await self.cleanup()

    async def receive_from_websocket(self):
        """Receive audio and video data from WebSocket client"""
        try:
            async for message in self.websocket:
                if self.stop_event.is_set():
                    break
                
                try:
                    data = json.loads(message)
                    
                    if data['type'] == 'audio':
                        # Convert audio data from JSON array to bytes
                        audio_array = data['data']
                        audio_bytes = bytes([int(x) & 0xFF for x in audio_array])
                        await self.audio_queue.put(audio_bytes)
                        
                    elif data['type'] == 'video':
                        # Decode base64 video frame
                        video_data = base64.b64decode(data['data'])
                        await self.video_queue.put(video_data)
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing WebSocket message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed by client")
            self.stop_event.set()
        except Exception as e:
            logger.error(f"Error receiving from WebSocket: {e}")
            self.stop_event.set()

    async def send_audio_to_gemini(self):
        """Send audio chunks to Gemini Live API"""
        try:
            while not self.stop_event.is_set() or not self.audio_queue.empty():
                try:
                    audio_data = await asyncio.wait_for(
                        self.audio_queue.get(), 
                        timeout=0.5
                    )
                    
                    await self.session.send_realtime_input(
                        media={
                            "data": audio_data,
                            "mime_type": f"audio/pcm;rate={AUDIO_SEND_SAMPLE_RATE}"
                        }
                    )
                    self.audio_queue.task_done()
                    
                except asyncio.TimeoutError:
                    if self.stop_event.is_set() and self.audio_queue.empty():
                        break
                    continue
                    
        except Exception as e:
            logger.error(f"Error sending audio to Gemini: {e}")

    async def send_video_to_gemini(self):
        """Send video frames to Gemini Live API"""
        try:
            while not self.stop_event.is_set() or not self.video_queue.empty():
                try:
                    video_data = await asyncio.wait_for(
                        self.video_queue.get(),
                        timeout=0.5
                    )
                    
                    # Process image
                    img = PIL.Image.open(io.BytesIO(video_data))
                    img.thumbnail([512, 512])
                    
                    # Convert to JPEG
                    image_io = io.BytesIO()
                    img.save(image_io, format="jpeg", quality=70)
                    image_io.seek(0)
                    image_bytes = image_io.read()
                    
                    # Send to Gemini
                    await self.session.send_realtime_input(
                        media={
                            "mime_type": "image/jpeg",
                            "data": base64.b64encode(image_bytes).decode()
                        }
                    )
                    self.video_queue.task_done()
                    
                except asyncio.TimeoutError:
                    if self.stop_event.is_set() and self.video_queue.empty():
                        break
                    continue
                    
        except Exception as e:
            logger.error(f"Error sending video to Gemini: {e}")

    async def receive_from_gemini(self):
        """Receive responses from Gemini and send to WebSocket"""
        try:
            async for response in self.session.receive():
                if self.stop_event.is_set():
                    break
                
                server_content = response.server_content
                
                # Handle interruptions
                if hasattr(server_content, "interrupted") and server_content.interrupted:
                    logger.info("Interruption detected from server")
                    self.audio_manager.interrupt()
                
                # Process model responses
                if server_content and server_content.model_turn:
                    for part in server_content.model_turn.parts:
                        # Handle audio response
                        if part.inline_data:
                            audio_data = part.inline_data.data
                            
                            # Send to WebSocket client
                            await self.websocket.send(json.dumps({
                                'type': 'audio',
                                'audio': base64.b64encode(audio_data).decode()
                            }))
                            
                            # Also play locally if needed
                            # self.audio_manager.add_audio(audio_data)
                        
                        # Handle text response
                        if part.text:
                            logger.info(f"Gemini text: {part.text}")
                            await self.websocket.send(json.dumps({
                                'type': 'transcript',
                                'text': part.text
                            }))
                
                # Handle turn complete
                if server_content and server_content.turn_complete:
                    logger.debug("Gemini turn complete")
                    
        except Exception as e:
            logger.error(f"Error receiving from Gemini: {e}")
            self.stop_event.set()

    async def cleanup(self):
        """Clean up session resources"""
        logger.info("Cleaning up session")
        self.stop_event.set()
        self.audio_manager.close()


async def handle_client(websocket, path):
    """Handle a new WebSocket client connection"""
    client_address = websocket.remote_address
    logger.info(f"New client connected: {client_address}")
    
    try:
        # Initialize Gemini client
        client_instance = genai.Client(
            vertexai=True,
            project=GOOGLE_CLOUD_PROJECT,
            location=GOOGLE_CLOUD_LOCATION
        )
        
        # Create and start session
        session = InsuranceAssistantSession(websocket, client_instance)
        await session.start()
        
    except Exception as e:
        logger.error(f"Error handling client {client_address}: {e}")
    finally:
        logger.info(f"Client disconnected: {client_address}")


async def main():
    """Start the WebSocket server"""
    logger.info(f"Starting Insurance Assistant WebSocket server on port {WEBSOCKET_PORT}")
    logger.info(f"Project: {GOOGLE_CLOUD_PROJECT}, Location: {GOOGLE_CLOUD_LOCATION}")
    logger.info(f"Model: {GEMINI_MODEL}")
    
    async with websockets.serve(handle_client, "0.0.0.0", WEBSOCKET_PORT):
        logger.info(f"Server started successfully on ws://0.0.0.0:{WEBSOCKET_PORT}")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
