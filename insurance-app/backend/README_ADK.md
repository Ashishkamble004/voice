# Cymbal Auto Insurance - ADK Implementation

This is an Agent Development Kit (ADK) based implementation of the Cymbal Auto Insurance vehicle damage claims assistant.

## What is ADK?

The Google Agent Development Kit (ADK) is a framework for building AI agents with Google's Gemini models. It provides:

- **Agent Management**: Structured way to define agents with instructions and tools
- **Session Management**: Built-in session handling for stateful conversations
- **Streaming Support**: Bidirectional streaming for real-time interactions
- **Tool Integration**: Easy integration of custom tools and RAG (Retrieval-Augmented Generation)

## Differences from Standard Implementation

### Standard Implementation (`server.py`)
- Direct WebSocket and Gemini Live API integration
- Manual session and state management
- Custom audio/video processing
- Lower-level control over API calls

### ADK Implementation (`server_adk.py`)
- Uses ADK Agent framework
- Built-in session management via `InMemorySessionService`
- Structured agent definition with `Agent` class
- `Runner` handles execution and streaming
- `LiveRequestQueue` for real-time input
- Better suited for adding tools and RAG retrieval

## Key ADK Components

### 1. Agent Definition
```python
self.agent = Agent(
    name="insurance_claims_agent",
    model=GEMINI_MODEL,
    instruction=INSURANCE_SYSTEM_INSTRUCTION,
    tools=[],  # Custom tools can be added here
)
```

### 2. Session Management
```python
self.session_service = InMemorySessionService()
session = await self.session_service.create_session(
    app_name="cymbal_auto_insurance",
    user_id=f"user_{client_id}",
    session_id=f"session_{client_id}",
)
```

### 3. Runner and Config
```python
runner = Runner(
    app_name="cymbal_auto_insurance",
    agent=self.agent,
    session_service=self.session_service,
)

run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    speech_config=types.SpeechConfig(...),
    response_modalities=["AUDIO"],
)
```

### 4. Live Request Queue
```python
live_request_queue = LiveRequestQueue()
live_request_queue.send_realtime(
    types.Blob(data=audio_bytes, mime_type="audio/pcm;rate=16000")
)
```

## Running the ADK Server

### Prerequisites
Same as standard implementation:
- Python 3.9+
- Google Cloud Project with Vertex AI enabled
- Required Python packages (see `requirements.txt`)

### Start the Server
```bash
cd insurance-app/backend

# Set environment variables
export GOOGLE_CLOUD_PROJECT=general-ak
export GOOGLE_CLOUD_LOCATION=us-central1

# Authenticate
gcloud auth application-default login

# Run ADK server
python server_adk.py
```

The ADK server will start on port 8765 (or `WEBSOCKET_PORT` if set).

## Frontend Compatibility

The ADK backend is **fully compatible** with the existing React frontend. No changes needed to the frontend code - it uses the same WebSocket protocol and message format.

```javascript
// Frontend connects the same way
const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8765';
```

## Adding Custom Tools (ADK Feature)

One advantage of ADK is easy tool integration. Example:

```python
def get_claim_status(claim_id: str) -> dict:
    """Get the status of an insurance claim."""
    # Implementation here
    return {"status": "pending", "claim_id": claim_id}

# Add to agent
self.agent = Agent(
    name="insurance_claims_agent",
    model=GEMINI_MODEL,
    instruction=INSURANCE_SYSTEM_INSTRUCTION,
    tools=[get_claim_status],  # Tools automatically available to agent
)
```

## Adding RAG Retrieval (ADK Feature)

ADK makes it easy to add knowledge bases:

```python
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

insurance_docs = VertexAiRagRetrieval(
    name="retrieve_insurance_docs",
    description="Retrieve insurance policy documents and guidelines",
    rag_resources=[
        rag.RagResource(
            rag_corpus="projects/general-ak/locations/us-central1/ragCorpora/YOUR_CORPUS_ID"
        )
    ],
    similarity_top_k=5,
)

# Add to agent tools
self.agent = Agent(
    name="insurance_claims_agent",
    model=GEMINI_MODEL,
    instruction=INSURANCE_SYSTEM_INSTRUCTION,
    tools=[insurance_docs],
)
```

## Cloud Run Deployment

The ADK version can be deployed the same way as the standard version:

```bash
# Deploy backend
cd insurance-app/backend
gcloud builds submit --config=cloudbuild.yaml

# The Dockerfile and cloudbuild.yaml work for both server.py and server_adk.py
# Just update CMD in Dockerfile to: CMD ["python", "server_adk.py"]
```

## When to Use ADK vs Standard

### Use ADK When:
- ✅ You need to add custom tools
- ✅ You want RAG retrieval from knowledge bases
- ✅ You need structured agent management
- ✅ You want built-in session handling
- ✅ You're building complex multi-agent systems

### Use Standard When:
- ✅ You need maximum control over API calls
- ✅ You want minimal dependencies
- ✅ You need custom audio processing
- ✅ You prefer direct WebSocket/API integration

## Architecture Comparison

### Standard Implementation
```
React Frontend
    ↓ WebSocket
Python WebSocket Server
    ↓ Direct API calls
Gemini Live API
```

### ADK Implementation
```
React Frontend
    ↓ WebSocket
Python WebSocket Server
    ↓ ADK Components
    ├── Agent (instructions + tools)
    ├── Runner (execution)
    ├── Session Service
    └── LiveRequestQueue
        ↓
Gemini Live API
```

## Performance

Both implementations have similar performance:
- **Latency**: ~same (ADK adds minimal overhead)
- **Memory**: ADK uses slightly more for session management
- **Scalability**: Both scale horizontally on Cloud Run

## Testing

Test the ADK server the same way as the standard server:

```bash
# Start frontend
cd insurance-app
npm start

# In another terminal, start ADK backend
cd insurance-app/backend
python server_adk.py

# Open http://localhost:3000 and test
```

## Troubleshooting

### ADK Import Errors
```bash
pip install google-adk
```

### Session Errors
ADK manages sessions automatically. If you get session errors, check:
- Session service is initialized
- Unique session IDs per client
- Sessions are properly closed on disconnect

### Tool Errors
If custom tools aren't working:
- Check function signatures match ADK requirements
- Tools need proper docstrings for agent understanding
- Verify tool is added to agent's tools list

## Learn More

- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/agent-builder)
- [Gemini Live API Docs](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
- [ADK GitHub Examples](https://github.com/googleapis/python-genai)

## Summary

The ADK implementation provides a more structured approach to building AI agents with Gemini, especially useful when you need:
- Custom tools
- RAG retrieval
- Complex agent workflows
- Better session management

Both implementations are production-ready and serve the same frontend. Choose based on your needs!
