from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

# Deleting a fixed Fluxo field from the selected month onward must be a real
# state change. We intentionally do not persist helper metadata such as
# __deletedFields because that column does not exist in Supabase.
old = "const updateFlux=p=>save({...data,fluxo:data.fluxo.map(x=>x.month===month?{...x,...p}:x)});"
new = "const updateFlux=p=>save({...data,fluxo:data.fluxo.map(x=>{if(p.__delete&&x.month>=month){const y={...x};for(const k of p.__delete)delete y[k];return y}return x.month===month?{...x,...p}:x})});"
if old in s:
    s = s.replace(old, new, 1)
elif "const updateFlux=p=>save({...data,fluxo:data.fluxo.map(x=>{" not in s:
    raise SystemExit('Fluxo update function pattern not found')

# This component is replaced later by patch-fluxo-delete-series.py. Keep the
# existing component here compatible with the future-month deletion semantics.
start = s.index('function Fluxo(')
end = s.index('function Prestadores(', start)
new_fluxo = r'''function Fluxo({data,month,setMonth,updateFlux,addSeries,updateSeries,stopSeries}){
  const f=data.fluxo.find(x=>x.month===month)||{},extras=data.entradas.filter(x=>x.month===month&&x.ativo!==false),custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false),prest=data.prestadores.filter(p=>p.month===month&&p.ativo!==false),fm=calcFluxoMonth(f,prest,custom,extras);
  const removeFixed=k=>updateFlux({__delete:[k]});
  return <><div className="toolbar"><MonthSelect month={month} setMonth={setMonth} months={data.fluxo.map(x=>x.month)}/></div><div className="kpis"><Kpi t="Entradas" v={fm.entries}/><Kpi t="Despesas" v={fm.expenses}/><Kpi t="Saldo" v={fm.balance}/></div><div className="grid2"><Section title="Entradas">{Object.prototype.hasOwnProperty.call(f,'salario')&&<Row label="Salário" value={f.salario} onChange={v=>updateFlux({salario:v})} action={<button className="ghost" onClick={()=>removeFixed('salario')}>Excluir</button>}/>} {Object.prototype.hasOwnProperty.call(f,'va')&&<Row label="VA" value={f.va} onChange={v=>updateFlux({va:v})} action={<button className="ghost" onClick={()=>removeFixed('va')}>Excluir</button>}/>} {extras.map(x=><Row key={x.id} label={x.nome} value={x.valor} onChange={v=>updateSeries('entradas',x.id,{valor:v})}/>}<button className="secondary" onClick={()=>{const n=prompt('Nome da nova entrada');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('entradas',n,v)}}}>+ Nova entrada</button><div className="total">Total <b>{BRL(fm.entries)}</b></div></Section><Section title="Despesas"><div className="note">Prestadores são calculados automaticamente. Excluir remove a partir deste mês e preserva os meses anteriores.</div>{FLUXO_FIELDS.filter(([k])=>Object.prototype.hasOwnProperty.call(f,k)).map(([k,l])=><Row key={k} label={l} value={f[k]} onChange={v=>updateFlux({[k]:v})} action={<button className="ghost" onClick={()=>removeFixed(k)}>Excluir</button>}/>)}{custom.map(x=><Row key={x.id} label={x.nome} value={x.valor} onChange={v=>updateSeries('despesas',x.id,{valor:v})}/>)}<Row label="Prestadores de Serviço" value={fm.employeeTotal} auto/><button className="secondary" onClick={()=>{const n=prompt('Nome da nova despesa');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('despesas',n,v)}}}>+ Nova conta</button></Section></div></>
}
'''
s = s[:start] + new_fluxo + s[end:]
p.write_text(s)
print('Applied future-month Fluxo deletion semantics')
