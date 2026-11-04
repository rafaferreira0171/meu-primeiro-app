from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

# The Dashboard component is restored earlier in the build. Convert its
# narrow monthly table into explicit, full-width mobile-friendly summary cards.
start = s.find('<Section title="Visão mensal">')
if start >= 0:
    end = s.find('</Section>', start)
    if end < 0:
        raise SystemExit('Monthly dashboard section is incomplete')
    end += len('</Section>')
    s = s[:start] + '''<Section title="Visão Mensal (12 meses)"><div className="monthly-cards">{rows.map(x=>{const scale=Math.max(x.entries,x.expenses,1);const monthName=['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ'][Number(x.m.slice(5,7))-1]||x.m;return <article className="monthly-card monthly-card-v2" key={x.m}><div className="monthly-card-head"><h3>{monthName}/{x.m.slice(0,4)}</h3><span>Projetado</span></div><div className="monthly-metric"><span>Entradas</span><div className="monthly-track"><i className="monthly-income" style={{width:`${Math.max(0,Math.min(100,x.entries/scale*100))}%`}}/></div><strong>{BRL(x.entries)}</strong></div><div className="monthly-metric"><span>Despesas</span><div className="monthly-track"><i className="monthly-expense" style={{width:`${Math.max(0,Math.min(100,x.expenses/scale*100))}%`}}/></div><strong>{BRL(x.expenses)}</strong></div><div className={`monthly-balance ${x.balance<0?'is-negative':'is-positive'}`}><span>Saldo</span><strong>{BRL(x.balance)}</strong></div></article>})}</div></Section>''' + s[end:]
elif 'monthly-card-v2' not in s:
    raise SystemExit('Monthly dashboard section was not found; refusing to continue')

# Replace only the negative-month count KPI with a compact detailed card.
s = s.replace(
    'negative=rows.filter(x=>x.balance<0).length',
    'negativeRows=rows.filter(x=>x.balance<0),negative=negativeRows.length'
)
old_negative = '<div className="kpis dash-negative-kpis"><Kpi t="Meses negativos" v={negative} kind="count"/></div>'
new_negative = '''<Section title="Meses Negativos"><div className="negative-months-card"><div className="negative-months-heading"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2.5"/><path d="M7 3v4M17 3v4M3 10h18"/></svg><strong>{negative} {negative===1?'mês':'meses'}</strong></div>{negativeRows.length?negativeRows.map(x=>{const label=['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ'][Number(x.m.slice(5,7))-1]+'/'+x.m.slice(0,4);return <div className="negative-month-row" key={x.m}><span>{label}</span><b>{BRL(x.balance)}</b></div>}):<div className="negative-month-empty">Nenhum mês com saldo negativo no período projetado.</div>}</div></Section>'''
if old_negative in s:
    s = s.replace(old_negative, new_negative, 1)
elif 'className="negative-months-card"' not in s:
    raise SystemExit('Negative-month KPI target not found; refusing to continue')

