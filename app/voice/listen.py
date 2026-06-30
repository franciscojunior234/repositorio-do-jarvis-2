import speech_recognition as sr

recognizer = sr.Recognizer()

def listen():

    with sr.Microphone() as source:

        print("Ouvindo...")

        recognizer.adjust_for_ambient_noise(source)

        audio = recognizer.listen(source)

    try:

        command = recognizer.recognize_google(
            audio,
            language="pt-BR"
        )

        print(f"Você: {command}")

        return command.lower()

    except:

        return "" 