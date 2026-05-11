FRIDAY – AI Voice Assistant

FRIDAY is a real-time AI-powered voice assistant inspired by futuristic virtual assistants like the one from Iron Man. The project combines speech recognition, natural language understanding, intelligent responses, and voice synthesis to create a smooth conversational AI experience.

The assistant is capable of understanding voice input, processing requests using modern large language models, executing tools/functions, and responding naturally with synthesized speech.

Features
Real-time conversational AI assistant
Voice input using Speech-to-Text (STT)
Natural AI-generated responses
Human-like voice synthesis using Text-to-Speech (TTS)
Function/tool calling support
Weather information integration
LiveKit RTC integration
Groq LLM integration
Intelligent conversational memory and personality prompts
Custom assistant persona (FRIDAY)
Low-latency voice interaction
Extensible architecture for future AI tools
Tech Stack
Languages
Python
AI / LLM
Groq API
Llama 3.3 70B Versatile
Voice Technologies
Deepgram (Speech-to-Text)
Cartesia Sonic TTS
Silero Voice Activity Detection
Realtime Communication
LiveKit Agents Framework
LiveKit Cloud
Environment & Utilities
Python Virtual Environment (venv)
dotenv
requests
Project Structure
Project_JARVIS/
│
├── agent.py
├── prompt.py
├── tools.py
├── requirements.txt
├── .env
├── .gitignore
└── venv/
How It Works
User speaks into the microphone.
Deepgram converts speech into text.
The text is processed by the Groq LLM.
The assistant generates a contextual response.
Cartesia converts the response into natural speech.
LiveKit manages the real-time communication session.
Function tools can be triggered dynamically for tasks like weather lookup.
Installation & Setup
1. Clone the Repository
git clone https://github.com/SaumayAshish/AI-Assistant-FRIDAY.git
cd AI-Assistant-FRIDAY
2. Create Virtual Environment
python -m venv venv

Activate virtual environment:

Windows
.\venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
4. Configure Environment Variables

Create a .env file in the project root.

Example:

LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret


GROQ_API_KEY=your_groq_api_key


DEEPGRAM_API_KEY=your_deepgram_api_key


CARTESIA_API_KEY=your_cartesia_api_key
Running the Project
Start the Assistant
python agent.py dev
Example Commands
“What is the weather in Delhi?”
“Introduce yourself.”
“Who created you?”
“Tell me a joke.”
“What can you do?”
Assistant Personality

FRIDAY is designed to:

Speak naturally and intelligently
Respond concisely
Maintain a futuristic AI personality
Be slightly witty and conversational
Act as a smart personal assistant
Future Enhancements
Computer vision integration
Screen understanding
Webcam-based interaction
Local automation support
Smart home integration
Calendar and productivity tools
Multimodal AI capabilities
Mobile app integration
Persistent memory system
Screenshots

Add screenshots of:

LiveKit console
Voice interaction
Assistant responses
Project architecture

inside an assets/ folder.

Author
Saumay Ashish
GitHub: https://github.com/SaumayAshish
LinkedIn: https://www.linkedin.com/in/saumay-ashish
License

This project is intended for educational, research, and portfolio purposes.
