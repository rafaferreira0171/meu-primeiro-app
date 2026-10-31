from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

if 'series-delete' not in s:
    raise SystemExit('Fluxo delete controls must be applied before paid checkbox')

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

# Fixed expense rows: attach Pago to every field in FLUXO_FIELDS, not just the first matching row.
fixed_block = re.search(r'(\{FLUXO_FIELDS\.map\(\(\[k,l\]\)=>)(.*?)(\)\}\{custom\.map)', s, re.S)
if fixed_block:
    body = fixed_block.group(2)
    row_pattern = r'(<Row key=\{k\} label=\{l\} value=\{f\[k\]\} onChange=\{v=>updateFlux\(\{\[k\]:v\}\)\})(?!\s*action=)'
    body2, n = re.subn(row_pattern, r'\1 action={paidAction(`fixed:${k}`)}', body)
    if n:
        s = s[:fixed_block.start(2)] + body2 + s[fixed_block.end(2):]
else:
    raise SystemExit('FLUXO_FIELDS expense block not found')

# Custom expense rows: every user-created expense gets its own marker.
old = "{deleteButton('despesas',x)}<span>{x.nome}</span><input type=\"number\" value={Number(x.valor||0)} onChange={e=>updateSeries('despesas',x.id,{valor:Number(e.target.value)||0})}/>"
new = "{deleteButton('despesas',x)}<span>{x.nome}</span><input type=\"number\" value={Number(x.valor||0)} onChange={e=>updateSeries('despesas',x.id,{valor:Number(e.target.value)||0})}/>{paidAction(`despesa:${x.id}`)}"
if old in s and 'paidAction(`despesa:${x.id}`)' not in s:
    s = s.replace(old, new, 1)

# Also support the canonical custom-row shape used by the restored Fluxo component.
old = "<Row key={x.id} label={x.nome} value={x.valor} onChange={v=>updateSeries('despesas',x.id,{valor:v})} action={<button className=\"ghost\" onClick={()=>stopSeries('despesas',x.series_id||x.id)}>Encerrar</button>}/>"
new = "<Row key={x.id} label={x.nome} value={x.valor} onChange={v=>updateSeries('despesas',x.id,{valor:v})} action={<>{paidAction(`despesa:${x.id}`)}<button className=\"ghost\" onClick={()=>stopSeries('despesas',x.series_id||x.id)}>Encerrar</button></>}/>"
if old in s and 'paidAction(`despesa:${x.id}`)' not in s:
    s = s.replace(old, new, 1)

# Prestadores are expenses, so they also get a marker.
old = '<Row label="Prestadores de Serviço" value={fm.employeeTotal} auto/>'
new = '<Row label="Prestadores de Serviço" value={fm.employeeTotal} auto action={paidAction(\'prestadores\')}/>'
if old in s:
    s = s.replace(old, new, 1)

# Explicitly remove any paid marker that an older patch may have left in Entradas.
fluxo_start = s.find('function Fluxo(')
fluxo_end = s.find('function Prestadores(', fluxo_start)
if fluxo_start >= 0 and fluxo_end > fluxo_start:
    fluxo = s[fluxo_start:fluxo_end]
    entradas_end = fluxo.find('<Section title="Despesas">')
    if entradas_end > 0:
        entradas = fluxo[:entradas_end]
        entradas = re.sub(r'\s*action=\{paidAction\([^)]*\)\}', '', entradas)
        entradas = re.sub(r'\s*\{paidAction\([^)]*\)\}', '', entradas)
        fluxo = entradas + fluxo[entradas_end:]
        s = s[:fluxo_start] + fluxo + s[fluxo_end:]

# Pass the authenticated user id so markers remain isolated per account.
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

print('Fluxo paid checkbox applied to every expense row, including all fixed fields, custom expenses, and providers; entries remain unmarked.')