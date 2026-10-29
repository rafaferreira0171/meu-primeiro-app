from pathlib import Path
import re

p=Path('src/main.jsx')
s=p.read_text()

s=s.replace(
    "import {signIn,signUp,signOut,getSession,onAuthStateChange} from './lib/auth'",
    "import {signIn,signUp,resendSignupConfirmation,signOut,getSession,onAuthStateChange} from './lib/auth'"
)

new_login='''function Login(){const[email,setEmail]=useState(''),[password,setPassword]=useState(''),[mode,setMode]=useState('login'),[message,setMessage]=useState(''),[busy,setBusy]=useState(false);const submit=async e=>{e.preventDefault();setBusy(true);setMessage('');try{const r=mode==='login'?await signIn(email,password):await signUp(email,password);if(r.error)throw r.error;if(mode==='signup'){if(r.data?.session){setMessage('Conta criada e acesso liberado.')}else{setMessage('Conta criada. Verifique seu e-mail para confirmar o acesso.')}}else{setMessage('Login realizado.')}}catch(err){setMessage(err.message||'Não foi possível autenticar.')}finally{setBusy(false)}};const resend=async()=>{setBusy(true);setMessage('');try{const r=await resendSignupConfirmation(email);if(r.error)throw r.error;setMessage('Novo e-mail de confirmação enviado.')}catch(err){setMessage(err.message||'Não foi possível reenviar o e-mail.')}finally{setBusy(false)}};return <div className="login"><form className="login-card" onSubmit={submit}><div className="brand big"><div className="mark">L</div><div><b>LookLiP</b><span>FINANCE</span></div></div><h1>{mode==='login'?'Seu dinheiro, sob controle.':'Criar acesso'}</h1><p>Conta independente do Base44.</p><input required type="email" placeholder="E-mail" value={email} onChange={e=>setEmail(e.target.value)}/><input required minLength={6} type="password" placeholder="Senha" value={password} onChange={e=>setPassword(e.target.value)}/><button className="primary wide" disabled={busy}>{busy?'Aguarde…':mode==='login'?'Entrar':'Criar conta'}</button>{message&&<small className="login-message">{message}</small>}{mode==='signup'&&<button type="button" className="linkbutton" onClick={resend} disabled={busy}>Reenviar confirmação</button>}<button type="button" className="linkbutton" onClick={()=>setMode(mode==='login'?'signup':'login')}>{mode==='login'?'Ainda não tenho conta':'Já tenho conta'}</button></form></div>}'''

# Replace only the Login function itself. The FinanceAssistant and other
# components may sit between Login and the React root and must survive.
pattern=r"function Login\(\)\{.*?\}\n(?=function |const root=)"
s2,n=re.subn(pattern,new_login+"\n",s,count=1,flags=re.S)
if n!=1:
    raise SystemExit('Login component marker not found')
p.write_text(s2)
print('Signup confirmation UI applied without consuming following components')
