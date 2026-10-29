from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

old = "function useFinance(){const[hasLoaded,setHasLoaded]=useState(false),[data,setData]=useState(seed),[busy,setBusy]=useState(false),[error,setError]=useState('');useEffect(()=>{let active=true;setBusy(true);loadData(seed).then(x=>{if(active)setData(normalizeData(x))}).catch(e=>{if(active)setError(e.message||'Não foi possível carregar os dados.')}).finally(()=>{if(active){setHasLoaded(true);setBusy(false)}});return()=>{active=false}},[]);const save=next=>{const n=normalizeData(next);setData(n);persistData(n).catch(e=>setError(e.message||'Erro ao sincronizar dados.'))};return{data,save,busy,error,setError,hasLoaded}}"

new = "function useFinance(session){const[hasLoaded,setHasLoaded]=useState(false),[data,setData]=useState(seed),[busy,setBusy]=useState(false),[error,setError]=useState('');useEffect(()=>{let active=true;if(session===undefined){setHasLoaded(false);return()=>{active=false}};if(!session){setData(seed);setHasLoaded(true);setBusy(false);setError('');return()=>{active=false}};setHasLoaded(false);setBusy(true);loadData(seed).then(x=>{if(active)setData(normalizeData(x))}).catch(e=>{if(active)setError(e.message||'Não foi possível carregar os dados.')}).finally(()=>{if(active){setHasLoaded(true);setBusy(false)}});return()=>{active=false}},[session?.user?.id]);const save=next=>{const n=normalizeData(next);setData(n);persistData(n).catch(e=>setError(e.message||'Erro ao sincronizar dados.'))};return{data,save,busy,error,setError,hasLoaded}}"

if old not in s:
    raise SystemExit('Expected useFinance implementation not found')
s = s.replace(old, new, 1)

old_app = "function App(){const{data,save,busy,error,setError,hasLoaded}=useFinance(),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[session,setSession]=useState(undefined),[confirm,setConfirm]=useState(null);"
new_app = "function App(){const[session,setSession]=useState(undefined),{data,save,busy,error,setError,hasLoaded}=useFinance(session),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[confirm,setConfirm]=useState(null);"
if old_app not in s:
    raise SystemExit('Expected App state initialization not found')
s = s.replace(old_app, new_app, 1)

p.write_text(s)
print('Auth/data reload behavior patched: logout clears only the session; login reloads the same user data from Supabase.')
