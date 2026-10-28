from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

# Give the two main Fluxo cards semantic hooks without changing the Section component.
s = s.replace('<Section title="Entradas">', '<div className="fluxo-card fluxo-entries"><Section title="Entradas">', 1)
s = s.replace('<div className="total">Total <b>{BRL(fm.entries)}</b></div>\n      </Section>', '<div className="total">Total <b>{BRL(fm.entries)}</b></div>\n      </Section></div>', 1)
s = s.replace('<Section title="Despesas">', '<div className="fluxo-card fluxo-expenses"><Section title="Despesas">', 1)
s = s.replace('<button className="secondary" onClick={()=>{const n=prompt(\'Nome da nova despesa\');if(n){const v=prompt(\'Valor mensal\');if(v!==null)addSeries(\'despesas\',n,v)}}}>+ Nova conta</button>\n      </Section>', '<button className="secondary" onClick={()=>{const n=prompt(\'Nome da nova despesa\');if(n){const v=prompt(\'Valor mensal\');if(v!==null)addSeries(\'despesas\',n,v)}}}>+ Nova conta</button>\n      </Section></div>', 1)

p.write_text(s)

m = Path('src/mobile.css')
css = r'''

/* LookLiP Finance visual hierarchy */
.fluxo-card>.card{height:100%;margin-bottom:18px}
.fluxo-entries>.card{background:#f2fbf6;border-color:#d9efe2;box-shadow:0 10px 28px rgba(74,155,118,.08)}
.fluxo-entries>.card .total{border-top-color:#d9efe2}
.fluxo-entries>.card .note{background:#e8f7ee}
.fluxo-expenses>.card{background:#fff8ed;border-color:#f4e2c4;box-shadow:0 10px 28px rgba(215,154,50,.08)}
.fluxo-expenses>.card .total{border-top-color:#f4e2c4}
.fluxo-expenses>.card .note{background:#fff1d9}

@media(max-width:800px){
  nav{background:rgba(255,255,255,.94);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border:1px solid rgba(15,22,35,.08);padding:6px;gap:3px;border-radius:20px;box-shadow:0 14px 38px rgba(15,22,35,.18)}
  nav button{position:relative;color:#7a8391;border-radius:14px;font-weight:700;transition:background .18s ease,color .18s ease,transform .18s ease}
  nav button:active{transform:scale(.96)}
  nav button.active{background:#eef3ff;color:var(--blue);box-shadow:none}
  nav button.active:after{content:'';position:absolute;bottom:3px;left:50%;width:18px;height:3px;border-radius:999px;background:var(--blue);transform:translateX(-50%)}
  nav button:first-letter{font-size:17px}
}
@media(max-width:520px){
  .fluxo-card>.card{margin-bottom:10px!important}
  .fluxo-entries>.card{background:#f4fcf7}
  .fluxo-expenses>.card{background:#fff9f0}
  nav{left:8px;right:8px;bottom:max(7px,env(safe-area-inset-bottom));padding:5px}
  nav button{min-height:54px;font-size:9px;padding:6px 2px;gap:4px}
}
'''
if '/* LookLiP Finance visual hierarchy */' not in css:
    m.write_text(m.read_text()+css)
print('Fluxo semantic cards and refined mobile tab bar applied')