# Replace only the projected balance evolution chart with a mobile-first line chart.
trend_start = s.find('<Section title={`Evolução do saldo')
if trend_start >= 0:
    trend_end = s.find('</Section>', trend_start)
    if trend_end < 0:
        raise SystemExit('Balance evolution section is incomplete')
    trend_end += len('</Section>')
    trend_markup = '''<Section title={`Evolução do Saldo (Projetado)`}><div className="balance-evolution-card"><div className="balance-evolution-highlights"><div className="balance-evolution-total"><span>Saldo projetado no período</span><strong>{BRL(rows.reduce((sum,x)=>sum+x.balance,0))}</strong></div><div className="balance-evolution-extremes"><div className="balance-extreme best"><span>Melhor mês</span><b>{best.m}</b><strong>{BRL(best.balance)}</strong></div><div className="balance-extreme worst"><span>Pior mês</span><b>{worst.m}</b><strong>{BRL(worst.balance)}</strong></div></div></div><div className="balance-line-chart"><svg viewBox="0 0 340 164" role="img" aria-label="Evolução projetada do saldo nos próximos 12 meses" preserveAspectRatio="none"><defs><linearGradient id="balance-positive-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#2f9b79" stopOpacity=".22"/><stop offset="100%" stopColor="#2f9b79" stopOpacity="0"/></linearGradient></defs>{[-1,0,1].map(v=><line key={v} x1="10" x2="330" y1={82-v*58} y2={82-v*58} stroke={v===0?'#9aa8b8':'#edf1f4'} strokeDasharray={v===0?'4 4':'0'} strokeWidth="1"/>)}{rows.slice(0,-1).map((x,i)=>{const y1=82-(x.balance/maxAbs)*58,y2=82-(rows[i+1].balance/maxAbs)*58,x1=14+i*(312/Math.max(1,rows.length-1)),x2=14+(i+1)*(312/Math.max(1,rows.length-1));return <line key={x.m} x1={x1} y1={y1} x2={x2} y2={y2} stroke={x.balance<0||rows[i+1].balance<0?'#d94b4b':'#2f9b79'} strokeWidth="3" strokeLinecap="round"/>})}{rows.map((x,i)=>{const cx=14+i*(312/Math.max(1,rows.length-1)),cy=82-(x.balance/maxAbs)*58;return <g key={x.m}><circle cx={cx} cy={cy} r="4.5" fill="#fff" stroke={x.balance<0?'#d94b4b':'#2f9b79'} strokeWidth="2.5"/><text x={cx} y="153" textAnchor="middle" fontSize="8" fill="#64748b">{['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ'][Number(x.m.slice(5,7))-1]}</text></g>})}</svg></div></div></Section>'''
    s = s[:trend_start] + trend_markup + s[trend_end:]
elif 'className="balance-line-chart"' not in s:
    raise SystemExit('Balance evolution section not found; refusing to continue')

# Render only the five largest projected expense categories, in descending order.
old_top = '<Section title="Maiores despesas"><div className="dash-ranking">{top.map(([name,value],i)=><div key={name}><span><b>{i+1}</b>{name}</span><strong>{BRL(value)}</strong></div>)}</div>{!top.length&&<div className="empty">Nenhuma despesa registrada.</div>}</Section>'
new_top = '<Section title="Maiores Despesas (Top 5 · Projetadas)"><div className="expense-top-five">{top.slice(0,5).map(([name,value],i)=>{const pct=allExp?value/allExp*100:0,bar=top[0]&&top[0][1]?value/top[0][1]*100:0,lower=name.toLowerCase(),symbol=lower.includes("moradia")||lower.includes("aluguel")?"⌂":lower.includes("alimenta")||lower.includes("mercado")?"♜":lower.includes("transporte")||lower.includes("combust")?"⌁":lower.includes("saúde")||lower.includes("saude")?"♡":"•••";return <div className="expense-top-row" key={name}><b className={"expense-rank rank-"+(i+1)}>{i+1}</b><span className="expense-symbol">{symbol}</span><div className="expense-detail"><strong>{name}</strong><div className="expense-track"><i style={{width:bar+"%"}}/></div></div><strong className="expense-value">{BRL(value)}</strong><b className="expense-share">{pct.toFixed(0)}%</b></div>})}</div>{!top.length&&<div className="empty">Nenhuma despesa registrada.</div>}</Section>'
if old_top in s:
    s = s.replace(old_top, new_top, 1)
elif 'className="expense-top-five"' not in s:
    raise SystemExit('Largest-expenses section not found; refusing to continue')

