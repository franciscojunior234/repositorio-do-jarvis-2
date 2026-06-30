import json
import os
import re
import shutil
import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import quote_plus

import requests


IOT_FILE = "iot_devices.json"

SITE_ALIASES = {
    "youtube": "https://youtube.com",
    "google": "https://google.com",
    "chatgpt": "https://chat.openai.com",
    "gmail": "https://mail.google.com",
    "whatsapp": "https://web.whatsapp.com",
    "instagram": "https://instagram.com",
    "facebook": "https://facebook.com",
    "github": "https://github.com",
    "netflix": "https://netflix.com",
    "tiktok": "https://tiktok.com",
    "x": "https://x.com",
    "twitter": "https://x.com",
    "linkedin": "https://linkedin.com",
    "canva": "https://canva.com",
}

CHROME_CANDIDATES = [
    "chrome.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

APP_ALIASES = {
    "calculadora": "calc.exe",
    "bloco de notas": "notepad.exe",
    "notepad": "notepad.exe",
    "explorador": "explorer.exe",
    "explorador de arquivos": "explorer.exe",
    "paint": "mspaint.exe",
    "prompt": "cmd.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "terminal": "wt.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
}


def execute_command(command):
    command = (command or "").strip()
    command_lower = command.lower()

    iot_response = execute_iot_command(command_lower)
    if iot_response:
        return iot_response

    search_target = extract_search_target(command)
    if search_target:
        webbrowser.open(f"https://www.google.com/search?q={quote_plus(search_target)}")
        return f"Pesquisando {search_target}."

    open_target = extract_open_target(command)
    if open_target:
        return open_anything(open_target)

    return None


def extract_search_target(command):
    match = re.search(r"^(pesquise|pesquisar|procure|buscar)\s+(.+)$", command, re.IGNORECASE)
    if match:
        return clean_target(match.group(2))
    return None


def extract_open_target(command):
    match = re.search(
        r"^(abra|abrir|abre|inicie|iniciar|execute|executar)\s+(.+)$",
        command,
        re.IGNORECASE,
    )
    if match:
        return clean_target(match.group(2))
    return None


def open_anything(target):
    target = clean_target(target)
    target_lower = target.lower()

    app_response = open_application(target)
    if app_response:
        return app_response

    site_url = resolve_site(target_lower, target)
    open_url_in_chrome(site_url)
    return f"Nao encontrei {target} instalado. Abrindo no Chrome."


def resolve_site(target_lower, target):
    if target_lower in SITE_ALIASES:
        return SITE_ALIASES[target_lower]

    if target_lower.startswith(("http://", "https://")):
        return target

    if target_lower.startswith("www."):
        return f"https://{target}"

    if looks_like_domain(target_lower):
        return f"https://{target}"

    if " " not in target_lower and "." not in target_lower:
        return f"https://{target_lower}.com"

    return f"https://www.google.com/search?q={quote_plus(target)}"


def open_url_in_chrome(url):
    chrome = find_chrome()
    if chrome:
        subprocess.Popen([chrome, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True

    webbrowser.open(url)
    return False


def find_chrome():
    for candidate in CHROME_CANDIDATES:
        resolved = shutil.which(candidate) or candidate
        if Path(resolved).exists():
            return str(resolved)

    local_app_data = os.environ.get("LocalAppData")
    if local_app_data:
        candidate = Path(local_app_data) / "Google" / "Chrome" / "Application" / "chrome.exe"
        if candidate.exists():
            return str(candidate)

    return None


def open_application(app_name):
    alias = APP_ALIASES.get(app_name.lower())
    if alias and launch_executable(alias):
        return f"Abrindo {app_name}."

    shortcut = find_start_menu_shortcut(app_name)
    if shortcut:
        os.startfile(shortcut)
        return f"Abrindo {shortcut.stem}."

    executable = find_executable(app_name)
    if executable and launch_executable(str(executable)):
        return f"Abrindo {app_name}."

    executable = find_installed_executable(app_name)
    if executable and launch_executable(str(executable)):
        return f"Abrindo {executable.stem}."

    return None


def launch_executable(command):
    executable = shutil.which(command) or command
    try:
        subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False


def find_executable(app_name):
    candidates = candidate_executable_names(app_name)
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return Path(resolved)
    return None


def find_start_menu_shortcut(app_name):
    start_dirs = [
        Path(os.environ.get("ProgramData", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path(os.environ.get("AppData", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    ]

    best_match = None
    best_score = 0
    query = normalize_name(app_name)

    for start_dir in [path for path in start_dirs if path.exists()]:
        for shortcut in start_dir.rglob("*.lnk"):
            score = match_score(query, normalize_name(shortcut.stem))
            if score > best_score:
                best_match = shortcut
                best_score = score

    return best_match if best_score >= 2 else None


def find_installed_executable(app_name):
    roots = [
        Path(os.environ.get("ProgramFiles", "")),
        Path(os.environ.get("ProgramFiles(x86)", "")),
        Path(os.environ.get("LocalAppData", "")) / "Programs",
    ]

    query = normalize_name(app_name)
    best_match = None
    best_score = 0

    for root in [path for path in roots if path.exists()]:
        for executable in root.glob("*/*.exe"):
            score = max(
                match_score(query, normalize_name(executable.stem)),
                match_score(query, normalize_name(executable.parent.name)),
            )
            if score > best_score:
                best_match = executable
                best_score = score

    return best_match if best_score >= 2 else None


def candidate_executable_names(app_name):
    normalized = normalize_name(app_name)
    compact = normalized.replace(" ", "")
    underscored = normalized.replace(" ", "_")
    dashed = normalized.replace(" ", "-")
    names = {normalized, compact, underscored, dashed}
    return [name if name.endswith(".exe") else f"{name}.exe" for name in names]


def looks_like_domain(value):
    return bool(re.match(r"^[a-z0-9][a-z0-9.-]+\.[a-z]{2,}(/.*)?$", value))


def clean_target(value):
    return re.sub(r"\s+", " ", value.strip().strip(".!?,;:"))


def normalize_name(value):
    value = clean_target(value).lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return clean_target(value)


def match_score(query, candidate):
    if not query or not candidate:
        return 0

    if query == candidate:
        return 4

    if query in candidate:
        return 3

    query_words = set(query.split())
    candidate_words = set(candidate.split())
    return len(query_words & candidate_words)


def execute_iot_command(command):
    if not any(word in command for word in ["luz", "lampada", "tomada", "ar condicionado", "iot"]):
        return None

    action = None
    if any(word in command for word in ["ligar", "acender", "ativar"]):
        action = "on"
    elif any(word in command for word in ["desligar", "apagar", "desativar"]):
        action = "off"

    if not action:
        return None

    devices = load_iot_devices()
    matched_name, device = find_iot_device(command, devices)

    if not device:
        return (
            "Ainda nao encontrei esse dispositivo IoT configurado. "
            "Adicione ele no arquivo iot_devices.json."
        )

    url = device.get(action)
    if not url:
        return f"O dispositivo {matched_name} nao tem acao {action} configurada."

    try:
        response = requests.post(url, timeout=5)
        if response.status_code >= 400:
            return f"Tentei controlar {matched_name}, mas o dispositivo respondeu com erro."
        return f"Pronto, {matched_name} foi {'ligado' if action == 'on' else 'desligado'}."
    except requests.RequestException:
        return f"Nao consegui conectar ao dispositivo {matched_name} agora."


def load_iot_devices():
    if not os.path.exists(IOT_FILE):
        return {}

    try:
        with open(IOT_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def find_iot_device(command, devices):
    for name, device in devices.items():
        aliases = [name] + device.get("aliases", [])
        if any(alias.lower() in command for alias in aliases):
            return name, device
    return None, None
