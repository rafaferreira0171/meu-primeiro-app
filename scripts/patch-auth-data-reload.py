from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

start = s.find('function useFinance(')
end = s.find('function Modal(', start)
if start < 0 or end < 0:
    raise SystemExit('Finance hook boundaries not found')

new_hook = "function useFinance(session){const[hasLoaded,setHasLoaded]=useState(false),[data,setData]=useState(seed),[busy,setBusy]=useState(false),[error,setError]=useState('');useEffect(()=>{let active=true;if(session===undefined){setHasLoaded(false);return()=>{active=false}};if(!session){setData(seed);setHasLoaded(true);setBusy(false);setError('');return()=>{active=false}};setHasLoaded(false);setBusy(true);loadData(seed).then(x=>{if(active)setData(normalizeData(x))}).catch(e=>{if(active)setError(e.message||'Não foi possível carregar os dados.')}).finally(()=>{if(active){setHasLoaded(true);setBusy(false)}});return()=>{active=false}},[session?.user?.id]);const save=next=>{const n=normalizeData(next);setData(n);persistData(n).catch(e=>setError(e.message||'Erro ao sincronizar dados.'))};return{data,save,busy,error,setError,hasLoaded}}\n"
s = s[:start] + new_hook + s[end:]

old_app_start = s.find('function App(){')
old_app_end = s.find('function Splash(){', old_app_start)
if old_app_start < 0 or old_app_end < 0:
    raise SystemExit('App boundaries not found')

app = s[old_app_start:old_app_end]
old_decl = "const{data,save,busy,error,setError,hasLoaded}=useFinance(),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[session,setSession]=useState(undefined),[confirm,setConfirm]=useState(null);"
new_decl = "const[session,setSession]=useState(undefined),{data,save,busy,error,setError,hasLoaded}=useFinance(session),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[confirm,setConfirm]=useState(null);"
if old_decl in app:
    app = app.replace(old_decl, new_decl, 1)
elif 'useFinance(session)' not in app:
    raise SystemExit('App state declaration not found')
s = s[:old_app_start] + app + s[old_app_end:]

p.write_text(s)
print('Auth/data reload patch applied: logout clears only the session; login reloads the same user data from Supabase.')
