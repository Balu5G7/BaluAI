# JARVIS AI Assistant

Welcome to the JARVIS AI project. This repository contains the source code for an advanced, cross-platform personal AI assistant utilizing a Python backend (PC Server) and a Flutter mobile application (Remote Interface).

---

## Architecture Overview

The system architecture is divided into two primary components:

1. **`jarvis_pc/` (Core Server):** A Python-based FastAPI server responsible for handling speech-to-text processing, LLM integration (Claude/Gemini/Ollama), automated PC operations, and WebSocket communication.
2. **`jarvis_mobile/` (Remote Application):** A Flutter application that establishes a WebSocket connection with the PC server. It provides a real-time HUD (Heads-Up Display) for system telemetry, voice command execution, and chat history.

---

## Core Features

- **Wake Word Activation:** Implements continuous background listening to detect the designated wake word ("Hey Jarvis").
- **Natural Language Processing:** Integrates with advanced Large Language Models for context-aware conversational capabilities.
- **Biometric Security:** Utilizes DeepFace facial recognition to authenticate the owner and restrict unauthorized access.
- **System Automation:** Executes local system commands including application management, file operations, power state controls, and web queries.
- **Remote Telemetry & Control:** Supports remote operations and system status monitoring via an integrated Telegram bot.
- **Automated Deployment:** Includes scripts for seamless integration with Windows Startup.

---

## Prerequisites

Ensure the following dependencies are installed prior to deployment:
- **Python 3.10 or higher** (Required for the backend server)
- **Flutter SDK** (Required for compiling the mobile application)
- **Android Studio** (Required for Android device deployment and APK generation)

---

## Installation & Deployment Guide

### Part 1: Configuring the PC Server

1. **Initialize the Server Environment:**
   Navigate to the backend directory:
   ```bash
   cd jarvis_pc
   ```

2. **Establish the Virtual Environment:**
   ```bash
   python -m venv venv
   ```
   Activate the environment:
   - On Windows: `.\venv\Scripts\activate`
   - On Mac/Linux: `source venv/bin/activate`

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   - Duplicate the `.env.example` file and rename it to `.env`.
   - Populate the file with the required API keys (e.g., ElevenLabs, Gemini, Telegram Bot Token).

5. **Initialize the Application:**
   ```bash
   python main.py
   ```
   The server will initialize the FastAPI instance and commence background listening.

### Part 2: Compiling the Mobile Application

1. **Navigate to the Application Directory:**
   ```bash
   cd jarvis_mobile
   ```

2. **Resolve Dependencies:**
   ```bash
   flutter pub get
   ```

3. **Compile the Android Package (APK):**
   ```bash
   flutter build apk --release
   ```
   *Note: If the Flutter CLI is not recognized in the system path, open the `jarvis_mobile` directory using Android Studio and compile via `Build > Build Bundle(s) / APK(s) > Build APK(s)`.*

4. **Deploy to Device:** 
   Transfer and install the generated APK file on the target Android device.
5. **Establish Connection:** 
   Launch the application and input the host PC's local IP address (e.g., `192.168.1.5`) and configured port (`8765`) to initiate the WebSocket link.

---

## Operational Guidelines

- **Local Voice Activation:** Speak the wake word in proximity to the host machine's microphone to trigger the command listener.
- **Remote Application Control:** Use the mobile application's microphone interface to dispatch commands over the local network.
- **External Remote Control:** Utilize the configured Telegram bot to issue commands and receive status updates remotely over the internet.
