from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

# The Dashboard component is restored earlier in the build. Convert its
# narrow monthly table into explicit, full-width mobile-friendly summary cards.
old = '''<Section title="Visão mensal"><div className="table-wrap"><table><thead><tr><th>Mês</th><th>Entradas</th><th>Despesas</th><th>Saldo</th></tr></thead><tbody>{rows.map(x=><tr key={x.m}><td>{x.m}</td><td>{BRL(x.entries)}</td><td>{BRL(x.expenses)}</td><td className={x.balance<0?'negative':''}>{BRL(x.balance)}</td></tr>)}</tbody></table></div></Section>'''
new = '''<Section title="Visão mensal"><div className="monthly-cards">{rows.map(x=><article className="monthly-card" key={x.m}><h3>{x.m}</h3><div className="monthly-card-row"><span>Entradas</span><strong>{BRL(x.entries)}</strong></div><div className="monthly-card-row"><span>Despesas</span><strong>{BRL(x.expenses)}</strong></div><div className="monthly-card-row"><span>Saldo</span><strong className={x.balance<0?'negative':''}>{BRL(x.balance)}</strong></div></article>)}</div></Section>'''
if old in s:
    s = s.replace(old, new, 1)
elif 'className="monthly-cards"' not in s:
    raise SystemExit('Monthly dashboard table target was not found; refusing to claim the layout was fixed')
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
    css += '\\n' + rules
css_path.write_text(css)
print('Monthly Dashboard converted to responsive summary cards')
