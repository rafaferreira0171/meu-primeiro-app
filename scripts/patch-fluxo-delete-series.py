from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

start = s.find('function Fluxo(')
end = s.find('\nfunction Prestadores(', start)
if start < 0 or end < 0:
    raise SystemExit('Fluxo component boundaries not found')

new_fluxo = r'''function Fluxo({data,month,setMonth,updateFlux,addSeries,updateSeries,stopSeries}){const f=data.fluxo.find(x=>x.month===month)||{},extras=data.entradas.filter(x=>x.month===month&&x.ativo!==false),custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false),fm=calcFluxoMonth(f,data.prestadores.filter(p=>p.month===month&&p.ativo!==false),custom,extras);const deleteButton=(field,x)=> <button type="button" className="series-delete" title="Excluir a partir do próximo mês" aria-label={`Excluir ${x.nome} a partir do próximo mês`} onClick={()=>stopSeries(field,x.series_id||x.id)}>×</button>;return <><div className="toolbar"><MonthSelect month={month} setMonth={setMonth} months={data.fluxo.map(x=>x.month)}/></div><div className="kpis"><Kpi t="Entradas" v={fm.entries}/><Kpi t="Despesas" v={fm.expenses}/><Kpi t="Saldo" v={fm.balance}/></div><div className="grid2"><Section title="Entradas"><Row label="Salário" value={f.salario} onChange={v=>updateFlux({salario:v})}/><Row label="VA" value={f.va} onChange={v=>updateFlux({va:v})}/>{extras.map(x=><div className="row series-row" key={x.id}>{deleteButton('entradas',x)}<span>{x.nome}</span><input type="number" value={Number(x.valor||0)} onChange={e=>updateSeries('entradas',x.id,{valor:Number(e.target.value)||0})}/></div>)}<button className="secondary" onClick={()=>{const n=prompt('Nome da nova entrada');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('entradas',n,v)}}}>+ Nova entrada</button><div className="total">Total <b>{BRL(fm.entries)}</b></div></Section><Section title="Despesas"><div className="note">Prestadores entram automaticamente. Encerrar preserva o histórico.</div>{FLUXO_FIELDS.map(([k,l])=><Row key={k} label={l} value={f[k]} onChange={v=>updateFlux({[k]:v})}/>)}{custom.map(x=><div className="row series-row" key={x.id}>{deleteButton('despesas',x)}<span>{x.nome}</span><input type="number" value={Number(x.valor||0)} onChange={e=>updateSeries('despesas',x.id,{valor:Number(e.target.value)||0})}/></div>)}<Row label="Prestadores de Serviço" value={fm.employeeTotal} auto/><button className="secondary" onClick={()=>{const n=prompt('Nome da nova despesa');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('despesas',n,v)}}}>+ Nova conta</button></Section></div></>}
'''

s = s[:start] + new_fluxo + s[end:]
p.write_text(s)
print('Fluxo now has left-side delete buttons for recurring entries and custom expenses.')
