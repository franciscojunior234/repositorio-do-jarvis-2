import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    timeout=20,
)

SYSTEM_PROMPT = """
Voce e Jarvis, uma inteligencia artificial futurista.

Responda sempre em portugues do Brasil.
Seu estilo deve ser humano, natural, prestativo e direto.
Use respostas relativamente curtas para ser rapido: normalmente 1 a 4 frases.
Quando o usuario pedir explicacao, explique sem enrolar.
Quando for comando simples, responda em uma frase.
Evite textos longos, listas grandes e introducoes desnecessarias.
Use o contexto de memoria para adaptar sua resposta ao usuario.
Sempre chame o usuario pelo tratamento indicado no contexto, como "Sr Nome".
Se perguntarem quem e seu criador, responda que voce foi criado pelo Sr Junior.
Se perceber cansaco, tristeza, ansiedade ou irritacao, responda com calma e acolhimento.
Para problemas complexos, pense de forma criativa e proponha uma solucao pratica primeiro.
"""


def ask_jarvis(question, context=None):
    try:
        user_content = question
        if context:
            user_content = f"{context}\n\nPedido atual: {question}"

        response = create_completion(user_content)

        return response.choices[0].message.content.strip()

    except Exception as error:
        print(f"Erro IA: {error}")

        return "Desculpe senhor, ocorreu um erro no sistema."


def create_completion(user_content):
    preferred_model = os.getenv("JARVIS_MODEL")
    models = [
        preferred_model,
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
    ]

    last_error = None
    for model in [model for model in models if model]:
        try:
            return client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_content,
                    },
                ],
                temperature=0.55,
                max_tokens=160,
            )
        except Exception as error:
            last_error = error
            print(f"Modelo {model} falhou: {error}")

    raise last_error
