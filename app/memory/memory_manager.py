import json
import os


MEMORY_FILE = "memory.json"


def load_memory():

    if not os.path.exists(MEMORY_FILE):

        with open(MEMORY_FILE, "w") as file:

            json.dump({}, file)

    with open(MEMORY_FILE, "r") as file:

        return json.load(file)


def save_memory(memory):

    with open(MEMORY_FILE, "w") as file:

        json.dump(memory, file, indent=4)


def remember_information(command):

    memory = load_memory()

    command = command.lower()

    if "meu nome é" in command:

        name = command.split(
            "meu nome é"
        )[-1].strip()

        memory["nome"] = name

        save_memory(memory)

        return (
            f"Entendido senhor. "
            f"Vou lembrar que seu nome é {name}."
        )

    return None


def recall_information(command):

    memory = load_memory()

    command = command.lower()

    if "qual meu nome" in command:

        if "nome" in memory:

            return (
                f"Seu nome é "
                f"{memory['nome']}."
            )

        else:

            return (
                "Ainda não sei seu nome senhor."
            )

    return None 