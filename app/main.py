import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Z")

PUBLIC = Path(__file__).resolve().parent.parent / "public"


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    use_web: bool = True


SYSTEM = """Você é Z, uma IA pessoal criada para ajudar o usuário de forma prática, clara e competente.
Responda principalmente em português do Brasil, a menos que o usuário peça outro idioma.
Se não souber algo, diga claramente.
Não invente fatos, links ou resultados.
Ajude com trabalho, estudos, construção, vidros, viagens, tecnologia, organização, escrita, imagens e assuntos gerais.
Se o pedido envolver uma ação externa (enviar mensagem, comprar, movimentar dinheiro, apagar algo etc.), peça confirmação antes de executar qualquer ação.
"""


@app.get("/")
def home():
    return FileResponse(PUBLIC / "index.html")


@app.get("/manifest.json")
def manifest():
    return FileResponse(
        PUBLIC / "manifest.json",
        media_type="application/manifest+json"
    )


@app.post("/chat")
def chat(req: ChatRequest):
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        return {
            "reply": "A chave da OpenAI não está configurada na Vercel."
        }

    client = OpenAI(api_key=api_key)

    messages = [
        {"role": "system", "content": SYSTEM}
    ]

    for item in req.history:
        if item.get("role") in ["user", "assistant"]:
            messages.append({
                "role": item["role"],
                "content": item.get("content", "")
            })

    messages.append({
        "role": "user",
        "content": req.message
    })

    response = client.chat.completions.create(
        model="gpt-5",
        messages=messages
    )

    return {
        "reply": response.choices[0].message.content
    }