import pyttsx3

engine = pyttsx3.init()

engine.setProperty("rate", 180)

voices = engine.getProperty("voices")

if len(voices) > 0:
    engine.setProperty("voice", voices[0].id)

def speak(text):

    print(f"\nJarvis: {text}\n")

    engine.say(text)

    engine.runAndWait() 