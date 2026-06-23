import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


HOST = "127.0.0.1"
PORT = 8765


def process_command(message):
    command = (message or "").strip()

    if not command:
        return {
            "response": "Digite ou fale um comando para eu executar.",
            "source": "system",
        }

    try:
        from app.memory.memory_manager import recall_information, remember_information

        memory_response = remember_information(command)
        if memory_response:
            return {"response": memory_response, "source": "memory"}

        recall_response = recall_information(command)
        if recall_response:
            return {"response": recall_response, "source": "memory"}
    except Exception as error:
        print(f"Erro no modulo de memoria: {error}")

    try:
        from app.automation.system_control import execute_command

        automation_response = execute_command(command)
        if automation_response:
            return {"response": automation_response, "source": "automation"}
    except Exception as error:
        print(f"Erro no modulo de automacao: {error}")

    try:
        from app.brain.ai_engine import ask_jarvis

        return {"response": ask_jarvis(command), "source": "ai"}
    except Exception as error:
        print(f"Erro no modulo de IA: {error}")
        return {
            "response": (
                "Nao consegui acessar a IA agora. Verifique as dependencias Python "
                "e a variavel GROQ_API_KEY."
            ),
            "source": "error",
        }


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

            result = process_command(transcript)
            speak_if_requested(result["response"], payload.get("speak", True))
            self._send_json(200, {"transcript": transcript, **result})
            return

        result = process_command(payload.get("message", ""))
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
