import json
import os
import re
from datetime import datetime


MEMORY_FILE = "memory.json"

DEFAULT_MEMORY = {
    "profile": {},
    "preferences": {},
    "facts": {},
    "mood_history": [],
    "interaction_count": 0,
}

MOOD_KEYWORDS = {
    "feliz": ["feliz", "animado", "otimo", "boa", "legal", "show", "perfeito"],
    "triste": ["triste", "mal", "chateado", "desanimado", "sozinho"],
    "irritado": ["irritado", "raiva", "bravo", "nervoso", "estressado"],
    "ansioso": ["ansioso", "preocupado", "medo", "inseguro", "tenso"],
    "cansado": ["cansado", "exausto", "sono", "esgotado"],
}


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        save_memory(DEFAULT_MEMORY.copy())

    with open(MEMORY_FILE, "r", encoding="utf-8") as file:
        try:
            memory = json.load(file)
        except json.JSONDecodeError:
            memory = DEFAULT_MEMORY.copy()

    return normalize_memory(memory)


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4, ensure_ascii=False)


def normalize_memory(memory):
    normalized = DEFAULT_MEMORY.copy()
    normalized.update(memory or {})

    for key in ["profile", "preferences", "facts"]:
        if not isinstance(normalized.get(key), dict):
            normalized[key] = {}

    if not isinstance(normalized.get("mood_history"), list):
        normalized["mood_history"] = []

    if not isinstance(normalized.get("interaction_count"), int):
        normalized["interaction_count"] = 0

    return normalized


def remember_information(command):
    memory = load_memory()
    original_command = command.strip()
    command_lower = original_command.lower()

    name = extract_after_patterns(
        original_command,
        [
            r"\bmeu nome e\s+(.+)",
            r"\bme chamo\s+(.+)",
            r"\bpode me chamar de\s+(.+)",
        ],
    )
    if name:
        memory["profile"]["nome"] = clean_value(name)
        save_memory(memory)
        return f"Entendido. Vou lembrar que seu nome e {memory['profile']['nome']}."

    preference = extract_after_patterns(
        original_command,
        [
            r"\beu gosto de\s+(.+)",
            r"\bgosto de\s+(.+)",
            r"\bprefiro\s+(.+)",
            r"\bminha preferencia e\s+(.+)",
        ],
    )
    if preference:
        value = clean_value(preference)
        key = slugify(value[:35])
        memory["preferences"][key] = value
        save_memory(memory)
        return f"Boa, vou lembrar que voce prefere {value}."

    fact = extract_fact(original_command)
    if fact:
        key, value = fact
        memory["facts"][key] = value
        save_memory(memory)
        return f"Anotado. Vou lembrar: {key} e {value}."

    if "esqueca" in command_lower or "apague da memoria" in command_lower:
        memory["facts"].clear()
        memory["preferences"].clear()
        save_memory(memory)
        return "Pronto, limpei suas preferencias e fatos salvos."

    return None


def recall_information(command):
    memory = load_memory()
    command_lower = command.lower()

    if "qual meu nome" in command_lower or "como eu me chamo" in command_lower:
        name = memory["profile"].get("nome")
        if name:
            return f"Seu nome e {name}."
        return "Ainda nao sei seu nome."

    if "o que voce lembra" in command_lower or "minha memoria" in command_lower:
        return summarize_memory(memory)

    if "minhas preferencias" in command_lower or "do que eu gosto" in command_lower:
        preferences = list(memory["preferences"].values())
        if preferences:
            return "Voce ja me contou que prefere: " + ", ".join(preferences[:5]) + "."
        return "Ainda nao tenho preferencias suas salvas."

    return None


def record_interaction(command):
    memory = load_memory()
    mood = detect_mood(command)

    memory["interaction_count"] += 1
    if mood:
        memory["mood_history"].append(
            {
                "mood": mood,
                "at": datetime.now().isoformat(timespec="seconds"),
            }
        )
        memory["mood_history"] = memory["mood_history"][-20:]

    save_memory(memory)
    return mood


def build_ai_context(command, user_name=None):
    memory = load_memory()
    mood = detect_mood(command) or latest_mood(memory)
    display_name = clean_value(user_name) if user_name else memory["profile"].get("nome")

    context = {
        "nome": display_name,
        "preferencias": list(memory["preferences"].values())[:6],
        "fatos": memory["facts"],
        "humor_detectado": mood,
        "total_interacoes": memory["interaction_count"],
    }

    lines = ["Contexto do usuario para personalizacao:"]
    if context["nome"]:
        lines.append(f"- Nome: {context['nome']}")
        lines.append(f"- Tratamento obrigatorio: Sr {context['nome'].split()[0]}")
    else:
        lines.append("- Tratamento obrigatorio: Sr")
    if context["preferencias"]:
        lines.append("- Preferencias: " + ", ".join(context["preferencias"]))
    if context["fatos"]:
        facts = [f"{key}: {value}" for key, value in list(context["fatos"].items())[:6]]
        lines.append("- Fatos lembrados: " + "; ".join(facts))
    if context["humor_detectado"]:
        lines.append(f"- Humor percebido: {context['humor_detectado']}")
    lines.append(f"- Interacoes registradas: {context['total_interacoes']}")

    return "\n".join(lines)


def detect_mood(command):
    command_lower = command.lower()
    for mood, keywords in MOOD_KEYWORDS.items():
        if any(keyword in command_lower for keyword in keywords):
            return mood
    return None


def latest_mood(memory):
    history = memory.get("mood_history") or []
    if history:
        return history[-1].get("mood")
    return None


def summarize_memory(memory):
    parts = []
    name = memory["profile"].get("nome")
    if name:
        parts.append(f"seu nome e {name}")

    preferences = list(memory["preferences"].values())
    if preferences:
        parts.append("voce prefere " + ", ".join(preferences[:5]))

    if memory["facts"]:
        facts = [f"{key} e {value}" for key, value in list(memory["facts"].items())[:5]]
        parts.append("lembro que " + "; ".join(facts))

    mood = latest_mood(memory)
    if mood:
        parts.append(f"seu humor recente parece {mood}")

    if not parts:
        return "Ainda nao tenho muita coisa salva sobre voce."

    return "Eu lembro que " + ". Tambem ".join(parts) + "."


def extract_after_patterns(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_fact(text):
    match = re.search(r"\b(lembre que|anote que)\s+(.+?)\s+e\s+(.+)", text, re.IGNORECASE)
    if not match:
        return None

    key = clean_value(match.group(2)).lower()
    value = clean_value(match.group(3))
    return key, value


def clean_value(value):
    return value.strip().strip(".!?,;:")


def slugify(value):
    value = clean_value(value).lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "preferencia"
