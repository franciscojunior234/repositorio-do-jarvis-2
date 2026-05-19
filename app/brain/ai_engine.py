from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """
Você é Jarvis, uma inteligência artificial futurista.

Características:
- Inteligente
- Elegante
- Prestativo
- Objetivo
- Natural
"""

def ask_jarvis(question):

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as error:

        print(f"Erro IA: {error}")

        return "Desculpe senhor, ocorreu um erro no sistema."