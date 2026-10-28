from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

if 'function FinanceAssistant(' not in s:
    marker = "const root=document.getElementById('root')"
    component = r'''
function FinanceAssistant({data,save,month}){
  const[open,setOpen]=useState(false),[text,setText]=useState(''),[listening,setListening]=useState(false),[draft,setDraft]=useState(null),[message,setMessage]=useState('');
  const normalize=v=>String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  const parseValue=v=>{const n=String(v||'').replace(/r\$\s*/ig,'').replace(/\./g,'').replace(',','.').match(/\d+(?:\.\d+)?/);return n?Number(n[0]):0};
  const findAccount=name=>{const q=normalize(name);const accounts=data.budgetAccounts.filter(a=>a.month===month&&a.ativo!==false);return accounts.find(a=>normalize(a.nome)===q)||accounts.find(a=>normalize(a.nome).includes(q)||q.includes(normalize(a.nome)))||null};
  const parse=raw=>{
    const value=parseValue(raw);if(!value)return null;
    const q=normalize(raw);
    const accounts=data.budgetAccounts.filter(a=>a.month===month&&a.ativo!==false);
    const account=accounts.find(a=>q.includes(normalize(a.nome)))||accounts.find(a=>a.legacy_key&&q.includes(normalize(a.legacy_key)))||null;
    if(!account)return {value,account:null,raw};
    return {value,account,raw};
  };
  const submit=()=>{const d=parse(text);if(!d){setMessage('Não consegui identificar um valor. Ex.: “50 reais no Mercado”.');return}if(!d.account){setDraft(d);setMessage('Identifiquei o valor, mas não encontrei o Budget. Escolha uma conta abaixo.');return}setDraft(d);setMessage('Confira o lançamento antes de confirmar.')};
  const confirm=()=>{if(!draft?.account||!draft.value)return;save({...data,gastos:[...data.gastos,{id:crypto.randomUUID(),month,conta:draft.account.legacy_key||draft.account.id,budget_account_id:draft.account.id,valor:Math.abs(draft.value)}]});setText('');setDraft(null);setMessage('Lançamento registrado no Budget.');setTimeout(()=>setMessage(''),2200)};
  const startVoice=()=>{const SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR){setMessage('Seu navegador não disponibilizou reconhecimento de voz. Use o campo de texto ou o ditado do teclado.');return}const r=new SR();r.lang='pt-BR';r.interimResults=false;r.maxAlternatives=1;r.onstart=()=>setListening(true);r.onend=()=>setListening(false);r.onerror=()=>{setListening(false);setMessage('Não consegui ouvir. Tente novamente.')};r.onresult=e=>{const heard=e.results?.[0]?.[0]?.transcript||'';setText(heard);setTimeout(()=>{const d=parse(heard);if(d?.account){setDraft(d);setMessage('Confira o lançamento antes de confirmar.')}else if(d){setDraft(d);setMessage('Identifiquei o valor, mas não encontrei o Budget. Escolha uma conta abaixo.')}} ,0)};r.start()};
  const chooseAccount=a=>setDraft(d=>d?{...d,account:a}:d);
  return <><button className="finance-fab" onClick={()=>{setOpen(true);setMessage('');startVoice()}} aria-label="Abrir Finance"><span>✦</span><b>Finance</b></button>{open&&<div className="finance-overlay" onMouseDown={e=>e.target===e.currentTarget&&setOpen(false)}><section className="finance-assistant" role="dialog" aria-modal="true" aria-label="Assistente Finance"><div className="finance-assistant-head"><div><strong>Finance</strong><span>Assistente do seu dinheiro</span></div><button className="icon-button" onClick={()=>setOpen(false)} aria-label="Fechar">×</button></div><div className="finance-assistant-body"><div className="finance-bubble">Diga ou escreva algo como <b>“50 reais no Budget Mercado”</b>.</div><div className="finance-input-wrap"><input value={text} onChange={e=>setText(e.target.value)} onKeyDown={e=>{if(e.key==='Enter')submit()}} placeholder="Ex.: 50 reais no Mercado"/><button className={listening?'voice-button listening':'voice-button'} onClick={startVoice} aria-label="Falar">{listening?'●':'🎙️'}</button></div><button className="primary wide" onClick={submit}>Interpretar lançamento</button>{message&&<div className="finance-message">{message}</div>}{draft&&<div className="finance-preview"><div><span>Valor</span><strong>{BRL(draft.value)}</strong></div><div><span>Budget</span>{draft.account?<strong>{draft.account.nome}</strong>:<select value="" onChange={e=>chooseAccount(data.budgetAccounts.find(a=>a.id===e.target.value))}><option value="">Selecionar conta…</option>{data.budgetAccounts.filter(a=>a.month===month&&a.ativo!==false).map(a=><option key={a.id} value={a.id}>{a.nome}</option>)}</select>}</div>{draft.account&&<button className="primary wide" onClick={confirm}>Confirmar lançamento</button>}</div>}</div></section></div>}</>}
'''
    if marker not in s:
        raise SystemExit('main root marker not found')
    s = s.replace(marker, component + '\n' + marker, 1)

