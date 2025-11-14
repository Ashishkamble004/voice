"""
Cymbal Auto Insurance - ADK-based Multimodal Backend
Agent Development Kit implementation for vehicle damage assessment
"""

import asyncio
import base64
import io
import json
import logging
import os

import PIL.Image
from google.adk.agents import Agent, LiveRequestQueue
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
import websockets

load_dotenv()

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
WEBSOCKET_PORT = int(os.getenv('WEBSOCKET_PORT', '8765'))
VOICE_NAME = os.getenv('VOICE_NAME', 'Puck')
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000

# Insurance assistant system instruction for ADK Agent
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


class InsuranceADKServer:
    """WebSocket server implementation using Google ADK for insurance claims."""
    
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.active_clients = {}
        
        # Initialize ADK Agent
        self.agent = Agent(
            name="insurance_claims_agent",
            model=GEMINI_MODEL,
            instruction=INSURANCE_SYSTEM_INSTRUCTION,
            tools=[],  # Add custom tools here if needed
        )
        
        # Create session service
        self.session_service = InMemorySessionService()
        
        logger.info(f"Insurance ADK Server initialized with model: {GEMINI_MODEL}")

    async def handle_client(self, websocket, path):
        """Handle a new WebSocket client connection."""
        client_id = id(websocket)
        client_address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"New client connected: {client_address} (ID: {client_id})")
        
        try:
            await self.process_client(websocket, client_id)
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            if client_id in self.active_clients:
                del self.active_clients[client_id]
            logger.info(f"Client disconnected: {client_address} (ID: {client_id})")

    async def process_client(self, websocket, client_id):
        """Process audio and video from the client using ADK."""
        # Store reference to client
        self.active_clients[client_id] = websocket
        
        # Create session for this client
        session = await self.session_service.create_session(
            app_name="cymbal_auto_insurance",
            user_id=f"user_{client_id}",
            session_id=f"session_{client_id}",
        )
        
        # Create runner
        runner = Runner(
            app_name="cymbal_auto_insurance",
            agent=self.agent,
            session_service=self.session_service,
        )
        
        # Create live request queue
        live_request_queue = LiveRequestQueue()
        
        # Create run config with audio settings
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=VOICE_NAME
                    )
                ),
                enable_automatic_vad=True,
            ),
            response_modalities=["AUDIO"],
            output_audio_transcription=types.AudioTranscriptionConfig(),
            input_audio_transcription=types.AudioTranscriptionConfig(),
        )
        
        # Queues for audio and video data from the client
        audio_queue = asyncio.Queue()
        video_queue = asyncio.Queue()
        
        async with asyncio.TaskGroup() as tg:
            # Task to process incoming WebSocket messages
            async def handle_websocket_messages():
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        if data.get("type") == "audio":
                            # Get audio data from JSON array
                            audio_array = data.get("data", [])
                            # Convert to bytes
                            audio_bytes = bytes([int(x) & 0xFF for x in audio_array])
                            await audio_queue.put(audio_bytes)
                        elif data.get("type") == "video":
                            # Decode base64 video frame
                            video_b64 = data.get("data", "")
                            video_bytes = base64.b64decode(video_b64)
                            await video_queue.put(video_bytes)
                        elif data.get("type") == "end":
                            logger.info("Received end signal from client")
                    except json.JSONDecodeError:
                        logger.error("Invalid JSON message received")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")

            # Task to process and send audio to Gemini via ADK
            async def process_and_send_audio():
                while True:
                    try:
                        data = await audio_queue.get()
                        
                        # Send the audio data to Gemini through ADK
                        live_request_queue.send_realtime(
                            types.Blob(
                                data=data,
                                mime_type=f"audio/pcm;rate={SEND_SAMPLE_RATE}",
                            )
                        )
                        
                        audio_queue.task_done()
                    except Exception as e:
                        logger.error(f"Error processing audio: {e}")

            # Task to process and send video frames to Gemini via ADK
            async def process_and_send_video():
                while True:
                    try:
                        video_bytes = await video_queue.get()
                        
                        # Send the video frame to Gemini through ADK
                        live_request_queue.send_realtime(
                            types.Blob(
                                data=video_bytes,
                                mime_type="image/jpeg",
                            )
                        )
                        
                        video_queue.task_done()
                    except Exception as e:
                        logger.error(f"Error processing video: {e}")

            # Task to receive and process responses from ADK
            async def receive_and_process_responses():
                try:
                    # Start the agent run
                    async for response in runner.run(
                        input=live_request_queue,
                        session=session,
                        config=run_config,
                    ):
                        # Handle different response types
                        if hasattr(response, 'server_content') and response.server_content:
                            server_content = response.server_content
                            
                            # Handle audio responses
                            if hasattr(server_content, 'model_turn') and server_content.model_turn:
                                for part in server_content.model_turn.parts:
                                    if hasattr(part, 'inline_data') and part.inline_data:
                                        # Send audio back to client
                                        audio_data = part.inline_data.data
                                        await websocket.send(json.dumps({
                                            'type': 'audio',
                                            'audio': base64.b64encode(audio_data).decode()
                                        }))
                                    
                                    if hasattr(part, 'text') and part.text:
                                        # Send text transcript
                                        logger.info(f"AI Response: {part.text}")
                                        await websocket.send(json.dumps({
                                            'type': 'transcript',
                                            'text': part.text
                                        }))
                            
                            # Handle turn complete
                            if hasattr(server_content, 'turn_complete') and server_content.turn_complete:
                                logger.debug("Turn complete")
                                
                except Exception as e:
                    logger.error(f"Error in response processing: {e}")

            # Start all tasks
            tg.create_task(handle_websocket_messages())
            tg.create_task(process_and_send_audio())
            tg.create_task(process_and_send_video())
            tg.create_task(receive_and_process_responses())

    async def start(self):
        """Start the WebSocket server."""
        logger.info(f"Starting Cymbal Auto Insurance ADK server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"Server started successfully on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever


async def main():
    """Main entry point."""
    server = InsuranceADKServer(host="0.0.0.0", port=WEBSOCKET_PORT)
    await server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
