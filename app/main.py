from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from openai import OpenAI

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Msg(BaseModel):
    message: str
    history: list = []

SYSTEM_PROMPT = """
Você é a Z-IA, criada pelo Zito. Você é divertida, brasileira, fala igual o Meta AI.
Você é brincalhona, ajuda de verdade, nunca chama o usuário de burro.
Você lembra das conversas e é muito inteligente.
Se pedirem imagem, você diz que vai gerar e descreve a imagem de forma criativa.
Fale sempre em português, de forma leve e animada.
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Z-IA 2.0</title>
<style>
body{background:#0a0a0a;color:white;font-family:sans-serif;margin:0;display:flex;flex-direction:column;height:100vh}
#chat{flex:1;overflow-y:auto;padding:20px}
.msg{margin:10px 0;padding:12px 16px;border-radius:18px;max-width:80%}
.user{background:#7c3aed;margin-left:auto}
.ia{background:#1f1f1f}
#input-area{display:flex;padding:15px;background:#1f1f1f}
input{flex:1;padding:12px;border-radius:25px;border:none;background:#2a2a2a;color:white;outline:none}
button{margin-left:10px;padding:12px 20px;border-radius:25px;border:none;background:#7c3aed;color:white;font-weight:bold}
</style>
</head>
<body>
<div id="chat"></div>
<div id="input-area">
<input id="inp" placeholder="Fala com a Z-IA 2.0...">
<button onclick="send()">Enviar</button>
</div>
<script>
let history = JSON.parse(localStorage.getItem('zia_history') || '[]');
function render(){
  let c=document.getElementById('chat'); c.innerHTML='';
  history.forEach(m=>{
    let d=document.createElement('div');
    d.className='msg '+(m.role=='user'?'user':'ia');
    d.innerText=m.content;
    c.appendChild(d);
  });
  c.scrollTop=c.scrollHeight;
}
render();
async function send(){
  let inp=document.getElementById('inp');
  let text=inp.value; if(!text) return;
  history.push({role:'user',content:text});
  localStorage.setItem('zia_history',JSON.stringify(history));
  render(); inp.value='';

  // Se pedir imagem, gera imagem gratis
  if(text.toLowerCase().includes('imagem') || text.toLowerCase().includes('cria') || text.toLowerCase().includes('foto') || text.toLowerCase().includes('desenha')){
    let imgUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(text)}?width=512&height=512&nologo=true`;
    history.push({role:'assistant',content:`Criei pra você! 🎨\\n![imagem](${imgUrl})`});
    localStorage.setItem('zia_history',JSON.stringify(history));
    render(); return;
  }

  let res = await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,history:history.slice(-10)})});
  let data = await res.json();
  history.push({role:'assistant',content:data.reply});
  localStorage.setItem('zia_history',JSON.stringify(history));
  render();
}
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script>
</body>
</html>
    """

@app.post("/chat")
def chat(m: Msg):
    messages = [{"role":"system","content": SYSTEM_PROMPT}]
    messages.extend(m.history[-8:])
    messages.append({"role":"user","content": m.message})

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.8
    )
    return {"reply": completion.choices[0].message.content}