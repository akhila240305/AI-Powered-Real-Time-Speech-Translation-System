from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import whisper
from gtts import gTTS
from deep_translator import GoogleTranslator
import subprocess
import os
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD = "uploads"
OUTPUT = "outputs"
os.makedirs(UPLOAD, exist_ok=True)
os.makedirs(OUTPUT, exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

print("Loading Whisper small model...")
model = whisper.load_model("small.en")
print("Whisper ready.")

def to_wav(input_path, wav_path):
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ac", "1",
            "-ar", "16000",
            wav_path
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def youtube_to_wav(url, wav_path):
    subprocess.run(
        ["yt-dlp", "-x", "--audio-format", "wav", "-o", wav_path, url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

@app.post("/translate")
async def translate(
    input_type: str = Form(...),     
    file: UploadFile = File(None),
    youtube_url: str = Form(None),
    src_lang: str = Form("hi"),
    target_lang: str = Form("en")
):
    print(">>> /translate called")

    uid = str(uuid.uuid4())
    raw = f"{UPLOAD}/{uid}_raw"
    wav = f"{UPLOAD}/{uid}.wav"

    if input_type in ["mic", "audio", "video"]:
        ext = os.path.splitext(file.filename)[1]
        raw += ext
        with open(raw, "wb") as f:
            f.write(await file.read())
        to_wav(raw, wav)

    elif input_type == "youtube":
        youtube_to_wav(youtube_url, wav)

    else:
        return {"error": "Invalid input type"}
    result = model.transcribe(wav, language=src_lang)
    text = result["text"]

    translated = GoogleTranslator(
        source=src_lang,
        target=target_lang
    ).translate(text)

    mp3 = f"{OUTPUT}/{uid}.mp3"
    gTTS(translated, lang=target_lang).save(mp3)

    return {
        "detected_text": text,
        "translated_text": translated,
        "audio_file": mp3
    }
