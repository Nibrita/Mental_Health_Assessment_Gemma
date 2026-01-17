from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from ollama import Client
from faster_whisper import WhisperModel
from phq9_session import PHQ9Session
import os
import tempfile
import uuid
import torch
from TTS.api import TTS
import re

load_dotenv()

app = FastAPI()
ollama_client = Client()
phq9_session = PHQ9Session()

# Load Whisper once
model = WhisperModel("medium", compute_type="int8", device="cpu")

# Load Coqui TTS once with the Bangla female model
device = "cuda" if torch.cuda.is_available() else "cpu"
tts_model_name = 'tts_models/bn/custom/vits-female'  # Replaced with the female model
tts = TTS(model_name=tts_model_name).to(device)

os.makedirs("tts_audio", exist_ok=True)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend and audio
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/tts_audio", StaticFiles(directory="tts_audio"), name="tts_audio")

class UserInput(BaseModel):
    user_response: str

@app.get("/")
async def root():
    return FileResponse("static/upload.html")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio.write(await file.read())
            temp_path = temp_audio.name

        segments, _ = model.transcribe(temp_path, language="bn")
        transcript = " ".join([segment.text for segment in segments])
        return {"transcript": transcript}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

def detect_and_respond(text):
    if phq9_session.started:  # If PHQ-9 session is started, do not call Ollama
        return None  # This ensures no Ollama response is triggered during PHQ-9 questions
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are a friendly mental health assistant. "
                "If the user seems sad, anxious, or overwhelmed, gently guide them through a PHQ-9 assessment. "
                "Otherwise, chat naturally like a supportive friend."
            )
        },
        {"role": "user", "content": text}
    ]
    response = ollama_client.chat(model="gemma3n:e2b", messages=messages)
    return response['message']['content']

def is_bangla(text: str) -> bool:
    return bool(re.search(r'[\u0980-\u09FF]', text))

def generate_tts_audio(text: str) -> str:
    filename = f"{uuid.uuid4()}.wav"
    filepath = os.path.join("tts_audio", filename)
    tts.tts_to_file(text=text, file_path=filepath)
    return f"/tts_audio/{filename}"

@app.post("/phq")
async def phq(input: UserInput):
    user_text = input.user_response.strip().lower()

    # If user says "start the assessment", start the PHQ-9 session
    if user_text in ["start", "start the assessment"] or phq9_session.started:
        result = phq9_session.process_response(user_text)
        bot_msg = result["bot_message"]
    else:
        # If PHQ-9 has not started, use Ollama for conversation
        bot_msg = detect_and_respond(user_text)
    
    if is_bangla(bot_msg):
        audio_url = generate_tts_audio(bot_msg)
        return {
            "response": bot_msg,
            "audio_url": audio_url,
            "use_browser_tts": False,
            "interrupted": result.get("interrupted", False) if 'result' in locals() else False
        }
    else:
        return {
            "response": bot_msg,
            "use_browser_tts": True,
            "interrupted": result.get("interrupted", False) if 'result' in locals() else False
        }

@app.post("/phq/reset")
async def phq_reset():
    phq9_session.reset()
    return {"status": "reset"}


