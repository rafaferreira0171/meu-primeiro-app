from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

# The selected month is the only month affected. Fixed fields are physically
# removed from that month's Fluxo object; other months keep their values.
s = re.sub(r"const effectiveFluxo=.*?\n", "const effectiveFluxo=f=>f||{}\n", s, count=1)

old = "const updateFlux=p=>save({...data,fluxo:data.fluxo.map(x=>x.month===month?{...x,...p}:x)});"
new = "const updateFlux=p=>save({...data,fluxo:data.fluxo.map(x=>{if(x.month!==month)return x;const y={...x,...p};for(const k of (p.__delete||[]))delete y[k];delete y.__delete;return y})});"
if old in s:
    s = s.replace(old, new, 1)

start = s.index('function Fluxo(')
end = s.index('function Prestadores(', start)
new_fluxo = r'''function Fluxo({data,month,setMonth,updateFlux,addSeries,updateSeries,stopSeries}){
  const f=data.fluxo.find(x=>x.month===month)||{}
  const extras=data.entradas.filter(x=>x.month===month&&x.ativo!==false)
  const custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false)
  const prest=data.prestadores.filter(p=>p.month===month&&p.ativo!==false)
  const fm=calcFluxoMonth(effectiveFluxo(f),prest,custom,extras)
  const removeFixed=k=>updateFlux({__delete:[k]})
  const removeSeries=(field,id)=>save({...data,[field]:data[field].map(x=>x.id===id&&x.month===month?{...x,ativo:false}:x)})
  const fixed=FLUXO_FIELDS.filter(([k])=>Object.prototype.hasOwnProperty.call(f,k))
  return <><div className="toolbar"><MonthSelect month={month} setMonth={setMonth} months={data.fluxo.map(x=>x.month)}/></div>
    <div className="kpis"><Kpi t="Entradas" v={fm.entries}/><Kpi t="Despesas" v={fm.expenses}/><Kpi t="Saldo" v={fm.balance}/></div>
    <div className="grid2">
      <Section title="Entradas">
        {Object.prototype.hasOwnProperty.call(f,'salario')&&<Row label="Salário" value={f.salario} onChange={v=>updateFlux({salario:v})} action={<button className="ghost" onClick={()=>removeFixed('salario')}>Excluir</button>}/>} 
        {Object.prototype.hasOwnProperty.call(f,'va')&&<Row label="VA" value={f.va} onChange={v=>updateFlux({va:v})} action={<button className="ghost" onClick={()=>removeFixed('va')}>Excluir</button>}/>} 
        {extras.map(x=><Row key={x.id} label={x.nome} value={x.valor} onChange={v=>updateSeries('entradas',x.id,{valor:v})} action={<button className="ghost" onClick={()=>removeSeries('entradas',x.id)}>Excluir</button>}/>)}
        <button className="secondary" onClick={()=>{const n=prompt('Nome da nova entrada');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('entradas',n,v)}}}>+ Nova entrada</button>
        <div className="total">Total <b>{BRL(fm.entries)}</b></div>
      </Section>
      <Section title="Despesas">
        <div className="note">Prestadores são calculados automaticamente. Imposto é editável. Excluir remove a informação somente deste mês.</div>
        {fixed.map(([k,l])=><Row key={k} label={l} value={f[k]} onChange={v=>updateFlux({[k]:v})} action={<button className="ghost" onClick={()=>removeFixed(k)}>Excluir</button>}/>)}
        {custom.map(x=><Row key={x.id} label={x.nome} value={x.valor} onChange={v=>updateSeries('despesas',x.id,{valor:v})} action={<button className="ghost" onClick={()=>removeSeries('despesas',x.id)}>Excluir</button>}/>)}
        <Row label="Prestadores de Serviço" value={fm.employeeTotal} auto/>
        <button className="secondary" onClick={()=>{const n=prompt('Nome da nova despesa');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('despesas',n,v)}}}>+ Nova conta</button>
      </Section>
    </div>
  </>
}
'''
s = s[:start] + new_fluxo + s[end:]

# Transfer options must use only fields that still exist in the selected month.
if 'function transferOptions(' in s:
    start = s.index('function transferOptions(')
    end = s.index('function transferValue(', start)
    new_transfer = r'''function transferOptions(data,month){const f=data.fluxo.find(x=>x.month===month)||{},fixed=FLUXO_FIELDS.filter(([key])=>Object.prototype.hasOwnProperty.call(f,key)).map(([key,label])=>({id:`fluxo:${key}`,label,value:Number(f[key]||0)})),custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false).map(x=>({id:`despesa:${x.id}`,label:x.nome,value:Number(x.valor||0)})),prestadoresTotal=data.prestadores.filter(x=>x.month===month&&x.ativo!==false).reduce((s,p)=>{const bruto=totalPrestador(p);const pct=Math.min(100,Math.max(0,Number(p.fluxo_percent??100)));return s+bruto*pct/100},0),prestadores=prestadoresTotal>0?[{id:'fluxo:prestadores',label:'Prestadores de Serviço',value:prestadoresTotal}]:[];return [...fixed,...prestadores,...custom].filter(x=>x.value>0)}
'''
    s = s[:start] + new_transfer + s[end:]

s = s.replace('calcFluxoMonth(f,prest,despesas,entradas)', 'calcFluxoMonth(effectiveFluxo(f),prest,despesas,entradas)')
s = s.replace("const expenseMap=new Map(),f=data.fluxo.find(x=>x.month===refMonth)||{};", "const expenseMap=new Map(),f=effectiveFluxo(data.fluxo.find(x=>x.month===refMonth)||{});")

p.write_text(s)
print('Applied true month-only deletion for Fluxo entries and expenses')
