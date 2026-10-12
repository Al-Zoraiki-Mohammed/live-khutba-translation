# Live Khutba AI Translation System

A real-time, AI-powered transcription and translation system designed for Friday Khutbas in mosques. It listens to the live audio feed, detects natural speech pauses using Voice Activity Detection (VAD), transcribes Arabic speech accurately using OpenAI Whisper, translates it into professional English using GPT-4o-mini (maintaining strict rules for Quranic verses and Hadith references), and streams it instantly to a sleek, large-format web interface meant for mosque display screens alongside prayer timetable software (like Mawaqit).

---

## 🎯 The Problem & Solution

* **The Problem:** Non-Arabic speaking congregants, youth, and new Muslims often struggle to follow the Friday Khutba, missing out on crucial reminders, Quranic explanations, and Islamic teachings.
* **The Solution:** This application hooks into the mosque's audio system, processes the live speech locally via Python, and renders a live, cinema-quality typing transcription feed on a browser screen with zero manual intervention required by mosque volunteers.

---

## 📂 Project Architecture

```text
Live-khutba-translator/
├── backend/
│   └── app.py          # Main backend (PyAudio, Silero VAD, OpenAI API, WebSockets)
├── frontend/
│   └── index.html      # Real-time WebSocket display interface (Kiosk optimized)
├── pyproject.toml        # Project dependencies managed via uv
├── run_khutba.bat        # Single-click automation script for Windows
└── run_khutba.sh         # Single-click automation script for Linux / macOS
```

## ⚙️ Prerequisites
1. Python 3.10 or higher installed on the host machine.
2. uv package manager installed (Astral uv docs):
    - Windows (PowerShell):
       - To install uv on Windows, run this command:

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

    - Linux / macOS:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

3. OpenAI API Key with access to Whisper and GPT-4o models.

## 🔑 Configuration
1. Clone or copy the project folder onto the mosque computer.
2. Inside your project root, create a `.env` file inside the `backend/` folder (or root depending on your loader):

   ```text
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

## 🚀 Running the Project
### Option A: Fully Automated Single-Click (Recommended for Mosque Staff)
We have provided single-click scripts that automatically spin up the uv environment, start the backend WebSocket server on port 8765, launch your default browser into full-screen kiosk mode pointing to index.html, and can auto-shutdown after a designated duration (e.g., 45 minutes of Khutba time).
### 🪟 For Windows (run_khutba.bat)
Simply double-click run_khutba.bat from your project folder.

### 🐧🍎 For Linux / macOS (run_khutba.sh)
    1. Make the script executable once:

   ```bash
   chmod +x run_khutba.sh
   ```

2. Double-click or run from terminal:

   ```bash
   ./run_khutba.sh
   ```

### Option B: Manual Execution (For Development & Testing)
If you prefer running components manually in separate terminal windows:
1. Sync dependencies and start the backend server:

 ```bash
  uv run python backend/app.py
  ```
 This boots up the WebSocket server on ws://localhost:8765 and initializes the PyAudio stream.
 
2. Open the frontend display:
- Double-click frontend/index.html to open it directly in any modern browser or map it to your secondary display screen next to your prayer timetable display.
