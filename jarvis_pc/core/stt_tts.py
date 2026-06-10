import speech_recognition as sr
import os
import pygame
import keyboard
from gui import set_animation_state

os.environ.setdefault('SDL_AUDIODRIVER', 'directsound')

try:
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    print("[Audio] pygame mixer initialized successfully.")
except Exception as e:
    print(f"[Audio Warning] pygame mixer init failed: {e}. Audio will be skipped.")
    pygame.mixer = None


def speak(text: str):
    print(f"JARVIS: {text}")
    set_animation_state("speaking")

    try:
        voice = "en-US-GuyNeural"
        audio_file = "temp_speech.mp3"
        safe_text = text.replace('"', '\\"')
        
        elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
        
        if elevenlabs_key:
            import requests
            # Using 'George' voice ID which sounds like a British Butler
            voice_id = "JBFqnCBsd6RMkjVDRZzb" 
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": elevenlabs_key
            }
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            }
            res = requests.post(url, json=data, headers=headers)
            if res.status_code == 200:
                with open(audio_file, 'wb') as f:
                    f.write(res.content)
            else:
                print(f"[TTS] ElevenLabs failed ({res.status_code}), falling back to Edge-TTS")
                os.system(f'edge-tts --voice {voice} --text "{safe_text}" --write-media {audio_file}')
        else:
            os.system(f'edge-tts --voice {voice} --text "{safe_text}" --write-media {audio_file}')

        if pygame.mixer is None:
            try:
                os.environ['SDL_AUDIODRIVER'] = 'directsound'
                pygame.mixer.pre_init(44100, -16, 2, 2048)
                pygame.mixer.init()
                print("[Audio] Mixer re-initialized successfully.")
            except Exception as retry_e:
                print(f"[Audio] Retry failed: {retry_e}")

        if pygame.mixer is None:
            print("[Audio] Mixer not available, skipping playback.")
        else:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():

                if keyboard.is_pressed('esc'):
                    pygame.mixer.music.stop()
                    print("[Speech Interrupted by ESC key]")
                    break

                pygame.time.Clock().tick(30)

            pygame.mixer.music.unload()

        try:
            os.remove(audio_file)
        except:
            pass

    except Exception as e:
        print("TTS Error:", e)

    set_animation_state("idle")


def listen_for_command() -> str:
    recognizer = sr.Recognizer()

    recognizer.energy_threshold = 400
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8

    try:
        with sr.Microphone() as source:
            print("Listening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.7
            )

            audio = recognizer.listen(
                source,
                timeout=7,
                phrase_time_limit=10
            )

            with open("temp.wav", "wb") as f:
                f.write(audio.get_wav_data())

            print("Processing...")

            text = recognizer.recognize_google(
                audio,
                language="en-IN"
            )

            print(f"You: {text}")

            return text.lower()

    except sr.WaitTimeoutError:
        print("[STT] Timeout — no speech detected within 7 seconds.")
        return ""

    except sr.UnknownValueError:
        print("[STT] Could not understand the audio.")
        return ""

    except sr.RequestError as e:
        print(f"[STT] Google Speech API error: {e}")
        return ""

    except Exception as e:
        print(f"[STT] Microphone error: {e}")
        return ""