from pathlib import Path

p = Path('src/styles.css')
s = p.read_text()
old = '.login input{width:100%;padding:12px 13px;border:1px solid #dfe4eb;border-radius:10px;margin-bottom:10px;min-height:44px}'
new = '.login input{width:100%;padding:12px 13px;border:1px solid #dfe4eb;border-radius:10px;margin-bottom:10px;min-height:44px;font-size:16px;-webkit-text-size-adjust:100%}'
if old in s:
    s = s.replace(old, new, 1)
elif new in s:
    print('iPhone login style patch already applied; leaving it unchanged')
else:
    raise SystemExit('Login input style pattern is neither legacy nor already patched')
p.write_text(s)
print('iPhone login inputs are now 16px to prevent Safari auto-zoom.')
