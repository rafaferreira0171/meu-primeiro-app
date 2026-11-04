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
    s = s[:start] + '''<Section title="Visão Mensal (12 meses)"><div className="monthly-cards">{rows.map(x=>{const scale=Math.max(x.entries,x.expenses,1);const monthName=['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ'][Number(x.m.slice(5,7))-1]||x.m;return <article className="monthly-card monthly-card-v2" key={x.m}><div className="monthly-card-head"><h3>{monthName}/{x.m.slice(0,4)}</h3><span>Projetado</span></div><div className="monthly-metric"><span>Entradas</span><div className="monthly-track"><i className="monthly-income" style={{width:`\${Math.max(0,Math.min(100,x.entries/scale*100))}%`}}/></div><strong>{BRL(x.entries)}</strong></div><div className="monthly-metric"><span>Despesas</span><div className="monthly-track"><i className="monthly-expense" style={{width:`\${Math.max(0,Math.min(100,x.expenses/scale*100))}%`}}/></div><strong>{BRL(x.expenses)}</strong></div><div className={`monthly-balance \${x.balance<0?'is-negative':'is-positive'}`}><span>Saldo</span><strong>{BRL(x.balance)}</strong></div></article>})}</div></Section>''' + s[end:]
elif 'monthly-card-v2' not in s:
    raise SystemExit('Monthly dashboard section was not found; refusing to continue')
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
