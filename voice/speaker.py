from gtts import gTTS
import pygame
import os

def speak(text):
    print(f"🤖 zara (Tamil): {text}")
    tts = gTTS(text=text, lang='ta')
    tts.save("voice.mp3")

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("voice.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

    pygame.mixer.quit()
    os.remove("voice.mp3")
