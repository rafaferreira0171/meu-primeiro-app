from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

s = s.replace('<Section title="Entradas">', '<div className="fluxo-card fluxo-entries"><Section title="Entradas">', 1)
s = s.replace('<div className="total">Total <b>{BRL(fm.entries)}</b></div>\n      </Section>', '<div className="total">Total <b>{BRL(fm.entries)}</b></div>\n      </Section></div>', 1)
s = s.replace('<Section title="Despesas">', '<div className="fluxo-card fluxo-expenses"><Section title="Despesas">', 1)
s = s.replace('<button className="secondary" onClick={()=>{const n=prompt(\'Nome da nova despesa\');if(n){const v=prompt(\'Valor mensal\');if(v!==null)addSeries(\'despesas\',n,v)}}}>+ Nova conta</button>\n      </Section>', '<button className="secondary" onClick={()=>{const n=prompt(\'Nome da nova despesa\');if(n){const v=prompt(\'Valor mensal\');if(v!==null)addSeries(\'despesas\',n,v)}}}>+ Nova conta</button>\n      </Section></div>', 1)

# Compact, premium bottom navigation labels for small screens.
old_nav = "<nav>{[['fluxo','↔','Fluxo'],['prestadores','●','Prestadores'],['transferencias','▣','Transferências'],['budget','◫','Entradas x Budget'],['dash','◈','LookLiP Dash']].map(([k,i,l])=><button key={k} className={tab===k?'active':''} onClick={()=>setTab(k)}>{i} {l}</button>)}</nav>"
new_nav = "<nav aria-label=\"Navegação principal\">{[['fluxo','↔','Fluxo'],['prestadores','●','Prestadores'],['transferencias','▣','Transf.'],['budget','◫','Budget'],['dash','◈','Dash']].map(([k,i,l])=><button key={k} className={tab===k?'active':''} onClick={()=>setTab(k)}><span className=\"nav-icon\">{i}</span><span className=\"nav-label\">{l}</span></button>)}</nav>"
s = s.replace(old_nav, new_nav, 1)

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
  nav{position:fixed!important;display:flex!important;left:12px!important;right:12px!important;bottom:max(8px,env(safe-area-inset-bottom))!important;top:auto!important;width:auto!important;height:auto!important;max-width:none!important;z-index:9999!important;background:rgba(255,255,255,.97)!important;backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(15,22,35,.10)!important;padding:6px!important;gap:4px!important;border-radius:22px!important;box-shadow:0 16px 42px rgba(15,22,35,.20)!important;margin:0!important;overflow:visible!important}
  nav button{position:relative!important;flex:1!important;min-width:0!important;width:auto!important;color:#7a8391!important;background:transparent!important;border:0!important;border-radius:15px!important;font-weight:700!important;transition:background .18s ease,color .18s ease,transform .18s ease;white-space:nowrap!important}
  nav button:active{transform:scale(.96)}
  nav button:hover{background:#f7f9fc!important;color:var(--ink)!important}
  nav button.active{background:#eef3ff!important;color:var(--blue)!important;box-shadow:inset 0 0 0 1px rgba(57,114,232,.06)!important}
  nav button.active:after{content:'';position:absolute!important;bottom:3px!important;left:50%!important;width:20px!important;height:3px!important;border-radius:999px!important;background:var(--blue)!important;transform:translateX(-50%)!important}
  nav .nav-icon{display:block!important;font-size:16px!important;line-height:16px!important;margin-bottom:3px!important}
  nav .nav-label{display:block!important;font-size:9px!important;line-height:12px!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important;max-width:100%!important}
  main{padding-bottom:112px}
}
@media(max-width:520px){
  .fluxo-card>.card{margin-bottom:10px!important}
  .fluxo-entries>.card{background:#f4fcf7}
  .fluxo-expenses>.card{background:#fff9f0}
  nav{left:8px!important;right:8px!important;bottom:max(7px,env(safe-area-inset-bottom))!important;padding:5px!important;border-radius:20px!important}
  nav button{min-height:54px!important;font-size:9px!important;padding:6px 2px!important;gap:4px!important}
}
'''
text = m.read_text()
if '/* LookLiP Finance visual hierarchy */' not in text:
    m.write_text(text + css)
else:
    text = re.sub(r'/\* LookLiP Finance visual hierarchy \*/.*', css.strip()+"\n", text, flags=re.S)
    m.write_text(text)
print('Fluxo semantic cards and refined bottom navigation applied')
