export async function POST(req){
  const {pergunta} = await req.json();
  let extra = "";
  try{
    if(/temperatura|clima/i.test(pergunta)){
      let cidade = pergunta.match(/em\s+([^?.,!]+)/i)?.[1]?.replace(/agora/gi,"").trim() || "Boston";
      const r = await fetch(`https://wttr.in/${encodeURIComponent(cidade)}?format=j1`);
      const j = await r.json();
      const a = j.current_condition?.[0];
      if(a) extra = `DADO REAL: ${cidade} ${a.temp_C}°C, ${a.weatherDesc?.[0]?.value}.`;
    }
  }catch(e){}

  const groq = await fetch("https://api.groq.com/openai/v1/chat/completions",{
    method:"POST",
    headers:{
      "Authorization": `Bearer ${process.env.GROQ_KEY}`,
      "Content-Type":"application/json"
    },
    body: JSON.stringify({
      model: "llama-3.3-70b-versatile",
      messages:[
        {role:"system", content:`Você é a Z 🐻 pt-BR curta. Dado: ${extra}`},
        {role:"user", content: pergunta}
      ]
    })
  });
  const data = await groq.json();
  if(data.error) return Response.json({resposta: `Erro: ${data.error.message}`});
  return Response.json({resposta: data.choices?.[0]?.message?.content});
}