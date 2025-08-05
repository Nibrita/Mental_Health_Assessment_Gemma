# Voice Bot Project

This is a demo project for a voice-enabled mental health chatbot using FastAPI and OpenAI.
# Voice-Enabled PHQ-9 Mental Health Assistant

A multilingual, voice-capable chatbot for mental health self-assessment based on the PHQ-9 questionnaire.  
Supports Bangla and English conversations with empathetic voice replies, powered by **Gemma 3n**, **FastAPI**, and open-source voice tools.

[View Full Project Report (Google Doc)](https://docs.google.com/document/d/1kfWjKB05gqbQSdX4Ep7T6VNGSQgcwyWUT9FtlnCCNTk/edit?tab=t.0)


---

## Features

- PHQ-9 depression self-screening with conversational, kind support  
- Multilingual input and output: Bangla and English text & voice  
- Bangla TTS via Coqui, English voice via browser SpeechSynthesis API  
- Local LLM-powered empathetic responses using Gemma 3n (via Ollama)  
- Runs offline-friendly, preserving user privacy

---

## How to Run the Project (Django + FastAPI)

This project runs two servers simultaneously:

### 1. Django Server (Frontend)

In the first terminal, activate your environment if needed, then run:

```bash
python manage.py runserver
````

Access the Django frontend at:
`http://127.0.0.1:8000`

---

### 2. FastAPI Voice Bot Server

Open a **second terminal** and do the following:

* Activate your Poetry environment:

```bash
poetry shell
```

* Install dependencies (if not done yet):

```bash
poetry install
pip install TTS
```

* Run FastAPI with uvicorn on port 8001:

```bash
uvicorn app:app --reload --port 8001
```

The FastAPI voice bot API will be available at:
`http://127.0.0.1:8001`

---

## Usage

* Interact with the voice bot through the Django frontend
* Speak or type in Bangla or English
* Receive text and voice replies in the same language
* Bot conducts PHQ-9 assessment and responds empathetically

---

## Tech Stack

* Django — main backend and frontend server
* FastAPI + Uvicorn — voice bot API server
* LangChain + Ollama — Gemma 3n LLM integration
* Coqui TTS — Bangla text-to-speech
* Browser SpeechSynthesis API — English text-to-speech
* Faster-Whisper — speech-to-text for voice input
* HTML/JS — frontend UI




## Disclaimer

This tool is for mental health self-assessment and support only — not a replacement for professional diagnosis or treatment. Seek professional help if in distress.

---


