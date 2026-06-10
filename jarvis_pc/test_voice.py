import asyncio
import edge_tts

async def speak(text):
    communicate = edge_tts.Communicate(
        text,
        voice="en-US-GuyNeural"
    )
    await communicate.save("jarvis.mp3")

asyncio.run(speak("Hello Balu. I am Jarvis."))
