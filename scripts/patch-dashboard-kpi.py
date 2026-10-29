from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

# Optional formatting enhancement. The restored Finance component can expose
# a different Kpi implementation, so this patch must not block a production
# Pages build when its historical text target is absent.
old = "function Kpi({t,v,kind}){return <div className=\"kpi\"><span>{t}</span><strong>{kind==='count'?Number(v||0):t.toLowerCase().includes('compromet')?`${Number(v||0).toFixed(1)}%`:BRL(v)}</strong></div>}"
new = "function Kpi({t,v,kind}){const label=t.toLowerCase();const percent=label.includes('compromet')||label.includes('utiliza');return <div className=\"kpi\"><span>{t}</span><strong>{kind==='count'?Number(v||0):percent?`${Number(v||0).toFixed(1)}%`:BRL(v)}</strong></div>}"
if old in s:
    p.write_text(s.replace(old,new,1))
    print('Dashboard KPI percentage formatting applied')
else:
    print('Dashboard KPI target is already absent; skipping optional KPI enhancement')
