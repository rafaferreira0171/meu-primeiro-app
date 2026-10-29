from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

month_effect = "useEffect(()=>{setMonth(currentMonth())},[tab]);"
if month_effect not in s:
    app_start = s.find('function App(){')
    if app_start < 0:
        raise SystemExit('App function marker not found')
    app_end = s.find(';', app_start)
    if app_end < 0:
        raise SystemExit('App declaration terminator not found')
    s = s[:app_end + 1] + month_effect + s[app_end + 1:]

# Keep finance data tied to the authenticated user. This prevents logout/login
# from reusing the previous user's in-memory state and also makes later auth
# patches idempotent.
old_legacy = "function useFinance(){const[hasLoaded,setHasLoaded]=useState(false),[data,setData]=useState(seed),[busy,setBusy]=useState(false),[error,setError]=useState('');useEffect(()=>{let active=true;setBusy(true);loadData(seed).then(x=>{if(active)setData(normalizeData(x))}).catch(e=>{if(active)setError(e.message||'Não foi possível carregar os dados.')}).finally(()=>{if(active){setHasLoaded(true);setBusy(false)}});return()=>{active=false}},[]);const save=next=>{const n=normalizeData(next);setData(n);persistData(n).catch(e=>setError(e.message||'Erro ao sincronizar dados.'))};return{data,save,busy,error,setError,hasLoaded}}"
old_session_safe = "function useFinance(){const[hasLoaded,setHasLoaded]=useState(false),[data,setData]=useState(seed),[busy,setBusy]=useState(false),[error,setError]=useState('');useEffect(()=>{let active=true;setBusy(true);getSession().then(()=>loadData(seed)).then(x=>{if(active)setData(normalizeData(x))}).catch(e=>{if(active)setError(e.message||'Não foi possível carregar os dados.')}).finally(()=>{if(active){setHasLoaded(true);setBusy(false)}});return()=>{active=false}},[]);const save=next=>{const n=normalizeData(next);setData(n);persistData(n).catch(e=>setError(e.message||'Erro ao sincronizar dados.'))};return{data,save,busy,error,setError,hasLoaded}}"
new_hook = "function useFinance(session){const[hasLoaded,setHasLoaded]=useState(false),[data,setData]=useState(seed),[busy,setBusy]=useState(false),[error,setError]=useState('');useEffect(()=>{let active=true;if(session===undefined){setHasLoaded(false);return()=>{active=false}};if(!session){setData(seed);setHasLoaded(true);setBusy(false);setError('');return()=>{active=false}};setHasLoaded(false);setBusy(true);loadData(seed).then(x=>{if(active)setData(normalizeData(x))}).catch(e=>{if(active)setError(e.message||'Não foi possível carregar os dados.')}).finally(()=>{if(active){setHasLoaded(true);setBusy(false)}});return()=>{active=false}},[session?.user?.id]);const save=next=>{const n=normalizeData(next);setData(n);persistData(n).catch(e=>setError(e.message||'Erro ao sincronizar dados.'))};return{data,save,busy,error,setError,hasLoaded}}"

if old_legacy in s:
    s = s.replace(old_legacy, new_hook, 1)
elif old_session_safe in s:
    s = s.replace(old_session_safe, new_hook, 1)
elif 'function useFinance(session)' in s:
    print('Auth-aware Finance hook already present')
else:
    raise SystemExit('useFinance hook pattern is neither legacy nor already patched')

# Update App's hook call without depending on the exact order of other state
# declarations produced by the build patch chain.
old_use = "const{data,save,busy,error,setError,hasLoaded}=useFinance()"
new_use = "const[session,setSession]=useState(undefined),{data,save,busy,error,setError,hasLoaded}=useFinance(session)"
if old_use in s:
    s = s.replace(old_use, new_use, 1)
    s = s.replace(",[session,setSession]=useState(undefined)", "", 1)
elif 'useFinance(session)' not in s:
    raise SystemExit('App finance hook call is neither legacy nor already patched')

p.write_text(s)
print('Current month is enforced on tab changes and Finance data now reloads per authenticated user session.')