old = "</main>{confirm&&<Modal title={confirm.title}"
new = "</main><FinanceAssistant data={data} save={save} month={month}/>{confirm&&<Modal title={confirm.title}"
if old not in s:
    raise SystemExit('App insertion point not found')
s = s.replace(old, new, 1)

# Voice UX: spoken Portuguese numbers, guaranteed stop after a result, and a clean new session.
s = s.replace("import React,{useEffect,useState} from 'react'", "import React,{useEffect,useState} from 'react'")
old_parse = "const parseValue=v=>{const n=String(v||'').replace(/r\\$\\s*/ig,'').replace(/\\./g,'').replace(',','.').match(/\\d+(?:\\.\\d+)?/);return n?Number(n[0]):0};"
new_parse = r'''const parseValue=v=>{const raw=normalize(v).replace(/r\$\s*/g,'').replace(/ reais?/g,' ').trim();const n=raw.replace(/\./g,'').replace(',','.').match(/\d+(?:\.\d+)?/);if(n)return Number(n[0]);const ones={zero:0,um:1,uma:1,dois:2,duas:2,tres:3,quatro:4,cinco:5,seis:6,sete:7,oito:8,nove:9,dez:10,onze:11,doze:12,treze:13,quatorze:14,catorze:14,quinze:15,dezesseis:16,dezessete:17,dezoito:18,dezenove:19};const tens={vinte:20,trinta:30,quarenta:40,cinquenta:50,sessenta:60,setenta:70,oitenta:80,noventa:90};const words=raw.replace(/\be\b/g,' ').split(/\s+/).filter(Boolean);let total=0;for(const w of words){if(Object.prototype.hasOwnProperty.call(ones,w)){total+=ones[w];continue}if(Object.prototype.hasOwnProperty.call(tens,w)){total+=tens[w];continue}if(w==='cem'||w==='cento'){total+=100;continue}if(w==='duzentos'||w==='duzentas'){total+=200;continue}if(w==='trezentos'||w==='trezentas'){total+=300;continue}if(w==='quatrocentos'||w==='quatrocentas'){total+=400;continue}if(w==='quinhentos'){total+=500;continue}if(w==='seiscentos'||w==='seiscentas'){total+=600;continue}if(w==='setecentos'||w==='setecentas'){total+=700;continue}if(w==='oitocentos'||w==='oitocentas'){total+=800;continue}if(w==='novecentos'||w==='novecentas'){total+=900;continue}}return total};'''
if old_parse in s:
    s = s.replace(old_parse,new_parse,1)

old_voice = r'''const startVoice=()=>{const SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR){setMessage('Seu navegador não disponibilizou reconhecimento de voz. Use o campo de texto ou o ditado do teclado.');return}const r=new SR();r.lang='pt-BR';r.interimResults=false;r.maxAlternatives=1;r.onstart=()=>setListening(true);r.onend=()=>setListening(false);r.onerror=()=>{setListening(false);setMessage('Não consegui ouvir. Tente novamente.')};r.onresult=e=>{const heard=e.results?.[0]?.[0]?.transcript||'';setText(heard);setTimeout(()=>{const d=parse(heard);if(d?.account){setDraft(d);setMessage('Confira o lançamento antes de confirmar.')}else if(d){setDraft(d);setMessage('Identifiquei o valor, mas não encontrei o Budget. Escolha uma conta abaixo.')}} ,0)};r.start()};'''
new_voice = r'''const startVoice=()=>{const SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR){setMessage('Seu navegador não disponibilizou reconhecimento de voz. Use o campo de texto ou o ditado do teclado.');return}setMessage('');setListening(true);const r=new SR();r.lang='pt-BR';r.continuous=false;r.interimResults=false;r.maxAlternatives=1;let finished=false;const finish=heard=>{if(finished)return;finished=true;try{r.stop()}catch(e){}setListening(false);if(!heard){setMessage('Não consegui ouvir. Tente novamente.');return}setText(heard);const d=parse(heard);if(d?.account){setDraft(d);setMessage('Confira o lançamento antes de confirmar.')}else if(d){setDraft(d);setMessage('Identifiquei o valor, mas não encontrei o Budget. Escolha uma conta abaixo.')}else{setMessage('Não identifiquei o valor. Tente dizer, por exemplo, “cinco reais gasolina”.')}};r.onstart=()=>setListening(true);r.onend=()=>{if(!finished)setListening(false)};r.onerror=e=>{finished=true;setListening(false);if(e?.error!=='aborted')setMessage('Não consegui ouvir. Tente novamente.')};r.onresult=e=>{const heard=e.results?.[0]?.[0]?.transcript||'';finish(heard)};try{r.start()}catch(e){setListening(false);setMessage('Não consegui iniciar o microfone. Tente novamente.')}};'''
if old_voice in s:
    s = s.replace(old_voice,new_voice,1)

