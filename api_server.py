import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


HOST = "127.0.0.1"
PORT = 8765


def process_command(message, user_name=None):
    command = (message or "").strip()
    salutation = build_salutation(user_name)

    if not command:
        return {
            "response": with_salutation(
                "Digite ou fale um comando para eu executar.",
                salutation,
            ),
            "source": "system",
        }

    creator_response = answer_creator_question(command, salutation)
    if creator_response:
        return {"response": creator_response, "source": "system"}

    try:
        from app.memory.memory_manager import (
            build_ai_context,
            recall_information,
            record_interaction,
            remember_information,
        )

        record_interaction(command)

        memory_response = remember_information(command)
        if memory_response:
            return {"response": with_salutation(memory_response, salutation), "source": "memory"}

        recall_response = recall_information(command)
        if recall_response:
            return {"response": with_salutation(recall_response, salutation), "source": "memory"}
    except Exception as error:
        print(f"Erro no modulo de memoria: {error}")

    try:
        from app.automation.system_control import execute_command

        automation_response = execute_command(command)
        if automation_response:
            return {
                "response": with_salutation(automation_response, salutation),
                "source": "automation",
            }
    except Exception as error:
        print(f"Erro no modulo de automacao: {error}")

    try:
        from app.brain.ai_engine import ask_jarvis

        context = build_ai_context(command, user_name=user_name)
        response = ask_jarvis(command, context=context)
        return {"response": with_salutation(response, salutation), "source": "ai"}
    except Exception as error:
        print(f"Erro no modulo de IA: {error}")
        return {
            "response": with_salutation(
                (
                    "Nao consegui acessar a IA agora. Verifique as dependencias Python "
                    "e a variavel GROQ_API_KEY."
                ),
                salutation,
            ),
            "source": "error",
        }


def build_salutation(user_name):
    clean_name = (user_name or "").strip()
    if not clean_name:
        return "Sr"

    first_name = clean_name.split()[0].strip()
    return f"Sr {first_name}" if first_name else "Sr"


def with_salutation(response, salutation):
    response = (response or "").strip()
    if not response:
        return salutation

    response_lower = response.lower()
    salutation_lower = salutation.lower()

    if response_lower.startswith(salutation_lower):
        return response

    return f"{salutation}, {response[0].lower()}{response[1:]}"


def answer_creator_question(command, salutation):
    command_lower = command.lower()
    creator_terms = [
        "seu criador",
        "quem te criou",
        "quem criou voce",
        "quem criou você",
        "quem e seu criador",
        "quem é seu criador",
        "criador do jarvis",
    ]

    if any(term in command_lower for term in creator_terms):
        return with_salutation("fui criado pelo Sr Junior.", salutation)

    return None


def speak_if_requested(text, enabled):
    if not enabled:
        return

    try:
        from app.voice.speak import speak

        speak(text)
    except Exception as error:
        print(f"Erro ao falar resposta: {error}")


class JarvisRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(204, {})

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/status":
            self._send_json(
                200,
                {
                    "status": "online",
                    "service": "jarvis-api",
                    "host": HOST,
                    "port": PORT,
                },
            )
            return

        self._send_json(404, {"error": "Rota nao encontrada."})

    def do_POST(self):
        path = urlparse(self.path).path

        if path not in {"/api/chat", "/api/listen"}:
            self._send_json(404, {"error": "Rota nao encontrada."})
            return

        payload = self._read_json_body()

        if path == "/api/listen":
            try:
                from app.voice.listen import listen

                transcript = listen()
            except Exception as error:
                self._send_json(
                    500,
                    {"error": f"Nao consegui acessar o microfone: {error}"},
                )
                return

            result = process_command(transcript, payload.get("user_name"))
            speak_if_requested(result["response"], payload.get("speak", True))
            self._send_json(200, {"transcript": transcript, **result})
            return

        result = process_command(payload.get("message", ""), payload.get("user_name"))
        speak_if_requested(result["response"], payload.get("speak", False))
        self._send_json(200, result)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length == 0:
            return {}

        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw_body)
        except json.JSONDecodeError:
            return {}

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


def main():
    server = ThreadingHTTPServer((HOST, PORT), JarvisRequestHandler)
    print(f"API online em http://{HOST}:{PORT}")
    print(f"Status: http://{HOST}:{PORT}/api/status")
    server.serve_forever()


if __name__ == "__main__":
    main()
