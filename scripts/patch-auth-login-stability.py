from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

old = "useEffect(()=>{let active=true;getSession().then(s=>{if(active)setSession(s)}).catch(()=>{if(active)setSession(null)});const s=onAuthStateChange(setSession);return()=>{active=false;s.data.subscription.unsubscribe()}},[])"
new = "useEffect(()=>{let active=true;const timeout=new Promise(resolve=>setTimeout(()=>resolve(null),5000));Promise.race([getSession(),timeout]).then(s=>{if(active)setSession(s)}).catch(()=>{if(active)setSession(null)});const s=onAuthStateChange(setSession);return()=>{active=false;s.data.subscription.unsubscribe()}},[])"
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('Expected auth session initializer not found; refusing to alter unknown source')

s = s.replace('<p>Conta independente do Base44.</p>', '')
s = s.replace('Conta independente do Base44.', '')

p.write_text(s)
print('Auth startup hardened: login screen appears if session lookup takes too long; Base44 branding removed.')
