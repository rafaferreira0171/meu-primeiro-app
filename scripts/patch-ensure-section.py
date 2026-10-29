from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

if 'function Section({' in s:
    print('Section component already present')
    raise SystemExit(0)

component = "function Section({title,children,action}){return <section className=\"card\"><div className=\"section-title\"><h2>{title}</h2>{action}</div>{children}</section>}\n"
marker = 'function Fluxo('
if marker not in s:
    raise SystemExit('Fluxo component marker not found while restoring Section')
s = s.replace(marker, component + marker, 1)
p.write_text(s)
print('Section component restored before Fluxo')
