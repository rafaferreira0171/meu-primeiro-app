from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

helper = "const effectiveFluxo=f=>{const out={...f};for(const k of (f?.excluidas||[]))out[k]=0;return out}\n"
if 'const effectiveFluxo=' not in s:
    s = s.replace("const BRL=n=>(Number(n)||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'})\n", "const BRL=n=>(Number(n)||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'})\n" + helper)

start = s.index('function Fluxo(')
end = s.index('function Prestadores(', start)
new_fluxo = r'''function Fluxo({data,month,setMonth,updateFlux,addSeries,updateSeries,stopSeries}){const f=data.fluxo.find(x=>x.month===month)||{},ef=effectiveFluxo(f),extras=data.entradas.filter(x=>x.month===month&&x.ativo!==false),custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false),fm=calcFluxoMonth(ef,data.prestadores.filter(p=>p.month===month&&p.ativo!==false),custom,extras);const excluded=new Set(f.excluidas||[]);const toggleFixed=k=>{const next=new Set(f.excluidas||[]);if(next.has(k))next.delete(k);else next.add(k);updateFlux({excluidas:[...next]})};return <><div className="toolbar"><MonthSelect month={month} setMonth={setMonth} months={data.fluxo.map(x=>x.month)}/></div><div className="kpis"><Kpi t="Entradas" v={fm.entries}/><Kpi t="Despesas" v={fm.expenses}/><Kpi t="Saldo" v={fm.balance}/></div><div className="grid2"><Section title="Entradas"><Row label="Salário" value={f.salario} onChange={v=>updateFlux({salario:v})}/><Row label="VA" value={f.va} onChange={v=>updateFlux({va:v})}/>{extras.map(x=><Row key={x.id} label={x.nome} value={x.valor} onChange={v=>updateSeries('entradas',x.id,{valor:v})} action={<button className="ghost" onClick={()=>stopSeries('entradas',x.series_id||x.id)}>Encerrar</button>}/>)}<button className="secondary" onClick={()=>{const n=prompt('Nome da nova entrada');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('entradas',n,v)}}}>+ Nova entrada</button><div className="total">Total <b>{BRL(fm.entries)}</b></div></Section><Section title="Despesas"><div className="note">Prestadores são calculados automaticamente. Imposto é editável. Excluir uma despesa fixa vale somente para este mês.</div>{FLUXO_FIELDS.map(([k,l])=><Row key={k} label={l} value={f[k]} onChange={v=>updateFlux({[k]:v})} action={<button className="ghost" onClick={()=>toggleFixed(k)}>{excluded.has(k)?'Incluir':'Excluir'}</button>}/>)}{custom.map(x=><Row key={x.id} label={x.nome} value={x.valor} onChange={v=>updateSeries('despesas',x.id,{valor:v})} action={<button className="ghost" onClick={()=>stopSeries('despesas',x.series_id||x.id)}>Encerrar</button>}/>)}<Row label="Prestadores de Serviço" value={fm.employeeTotal} auto/><Row label="Imposto" value={f.imposto??fm.tax} onChange={v=>updateFlux({imposto:v})}/><button className="secondary" onClick={()=>{const n=prompt('Nome da nova despesa');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('despesas',n,v)}}}>+ Nova conta</button></Section></div></>}
'''
s = s[:start] + new_fluxo + s[end:]

# Transfer selection must respect month-only exclusions and include provider total.
old = "function transferOptions(data,month){const f=data.fluxo.find(x=>x.month===month)||{},fixed=FLUXO_FIELDS.map(([key,label])=>({id:`fluxo:${key}`,label,value:Number(f[key]||0)})),custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false).map(x=>({id:`despesa:${x.id}`,label:x.nome,value:Number(x.valor||0)}));return [...fixed,...custom].filter(x=>x.value>0)}"
new = "function transferOptions(data,month){const f=data.fluxo.find(x=>x.month===month)||{},ef=effectiveFluxo(f),fixed=FLUXO_FIELDS.map(([key,label])=>({id:`fluxo:${key}`,label,value:Number(ef[key]||0)})),prest=data.prestadores.filter(x=>x.month===month&&x.ativo!==false).reduce((s,x)=>s+totalPrestador(x)*(Number(x.percentual_fluxo??x.pct_fluxo??x.percentual??100)/100),0),custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false).map(x=>({id:`despesa:${x.id}`,label:x.nome,value:Number(x.valor||0)}));const all=[...fixed];if(prest>0)all.push({id:'prestadores:total',label:'Prestadores de Serviço',value:prest});return [...all,...custom].filter(x=>x.value>0)}"
if old not in s:
    raise SystemExit('transferOptions pattern not found')
s = s.replace(old, new)

# Make Dashboard calculations honor month-only exclusions.
s = s.replace('calcFluxoMonth(f,prest,despesas,entradas)', 'calcFluxoMonth(effectiveFluxo(f),prest,despesas,entradas)')
s = s.replace("const expenseMap=new Map(),f=data.fluxo.find(x=>x.month===refMonth)||{};", "const expenseMap=new Map(),f=effectiveFluxo(data.fluxo.find(x=>x.month===refMonth)||{});")

p.write_text(s)
print('Applied month-only exclusion for fixed Fluxo expenses')
