from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

if 'series-delete' not in s:
    raise SystemExit('Fluxo delete controls must be applied before paid checkbox')

# The delete-series patch owns the complete Fluxo component. Add the paid
# state/UI into that already-correct component instead of replacing it.
old_sig = 'function Fluxo({data,save,month,setMonth,updateFlux,addSeries,updateSeries,stopSeries})'
new_sig = 'function Fluxo({data,save,month,setMonth,updateFlux,addSeries,updateSeries,stopSeries,userId})'
if old_sig in s:
    s = s.replace(old_sig, new_sig, 1)
elif 'userId})' not in s[s.find('function Fluxo('):s.find('function Prestadores(', s.find('function Fluxo('))]:
    raise SystemExit('Fluxo signature pattern not found')

marker = 'fm=calcFluxoMonth(f,prest,custom,extras);'
paid_state = 'fm=calcFluxoMonth(f,prest,custom,extras);const storageKey=`looklip-fluxo-paid:${userId||\'demo\'}`,[paid,setPaid]=useState(()=>{try{return JSON.parse(localStorage.getItem(storageKey)||\'{}\')}catch{return {}}});const togglePaid=key=>setPaid(prev=>{const next={...prev,[`${month}:${key}`]:!prev[`${month}:${key}`]};try{localStorage.setItem(storageKey,JSON.stringify(next))}catch{}return next});const isPaid=key=>paid[`${month}:${key}`]===true;const paidAction=key=><label className="paid-check"><input type="checkbox" checked={isPaid(key)} onChange={()=>togglePaid(key)}/><span>Pago</span></label>;'
if 'looklip-fluxo-paid:' not in s:
    if marker not in s:
        raise SystemExit('Fluxo calculation marker not found')
    s = s.replace(marker, paid_state, 1)

# Fixed expense rows: append the checkbox to every fixed expense row.
old = '<span>{l}</span><input type="number" value={Number(f[k]||0)} onChange={e=>updateFlux({[k]:Number(e.target.value)||0})}/>'
new = '<span>{l}</span><input type="number" value={Number(f[k]||0)} onChange={e=>updateFlux({[k]:Number(e.target.value)||0})}/>{paidAction(`fixed:${k}`)}'
if old in s and 'paidAction(`fixed:${k}`)' not in s:
    s = s.replace(old, new, 1)

# Custom expense rows: append the checkbox before the existing series delete button.
old = "{deleteButton('despesas',x)}<span>{x.nome}</span><input type=\"number\" value={Number(x.valor||0)} onChange={e=>updateSeries('despesas',x.id,{valor:Number(e.target.value)||0})}/>"
new = "{deleteButton('despesas',x)}<span>{x.nome}</span><input type=\"number\" value={Number(x.valor||0)} onChange={e=>updateSeries('despesas',x.id,{valor:Number(e.target.value)||0})}/>{paidAction(`despesa:${x.id}`)}"
if old in s and 'paidAction(`despesa:${x.id}`)' not in s:
    s = s.replace(old, new, 1)

# Provider line gets its own payment marker.
old = '<Row label="Prestadores de Serviço" value={fm.employeeTotal} auto/>'
new = '<Row label="Prestadores de Serviço" value={fm.employeeTotal} auto action={paidAction(\'prestadores\')}/>'
if old in s:
    s = s.replace(old, new, 1)

# Pass the authenticated user id so paid markers remain isolated per account.
old = '<Fluxo data={data} save={save} month={month} setMonth={setMonth} updateFlux={updateFlux} addSeries={addSeries} updateSeries={updateSeries} stopSeries={stopSeries}/>'
new = '<Fluxo data={data} save={save} month={month} setMonth={setMonth} updateFlux={updateFlux} addSeries={addSeries} updateSeries={updateSeries} stopSeries={stopSeries} userId={session?.user?.id}/>'
if old in s:
    s = s.replace(old, new, 1)

p.write_text(s)

cssp = Path('src/styles.css')
css = cssp.read_text()
if '.paid-check{' not in css:
    css += '\n.paid-check{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;white-space:nowrap;cursor:pointer}.paid-check input{width:16px;height:16px;margin:0;accent-color:#1f9d55}.paid-check input:checked+span{color:#1f9d55}\n'
    cssp.write_text(css)

print('Fluxo paid checkbox applied to fixed expenses, custom expenses and providers.')
