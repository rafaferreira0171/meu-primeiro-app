from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

old_update_null = "const updateFlux=p=>save({...data,fluxo:data.fluxo.map(x=>{if(p.__delete&&x.month>=month){const y={...x};for(const k of p.__delete)y[k]=null;return y}return x.month===month?{...x,...p}:x})});"
old_update_base = "const updateFlux=p=>save({...data,fluxo:data.fluxo.map(x=>x.month===month?{...x,...p}:x)});"
old_update_delete = "const updateFlux=p=>save({...data,fluxo:data.fluxo.map(x=>{if(p.__delete&&x.month>=month){const y={...x};for(const k of p.__delete)delete y[k];return y}return x.month===month?{...x,...p}:x})});"
new_update = "const updateFlux=p=>{if(p.__delete){const keys=p.__delete;const stateRows=keys.map(k=>({id:crypto.randomUUID(),series_id:`__fixed_state__:${k}`,month,nome:`__fixed_state__:${k}`,valor:0,ativo:false}));const fluxo=data.fluxo.map(x=>{if(x.month<month)return x;const y={...x};for(const k of keys)y[k]=0;return y});const names=keys.map(k=>`__fixed_state__:${k}`);save({...data,fluxo,entradas:[...data.entradas.filter(x=>!(names.includes(String(x.nome||'').toLowerCase())&&x.month>=month)&&!(String(x.nome||'').toLowerCase().startsWith('__fixed__:')&&x.month>=month)),...stateRows]});return}save({...data,fluxo:data.fluxo.map(x=>x.month===month?{...x,...p}:x)});};"
if old_update_null in s:
    s = s.replace(old_update_null, new_update, 1)
elif old_update_base in s:
    s = s.replace(old_update_base, new_update, 1)
elif old_update_delete in s:
    s = s.replace(old_update_delete, new_update, 1)
else:
    s, count = re.subn(r'const updateFlux=p=>save\(\{\.\.\.data,fluxo:data\.fluxo\.map\(x=>x\.month===month\?\{\.\.\.x,\.\.\.p\}:x\)\}\);', new_update, s, count=1)
    if count == 0 and new_update not in s:
        raise SystemExit('Fluxo update function pattern not found')

old_add_simple = "const addSeries=(field,nome,valor)=>{const id=crypto.randomUUID();const numericValue=parseMoney(valor);save({...data,[field]:[...data[field],{id,series_id:id,month,nome,valor:numericValue,ativo:true}]})};"
old_add_special = "const addSeries=(field,nome,valor)=>{const numericValue=parseMoney(valor);const normalized=String(nome||'').trim().toLowerCase();if(field==='entradas'&&(normalized==='salário'||normalized==='salario'||normalized==='va')){const key=normalized==='va'?'va':'salario';save({...data,fluxo:data.fluxo.map(x=>x.month>=month?{...x,[key]:numericValue}:x)});return}const id=crypto.randomUUID();save({...data,[field]:[...data[field],{id,series_id:id,month,nome,valor:numericValue,ativo:true}]})};"
new_add = "const addSeries=(field,nome,valor)=>{const id=crypto.randomUUID();const numericValue=parseMoney(valor);const normalized=String(nome||'').trim().toLowerCase();if(field==='entradas'&&(normalized==='salário'||normalized==='salario'||normalized==='va')){const key=normalized==='va'?'va':'salario';const stateName=`__fixed_state__:${key}`;const cleanEntries=data.entradas.filter(x=>!(String(x.nome||'').toLowerCase()===stateName&&x.month>=month)&&!(String(x.nome||'').toLowerCase()===`__fixed__:${key}`&&x.month>=month));save({...data,fluxo:data.fluxo.map(x=>x.month>=month?{...x,[key]:numericValue}:x),entradas:[...cleanEntries,{id,series_id:stateName,month,nome:stateName,valor:numericValue,ativo:true}]});return}save({...data,[field]:[...data[field],{id,series_id:id,month,nome,valor:numericValue,ativo:true}]})};"
if old_add_simple in s:
    s = s.replace(old_add_simple, new_add, 1)
elif old_add_special in s:
    s = s.replace(old_add_special, new_add, 1)
elif new_add not in s:
    raise SystemExit('addSeries pattern not found')

start = s.find('function Fluxo(')
end = s.find('\nfunction Prestadores(', start)
if start < 0 or end < 0:
    raise SystemExit('Fluxo component boundaries not found')