old_open = "onClick={()=>{setOpen(true);setMessage('');startVoice()}} aria-label=\"Abrir Finance\""
new_open = "onClick={()=>{setOpen(true);setText('');setDraft(null);setMessage('');startVoice()}} aria-label=\"Abrir Finance\""
if old_open in s:
    s = s.replace(old_open,new_open,1)

p.write_text(s)

css = Path('src/styles.css')
c = css.read_text()
if '.finance-fab{' not in c:
    c += r'''
/* Finance AI assistant */
.finance-fab{position:fixed;right:22px;bottom:22px;z-index:10000;border:0;border-radius:999px;padding:10px 16px 10px 12px;display:flex;align-items:center;gap:7px;background:var(--ink);color:#fff;box-shadow:0 14px 34px rgba(15,22,35,.25);cursor:pointer;font-weight:800;transition:.2s ease}.finance-fab:hover{transform:translateY(-2px);box-shadow:0 18px 38px rgba(15,22,35,.3)}.finance-fab span{width:26px;height:26px;border-radius:50%;display:grid;place-items:center;background:#fff;color:var(--blue);font-size:15px}.finance-fab b{font-size:12px}.finance-overlay{position:fixed;inset:0;background:rgba(15,22,35,.25);backdrop-filter:blur(3px);-webkit-backdrop-filter:blur(3px);z-index:10001;display:grid;place-items:end;padding:22px}.finance-assistant{width:min(430px,100%);max-height:62vh;background:#fff;border:1px solid var(--line);border-radius:24px;box-shadow:0 24px 70px rgba(15,22,35,.25);overflow:auto}.finance-assistant-head{display:flex;align-items:center;justify-content:space-between;padding:16px 18px 12px;border-bottom:1px solid #eef1f4}.finance-assistant-head strong{display:block;font-size:20px;letter-spacing:-.03em}.finance-assistant-head span{display:block;margin-top:3px;color:var(--muted);font-size:10px}.finance-assistant-body{padding:14px 18px 16px}.finance-bubble{background:#f4f7ff;border:1px solid #e0e8ff;border-radius:14px;padding:10px 12px;font-size:12px;line-height:1.45;color:#596579;margin-bottom:10px}.finance-input-wrap{display:flex;gap:8px}.finance-input-wrap input{flex:1;min-width:0;border:1px solid #dfe4eb;border-radius:12px;padding:10px 13px;min-height:46px;font-size:16px}.finance-input-wrap input:focus{outline:2px solid #3972e84d;border-color:#b9cbf6}.voice-button{width:46px;min-width:46px;border:0;border-radius:12px;background:var(--blue-soft);color:var(--blue);font-size:18px;cursor:pointer}.voice-button.listening{background:#fff0f0;color:var(--danger);animation:finance-pulse 1s infinite}.finance-assistant-body>.wide{margin-top:8px}.finance-message{margin-top:8px;background:#f7f9fb;border-radius:10px;padding:9px 10px;font-size:11px;color:#697384;line-height:1.4}.finance-preview{margin-top:10px;border:1px solid #e5e9ef;border-radius:15px;padding:11px 13px;background:#fbfcfd}.finance-preview>div{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:6px 0;border-bottom:1px solid #eef1f4}.finance-preview>div:last-of-type{border-bottom:0}.finance-preview span{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}.finance-preview strong{font-size:13px}.finance-preview select{max-width:190px;border:1px solid #dfe4eb;border-radius:9px;padding:8px;background:#fff}.finance-preview .wide{margin-top:8px}@keyframes finance-pulse{50%{transform:scale(.92);opacity:.7}}@media(max-width:800px){.finance-fab{right:14px;bottom:92px}.finance-overlay{padding:10px;place-items:end center}.finance-assistant{max-height:58vh;border-radius:22px}.finance-assistant-body{padding:13px 15px 15px}}@media(max-width:520px){.finance-fab{right:12px;bottom:88px;padding:9px 13px 9px 10px}.finance-fab b{font-size:11px}.finance-assistant{width:100%;max-height:55vh}}
'''
    css.write_text(c)
print('Finance assistant patch applied')
