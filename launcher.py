#!/usr/bin/env python3
"""
JARVIS Unified Launcher
Inicia o backend Python e o frontend React em um único comando.
Aguarda pelo wake word "Olá, Jarvis" para ativar o sistema.
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent.parent if Path(__file__).parent.name == "JARVIS-IA" else Path(__file__).parent
JARVIS_IA_DIR = BASE_DIR / "JARVIS-IA"
FRONTEND_DIR = BASE_DIR / "frontend"

def start_api_server():
    """Inicia o servidor Python API."""
    print("🚀 Iniciando servidor Python API...")
    os.chdir(JARVIS_IA_DIR)
    
    try:
        # Herda stdout/stderr para ver os logs
        subprocess.Popen(
            [sys.executable, "api_server.py"],
            stdout=None,
            stderr=None
        )
        time.sleep(2)  # Aguarda servidor iniciar
        print("✅ Servidor Python iniciado em http://127.0.0.1:8765")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor Python: {e}")

def start_frontend():
    """Inicia o servidor Vite do frontend."""
    print("🚀 Iniciando servidor Frontend (Vite)...")
    os.chdir(FRONTEND_DIR)
    
    try:
        # No Windows, usa npm.cmd
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        
        # Herda stdout/stderr para ver os logs
        subprocess.Popen(
            [npm_cmd, "run", "dev"],
            shell=True,
            stdout=None,
            stderr=None
        )
        time.sleep(3)  # Aguarda servidor iniciar
        print("✅ Frontend iniciado em http://localhost:5173")
    except Exception as e:
        print(f"❌ Erro ao iniciar frontend: {e}")
        print("   Tente iniciar manualmente: cd frontend && npm run dev")

def open_browser():
    """Abre o navegador Chrome com o frontend."""
    print("🌐 Abrindo navegador Chrome...")
    time.sleep(3)  # Aguarda o servidor iniciar
    
    try:
        webbrowser.get('windows-default').open('http://localhost:5173')
    except:
        try:
            webbrowser.open('http://localhost:5173')
        except Exception as e:
            print(f"⚠️  Erro ao abrir navegador: {e}")
            print("   Acesse manualmente: http://localhost:5173")

def main():
    """Inicia todos os serviços."""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║         🤖 JARVIS - Sistema Unificado 🤖             ║
    ║                                                       ║
    ║  Diga "Olá, Jarvis" para ativar o assistente         ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    # Inicia os serviços em threads
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    
    api_thread.start()
    frontend_thread.start()
    browser_thread.start()
    
    print("\n⏳ Aguardando inicialização dos serviços...")
    time.sleep(5)
    
    print("\n✨ Sistema pronto! Diga 'Olá, Jarvis' para começar...")
    print("   Para sair, diga 'desligar' ou feche o programa.")
    
    # Mantém o programa rodando
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Desligando JARVIS...")
        sys.exit(0)

if __name__ == "__main__":
    main()
