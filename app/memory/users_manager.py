import json
import os
import uuid
from datetime import datetime

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        save_users([])
        return []
    
    with open(USERS_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4, ensure_ascii=False)

def register_user(name, email, password):
    users = load_users()
    normalized_email = email.strip().lower()
    
    # Verifica se o email ja esta cadastrado
    if any(u.get("email") == normalized_email for u in users):
        return None, "Ja existe uma conta com este email."
        
    user = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "email": normalized_email,
        "password": password,
        "plan": "Licenca inicial",
        "createdAt": datetime.now().isoformat()
    }
    
    users.append(user)
    save_users(users)
    return user, None

def login_user(email, password):
    users = load_users()
    normalized_email = email.strip().lower()
    
    for user in users:
        if user.get("email") == normalized_email:
            if user.get("password") == password:
                return user, None
            else:
                return None, "Senha incorreta."
                
    return None, "Conta nao encontrada."

def recover_password(email):
    users = load_users()
    normalized_email = email.strip().lower()
    
    for user in users:
        if user.get("email") == normalized_email:
            return user, None
            
    return None, "Nenhuma conta foi encontrada com este email."
