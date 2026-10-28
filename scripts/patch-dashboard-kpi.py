from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()
old = "function Kpi({t,v,kind}){return <div className=\"kpi\"><span>{t}</span><strong>{kind==='count'?Number(v||0):t.toLowerCase().includes('compromet')?`${Number(v||0).toFixed(1)}%`:BRL(v)}</strong></div>}"
new = "function Kpi({t,v,kind}){const label=t.toLowerCase();const percent=label.includes('compromet')||label.includes('utiliza');return <div className=\"kpi\"><span>{t}</span><strong>{kind==='count'?Number(v||0):percent?`${Number(v||0).toFixed(1)}%`:BRL(v)}</strong></div>}"
if old not in s:
    raise SystemExit('Kpi target not found')
p.write_text(s.replace(old,new,1))
print('Dashboard KPI percentage formatting applied')
