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

# Add a fourth KPI without changing the Fluxo calculation structure.
kpi_old = '<div className="kpis"><Kpi t="Entradas" v={fm.entries}/><Kpi t="Despesas" v={fm.expenses}/><Kpi t="Saldo" v={fm.balance}/></div>'
kpi_new = '<div className="kpis fluxo-kpis"><Kpi t="Entradas" v={fm.entries}/><Kpi t="Despesas" v={fm.expenses}/><Kpi t="Saldo" v={fm.balance}/><Kpi t="Total a vencer" v={totalPending}/></div>'
if kpi_old in s:
    s = s.replace(kpi_old, kpi_new, 1)
elif 'Total a vencer' not in s:
    raise SystemExit('Fluxo KPI block not found')

# Calculate Total a vencer from the same expense rows that have Pago controls.
pending_marker = 'const fixedExpenses=FLUXO_FIELDS.filter(([k])=>!fixedDeleted(k));return <>'
pending_new = 'const fixedExpenses=FLUXO_FIELDS.filter(([k])=>!fixedDeleted(k));const pendingFixed=fixedExpenses.reduce((sum,[k])=>sum+(isPaid(`fixed:${k}`)?0:Number(f[k]||0)),0);const pendingCustom=custom.reduce((sum,x)=>sum+(isPaid(`despesa:${x.id}`)?0:Number(x.valor||0)),0);const pendingPrest=isPaid(\'prestadores\')?0:Number(fm.employeeTotal||0);const totalPending=pendingFixed+pendingCustom+pendingPrest;return <>'
if pending_marker in s:
    s = s.replace(pending_marker, pending_new, 1)
elif 'const totalPending=' not in s:
    raise SystemExit('Fluxo fixed expense marker not found')

p.write_text(s)

cssp = Path('src/styles.css')
css = cssp.read_text()
paid_css = r'.paid-check{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:600;white-space:nowrap;cursor:pointer;flex:0 0 auto}.paid-check input{width:13px!important;height:13px!important;min-width:13px!important;min-height:13px!important;max-width:13px!important;max-height:13px!important;margin:0!important;padding:0!important;flex:0 0 13px!important;accent-color:#1f9d55}.paid-check input:checked+span{color:#1f9d55}.paid-inline-name{display:inline-flex;align-items:center;gap:7px;min-width:0;white-space:nowrap}.series-row>.paid-inline-name{flex:1 1 auto;overflow:hidden;text-overflow:ellipsis}.row .paid-check+span{min-width:0}'
css = re.sub(r'\.paid-check\{[^}]*\}\.paid-check input\{[^}]*\}\.paid-check input:checked\+span\{[^}]*\}(?:\.paid-inline-name\{[^}]*\}\.row>\.paid-check\{[^}]*\}\.row \.paid-check\+span\{[^}]*\})?', paid_css, css)
if '.paid-check{' not in css:
    css += '\n' + paid_css + '\n'
css += '\n.fluxo-kpis{grid-template-columns:repeat(4,1fr)}.fluxo-kpis .kpi:nth-child(4){border-top:3px solid #7b8491}@media(max-width:800px){.fluxo-kpis{grid-template-columns:repeat(2,1fr)}}@media(max-width:520px){.fluxo-kpis{grid-template-columns:repeat(2,1fr)}}\n'
cssp.write_text(css)

final_fluxo = s[s.find('function Fluxo('):s.find('\nfunction Prestadores(', s.find('function Fluxo('))]
required = ['paid-check', 'Pago', 'paidAction(`fixed:${k}`)', 'paidAction(`despesa:${x.id}`)', 'paid-inline-name', 'Total a vencer', 'totalPending']
missing = [x for x in required if x not in final_fluxo]
if missing:
    raise SystemExit('Fluxo paid/pending UI injection incomplete: ' + ', '.join(missing))

print('Fluxo paid checkbox and Total a vencer KPI validated.')