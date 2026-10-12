import asyncio
import os
import ssl
import tempfile
import wave
import numpy as np
import pyaudio
import torch
from dotenv import load_dotenv
from openai import OpenAI
import websockets

# Bypass SSL certificate verification for PyTorch hub downloads on macOS
ssl._create_default_https_context = ssl._create_unverified_context

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Silero VAD expects 16kHz
CHUNK = 512   # Frame size for Silero (512 samples = 32ms)

# VAD Parameters
SILENCE_THRESHOLD_MS = 800   # 800ms of silence signals the end of a sentence
MIN_SPEECH_DURATION_MS = 1500 # Ignore sounds/coughing shorter than 1.5 seconds
MAX_SPEECH_DURATION_S = 20   # Safety cutoff for continuous speaking without pause

# Load Silero VAD Model locally
print("📦 Loading Silero VAD model...")
model_vad, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=False,
    trust_repo=True
)
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

connected_clients = set()

async def register(websocket):
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)

async def broadcast_text(text):
    if connected_clients:
        await asyncio.gather(*[c.send(text) for c in connected_clients])

def save_frames_to_wav(frames, rate, sample_size):
    """Saves raw audio frames to a temporary WAV file."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_filename = temp_file.name
    temp_file.close()

    wf = wave.open(temp_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(sample_size)
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    return temp_filename

async def process_and_translate(audio_path):
    """Transcribes Arabic audio via Whisper and translates via GPT-4o-mini."""
    try:
        loop = asyncio.get_running_loop()

        def sync_api_calls():
            with open(audio_path, "rb") as audio_file:
                # 1. Transcribe Arabic audio accurately
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ar",
                    response_format="text"
                )
            
            arabic_text = transcript.strip()
            
            # Reject short noise or Whisper hallucinations
            if len(arabic_text) < 5 or any(h in arabic_text.lower() for h in ["subscribe", "channel"]):
                return None

            # 2. Translate Arabic to professional English
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
            "You are an expert Islamic translator for Friday Khutbas. "
            "Translate the following Arabic speech into clear, natural English. "
            "Output only the direct translation without extra commentary. "
            "If you do not understand a part of the Arabic source, simply skip it; do not guess or ask for clarification. "
            "Never output canned assistant phrases like 'Subscribe to the channel' or apologetic refusal messages like 'I cannot assist with that'. "
            "If the input audio is empty, unclear, or consists only of silence or background noise, output nothing at all. "
            "Please translate all Quranic verses using the 'Saheeh International' translation, and use the official Darussalam English translation style for any Hadith references."
        )
                    },
                    {"role": "user", "content": arabic_text}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()

        translated_text = await loop.run_in_executor(None, sync_api_calls)

        if translated_text:
            print(f"✨ Translation: {translated_text}")
            await broadcast_text(translated_text)

    except Exception as e:
        print(f"API Error: {e}")
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

async def audio_processing_loop():
    """Listens continuously and uses VAD to slice audio strictly at speech pauses."""
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)

    print("🎤 Listening... Speak in full sentences (VAD Active).")

    frames_buffer = []
    speaking = False
    silence_start_time = None
    speech_start_time = None

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames_buffer.append(data)

            audio_int16 = np.frombuffer(data, dtype=np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
            tensor_chunk = torch.from_numpy(audio_float32)

            speech_prob = model_vad(tensor_chunk, RATE).item()
            now = asyncio.get_event_loop().time()

            if speech_prob > 0.5:
                if not speaking:
                    speaking = True
                    speech_start_time = now
                    print("🗣️ Speech started...")
                silence_start_time = None
            else:
                if speaking:
                    if silence_start_time is None:
                        silence_start_time = now

                    silence_duration_ms = (now - silence_start_time) * 1000
                    speech_duration_ms = (now - speech_start_time) * 1000

                    if silence_duration_ms >= SILENCE_THRESHOLD_MS or speech_duration_ms >= (MAX_SPEECH_DURATION_S * 1000):
                        if speech_duration_ms >= MIN_SPEECH_DURATION_MS:
                            print(f"⏸️ Natural pause detected ({int(speech_duration_ms)}ms sentence). Processing...")
                            wav_path = save_frames_to_wav(frames_buffer, RATE, p.get_sample_size(FORMAT))
                            asyncio.create_task(process_and_translate(wav_path))

                        frames_buffer = []
                        speaking = False
                        silence_start_time = None

            await asyncio.sleep(0.001)

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

async def main():
    server = await websockets.serve(register, "localhost", 8765)
    print("🚀 WebSocket server started on ws://localhost:8765")
    await audio_processing_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down live translation service.")