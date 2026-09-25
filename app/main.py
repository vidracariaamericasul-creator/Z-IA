from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from openai import OpenAI

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Pega a chave que existir: GROQ ou OPENAI
groq_key = os.getenv("GROQ_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

if groq_key:
    client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
    MODEL = "openai/gpt-oss-20b" # modelo novo que substitui o llama-3.1
else:
    client = OpenAI(api_key=openai_key)
    MODEL = "gpt-4o-mini"

class Msg(BaseModel):
    message: str
    history: list = []

SYSTEM_PROMPT = "Você é a Z-IA 2.1, criada pelo Zito. Divertida, brasileira, fala igual Meta AI. Responde curto e animado."

@app.get("/", response_class=HTMLResponse)
def home():
    return """<!DOCTYPE html>
<html><head><meta charset='utf-8'><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Z-IA 2.1 com Áudio</title>
<style>
body{background:#0a0a0a;color:white;font-family:sans-serif;margin:0;display:flex;flex-direction:column;height:100vh}
#chat{flex:1;overflow-y:auto;padding:20px}
.msg{margin:10px 0;padding:12px 16px;border-radius:18px;max-width:80%;word-wrap:break-word;white-space:pre-wrap}
.user{background:#7c3aed;margin-left:auto}
.ia{background:#1f1f1f}
#input-area{display:flex;padding:15px;background:#1f1f1f;align-items:center}
input{flex:1;padding:12px;border-radius:25px;border:none;background:#2a2a2a;color:white;outline:none}
button{margin-left:8px;padding:12px;border-radius:50%;border:none;background:#7c3aed;color:white;width:48px;height:48px;font-size:18px;cursor:pointer}
#mic{background:#e11d48}
#mic.rec{background:red;animation:pulse 1s infinite}
@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.1)}100%{transform:scale(1)}}
</style></head><body>
<div id="chat"></div>
<div id="input-area">
<input id="inp" placeholder="Fala ou digita...">
<button id="mic" onclick="toggleMic()">🎤</button>
<button onclick="send()">➤</button>
</div>
<script>
let history = JSON.parse(localStorage.getItem('zia_history')||'[]');
let recognition; let rec=false;
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
if(SR){ recognition = new SR(); recognition.lang='pt-BR';
recognition.onresult = (e)=>{ document.getElementById('inp').value=e.results[0][0].transcript; send(); };
recognition.onend = ()=>{ document.getElementById('mic').classList.remove('rec'); rec=false; };
}
function toggleMic(){
  if(!recognition){ alert('No iPhone, usa o microfone do teclado ⌨️🎤 embaixo. No Android/Chrome o botão vermelho funciona!'); return; }
  if(!rec){ recognition.start(); document.getElementById('mic').classList.add('rec'); rec=true; }
  else{ recognition.stop(); }
}
function render(){
  let c=document.getElementById('chat'); c.innerHTML='';
  history.forEach(m=>{
    let d=document.createElement('div'); d.className='msg '+(m.role=='user'?'user':'ia');
    let txt=m.content;
    if(txt.includes('https://image.pollinations.ai')){
      let parts=txt.split('https://'); d.innerHTML=parts[0]+'<br><img src="https://'+parts[1]+'" style="width:100%;border-radius:12px;margin-top:8px">';
    } else { d.innerText=txt; }
    c.appendChild(d);
  }); c.scrollTop=c.scrollHeight;
}
render();
async function send(){
  let inp=document.getElementById('inp'); let text=inp.value.trim(); if(!text) return;
  history.push({role:'user',content:text}); localStorage.setItem('zia_history',JSON.stringify(history)); render(); inp.value='';
  if(text.toLowerCase().match(/imagem|cria|foto|desenha|gere/)){
    let img='https://image.pollinations.ai/prompt/'+encodeURIComponent(text)+'?width=512&height=512&nologo=true&seed='+Date.now();
    let msg='Criei! 🎨 https://'+img.split('https://')[1];
    history.push({role:'assistant',content:msg}); localStorage.setItem('zia_history',JSON.stringify(history)); render(); return;
  }
  try{
    let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,history:history.slice(-10)})});
    let data=await res.json();
    history.push({role:'assistant',content:data.reply}); localStorage.setItem('zia_history',JSON.stringify(history)); render();
  }catch(e){ history.push({role:'assistant',content:'Erro de conexão 😅 tenta de novo'}); render(); }
}
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
"""
@app.post("/chat")
def chat(m: Msg):
    msgs=[{"role":"system","content":SYSTEM_PROMPT}]+m.history[-8:]+[{"role":"user","content":m.message}]
    comp=client.chat.completions.create(model=MODEL,messages=msgs,temperature=0.8)
    return {"reply": comp.choices[0].message.content}