# Rebuild only the executive reading card in the approved compact dark layout.
old_exec = '<Section title="Leitura executiva"><div className="dash-insight"><b>Caixa projetado</b><span>Saldo médio dos próximos 11 meses: <strong>{BRL(avg)}</strong></span></div><div className="dash-insight"><b>Melhor mês</b><span>{best.m} · <strong>{BRL(best.balance)}</strong></span></div><div className="dash-insight"><b>Pior mês</b><span>{worst.m} · <strong className={worst.balance<0?\'negative\':\'\'}>{BRL(worst.balance)}</strong></span></div><div className="dash-insight"><b>Concentração</b><span>Top 3 despesas representam <strong>{allExp?(top3/allExp*100).toFixed(1):\'0.0\'}%</strong> do fluxo fixo considerado.</span></div></Section>'
new_exec = '''<section className="executive-reading-card"><div className="executive-reading-title"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.2 2 4.8 13h6l-.8 9L19.2 10h-6z"/></svg><strong>Leitura Executiva</strong><span>12 meses</span></div><div className="executive-reading-body"><div className="executive-reading-summary"><div className="executive-reading-line"><i className="exec-status positive">✓</i><span>{rows.filter(x=>x.balance>0).length} meses com saldo positivo</span></div><div className="executive-reading-line"><i className="exec-status negative">!</i><span>{negative} {negative===1?'mês':'meses'} com saldo negativo</span></div><div className="executive-reading-total"><i className="exec-bars"><b/><b/><b/></i><span>Saldo acumulado projetado:<strong>{BRL(rows.reduce((sum,x)=>sum+x.balance,0))}</strong></span></div></div><div className="executive-reading-divider"/><div className="executive-reading-extremes"><div className="executive-reading-extreme best"><i className="exec-calendar">▦</i><span><small>Melhor mês:</small><b>{['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ'][Number(best.m.slice(5,7))-1]}/{best.m.slice(0,4)} <strong>{BRL(best.balance)}</strong></b></span></div><div className="executive-reading-extreme worst"><i className="exec-calendar">▦</i><span><small>Pior mês:</small><b>{['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ'][Number(worst.m.slice(5,7))-1]}/{worst.m.slice(0,4)} <strong>{BRL(worst.balance)}</strong></b></span></div></div></div></section>'''
if old_exec in script:
    script = script.replace(old_exec,new_exec,1)
elif 'className="executive-reading-card"' not in script:
    raise SystemExit('Executive reading section not found; refusing to continue')
p.write_text(s)

css_path = Path('src/mobile.css')
css = css_path.read_text()
marker = '/* LookLiP monthly cards: fixed-width-safe mobile layout */'
rules = '''
/* LookLiP monthly cards: fixed-width-safe mobile layout */
.dash-content .monthly-cards{display:grid;grid-template-columns:minmax(0,1fr);gap:10px;width:100%;min-width:0}
.dash-content .monthly-card{display:block;width:100%;min-width:0;max-width:100%;box-sizing:border-box;padding:13px 14px;border:1px solid #e7ecf3;border-radius:15px;background:#fff;overflow:hidden}
.dash-content .monthly-card h3{margin:0 0 5px;padding:0 0 9px;border-bottom:1px solid #edf0f4;color:#29384f;font-size:13px;font-weight:800}
.dash-content .monthly-card-row{display:flex;align-items:center;justify-content:space-between;gap:10px;width:100%;min-width:0;padding:8px 0;border-bottom:1px solid #f0f2f6;box-sizing:border-box}
.dash-content .monthly-card-row:last-child{border-bottom:0;padding-bottom:2px}
.dash-content .monthly-card-row span{flex:0 0 78px;color:#7b8798;font-size:10px;font-weight:800;letter-spacing:.06em;text-transform:uppercase}
.dash-content .monthly-card-row strong{display:block;min-width:0;max-width:calc(100% - 88px);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:right;color:#172235;font-size:12px;font-weight:800;font-variant-numeric:tabular-nums}
@media(min-width:801px){.dash-content .monthly-cards{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''
if marker not in css:
    css += '\n' + rules
css_path.write_text(css)
print('Monthly Dashboard converted to responsive summary cards')
