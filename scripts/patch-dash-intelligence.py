# LookLiP Dash intelligence patch v3
# Keeps history intact and adds year/month reference filtering.
from pathlib import Path

p=Path('src/main.jsx')
s=p.read_text()

# Pass the shared reference month into Dash instead of forcing the current month.
s=s.replace("<Dash data={data}/>","<Dash data={data} month={month} setMonth={setMonth}/>")
s=s.replace("function Dash({data}){","function Dash({data,month,setMonth}){")
s=s.replace("<DashFluxo data={data}/>","<DashFluxo data={data} month={month} setMonth={setMonth}/>")

# Replace the month selector with separate year/month filters while retaining all stored history.
old="function MonthSelect({month,setMonth}){return <label>Mês de referência<select value={month} onChange={e=>setMonth(e.target.value)}>{[...new Set(MONTHS.concat(month))].sort().map(m=><option key={m}>{m}</option>)}</select></label>}"
new="""function MonthSelect({month,setMonth,months=MONTHS}){const all=[...new Set(months.concat(month))].filter(Boolean).sort();const years=[...new Set(all.map(m=>m.slice(0,4)))].sort();const year=month.slice(0,4);const yearMonths=all.filter(m=>m.slice(0,4)===year);const mm=month.slice(5,7);return <div className=\"month-filter\"><label>Ano<select value={year} onChange={e=>{const y=e.target.value;setMonth(all.find(m=>m.startsWith(y))||month)}}>{years.map(y=><option key={y}>{y}</option>)}</select></label><label>Mês<select value={mm} onChange={e=>setMonth(`${year}-${e.target.value}`)}>{yearMonths.map(m=><option key={m} value={m.slice(5,7)}>{m.slice(5,7)}</option>)}</select></label></div>}"""
if old in s:s=s.replace(old,new)

# Make Fluxo expose the complete stored month history to the filter.
s=s.replace("<MonthSelect month={month} setMonth={setMonth}/>","<MonthSelect month={month} setMonth={setMonth} months={data.fluxo.map(x=>x.month)}/>",1)

start=s.index('function DashFluxo(')
end=s.index('function DashBudget(', start)
new_dash='''function DashFluxo({data,month,setMonth}){
  const refMonth=month||currentMonth()
  const months=planningMonths(refMonth,12)
  const rows=months.map(m=>{
    const f=data.fluxo.find(x=>x.month===m)||{}
    const prest=data.prestadores.filter(x=>x.month===m&&x.ativo!==false)
    const entradas=data.entradas.filter(x=>x.month===m&&x.ativo!==false)
    const despesas=data.despesas.filter(x=>x.month===m&&x.ativo!==false)
    return {m,...calcFluxoMonth(f,prest,despesas,entradas)}
  })
  const current=rows.find(x=>x.m===refMonth)||rows[0]
  const expenseMap=new Map()
  const f=data.fluxo.find(x=>x.month===refMonth)||{}
  FLUXO_FIELDS.forEach(([key,label])=>{const v=Number(f[key]||0);if(v)expenseMap.set(label,v)})
  data.despesas.filter(x=>x.month===refMonth&&x.ativo!==false).forEach(x=>{const v=Number(x.valor||0);expenseMap.set(x.nome,(expenseMap.get(x.nome)||0)+v)})
  const prestadores=data.prestadores.filter(x=>x.month===refMonth&&x.ativo!==false)
  const prestTotal=prestadores.reduce((s,x)=>s+totalPrestador(x),0)
  if(prestTotal)expenseMap.set('Prestadores de Serviço',prestTotal)
  const tax=Number(current.tax||0)
  if(tax)expenseMap.set('Imposto',tax)
  const top=[...expenseMap.entries()].sort((a,b)=>b[1]-a[1]).slice(0,5)
  const fixedTotal=[...expenseMap.values()].reduce((s,v)=>s+v,0)
  const top3=top.slice(0,3).reduce((s,x)=>s+x[1],0)
  const avgFuture=rows.slice(1).reduce((s,x)=>s+x.balance,0)/Math.max(1,rows.length-1)
  const negative=rows.filter(x=>x.balance<0).length
  const worst=[...rows].sort((a,b)=>a.balance-b.balance)[0]
  const best=[...rows].sort((a,b)=>b.balance-a.balance)[0]
  const historyMonths=data.fluxo.map(x=>x.month)
  return <div className="dash-content">
    <div className="toolbar"><MonthSelect month={refMonth} setMonth={setMonth} months={historyMonths}/></div>
    <div className="kpis"><Kpi t="Entradas do mês" v={current.entries}/><Kpi t="Despesas do mês" v={current.expenses}/><Kpi t="Saldo do mês" v={current.balance}/><Kpi t="Comprometimento" v={current.entries?current.expenses/current.entries*100:0}/></div>
    <div className="grid2">
      <Section title="Leitura executiva"><div className="insight-grid"><div><span>Saldo médio futuro</span><strong>{BRL(avgFuture)}</strong></div><div><span>Melhor mês</span><strong>{best.m} · {BRL(best.balance)}</strong></div><div><span>Pior mês</span><strong>{worst.m} · {BRL(worst.balance)}</strong></div><div><span>Meses negativos</span><strong>{negative} de {rows.length}</strong></div><div><span>Concentração Top 3</span><strong>{fixedTotal?(top3/fixedTotal*100).toFixed(1):'0.0'}%</strong></div></div></Section>
      <Section title="Maiores despesas do mês"><div className="ranking">{top.map(([name,value],i)=><div className="rank-row" key={name}><span><b>{i+1}</b>{name}</span><strong>{BRL(value)}</strong></div>)}{!top.length&&<div className="empty">Nenhuma despesa registrada.</div>}</div></Section>
    </div>
    <Section title={`Fluxo projetado · 12 meses a partir de ${refMonth}`}><div className="trend">{rows.map(x=><div className={x.balance<0?'trend-item negative':'trend-item'} key={x.m}><span>{x.m.slice(5)}</span><i style={{height:`${Math.max(8,Math.min(100,Math.abs(x.balance)/(Math.max(...rows.map(r=>Math.abs(r.balance)),1))*100))}%`}}/><b>{BRL(x.balance)}</b></div>)}</div></Section>
    <Section title="Visão mensal"><div className="table-wrap"><table><thead><tr><th>Mês</th><th>Entradas</th><th>Despesas</th><th>Saldo</th></tr></thead><tbody>{rows.map(x=><tr key={x.m}><td>{x.m}</td><td>{BRL(x.entries)}</td><td>{BRL(x.expenses)}</td><td className={x.balance<0?'negative':''}>{BRL(x.balance)}</td></tr>)}</tbody></table></div></Section>
  </div>
}
'''
s=s[:start]+new_dash+s[end:]
p.write_text(s)
print('patched Dash with historical-safe year/month filter and rolling 12-month projection')
