from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

# Onboarding adds showOnboarding to the App hook declaration. Match the
# post-onboarding shape first, with a fallback for the pre-onboarding shape.
old_app = "function App(){const{data,save,busy,error,setError,hasLoaded}=useFinance(),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[session,setSession]=useState(undefined),[confirm,setConfirm]=useState(null),[showOnboarding,setShowOnboarding]=useState(false);"
new_app = old_app + "useEffect(()=>{setMonth(currentMonth())},[tab]);"

if "useEffect(()=>{setMonth(currentMonth())},[tab]);" not in s:
    if old_app in s:
        s = s.replace(old_app, new_app, 1)
    else:
        old_app_legacy = "function App(){const{data,save,busy,error,setError,hasLoaded}=useFinance(),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[session,setSession]=useState(undefined),[confirm,setConfirm]=useState(null);"
        if old_app_legacy not in s:
            raise SystemExit('App month initialization pattern not found')
        s = s.replace(old_app_legacy, old_app_legacy + "useEffect(()=>{setMonth(currentMonth())},[tab]);", 1)

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
