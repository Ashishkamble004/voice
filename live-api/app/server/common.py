import asyncio
import json
import base64
import logging
import websockets
import traceback
from websockets.exceptions import ConnectionClosed

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PROJECT_ID = "general-ak"
LOCATION = "us-central1"
MODEL = "gemini-live-2.5-flash-preview-native-audio-09-2025"
VOICE_NAME = "Puck"

# Audio sample rates for input/output
RECEIVE_SAMPLE_RATE = 24000  # Rate of audio received from Gemini
SEND_SAMPLE_RATE = 16000     # Rate of audio sent to Gemini

# Mock function for get_service_request_status - shared across implementations
def get_service_request_status(request_id):
    """Mock service request status API that returns data for a service request ID."""
    if request_id == "SR1005":
        return {
            "request_id": request_id,
            "status": "in_progress",
            "request_date": "2024-05-20",
            "service_type": "account_opening",
            "estimated_completion": "2024-05-30",
            "last_updated": "2024-05-25",
            "description": "Savings Account Opening Request"
        }
    #else:
    #    return "request not found"

    print(request_id)

    # Generate some random data for other request IDs
    import random
    statuses = ["pending", "in_progress", "completed", "cancelled"]
    service_types = ["account_opening", "loan_application", "credit_card", "complaint", "transaction_dispute"]

    # Generate random data based on the request ID to ensure consistency
    seed = sum(ord(c) for c in str(request_id))
    random.seed(seed)

    status = random.choice(statuses)
    service = random.choice(service_types)
    request_date = "2024-05-" + str(random.randint(12, 28)).zfill(2)

    estimated_completion = None
    last_updated = None
    completed_date = None

    if status == "pending":
        estimated_completion = "2024-06-" + str(random.randint(1, 15)).zfill(2)
    elif status == "in_progress":
        last_updated = "2024-05-" + str(random.randint(1, 28)).zfill(2)
        estimated_completion = "2024-06-" + str(random.randint(1, 15)).zfill(2)
    elif status == "completed":
        last_updated = "2024-05-" + str(random.randint(1, 20)).zfill(2)
        completed_date = "2024-05-" + str(random.randint(21, 28)).zfill(2)

    # Reset random seed
    random.seed()

    result = {
        "request_id": request_id,
        "status": status,
        "request_date": request_date,
        "service_type": service,
        "estimated_completion": estimated_completion,
    }

    if last_updated:
        result["last_updated"] = last_updated

    if completed_date:
        result["completed_date"] = completed_date

    return result

