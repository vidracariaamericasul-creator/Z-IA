"use client";
import { useState } from "react";

export default function Home(){
  const [chat,setChat]=useState([{quem:"z",txt:`Pronta! Agora pesquiso TUDO 🐻\n\nTesta:\n- Qual temperatura em Boston agora\n- Quem foi Einstein\n- Como fazer bolo`}]);
  const [input,setInput]=useState("");

  async function enviar(){
    if(!input.trim()) return;
    const pergunta=input;
    setChat(c=>[...c,{quem:"me",txt:pergunta},{quem:"z",txt:"Z pensando... 🐻"}]);
    setInput("");
    try{
      const r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({pergunta})});
      const j=await r.json();
      setChat(c=>{const nc=[...c]; nc[nc.length-1]={quem:"z",txt:j.resposta}; return nc;});
    }catch(e){
      setChat(c=>{const nc=[...c]; nc[nc.length-1]={quem:"z",txt:"Erro: "+e.message}; return nc;});
    }
  }

  return (
    <div style={{margin:0,background:"#0b141a",color:"#fff",height:"100vh",display:"flex",flexDirection:"column",fontFamily:"sans-serif"}}>
      <div style={{background:"#25D366",padding:10,textAlign:"center",fontWeight:"bold"}}>✅ Z - Pesquisa TUDO igual Meta AI</div>
      <div style={{flex:1,overflow:"auto",padding:"15px 10px 90px",display:"flex",flexDirection:"column",gap:8}}>
        {chat.map((m,i)=>(
          <div key={i} style={{alignSelf:m.quem==="me"?"flex-end":"flex-start",background:m.quem==="me"?"#005c4b":"#202c33",padding:"10px 14px",borderRadius:m.quem==="me"?"12px 0 12px 12px":"0 12px 12px 12px",maxWidth:"82%",whiteSpace:"pre-wrap"}}>{m.txt}</div>
        ))}
      </div>
      <div style={{position:"fixed",bottom:0,width:"100%",background:"#202c33",display:"flex",gap:8,padding:10,boxSizing:"border-box"}}>
        <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&enviar()} placeholder="Pergunte qualquer coisa..." style={{flex:1,padding:13,borderRadius:25,border:"none",background:"#2a3942",color:"#fff",outline:"none"}}/>
        <button onClick={enviar} style={{width:48,height:48,borderRadius:"50%",border:"none",background:"#25D366",color:"#fff"}}>➤</button>
      </div>
    </div>
  );
}