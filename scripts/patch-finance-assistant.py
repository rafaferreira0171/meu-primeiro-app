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
  return <><button className="finance-fab" onClick={()=>{setOpen(true);setMessage('')}} aria-label="Abrir Finance"><span>✦</span><b>Finance</b></button>{open&&<div className="finance-overlay" onMouseDown={e=>e.target===e.currentTarget&&setOpen(false)}><section className="finance-assistant" role="dialog" aria-modal="true" aria-label="Assistente Finance"><div className="finance-assistant-head"><div><strong>Finance</strong><span>Assistente do seu dinheiro</span></div><button className="icon-button" onClick={()=>setOpen(false)} aria-label="Fechar">×</button></div><div className="finance-assistant-body"><div className="finance-bubble">Diga ou escreva algo como <b>“50 reais no Budget Mercado”</b>.</div><div className="finance-input-wrap"><input autoFocus value={text} onChange={e=>setText(e.target.value)} onKeyDown={e=>{if(e.key==='Enter')submit()}} placeholder="Ex.: 50 reais no Mercado"/><button className={listening?'voice-button listening':'voice-button'} onClick={startVoice} aria-label="Falar">{listening?'●':'🎙️'}</button></div><button className="primary wide" onClick={submit}>Interpretar lançamento</button>{message&&<div className="finance-message">{message}</div>}{draft&&<div className="finance-preview"><div><span>Valor</span><strong>{BRL(draft.value)}</strong></div><div><span>Budget</span>{draft.account?<strong>{draft.account.nome}</strong>:<select value="" onChange={e=>chooseAccount(data.budgetAccounts.find(a=>a.id===e.target.value))}><option value="">Selecionar conta…</option>{data.budgetAccounts.filter(a=>a.month===month&&a.ativo!==false).map(a=><option key={a.id} value={a.id}>{a.nome}</option>)}</select>}</div>{draft.account&&<button className="primary wide" onClick={confirm}>Confirmar lançamento</button>}</div>}</div></section></div>}</>}
'''
    if marker not in s:
        raise SystemExit('main root marker not found')
    s = s.replace(marker, component + '\n' + marker, 1)

old = "</main>{confirm&&<Modal title={confirm.title}"
new = "</main><FinanceAssistant data={data} save={save} month={month}/>{confirm&&<Modal title={confirm.title}"
if old not in s:
    raise SystemExit('App insertion point not found')
s = s.replace(old, new, 1)
p.write_text(s)

css = Path('src/styles.css')
c = css.read_text()
if '.finance-fab{' not in c:
    c += r'''
/* Finance AI assistant */
.finance-fab{position:fixed;right:22px;bottom:22px;z-index:10000;border:0;border-radius:999px;padding:10px 16px 10px 12px;display:flex;align-items:center;gap:7px;background:var(--ink);color:#fff;box-shadow:0 14px 34px rgba(15,22,35,.25);cursor:pointer;font-weight:800;transition:.2s ease}.finance-fab:hover{transform:translateY(-2px);box-shadow:0 18px 38px rgba(15,22,35,.3)}.finance-fab span{width:26px;height:26px;border-radius:50%;display:grid;place-items:center;background:#fff;color:var(--blue);font-size:15px}.finance-fab b{font-size:12px}.finance-overlay{position:fixed;inset:0;background:rgba(15,22,35,.25);backdrop-filter:blur(3px);-webkit-backdrop-filter:blur(3px);z-index:10001;display:grid;place-items:end;padding:22px}.finance-assistant{width:min(430px,100%);background:#fff;border:1px solid var(--line);border-radius:24px;box-shadow:0 24px 70px rgba(15,22,35,.25);overflow:hidden}.finance-assistant-head{display:flex;align-items:center;justify-content:space-between;padding:18px 18px 14px;border-bottom:1px solid #eef1f4}.finance-assistant-head strong{display:block;font-size:20px;letter-spacing:-.03em}.finance-assistant-head span{display:block;margin-top:3px;color:var(--muted);font-size:10px}.finance-assistant-body{padding:18px}.finance-bubble{background:#f4f7ff;border:1px solid #e0e8ff;border-radius:14px;padding:12px;font-size:12px;line-height:1.5;color:#596579;margin-bottom:12px}.finance-input-wrap{display:flex;gap:8px}.finance-input-wrap input{flex:1;min-width:0;border:1px solid #dfe4eb;border-radius:12px;padding:12px 13px;min-height:46px;font-size:13px}.finance-input-wrap input:focus{outline:2px solid #3972e84d;border-color:#b9cbf6}.voice-button{width:46px;min-width:46px;border:0;border-radius:12px;background:var(--blue-soft);color:var(--blue);font-size:18px;cursor:pointer}.voice-button.listening{background:#fff0f0;color:var(--danger);animation:finance-pulse 1s infinite}.finance-assistant-body>.wide{margin-top:10px}.finance-message{margin-top:10px;background:#f7f9fb;border-radius:10px;padding:10px;font-size:11px;color:#697384;line-height:1.4}.finance-preview{margin-top:12px;border:1px solid #e5e9ef;border-radius:15px;padding:13px;background:#fbfcfd}.finance-preview>div{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:7px 0;border-bottom:1px solid #eef1f4}.finance-preview>div:last-of-type{border-bottom:0}.finance-preview span{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}.finance-preview strong{font-size:13px}.finance-preview select{max-width:190px;border:1px solid #dfe4eb;border-radius:9px;padding:8px;background:#fff}.finance-preview .wide{margin-top:10px}@keyframes finance-pulse{50%{transform:scale(.92);opacity:.7}}@media(max-width:800px){.finance-fab{right:14px;bottom:92px}.finance-overlay{padding:10px;place-items:end center}.finance-assistant{border-radius:22px;max-height:82vh;overflow:auto}.finance-assistant-body{padding:15px}}@media(max-width:520px){.finance-fab{right:12px;bottom:88px;padding:9px 13px 9px 10px}.finance-fab b{font-size:11px}.finance-assistant{width:100%}}
'''
    css.write_text(c)
print('Finance assistant patch applied')
