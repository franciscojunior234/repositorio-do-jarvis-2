import sys
import threading

from PyQt6.QtWidgets import QApplication

from app.voice.speak import speak
from app.voice.listen import listen
from app.brain.ai_engine import ask_jarvis
from app.interface.jarvis_ui import JarvisUI
from app.automation.system_control import execute_command

from app.memory.memory_manager import (
    remember_information,
    recall_information
)


WAKE_WORDS = [
    "jarvis",
    "friday",
    "computer"
]


def clean_command(command):

    for word in WAKE_WORDS:

        command = command.replace(
            word,
            ""
        )

    return command.strip()


def assistant_loop():

    speak("Sistema Jarvis iniciado.")

    while True:

        command = listen()

        if not command:
            continue

        print(f"Comando detectado: {command}")

        # DESLIGAR
        if "desligar" in command:

            speak("Encerrando sistema.")

            sys.exit()

        # WAKE WORD
        if any(
            word in command
            for word in WAKE_WORDS
        ):

            cleaned_command = clean_command(
                command
            )

            print(
                f"Comando limpo: {cleaned_command}"
            )

            try:

                # MEMÓRIA
                memory_response = remember_information(
                    cleaned_command
                )

                if memory_response:

                    speak(memory_response)

                    continue

                recall_response = recall_information(
                    cleaned_command
                )

                if recall_response:

                    speak(recall_response)

                    continue

                # AUTOMAÇÃO
                automation_response = execute_command(
                    cleaned_command
                )

                if automation_response:

                    speak(automation_response)

                    continue

                # IA
                from app.memory.memory_manager import build_ai_context, load_memory
                from api_server import with_salutation, build_salutation

                context = build_ai_context(cleaned_command)
                response = ask_jarvis(
                    cleaned_command,
                    context=context
                )

                memory = load_memory()
                user_name = memory.get("profile", {}).get("nome", "")
                salutation = build_salutation(user_name)

                final_response = with_salutation(response, salutation)
                speak(final_response)

            except Exception as error:

                print(f"Erro: {error}")

                speak(
                    "Desculpe senhor, ocorreu um erro no sistema."
                )


def main():

    assistant_thread = threading.Thread(
        target=assistant_loop,
        daemon=True
    )

    assistant_thread.start()

    app = QApplication(sys.argv)

    window = JarvisUI()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":

    main() 