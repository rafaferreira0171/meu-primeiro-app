from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()
start = s.find('function Prestadores(')
end = s.find('function transferOptions', start)
if start < 0 or end < 0:
    raise SystemExit('Prestadores component not found')

new = r'''function Prestadores({data,save,month,setMonth}){
  const rows=data.prestadores.filter(x=>x.month===month&&x.ativo!==false)
  const totalBruto=rows.reduce((s,x)=>s+totalPrestador(x),0)
  const totalFluxo=rows.reduce((s,x)=>{const pct=Math.min(100,Math.max(0,Number(x.fluxo_percent??100)));return s+totalPrestador(x)*pct/100},0)
  const add=()=>{const nome=prompt('Nome do prestador');if(!nome)return;const sid=crypto.randomUUID();const next=[...data.prestadores,...planningMonths(month,12).map(m=>({id:crypto.randomUUID(),prestador_id:sid,month:m,nome,salario:1400,dias_uteis:22,passagem_scs:0,passagem_sp:0,fluxo_percent:100,ativo:true}))];save({...data,prestadores:next})}
  const update=(id,p)=>save({...data,prestadores:data.prestadores.map(x=>x.id===id?{...x,...p}:x)})
  return <><div className="toolbar"><MonthSelect month={month} setMonth={setMonth} months={data.prestadores.map(x=>x.month)}/><button className="primary" onClick={add}>+ Prestador</button></div><Section title="Prestadores"><div className="kpis"><Kpi t="Custo bruto" v={totalBruto}/><Kpi t="Considerado no Fluxo" v={totalFluxo}/><Kpi t="Quantidade" v={rows.length} kind="count"/></div>{rows.map(p=>{const bruto=totalPrestador(p),pct=Math.min(100,Math.max(0,Number(p.fluxo_percent??100))),considerado=bruto*pct/100;return <div className="card provider-card" key={p.id}><div className="provider-head"><div><strong>{p.nome||'Prestador'}</strong><span>Composição do custo</span></div></div><Row label="Salário" value={p.salario} onChange={v=>update(p.id,{salario:v})}/><Row label="Dias úteis" value={p.dias_uteis} onChange={v=>update(p.id,{dias_uteis:v})}/><Row label="Passagem SCS" value={p.passagem_scs} onChange={v=>update(p.id,{passagem_scs:v})}/><Row label="Passagem SP" value={p.passagem_sp} onChange={v=>update(p.id,{passagem_sp:v})}/><div className="provider-total-control"><div><span>Total do prestador</span><strong>{BRL(bruto)}</strong></div><label><span>% considerar no Fluxo</span><input type="number" min="0" max="100" step="1" value={pct} onChange={e=>update(p.id,{fluxo_percent:Math.min(100,Math.max(0,Number(e.target.value)||0))})}/></label></div><div className="total">Total considerado no Fluxo <b>{BRL(considerado)}</b></div></div>})}{!rows.length&&<div className="empty">Nenhum prestador neste mês.</div>}</Section></>}
'''
s = s[:start] + new + s[end:]
p.write_text(s)
print('Prestadores: added per-provider Fluxo percentage and considered total')
