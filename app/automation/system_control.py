import webbrowser
import subprocess
import os


def open_application(app_name):

    try:

        os.system(f"start {app_name}")

        return f"Abrindo {app_name}."

    except:

        return None


def execute_command(command):

    command = command.lower()

    # =========================
    # ABRIR SITES
    # =========================

    if "youtube" in command:

        webbrowser.open(
            "https://youtube.com"
        )

        return "Abrindo YouTube."

    if "google" in command:

        webbrowser.open(
            "https://google.com"
        )

        return "Abrindo Google."

    if "chatgpt" in command:

        webbrowser.open(
            "https://chat.openai.com"
        )

        return "Abrindo ChatGPT."

    # =========================
    # PESQUISA GOOGLE
    # =========================

    if "pesquise" in command:

        search = command.replace(
            "pesquise",
            ""
        ).strip()

        webbrowser.open(
            f"https://www.google.com/search?q={search}"
        )

        return f"Pesquisando {search}."

    # =========================
    # ABRIR PROGRAMAS
    # =========================

    if "abra" in command:

        app_name = command.replace(
            "abra",
            ""
        ).strip()

        response = open_application(
            app_name
        )

        return response

    if "abrir" in command:

        app_name = command.replace(
            "abrir",
            ""
        ).strip()

        response = open_application(
            app_name
        )

        return response

    # =========================
    # WINDOWS
    # =========================

    if "calculadora" in command:

        os.system("calc")

        return "Abrindo calculadora."

    if "bloco de notas" in command:

        os.system("notepad")

        return "Abrindo bloco de notas."

    if "explorador de arquivos" in command:

        os.system("explorer")

        return "Abrindo explorador."

    return None 