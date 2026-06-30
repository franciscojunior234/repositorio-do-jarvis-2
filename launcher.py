#!/usr/bin/env python3
"""Launcher automatico do JARVIS."""

import shutil
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
API_SCRIPT = BASE_DIR / "api_server.py"
FRONTEND_URL = "http://localhost:5173"
API_URL = "http://127.0.0.1:8765"


def start_api_server():
    print("Iniciando servidor Python API...")

    if not API_SCRIPT.exists():
        print(f"Erro: API nao encontrada em {API_SCRIPT}")
        return None

    try:
        process = subprocess.Popen(
            [sys.executable, str(API_SCRIPT)],
            cwd=str(BASE_DIR),
        )
    except Exception as error:
        print(f"Erro ao iniciar servidor Python: {error}")
        return None

    print(f"Servidor Python iniciado em {API_URL}")
    return process


def start_frontend():
    print("Iniciando servidor Frontend (Vite)...")

    if not FRONTEND_DIR.exists():
        print(f"Erro: pasta frontend nao encontrada em {FRONTEND_DIR}")
        return None

    npm_cmd = find_npm()
    if not npm_cmd:
        print("Erro: npm nao encontrado. Instale o Node.js para iniciar sua interface React.")
        print("Download: https://nodejs.org/")
        return None

    try:
        node_cmd = find_node(npm_cmd)
        vite_script = FRONTEND_DIR / "node_modules" / "vite" / "bin" / "vite.js"
        env = os.environ.copy()
        npm_bin_dir = str(Path(npm_cmd).resolve().parent)
        env["PATH"] = npm_bin_dir + os.pathsep + env.get("PATH", "")

        if node_cmd and vite_script.exists():
            command = [node_cmd, str(vite_script), "--host", "127.0.0.1"]
        else:
            command = [npm_cmd, "run", "dev", "--", "--host", "127.0.0.1"]

        process = subprocess.Popen(
            command,
            cwd=str(FRONTEND_DIR),
            env=env,
        )
    except Exception as error:
        print(f"Erro ao iniciar frontend: {error}")
        return None

    print(f"Frontend iniciado em {FRONTEND_URL}")
    return process


def find_npm():
    npm_cmd = shutil.which("npm.cmd") or shutil.which("npm")
    if npm_cmd:
        return npm_cmd

    local_app_data = Path.home() / "AppData" / "Local"
    codex_runtime_dir = local_app_data / "OpenAI" / "Codex" / "runtimes"
    if codex_runtime_dir.exists():
        matches = list(codex_runtime_dir.glob("**/bin/npm.cmd"))
        if matches:
            return str(matches[0])

    return None


def find_node(npm_cmd):
    node_cmd = shutil.which("node.exe") or shutil.which("node")
    if node_cmd:
        return node_cmd

    npm_bin_dir = Path(npm_cmd).resolve().parent
    candidate = npm_bin_dir / "node.exe"
    if candidate.exists():
        return str(candidate)

    return None


def open_browser():
    print(f"Abrindo navegador em {FRONTEND_URL}...")

    try:
        # Tenta abrir usando o Google Chrome registrado no sistema
        chrome = webbrowser.get("chrome")
        chrome.open(FRONTEND_URL)
    except Exception:
        # Caso falhe, tenta localizar nos caminhos comuns de instalação do Chrome no Windows
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        opened = False
        for path in chrome_paths:
            if os.path.exists(path):
                try:
                    subprocess.Popen([path, FRONTEND_URL])
                    opened = True
                    break
                except Exception:
                    pass
        
        if not opened:
            # Fallback para o navegador padrão do sistema se o Chrome não estiver disponível
            try:
                webbrowser.open(FRONTEND_URL)
            except Exception as error:
                print(f"Nao consegui abrir o navegador automaticamente: {error}")
                print(f"Acesse manualmente: {FRONTEND_URL}")


def main():
    print("=" * 58)
    print("JARVIS - inicializacao automatica")
    print("=" * 58)

    processes = []

    api_process = start_api_server()
    if api_process:
        processes.append(api_process)

    frontend_process = start_frontend()
    if frontend_process:
        processes.append(frontend_process)

    time.sleep(3)

    if frontend_process:
        open_browser()

    if not processes:
        print("Nenhum servico foi iniciado. Corrija os erros acima e tente novamente.")
        return 1

    print()
    print("Sistema iniciado.")
    print(f"API: {API_URL}/api/status")
    print(f"Frontend: {FRONTEND_URL}")
    print("Pressione Ctrl+C para encerrar.")

    try:
        while True:
            for process in list(processes):
                if process.poll() is not None:
                    print(f"Processo encerrado com codigo {process.returncode}.")
                    processes.remove(process)

            if not processes:
                print("Todos os servicos foram encerrados.")
                return 1

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDesligando JARVIS...")
        for process in processes:
            process.terminate()
        return 0


if __name__ == "__main__":
    sys.exit(main())
