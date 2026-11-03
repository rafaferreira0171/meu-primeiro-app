from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

s = s.replace('<Section title="Entradas">', '<div className="fluxo-card fluxo-entries"><Section title="Entradas">', 1)
s = s.replace('<div className="total">Total <b>{BRL(fm.entries)}</b></div>\n      </Section>', '<div className="total">Total <b>{BRL(fm.entries)}</b></div>\n      </Section></div>', 1)
s = s.replace('<Section title="Despesas">', '<div className="fluxo-card fluxo-expenses"><Section title="Despesas">', 1)
s = s.replace('<button className="secondary" onClick={()=>{const n=prompt(\'Nome da nova despesa\');if(n){const v=prompt(\'Valor mensal\');if(v!==null)addSeries(\'despesas\',n,v)}}}>+ Nova conta</button>\n      </Section>', '<button className="secondary" onClick={()=>{const n=prompt(\'Nome da nova despesa\');if(n){const v=prompt(\'Valor mensal\');if(v!==null)addSeries(\'despesas\',n,v)}}}>+ Nova conta</button>\n      </Section></div>', 1)

old_nav = "<nav>{[['fluxo','↔','Fluxo'],['prestadores','●','Prestadores'],['transferencias','▣','Transferências'],['budget','◫','Entradas x Budget'],['dash','◈','LookLiP Dash']].map(([k,i,l])=><button key={k} className={tab===k?'active':''} onClick={()=>setTab(k)}>{i} {l}</button>)}</nav>"
new_nav = "<nav aria-label=\"Navegação principal\">{[['fluxo','↔','Fluxo'],['prestadores','●','Prestadores'],['transferencias','▣','Transf.'],['budget','◫','Budget'],['dash','◈','Dash']].map(([k,i,l])=><button key={k} className={tab===k?'active':''} onClick={()=>setTab(k)}><span className=\"nav-icon\">{i}</span><span className=\"nav-label\">{l}</span></button>)}</nav>"
s = s.replace(old_nav, new_nav, 1)

s = s.replace('<p>Conta independente do Base44.</p>', '', 1)
p.write_text(s)

