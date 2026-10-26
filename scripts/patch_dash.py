from pathlib import Path

path = Path('src/main.jsx')
text = path.read_text()
start = text.find('function Dash({data}){')
if start < 0:
    raise SystemExit('Dash function not found')

end = text.find('function App(', start)
if end < 0:
    raise SystemExit('App function not found after Dash')

replacement = '''function Dash({data}){const now=currentMonth(),plannedMonths=planningMonths(now,12),months=[...new Set(data.fluxo.map(x=>x.month))].sort(),rows=months.map(m=>{const f=data.fluxo.find(x=>x.month===m)||{};return{month:m,...calcFluxoMonth(f,data.prestadores.filter(p=>p.month===m&&p.ativo!==false),data.despesas.filter(d=>d.month===m&&d.ativo!==false),data.entradas.filter(e=>e.month===m&&e.ativo!==false))}}),current=rows.find(r=>r.month===now)||{month:now,entries:0,expenses:0,balance:0},planned=rows.filter(r=>plannedMonths.includes(r.month)),future=planned.filter(r=>r.month>now),avg=a=>a.length?a.reduce((s,x)=>s+x,0)/a.length:0,top={};data.despesas.filter(d=>plannedMonths.includes(d.month)&&d.ativo!==false).forEach(d=>top[d.nome]=(top[d.nome]||0)+Number(d.valor||0));const worst=future.length?future.reduce((a,b)=>a.balance<b.balance?a:b):null,best=future.length?future.reduce((a,b)=>a.balance>b.balance?a:b):null,negative=future.filter(r=>r.balance<0).length,commitment=current.entries?current.expenses/current.entries*100:0;return <><div className="kpis"><Kpi t="Entradas do mês" v={current.entries}/><Kpi t="Despesas do mês" v={current.expenses}/><Kpi t="Saldo planejado" v={current.balance}/><Kpi t="Comprometimento" v={commitment}/></div><div className="grid2"><Section title="Planejamento — 12 meses"><div className="note">Janela móvel: {now} + 11 meses. Histórico não é apagado.</div>{planned.map(r=><div className="subcard" key={r.month}><b>{r.month} {r.month===now?'• Atual':'• Planejado'}</b><div className="total">Entradas <b>{BRL(r.entries)}</b></div><div className="total">Despesas <b>{BRL(r.expenses)}</b></div><div className="total">Saldo <b>{BRL(r.balance)}</b></div></div>)}</Section><Section title="Leitura dos próximos meses"><div className="total">Média de entradas futuras <b>{BRL(avg(future.map(x=>x.entries)))}</b></div><div className="total">Média de despesas futuras <b>{BRL(avg(future.map(x=>x.expenses)))}</b></div><div className="total">Saldo médio futuro <b>{BRL(avg(future.map(x=>x.balance)))}</b></div>{worst&&<div className="total">Pior saldo projetado <b>{worst.month} · {BRL(worst.balance)}</b></div>}{best&&<div className="total">Melhor saldo projetado <b>{best.month} · {BRL(best.balance)}</b></div>}{negative>0&&<div className="alert">Atenção: {negative} mês(es) futuro(s) estão projetados com saldo negativo.</div>}</Section></div><Section title="Onde o dinheiro está indo?"><div className="note">Acumulado dos 12 meses planejados, sem incluir transferências.</div>{Object.entries(top).sort((a,b)=>b[1]-a[1]).slice(0,5).map(([n,v])=><div className="total" key={n}>{n}<b>{BRL(v)}</b></div>)}</Section></>}\n'''

path.write_text(text[:start] + replacement + text[end:])
print('Dash patched')
