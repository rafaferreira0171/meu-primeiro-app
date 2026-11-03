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

fluxo_start = s.find('function Fluxo(')
fluxo_end = s.find('\nfunction Prestadores(', fluxo_start)
if fluxo_start < 0 or fluxo_end < 0:
    raise SystemExit('Fluxo boundaries not found')
fluxo = s[fluxo_start:fluxo_end]
exp_start = fluxo.find('<Section title="Despesas">')
if exp_start < 0:
    raise SystemExit('Despesas section not found')
head, exp = fluxo[:exp_start], fluxo[exp_start:]

# Keep checkbox + Pago + expense name as one inline group.
old = '<span>{l}</span><input type="number" value={Number(f[k]||0)} onChange={e=>updateFlux({[k]:Number(e.target.value)||0})}/>'
new = '<span className="paid-inline-name">{paidAction(`fixed:${k}`)}{l}</span><input type="number" value={Number(f[k]||0)} onChange={e=>updateFlux({[k]:Number(e.target.value)||0})}/>'
if old in exp:
    exp = exp.replace(old, new, 1)

old = "{deleteButton('despesas',x)}<span>{x.nome}</span><input type=\"number\" value={Number(x.valor||0)} onChange={e=>updateSeries('despesas',x.id,{valor:Number(e.target.value)||0})}/>"
new = "{deleteButton('despesas',x)}<span className=\"paid-inline-name\">{paidAction(`despesa:${x.id}`)}{x.nome}</span><input type=\"number\" value={Number(x.valor||0)} onChange={e=>updateSeries('despesas',x.id,{valor:Number(e.target.value)||0})}/>"
if old in exp:
    exp = exp.replace(old, new, 1)

old = '<Row label="Prestadores de Serviço" value={fm.employeeTotal} auto/>'
new = '<Row label={<span className="paid-inline-name">{paidAction(\'prestadores\')}Prestadores de Serviço</span>} value={fm.employeeTotal} auto/>'
if old in exp:
    exp = exp.replace(old, new, 1)

s = s[:fluxo_start] + head + exp + s[fluxo_end:]

old = '<Fluxo data={data} save={save} month={month} setMonth={setMonth} updateFlux={updateFlux} addSeries={addSeries} updateSeries={updateSeries} stopSeries={stopSeries}/>'
new = '<Fluxo data={data} save={save} month={month} setMonth={setMonth} updateFlux={updateFlux} addSeries={addSeries} updateSeries={updateSeries} stopSeries={stopSeries} userId={session?.user?.id}/>'
if old in s:
    s = s.replace(old, new, 1)

p.write_text(s)

cssp = Path('src/styles.css')
css = cssp.read_text()
paid_css = r'.paid-check{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:600;white-space:nowrap;cursor:pointer;flex:0 0 auto}.paid-check input{width:13px!important;height:13px!important;min-width:13px!important;min-height:13px!important;max-width:13px!important;max-height:13px!important;margin:0!important;padding:0!important;flex:0 0 13px!important;accent-color:#1f9d55}.paid-check input:checked+span{color:#1f9d55}.paid-inline-name{display:inline-flex;align-items:center;gap:7px;min-width:0;white-space:nowrap}.series-row>.paid-inline-name{flex:1 1 auto;overflow:hidden;text-overflow:ellipsis}.row .paid-check+span{min-width:0}'
css = re.sub(r'\.paid-check\{[^}]*\}\.paid-check input\{[^}]*\}\.paid-check input:checked\+span\{[^}]*\}(?:\.paid-inline-name\{[^}]*\}\.row>\.paid-check\{[^}]*\}\.row \.paid-check\+span\{[^}]*\})?', paid_css, css)
if '.paid-check{' not in css:
    css += '\n' + paid_css + '\n'
cssp.write_text(css)

final_fluxo = s[s.find('function Fluxo('):s.find('\nfunction Prestadores(', s.find('function Fluxo('))]
required = ['paid-check', 'Pago', 'paidAction(`fixed:${k}`)', 'paidAction(`despesa:${x.id}`)', 'paid-inline-name']
missing = [x for x in required if x not in final_fluxo]
if missing:
    raise SystemExit('Fluxo paid UI injection incomplete: ' + ', '.join(missing))

print('Fluxo paid checkbox restored inline before expense names and validated.')