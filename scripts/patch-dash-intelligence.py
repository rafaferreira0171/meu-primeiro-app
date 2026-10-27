# LookLiP Dash intelligence patch v2
# Trigger validation: expense intelligence patch
# Trigger validation pass 2
from pathlib import Path
import re

p=Path('src/main.jsx')
s=p.read_text()
start=s.index('function DashFluxo(')
end=s.index('function DashBudget(', start)
new='''function DashFluxo({data}){
  const months=planningMonths(currentMonth(),12)
  const month=currentMonth()
  const rows=months.map(m=>{
    const f=data.fluxo.find(x=>x.month===m)||{}
    const prest=data.prestadores.filter(x=>x.month===m&&x.ativo!==false)
    const entradas=data.entradas.filter(x=>x.month===m&&x.ativo!==false)
    const despesas=data.despesas.filter(x=>x.month===m&&x.ativo!==false)
    return {m,...calcFluxoMonth(f,prest,despesas,entradas)}
  })
  const current=rows.find(x=>x.m===month)||rows[0]
  const expenseMap=new Map()
  const f=data.fluxo.find(x=>x.month===month)||{}
  FLUXO_FIELDS.forEach(([key,label])=>{const v=Number(f[key]||0);if(v)expenseMap.set(label,v)})
  data.despesas.filter(x=>x.month===month&&x.ativo!==false).forEach(x=>{const v=Number(x.valor||0);expenseMap.set(x.nome,(expenseMap.get(x.nome)||0)+v)})
  const prestadores=data.prestadores.filter(x=>x.month===month&&x.ativo!==false)
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
  return <div className="dash-content">
    <div className="kpis"><Kpi t="Entradas do mês" v={current.entries}/><Kpi t="Despesas do mês" v={current.expenses}/><Kpi t="Saldo do mês" v={current.balance}/><Kpi t="Comprometimento" v={current.entries?current.expenses/current.entries*100:0}/></div>
    <div className="grid2">
      <Section title="Leitura executiva"><div className="insight-grid"><div><span>Saldo médio futuro</span><strong>{BRL(avgFuture)}</strong></div><div><span>Melhor mês</span><strong>{best.m} · {BRL(best.balance)}</strong></div><div><span>Pior mês</span><strong>{worst.m} · {BRL(worst.balance)}</strong></div><div><span>Meses negativos</span><strong>{negative} de {rows.length}</strong></div><div><span>Concentração Top 3</span><strong>{fixedTotal?(top3/fixedTotal*100).toFixed(1):'0.0'}%</strong></div></div></Section>
      <Section title="Maiores despesas do mês"><div className="ranking">{top.map(([name,value],i)=><div className="rank-row" key={name}><span><b>{i+1}</b>{name}</span><strong>{BRL(value)}</strong></div>)}{!top.length&&<div className="empty">Nenhuma despesa registrada.</div>}</div></Section>
    </div>
    <Section title="Fluxo projetado · 12 meses"><div className="trend">{rows.map(x=><div className={x.balance<0?'trend-item negative':'trend-item'} key={x.m}><span>{x.m.slice(5)}</span><i style={{height:`${Math.max(8,Math.min(100,Math.abs(x.balance)/(Math.max(...rows.map(r=>Math.abs(r.balance)),1))*100))}%`}}/><b>{BRL(x.balance)}</b></div>)}</div></Section>
    <Section title="Visão mensal"><div className="table-wrap"><table><thead><tr><th>Mês</th><th>Entradas</th><th>Despesas</th><th>Saldo</th></tr></thead><tbody>{rows.map(x=><tr key={x.m}><td>{x.m}</td><td>{BRL(x.entries)}</td><td>{BRL(x.expenses)}</td><td className={x.balance<0?'negative':''}>{BRL(x.balance)}</td></tr>)}</tbody></table></div></Section>
  </div>
}
'''
p.write_text(s[:start]+new+s[end:])
print('patched DashFluxo')
