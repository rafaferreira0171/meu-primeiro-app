from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

# Reapply the signup confirmation UI first. That patch rewrites only Login,
# so the auth startup hardening below is guaranteed to be the final auth edit.
exec(Path('scripts/patch-auth-confirmation.py').read_text(), {'__name__': '__patch_auth_confirmation__'})
s = p.read_text()

# Add a hard timeout directly around the real getSession() call. This avoids
# depending on the exact formatting of the App initializer restored upstream.
if 'Promise.race([' not in s or 'setTimeout(()=>resolve(null),5000)' not in s:
    updated, count = re.subn(
        r'getSession\(\)\.then\(',
        'Promise.race([getSession(),new Promise(resolve=>setTimeout(()=>resolve(null),5000))]).then(',
        s,
        count=1,
    )
    if count != 1:
        raise SystemExit('Expected getSession initializer not found; refusing to alter unknown source')
    s = updated

# Never let finance-data loading block the logged-out login screen.
old_gate = "if(session===undefined||!hasLoaded)return <Splash/>;if(!session&&!hasSupabaseConfig()){}else if(!session&&hasSupabaseConfig())return <Login/>;"
new_gate = "if(session===undefined)return <Splash/>;if(!session&&!hasSupabaseConfig()){}else if(!session&&hasSupabaseConfig())return <Login/>;if(!hasLoaded)return <Splash/>;"
if old_gate in s:
    s = s.replace(old_gate, new_gate, 1)
elif new_gate not in s:
    raise SystemExit('Expected auth loading gate not found; refusing to alter unknown source')

s = s.replace('<p>Conta independente do Base44.</p>', '')
s = s.replace('Conta independente do Base44.', '')

p.write_text(s)
print('Auth startup hardened with a direct getSession timeout; signup confirmation resend preserved; Base44 branding removed.')
