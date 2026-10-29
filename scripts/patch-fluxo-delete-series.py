from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

# The prior Fluxo patch already owns updateFlux. This patch only adds the UI
# buttons and custom-series propagation, so it remains compatible with the
# future-month fixed-field deletion logic.
start = s.find('function Fluxo(')
end = s.find('\nfunction Prestadores(', start)
if start < 0 or end < 0:
    raise SystemExit('Fluxo component boundaries not found')

new_fluxo = r'''function Fluxo({data,save,month,setMonth,updateFlux,addSeries,updateSeries,stopSeries}){const f=data.fluxo.find(x=>x.month===month)||{},reserved=new Set(['salário','va']),extras=data.entradas.filter(x=>x.month===month&&x.ativo!==false&&!reserved.has(String(x.nome||'').trim().toLowerCase())),custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false),prest=data.prestadores.filter(p=>p.month===month&&p.ativo!==false),fm=calcFluxoMonth(f,prest,custom,extras);const removeFixed=k=>updateFlux({__delete:[k]});const removeSeries=(field,id)=>{const row=data[field].find(x=>x.id===id);const sid=row?.series_id||id;if(!sid)return;save({...data,[field]:data[field].filter(x=>(x.series_id||x.id)!==sid||x.month<month)})};const deleteButton=(field,x)=><button type="button" className="series-delete" title="Excluir a partir deste mês" aria-label={`Excluir ${x.nome} a partir deste mês`} onClick={()=>removeSeries(field,x.id)}>×</button>;const fixedEntries=[['salario','Salário'],['va','VA']].filter(([k])=>Object.prototype.hasOwnProperty.call(f,k));const fixedExpenses=FLUXO_FIELDS.filter(([k])=>Object.prototype.hasOwnProperty.call(f,k));return <><div className="toolbar"><MonthSelect month={month} setMonth={setMonth} months={data.fluxo.map(x=>x.month)}/></div><div className="kpis"><Kpi t="Entradas" v={fm.entries}/><Kpi t="Despesas" v={fm.expenses}/><Kpi t="Saldo" v={fm.balance}/></div><div className="grid2"><Section title="Entradas">{fixedEntries.map(([k,l])=><div className="row series-row" key={k}><button type="button" className="series-delete" title="Excluir a partir deste mês" aria-label={`Excluir ${l} a partir deste mês`} onClick={()=>removeFixed(k)}>×</button><span>{l}</span><input type="number" value={Number(f[k]||0)} onChange={e=>updateFlux({[k]:Number(e.target.value)||0})}/></div>)}{extras.map(x=><div className="row series-row" key={x.id}>{deleteButton('entradas',x)}<span>{x.nome}</span><input type="number" value={Number(x.valor||0)} onChange={e=>updateSeries('entradas',x.id,{valor:Number(e.target.value)||0})}/></div>)}<button className="secondary" onClick={()=>{const n=prompt('Nome da nova entrada');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('entradas',n,v)}}}>+ Nova entrada</button><div className="total">Total <b>{BRL(fm.entries)}</b></div></Section><Section title="Despesas"><div className="note">Excluir remove a partir deste mês e preserva os meses anteriores.</div>{fixedExpenses.map(([k,l])=><div className="row series-row" key={k}><button type="button" className="series-delete" title="Excluir a partir deste mês" aria-label={`Excluir ${l} a partir deste mês`} onClick={()=>removeFixed(k)}>×</button><span>{l}</span><input type="number" value={Number(f[k]||0)} onChange={e=>updateFlux({[k]:Number(e.target.value)||0})}/></div>)}{custom.map(x=><div className="row series-row" key={x.id}>{deleteButton('despesas',x)}<span>{x.nome}</span><input type="number" value={Number(x.valor||0)} onChange={e=>updateSeries('despesas',x.id,{valor:Number(e.target.value)||0})}/></div>)}<Row label="Prestadores de Serviço" value={fm.employeeTotal} auto/><button className="secondary" onClick={()=>{const n=prompt('Nome da nova despesa');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('despesas',n,v)}}}>+ Nova conta</button></Section></div></>}
'''
s = s[:start] + new_fluxo + s[end:]

# Give Fluxo access to the same save function used by the other tabs.
old_render = "<Fluxo data={data} month={month} setMonth={setMonth} updateFlux={updateFlux} addSeries={addSeries} updateSeries={updateSeries} stopSeries={stopSeries}/>"
new_render = "<Fluxo data={data} save={save} month={month} setMonth={setMonth} updateFlux={updateFlux} addSeries={addSeries} updateSeries={updateSeries} stopSeries={stopSeries}/>"
if old_render in s:
    s = s.replace(old_render, new_render, 1)
elif 'save={save} month={month} setMonth={setMonth} updateFlux={updateFlux}' not in s:
    raise SystemExit('Fluxo render call pattern not found')

p.write_text(s)
print('Fluxo delete buttons now cover fixed and custom rows; deletion propagates from selected month forward and preserves prior months. Duplicate custom Salário/VA rows are hidden.')
