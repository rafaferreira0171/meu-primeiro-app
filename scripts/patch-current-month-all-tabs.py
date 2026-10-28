from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

# The App declaration is transformed by several earlier build patches. Avoid
# depending on the exact hook list; insert the month-sync effect after the
# declaration's first semicolon instead.
month_effect = "useEffect(()=>{setMonth(currentMonth())},[tab]);"
if month_effect not in s:
    app_start = s.find('function App(){')
    if app_start < 0:
        raise SystemExit('App function marker not found')
    app_end = s.find(';', app_start)
    if app_end < 0:
        raise SystemExit('App declaration terminator not found')
    s = s[:app_end + 1] + month_effect + s[app_end + 1:]

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
