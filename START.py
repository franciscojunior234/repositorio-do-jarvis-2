"""
Batch script para iniciar JARVIS facilmente
Executa launcher.py e gerencia os processos
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Inicia JARVIS através do launcher"""
    
    # Caminho do diretório JARVIS DIA2
    jarvis_dia2 = Path(__file__).parent
    
    print("="*50)
    print("🤖 Iniciando JARVIS...")
    print("="*50)
    print()
    
    # Verifica se tem as variáveis de ambiente necessárias
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("⚠️  AVISO: GROQ_API_KEY não está configurada")
        print()
        print("Para usar a IA avançada, configure a variável de ambiente:")
        print()
        print("  Windows (PowerShell):")
        print("  $env:GROQ_API_KEY = 'sua-chave-aqui'")
        print()
        print("  Windows (CMD):")
        print("  set GROQ_API_KEY=sua-chave-aqui")
        print()
    
    # Inicia o launcher
    launcher_script = jarvis_dia2 / "launcher.py"
    
    print(f"Executando: {launcher_script}")
    print()
    
    try:
        subprocess.run(
            [sys.executable, str(launcher_script)],
            cwd=str(jarvis_dia2)
        )
    except KeyboardInterrupt:
        print("\n\n✅ JARVIS encerrado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao executar JARVIS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