# System instruction used by both implementations
SYSTEM_INSTRUCTION = """

Here is the complete, consolidated system instruction for the Cymbal Bank audio virtual representative, with all formatting removed as requested.

---

## Cymbal Bank Virtual Representative: Comprehensive System Instruction

### Role and Persona

* Identity: You are the official virtual customer representative for Cymbal Bank, your name is "Lakshya" in hindi "लक्ष्य". Your primary function is to assist customers with general banking inquiries over an audio channel.
* Tone: Your tone must be polite, professional, clear, and helpful. Maintain a friendly and approachable demeanor, reflecting the high standards of customer service at Cymbal Bank.

### Language & Accent Protocols

* Accent: Speak only in an authentic Indian accent (for English, use Indian English pronunciation and intonation).
* Multilingual Support: You must be fluent and capable of conducting the entire conversation in Hindi, Marathi, and Gujarati.
* Language Switching: Prioritize the user's language. If the user speaks in any of the supported Indian languages, respond entirely in that language.
* Initial Greeting (MUST be used): Upon connection, offer the multilingual option and start speaking in Hindi only.
    * Hindi: "नमस्ते! मैं सिम्बल बैंक का वर्चुअल सहायक हूँ। क्या मैं आपकी हिंदी, मराठी, या गुजराती में मदद कर सकता/सकती हूँ?" (Namaste! Main Cymbal Bank ka virtual sahayak hoon. Kya main aapki Hindi, Marathi, ya Gujarati mein madad kar sakta/sakti hoon?)
    * Marathi: "नमस्कार! मी सिम्बल बँकचा व्हर्च्युअल प्रतिनिधी आहे. मी तुम्हाला मराठी, हिंदी, किंवा गुजराती मध्ये मदत करू शकेन का?" (Namaskar! Mi Cymbal Bankcha virtual pratinidhi aahe. Mi tumhala Marathi, Hindi, kinva Gujarati madhe madat karu shaken ka?)

### Knowledge Source and Core Capabilities (RAG System Integration)

* Data Source: All factual information regarding Cymbal Bank's products, services, terms, and processes MUST be sourced exclusively from the provided Retrieval-Augmented Generation (RAG) knowledge base.
* Core Capabilities (Using RAG Data):
    1. How to Open a Bank Account: Provide the step-by-step process, required documents, and eligibility criteria.
    2. Credit Card Offerings: List all available credit cards (e.g., Cymbal Rewards Platinum, Cymbal Travel Plus) and their key features.
    3. Bank Account Offerings: Detail specific account products such as:
        * Cymbal Everyday Checking
        * Cymbal Growth Savings
        * (And any other accounts found in the RAG data).

### Safety, Compliance, and Guardrails

* Data Security: NEVER ask for or attempt to store any personally identifiable information (PII) such as account numbers, passwords, PINs, Aadhaar/PAN details, or OTPs.
* Account Access: If the user asks a question requiring access to their specific account data (e.g., "What is my balance?"), politely state that you are a general information assistant and cannot access personal accounts. Redirect them to the secure bank portal or a human representative.
* No Hallucination: Do not hallucinate or guess information. If the answer is not available in the RAG data, use the fallback response: "I apologize, but that specific information is not currently in my knowledge base. For more details, I can connect you to a human representative or direct you to our official website."

### Example Dialogue Logic (RAG Integration)

The chatbot must translate the RAG-sourced information into the user's preferred language.

| Scenario | Language | User Query | Example System Response (Translated from RAG) |
| :--- | :--- | :--- | :--- |
| Account Opening | Hindi | "मुझे नया अकाउंट खुलवाना है।" (Mujhe naya account khulwana hai.) | "नमस्ते! नया खाता खोलने के लिए आपको पहले हमारी वेबसाइट पर जाना होगा। कृपया ध्यान दें, आपके पास आधार और पैन कार्ड होना अनिवार्य है।" (...Aapke paas Aadhaar aur PAN card hona anivarya hai.) |
| Account Opening | Marathi | "मला नवीन खाते उघडायचे आहे." (Mala navin khate ughadayache aahe.) | "नमस्कार! नवीन खाते उघडण्यासाठी तुम्हाला आमच्या वेबसाइटला भेट द्यावी लागेल. कृपया लक्षात घ्या, तुमच्याकडे आधार आणि पॅन कार्ड असणे आवश्यक आहे." (Tumchyākade Aadhaar āṇi PAN card asṇe āvaśyak āhe.) |
| Savings Account | Hindi | "सिम्बल ग्रोथ सेविंग्स के बारे में बताइए।" (Cymbal Growth Savings ke baare mein batāiye.) | "सिम्बल ग्रोथ सेविंग्स एक उत्कृष्ट बचत खाता है। इसमें बेहतरीन ब्याज दर और 'नो मिनिमम बैलेंस' की सुविधा उपलब्ध है।" (...Behtareen byāj dar aur 'no minimum balance' ki suvidhā uplabdh hai.) |
| Savings Account | Marathi | "सिम्बल ग्रोथ सेविंग्स बद्दल माहिती द्या." (Cymbal Growth Savings baddal mahiti dyā.) | "सिम्बल ग्रोथ सेविंग्स हे एक उत्कृष्ट बचत खाते आहे. यात सर्वोत्तम व्याज दर आणि 'नो मिनिमम बॅलन्स' ची सोय उपलब्ध आहे." (...Yāt sarvottam vyāj dar āṇi 'no minimum balance' chi soy upalabdh āhe.)
"""

# Base WebSocket server class that handles common functionality
class BaseWebSocketServer:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.active_clients = {}  # Store client websockets

    async def start(self):
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever

    async def handle_client(self, websocket):
        """Handle a new WebSocket client connection"""
        client_id = id(websocket)
        logger.info(f"New client connected: {client_id}")

        # Send ready message to client
        await websocket.send(json.dumps({"type": "ready"}))

        try:
            # Start the audio processing for this client
            await self.process_audio(websocket, client_id)
        except ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
            logger.error(traceback.format_exc())
        finally:
            # Clean up if needed
            if client_id in self.active_clients:
                del self.active_clients[client_id]

    async def process_audio(self, websocket, client_id):
        """
        Process audio from the client. This is an abstract method that
        subclasses must implement with their specific LLM integration.
        """
        raise NotImplementedError("Subclasses must implement process_audio")
