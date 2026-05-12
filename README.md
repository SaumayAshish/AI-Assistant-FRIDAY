# FRIDAY – AI Voice Assistant

FRIDAY is a real-time AI-powered voice assistant inspired by futuristic virtual assistants like the one from Iron Man. The project combines speech recognition, natural language understanding, intelligent responses, live information retrieval, and voice synthesis to create a smooth conversational AI experience.

The assistant is capable of understanding voice input, processing requests using modern large language models, executing tools/functions, retrieving real-time information, and responding naturally with synthesized speech.

---

# Features

- Real-time conversational AI assistant
- Voice input using Speech-to-Text (STT)
- Natural AI-generated responses
- Human-like voice synthesis using Text-to-Speech (TTS)
- Function/tool calling support
- Real-time weather information integration
- Spotify integration and playback control
- Stock market news retrieval
- Global and Indian headline news support
- Live news integration using NewsAPI
- LiveKit RTC integration
- Groq LLM integration
- Intelligent conversational memory and personality prompts
- Custom assistant persona (FRIDAY)
- Low-latency voice interaction
- Extensible architecture for future AI tools

---

# Tech Stack

## Languages

- Python

## AI / LLM

- Groq API
- Llama 3.3 70B Versatile

## Voice Technologies

- Deepgram (Speech-to-Text)
- Cartesia Sonic TTS
- Silero Voice Activity Detection

## Realtime Communication

- LiveKit Agents Framework
- LiveKit Cloud

## APIs & Integrations

- Spotify Web API
- NewsAPI.org
- Weather API Integration

## Environment & Utilities

- Python Virtual Environment (venv)
- dotenv
- requests
- spotipy

---

# Project Structure

```bash
Project_JARVIS/
│
├── agent.py
├── prompt.py
├── tools.py
├── requirements.txt
├── .env
├── .gitignore
├── assets/
└── venv/
```

---

# How It Works

1. User speaks into the microphone.
2. Deepgram converts speech into text.
3. The text is processed by the Groq LLM.
4. FRIDAY determines whether tools/functions are required.
5. APIs are triggered dynamically for tasks like:
   - Weather updates
   - Spotify playback/search
   - Stock market news
   - Global and Indian news headlines
6. The assistant generates a contextual response.
7. Cartesia converts the response into natural speech.
8. LiveKit manages the real-time communication session.

---

# Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/SaumayAshish/AI-Assistant-FRIDAY.git
cd AI-Assistant-FRIDAY
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate virtual environment:

### Windows

```bash
.\venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

GROQ_API_KEY=your_groq_api_key

DEEPGRAM_API_KEY=your_deepgram_api_key

CARTESIA_API_KEY=your_cartesia_api_key

NEWS_API_KEY=your_newsapi_key

SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

---

# Running the Project

## Start the Assistant

```bash
python agent.py dev
```

---

# Example Commands

### General

- “Introduce yourself.”
- “Who created you?”
- “Tell me a joke.”
- “What can you do?”

### Weather

- “What is the weather in Delhi?”

### Spotify

- “Play Blinding Lights on Spotify.”
- “Pause the music.”
- “Play my liked songs.”

### News

- “Tell me the latest stock market news.”
- “Give me top global headlines.”
- “What’s happening in India today?”

---

# Assistant Personality

FRIDAY is designed to:

- Speak naturally and intelligently
- Respond concisely
- Maintain a futuristic AI personality
- Be slightly witty and conversational
- Act as a smart personal assistant

---

# Future Enhancements

- Computer vision integration
- Screen understanding
- Webcam-based interaction
- Local automation support
- Smart home integration
- Calendar and productivity tools
- Multimodal AI capabilities
- Mobile app integration
- Persistent memory system

---

# Screenshots

Add screenshots of:

- LiveKit console
- Voice interaction
- Assistant responses
- Spotify integration
- News retrieval
- Project architecture

inside an `assets/` folder.

---

# Author

## Saumay Ashish

- GitHub: https://github.com/SaumayAshish
- LinkedIn: https://www.linkedin.com/in/saumay-ashish

---

# License

This project is intended for educational, research, and portfolio purposes.
