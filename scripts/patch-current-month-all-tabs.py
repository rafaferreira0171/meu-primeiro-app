from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()
old = "function App(){const{data,save,busy,error,setError,hasLoaded}=useFinance(),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[session,setSession]=useState(undefined),[confirm,setConfirm]=useState(null);useEffect(()=>{let active=true;"
new = "function App(){const{data,save,busy,error,setError,hasLoaded}=useFinance(),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[session,setSession]=useState(undefined),[confirm,setConfirm]=useState(null);useEffect(()=>{setMonth(currentMonth())},[tab]);useEffect(()=>{let active=true;"
if old not in s:
    raise SystemExit('App month initialization pattern not found')
s = s.replace(old, new, 1)

# The first render can race with Supabase session restoration. Load the finance
# data only after the auth session is known, so AUTH_REQUIRED is never shown
# as a stale banner after a successful login/confirmation.
old_hook = "function useFinance(){const[hasLoaded,setHasLoaded]=useState(false),[data,setData]=useState(seed),[busy,setBusy]=useState(false),[error,setError]=useState('');useEffect(()=>{let active=true;setBusy(true);loadData(seed).then(x=>{if(active)setData(normalizeData(x))}).catch(e=>{if(active)setError(e.message||'Não foi possível carregar os dados.')}).finally(()=>{if(active){setHasLoaded(true);setBusy(false)}});return()=>{active=false}},[]);"
new_hook = "function useFinance(){const[hasLoaded,setHasLoaded]=useState(false),[data,setData]=useState(seed),[busy,setBusy]=useState(false),[error,setError]=useState('');useEffect(()=>{let active=true;setBusy(true);getSession().then(()=>loadData(seed)).then(x=>{if(active)setData(normalizeData(x))}).catch(e=>{if(active)setError(e.message||'Não foi possível carregar os dados.')}).finally(()=>{if(active){setHasLoaded(true);setBusy(false)}});return()=>{active=false}},[]);"
if old_hook not in s:
    raise SystemExit('useFinance session-race pattern not found')
s = s.replace(old_hook, new_hook, 1)

p.write_text(s)
print('Current month is enforced whenever the user enters or changes a Finance tab, and initial data loading waits for Supabase session restoration.')
