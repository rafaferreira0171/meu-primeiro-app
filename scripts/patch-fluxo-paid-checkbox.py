from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

fluxo = r'''function Fluxo({data,month,setMonth,updateFlux,addSeries,updateSeries,stopSeries,userId}){const f=data.fluxo.find(x=>x.month===month)||{},extras=data.entradas.filter(x=>x.month===month&&x.ativo!==false),custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false),fm=calcFluxoMonth(f,data.prestadores.filter(p=>p.month===month&&p.ativo!==false),custom,extras),storageKey=`looklip-fluxo-paid:${userId||'demo'}`,[paid,setPaid]=useState(()=>{try{return JSON.parse(localStorage.getItem(storageKey)||'{}')}catch{return {}}});const togglePaid=key=>setPaid(prev=>{const next={...prev,[`${month}:${key}`]:!prev[`${month}:${key}`]};try{localStorage.setItem(storageKey,JSON.stringify(next))}catch{}return next});const isPaid=key=>paid[`${month}:${key}`]===true;const paidAction=key=><label className="paid-check"><input type="checkbox" checked={isPaid(key)} onChange={()=>togglePaid(key)}/><span>Pago</span></label>;return <><div className="toolbar"><MonthSelect month={month} setMonth={setMonth} months={data.fluxo.map(x=>x.month)}/></div><div className="kpis"><Kpi t="Entradas" v={fm.entries}/><Kpi t="Despesas" v={fm.expenses}/><Kpi t="Saldo" v={fm.balance}/></div><div className="grid2"><Section title="Entradas"><Row label="Salário" value={f.salario} onChange={v=>updateFlux({salario:v})}/><Row label="VA" value={f.va} onChange={v=>updateFlux({va:v})}/>{extras.map(x=><Row key={x.id} label={x.nome} value={x.valor} onChange={v=>updateSeries('entradas',x.id,{valor:v})} action={<button className="ghost" onClick={()=>stopSeries('entradas',x.series_id||x.id)}>Encerrar</button>}/>)}<button className="secondary" onClick={()=>{const n=prompt('Nome da nova entrada');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('entradas',n,v)}}}>+ Nova entrada</button><div className="total">Total <b>{BRL(fm.entries)}</b></div></Section><Section title="Despesas"><div className="note">Marque as contas já pagas. A marcação é independente dos cálculos do Fluxo.</div>{FLUXO_FIELDS.map(([k,l])=><Row key={k} label={l} value={f[k]} onChange={v=>updateFlux({[k]:v})} action={paidAction(`fixed:${k}`)}/>)}{custom.map(x=><Row key={x.id} label={x.nome} value={x.valor} onChange={v=>updateSeries('despesas',x.id,{valor:v})} action={<>{paidAction(`despesa:${x.id}`)}<button className="ghost" onClick={()=>stopSeries('despesas',x.series_id||x.id)}>Encerrar</button></>}/>)}<Row label="Prestadores de Serviço" value={fm.employeeTotal} auto action={paidAction('prestadores')}/><button className="secondary" onClick={()=>{const n=prompt('Nome da nova despesa');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('despesas',n,v)}}}>+ Nova conta</button></Section></div></>}'''

pattern = r"function Fluxo\(\{.*?\}\n(?=function Prestadores\()"
s2, n = re.subn(pattern, fluxo + "\n", s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Fluxo component marker not found')
s = s2

mount = '<Fluxo data={data} save={save} month={month} setMonth={setMonth} updateFlux={updateFlux} addSeries={addSeries} updateSeries={updateSeries} stopSeries={stopSeries}/>'
mount_new = '<Fluxo data={data} month={month} setMonth={setMonth} updateFlux={updateFlux} addSeries={addSeries} updateSeries={updateSeries} stopSeries={stopSeries} userId={session?.user?.id}/>'
if mount in s:
    s = s.replace(mount, mount_new, 1)
else:
    mount = '<Fluxo data={data} month={month} setMonth={setMonth} updateFlux={updateFlux} addSeries={addSeries} updateSeries={updateSeries} stopSeries={stopSeries}/>'
    if mount not in s:
        raise SystemExit('Fluxo mount marker not found')
    s = s.replace(mount, mount_new, 1)

p.write_text(s)

cssp = Path('src/styles.css')
css = cssp.read_text()
if '.paid-check{' not in css:
    css += '\n.paid-check{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;white-space:nowrap;cursor:pointer}.paid-check input{width:16px;height:16px;margin:0;accent-color:#1f9d55}.paid-check input:checked+span{color:#1f9d55}\n'
    cssp.write_text(css)

print('Fluxo paid checkbox applied with per-user/per-month local persistence.')
