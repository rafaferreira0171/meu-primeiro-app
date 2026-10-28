from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()
old = "function App(){const{data,save,busy,error,setError,hasLoaded}=useFinance(),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[session,setSession]=useState(undefined),[confirm,setConfirm]=useState(null);useEffect(()=>{let active=true;"
new = "function App(){const{data,save,busy,error,setError,hasLoaded}=useFinance(),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[session,setSession]=useState(undefined),[confirm,setConfirm]=useState(null);useEffect(()=>{setMonth(currentMonth())},[tab]);useEffect(()=>{let active=true;"
if old not in s:
    raise SystemExit('App month initialization pattern not found')
s = s.replace(old, new, 1)
p.write_text(s)
print('Current month is enforced whenever the user enters or changes a Finance tab.')
