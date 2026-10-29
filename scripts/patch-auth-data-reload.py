from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

if 'function useFinance(session)' in s and 'useFinance(session)' in s:
    print('Auth/data reload patch already present')
    raise SystemExit(0)

old_legacy = "function useFinance(){const[hasLoaded,setHasLoaded]=useState(false),[data,setData]=useState(seed),[busy,setBusy]=useState(false),[error,setError]=useState('');useEffect(()=>{let active=true;setBusy(true);loadData(seed).then(x=>{if(active)setData(normalizeData(x))}).catch(e=>{if(active)setError(e.message||'Não foi possível carregar os dados.')}).finally(()=>{if(active){setHasLoaded(true);setBusy(false)}});return()=>{active=false}},[]);const save=next=>{const n=normalizeData(next);setData(n);persistData(n).catch(e=>setError(e.message||'Erro ao sincronizar dados.'))};return{data,save,busy,error,setError,hasLoaded}}"
old_session_safe = "function useFinance(){const[hasLoaded,setHasLoaded]=useState(false),[data,setData]=useState(seed),[busy,setBusy]=useState(false),[error,setError]=useState('');useEffect(()=>{let active=true;setBusy(true);getSession().then(()=>loadData(seed)).then(x=>{if(active)setData(normalizeData(x))}).catch(e=>{if(active)setError(e.message||'Não foi possível carregar os dados.')}).finally(()=>{if(active){setHasLoaded(true);setBusy(false)}});return()=>{active=false}},[]);const save=next=>{const n=normalizeData(next);setData(n);persistData(n).catch(e=>setError(e.message||'Erro ao sincronizar dados.'))};return{data,save,busy,error,setError,hasLoaded}}"
new_hook = "function useFinance(session){const[hasLoaded,setHasLoaded]=useState(false),[data,setData]=useState(seed),[busy,setBusy]=useState(false),[error,setError]=useState('');useEffect(()=>{let active=true;if(session===undefined){setHasLoaded(false);return()=>{active=false}};if(!session){setData(seed);setHasLoaded(true);setBusy(false);setError('');return()=>{active=false}};setHasLoaded(false);setBusy(true);loadData(seed).then(x=>{if(active)setData(normalizeData(x))}).catch(e=>{if(active)setError(e.message||'Não foi possível carregar os dados.')}).finally(()=>{if(active){setHasLoaded(true);setBusy(false)}});return()=>{active=false}},[session?.user?.id]);const save=next=>{const n=normalizeData(next);setData(n);persistData(n).catch(e=>setError(e.message||'Erro ao sincronizar dados.'))};return{data,save,busy,error,setError,hasLoaded}}"

if old_session_safe in s:
    s = s.replace(old_session_safe, new_hook, 1)
elif old_legacy in s:
    s = s.replace(old_legacy, new_hook, 1)
else:
    raise SystemExit('Expected Finance hook variant not found; refusing to alter unknown source')

# Make the App use the auth session as the data-loading key without relying on
# the exact declaration shape produced by other build patches.
old_use = "const{data,save,busy,error,setError,hasLoaded}=useFinance()"
new_use = "const[session,setSession]=useState(undefined),{data,save,busy,error,setError,hasLoaded}=useFinance(session)"
if old_use in s:
    s = s.replace(old_use, new_use, 1)
    # Remove the old duplicate session state that follows the month state.
    s = s.replace(",[session,setSession]=useState(undefined)", "", 1)
elif 'useFinance(session)' not in s:
    raise SystemExit('Expected App finance hook call not found')

p.write_text(s)
print('Auth/data reload patch applied: logout clears only the session; login reloads the same user data from Supabase.')
