import pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 160)  # Slightly faster for quick playback
def play_word(word):
    engine.say(word)
    engine.runAndWait()  # Plays instantly
play_word("")  # Near-zero latency