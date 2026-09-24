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

SYSTEM_PROMPT = "Você é a Z-IA 2.1, criada pelo Zito. Divertida, brasileira, fala igual Meta AI. Responde curto e animado."

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Z-IA 2.1 com Áudio</title>
<style>
body{background:#0a0a0a;color:white;font-family:sans-serif;margin:0;display:flex;flex-direction:column;height:100vh}
#chat{flex:1;overflow-y:auto;padding:20px}
.msg{margin:10px 0;padding:12px 16px;border-radius:18px;max-width:80%;word-wrap:break-word}
.user{background:#7c3aed;margin-left:auto}
.ia{background:#1f1f1f}
#input-area{display:flex;padding:15px;background:#1f1f1f;align-items:center}
input{flex:1;padding:12px;border-radius:25px;border:none;background:#2a2a2a;color:white;outline:none}
button{margin-left:8px;padding:12px;border-radius:50%;border:none;background:#7c3aed;color:white;width:48px;height:48px;font-size:18px}
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
if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR(); recognition.lang='pt-BR'; recognition.continuous=false;
  recognition.onresult = (e)=>{document.getElementById('inp').value=e.results[0][0].transcript; send();}
  recognition.onend = ()=>{document.getElementById('mic').classList.remove('rec'); rec=false;}
}
function toggleMic(){
  if(!recognition){alert('Seu navegador não suporta áudio, use Chrome no celular!');return;}
  if(!rec){recognition.start(); document.getElementById('mic').classList.add('rec'); rec=true;}
  else{recognition.stop();}
}
function render(){
  let c=document.getElementById('chat'); c.innerHTML='';
  history.forEach(m=>{
    let d=document.createElement('div'); d.className='msg '+(m.role=='user'?'user':'ia');
    d.innerText=m.content; c.appendChild(d);
  }); c.scrollTop=c.scrollHeight;
}
render();
async function send(){
  let inp=document.getElementById('inp'); let text=inp.value; if(!text) return;
  history.push({role:'user',content:text});