new_fluxo = r'''function Fluxo({data,save,month,setMonth,updateFlux,addSeries,updateSeries,stopSeries}){const f=data.fluxo.find(x=>x.month===month)||{},fixedEvents=data.entradas.filter(x=>{const n=String(x.nome||'').toLowerCase();return (n.startsWith('__fixed_state__:')||n.startsWith('__fixed__:'))&&x.month<=month}).sort((a,b)=>a.month.localeCompare(b.month)),fixedDeleted=k=>{const state=fixedEvents.filter(x=>String(x.nome||'').toLowerCase()===`__fixed_state__:${k}`);const legacy=fixedEvents.filter(x=>String(x.nome||'').toLowerCase()===`__fixed__:${k}`);const e=[...legacy,...state].sort((a,b)=>a.month.localeCompare(b.month)).at(-1);return e?.nome?.toLowerCase().startsWith('__fixed__:')?e.ativo===false:e?.ativo===false},extras=data.entradas.filter(x=>x.month===month&&x.ativo!==false&&!String(x.nome||'').toLowerCase().startsWith('__fixed_state__:')&&!String(x.nome||'').toLowerCase().startsWith('__fixed__:')&&!['salário','salario','va'].includes(String(x.nome||'').trim().toLowerCase())),custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false),prest=data.prestadores.filter(p=>p.month===month&&p.ativo!==false),fm=calcFluxoMonth(f,prest,custom,extras);const removeFixed=k=>updateFlux({__delete:[k]});const removeSeries=(field,id)=>{const row=data[field].find(x=>x.id===id);const sid=row?.series_id||id;if(!sid)return;save({...data,[field]:data[field].map(x=>(x.series_id||x.id)===sid&&x.month>=month?{...x,ativo:false}:x)})};const deleteButton=(field,x)=><button type="button" className="series-delete" title="Excluir a partir deste mês" aria-label={`Excluir ${x.nome} a partir deste mês`} onClick={()=>removeSeries(field,x.id)}>×</button>;const fixedEntries=[['salario','Salário'],['va','VA']].filter(([k])=>!fixedDeleted(k));const fixedExpenses=FLUXO_FIELDS.filter(([k])=>!fixedDeleted(k));return <><div className="toolbar"><MonthSelect month={month} setMonth={setMonth} months={data.fluxo.map(x=>x.month)}/></div><div className="kpis"><Kpi t="Entradas" v={fm.entries}/><Kpi t="Despesas" v={fm.expenses}/><Kpi t="Saldo" v={fm.balance}/></div><div className="grid2"><Section title="Entradas">{fixedEntries.map(([k,l])=><div className="row series-row" key={k}><button type="button" className="series-delete" title="Excluir a partir deste mês" aria-label={`Excluir ${l} a partir deste mês`} onClick={()=>removeFixed(k)}>×</button><span>{l}</span><input type="number" value={Number(f[k]||0)} onChange={e=>updateFlux({[k]:Number(e.target.value)||0})}/></div>)}{extras.map(x=><div className="row series-row" key={x.id}>{deleteButton('entradas',x)}<span>{x.nome}</span><input type="number" value={Number(x.valor||0)} onChange={e=>updateSeries('entradas',x.id,{valor:Number(e.target.value)||0})}/></div>)}<button className="secondary" onClick={()=>{const n=prompt('Nome da nova entrada');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('entradas',n,v)}}}>+ Nova entrada</button><div className="total">Total <b>{BRL(fm.entries)}</b></div></Section><Section title="Despesas"><div className="note">Excluir remove a partir deste mês e preserva os meses anteriores.</div>{fixedExpenses.map(([k,l])=><div className="row series-row" key={k}><button type="button" className="series-delete" title="Excluir a partir deste mês" aria-label={`Excluir ${l} a partir deste mês`} onClick={()=>removeFixed(k)}>×</button><span>{l}</span><input type="number" value={Number(f[k]||0)} onChange={e=>updateFlux({[k]:Number(e.target.value)||0})}/></div>)}{custom.map(x=><div className="row series-row" key={x.id}>{deleteButton('despesas',x)}<span>{x.nome}</span><input type="number" value={Number(x.valor||0)} onChange={e=>updateSeries('despesas',x.id,{valor:Number(e.target.value)||0})}/></div>)}<Row label="Prestadores de Serviço" value={fm.employeeTotal} auto/><button className="secondary" onClick={()=>{const n=prompt('Nome da nova despesa');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('despesas',n,v)}}}>+ Nova conta</button></Section></div></>}
'''
s = s[:start] + new_fluxo + s[end:]

old_render = "<Fluxo data={data} month={month} setMonth={setMonth} updateFlux={updateFlux} addSeries={addSeries} updateSeries={updateSeries} stopSeries={stopSeries}/>"
new_render = "<Fluxo data={data} save={save} month={month} setMonth={setMonth} updateFlux={updateFlux} addSeries={addSeries} updateSeries={updateSeries} stopSeries={stopSeries}/>"
if old_render in s:
    s = s.replace(old_render, new_render, 1)
elif 'save={save} month={month} setMonth={setMonth} updateFlux={updateFlux}' not in s:
    raise SystemExit('Fluxo render call pattern not found')

p.write_text(s)
print('Fluxo fixed-field deletion now uses independent per-field state markers for Salário and VA.')