m = Path('src/mobile.css')
css = r'''

/* LookLiP Finance visual redesign — Dinzo-inspired hierarchy, LookLiP palette */
:root{
  --looklip-navy:#0f1623;
  --looklip-slate:#3b4559;
  --looklip-teal:#159b98;
  --looklip-teal-soft:#e8f7f6;
  --looklip-green:#3f9b74;
  --looklip-green-soft:#eef9f3;
  --looklip-red:#d95454;
  --looklip-red-soft:#fff1f1;
}

body{background:#f5f7f9}
.app header{padding-top:18px;padding-bottom:14px}
.brand b{color:var(--looklip-navy)}
.head-actions .ghost{background:#eef1f5;color:var(--looklip-slate)}

/* Dashboard-style KPI hierarchy */
.kpis{gap:12px}
.kpi{border-radius:20px;padding:18px 18px 17px;background:#fff;box-shadow:0 10px 28px rgba(15,22,35,.06)}
.kpi span{color:#788293}
.kpi strong{color:var(--looklip-navy)}

/* Month selector becomes a compact app-like chip */
.month-filter{border-radius:999px;padding:4px 6px;background:#fff;box-shadow:0 7px 20px rgba(15,22,35,.06)}
.month-filter select{background:#f4f7fa;border-radius:999px}

/* Fluxo cards: clear income/expense separation */
.fluxo-card>.card{height:100%;margin-bottom:18px;border-radius:22px;padding:20px;box-shadow:0 12px 32px rgba(15,22,35,.06)}
.fluxo-entries>.card{background:var(--looklip-green-soft);border-color:#d8eee2;box-shadow:0 12px 32px rgba(63,155,116,.08)}
.fluxo-entries>.card .section-title h2{color:#287755}
.fluxo-entries>.card .total{border-top-color:#d8eee2}
.fluxo-entries>.card .note{background:#e5f6ed;color:#47745f}
.fluxo-expenses>.card{background:var(--looklip-red-soft);border-color:#f0d8d8;box-shadow:0 12px 32px rgba(217,84,84,.07)}
.fluxo-expenses>.card .section-title h2{color:#a53e3e}
.fluxo-expenses>.card .total{border-top-color:#f0d8d8}
.fluxo-expenses>.card .note{background:#ffe9e9;color:#8b5b5b}

/* Shared card language */
.card{border-radius:20px;box-shadow:0 10px 28px rgba(15,22,35,.055)}
.section-title h2{font-weight:800}
.primary{background:var(--looklip-teal);box-shadow:0 7px 18px rgba(21,155,152,.22)}
.secondary{background:var(--looklip-teal-soft);color:#087976}
.secondary:hover{background:#d9f1f0}

/* Dash */
.dashhead h1{color:var(--looklip-navy)}
.dash-tabs button.active{background:var(--looklip-teal);box-shadow:0 6px 16px rgba(21,155,152,.22)}
.dashhead~.kpis .kpi:first-child{border-top-color:var(--looklip-teal)}
.dashhead~.kpis .kpi:nth-child(2){border-top-color:#d79a32}
.dashhead~.kpis .kpi:nth-child(3){border-top-color:var(--looklip-green)}
.dash-trend i{background:var(--looklip-teal)}

@media(max-width:800px){
  nav{position:fixed!important;display:flex!important;left:12px!important;right:12px!important;bottom:max(8px,env(safe-area-inset-bottom))!important;top:auto!important;width:auto!important;max-width:none!important;z-index:9999!important;background:rgba(255,255,255,.97)!important;backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(15,22,35,.10)!important;padding:6px!important;gap:4px!important;border-radius:22px!important;box-shadow:0 16px 42px rgba(15,22,35,.20)!important;margin:0!important;overflow:visible!important}
  nav button{position:relative!important;flex:1!important;min-width:0!important;width:auto!important;color:#7a8391!important;background:transparent!important;border:0!important;border-radius:15px!important;font-weight:700!important;transition:background .18s ease,color .18s ease,transform .18s ease;white-space:nowrap!important}
  nav button:active{transform:scale(.96)}
  nav button:hover{background:#f7f9fc!important;color:var(--looklip-navy)!important}
  nav button.active{background:var(--looklip-teal-soft)!important;color:#087976!important;box-shadow:inset 0 0 0 1px rgba(21,155,152,.08)!important}
  nav button.active:after{content:'';position:absolute!important;bottom:3px!important;left:50%!important;width:20px!important;height:3px!important;border-radius:999px!important;background:var(--looklip-teal)!important;transform:translateX(-50%)!important}
  nav .nav-icon{display:block!important;font-size:16px!important;line-height:16px!important;margin-bottom:3px!important}
  nav .nav-label{display:block!important;font-size:9px!important;line-height:12px!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important;max-width:100%!important}
  main{padding-bottom:112px}
  .toolbar{padding-top:4px}
  .month-filter{min-height:46px}
  .kpis{gap:9px}
  .kpi{border-radius:17px;padding:14px!important}
  .fluxo-card>.card{margin-bottom:10px!important;border-radius:19px!important;padding:16px!important}
}
@media(max-width:520px){
  nav{left:8px!important;right:8px!important;bottom:max(7px,env(safe-area-inset-bottom))!important;padding:5px!important;border-radius:20px!important}
  nav button{min-height:54px!important;font-size:9px!important;padding:6px 2px!important;gap:4px!important}
  .kpi span{font-size:9px}
  .kpi strong{font-size:17px!important}
  .fluxo-entries>.card{background:#f3fbf6}
  .fluxo-expenses>.card{background:#fff7f7}
}
'''
text = m.read_text()
marker = '/* LookLiP Finance visual redesign — Dinzo-inspired hierarchy, LookLiP palette */'
if marker not in text:
    m.write_text(text + css)
else:
    text = re.sub(r'/\* LookLiP Finance visual redesign — Dinzo-inspired hierarchy, LookLiP palette \*/.*', css.strip()+"\n", text, flags=re.S)
    m.write_text(text)
print('LookLiP Finance visual redesign applied')
