# 🧠 JARVIS AI Assistant

Welcome to the **JARVIS AI** project! This is an advanced, cross-platform personal AI assistant built with a Python backend (PC Brain) and a Flutter mobile application (Remote Control).

---

## ✨ Features

- **Wake Word Detection:** Continuously listens for "Hey Jarvis" to activate.
- **Natural Conversation:** Powered by advanced LLMs (Claude/Gemini/Ollama) for deep contextual understanding.
- **Facial Security:** Uses DeepFace to recognize the owner and lock out unauthorized users.
- **System Control:** Can open/close apps, shutdown, sleep, take screenshots, and manage files on the PC.
- **Telegram Integration:** Remote control and notifications via a Telegram bot.
- **Sci-Fi Mobile App:** A stunning Flutter-based mobile HUD to view PC status, send commands, and talk to Jarvis remotely via WebSockets.
- **Auto-Startup:** Configured to start automatically when Windows boots.

---

## 🏗️ Architecture

The project is split into two main components:

1. **`jarvis_pc/` (The Brain):** A Python FastApi server that handles speech-to-text, LLM processing, PC automation, and WebSocket broadcasting.
2. **`jarvis_mobile/` (The Remote):** A Flutter app that connects to the PC server. It features an Iron Man style UI with voice waveform visualizers, real-time PC metrics (CPU/RAM), and a chat interface.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.10+** (For the PC server)
- **Flutter SDK** (For building the Mobile App)
- **Android Studio** (For deploying the app to your phone)

---

## 🚀 Setup Instructions

### Part 1: Setting up the PC Server (Brain)

1. **Navigate to the PC folder:**
   ```bash
   cd jarvis_pc
   ```

2. **Create a Virtual Environment & Install Dependencies:**
   ```bash
   python -m venv venv
   # Activate the virtual environment
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   - Copy `.env.example` to `.env`.
   - Add your API keys (e.g., ElevenLabs, Gemini, Claude, Telegram Bot Token).

4. **Run JARVIS:**
   ```bash
   python main.py
   ```
   *JARVIS will now be listening for his wake word!*

### Part 2: Setting up the Mobile App

1. **Navigate to the Mobile folder:**
   ```bash
   cd jarvis_mobile
   ```

2. **Get Flutter Packages:**
   ```bash
   flutter pub get
   ```

3. **Build the Android App (APK):**
   ```bash
   flutter build apk --release
   ```
   *Note: If you get a 'flutter not found' error, open the `jarvis_mobile` folder in **Android Studio** and build the APK via `Build > Build Bundle(s) / APK(s) > Build APK(s)`.*

4. **Install the APK on your Android Phone.**
5. **Open the App:** Enter your PC's local IP address (e.g., `192.168.1.5`) and the default port (`8765`) to establish the connection!

---

## 💡 Usage

- **Voice Command:** Say "Hey Jarvis" near your PC to wake it up, then give your command.
- **Mobile Control:** Tap the mic button on the mobile app to send a command remotely.
- **Telegram:** Message your connected Telegram bot to execute commands when you are away from home.

Enjoy your very own intelligent assistant! 🚀
