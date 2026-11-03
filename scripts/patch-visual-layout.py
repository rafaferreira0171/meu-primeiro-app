from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

s = s.replace('<Section title="Entradas">', '<div className="fluxo-card fluxo-entries"><Section title="Entradas">', 1)
s = s.replace('<div className="total">Total <b>{BRL(fm.entries)}</b></div>\n      </Section>', '<div className="total">Total <b>{BRL(fm.entries)}</b></div>\n      </Section></div>', 1)
s = s.replace('<Section title="Despesas">', '<div className="fluxo-card fluxo-expenses"><Section title="Despesas">', 1)
s = s.replace('<button className="secondary" onClick={()=>{const n=prompt(\'Nome da nova despesa\');if(n){const v=prompt(\'Valor mensal\');if(v!==null)addSeries(\'despesas\',n,v)}}}>+ Nova conta</button>\n      </Section>', '<button className="secondary" onClick={()=>{const n=prompt(\'Nome da nova despesa\');if(n){const v=prompt(\'Valor mensal\');if(v!==null)addSeries(\'despesas\',n,v)}}}>+ Nova conta</button>\n      </Section></div>', 1)

old_nav = "<nav>{[['fluxo','↔','Fluxo'],['prestadores','●','Prestadores'],['transferencias','▣','Transferências'],['budget','◫','Entradas x Budget'],['dash','◈','LookLiP Dash']].map(([k,i,l])=><button key={k} className={tab===k?'active':''} onClick={()=>setTab(k)}>{i} {l}</button>)}</nav>"
new_nav = "<nav aria-label=\"Navegação principal\">{[['fluxo','↔','Fluxo'],['prestadores','●','Prestadores'],['transferencias','▣','Transf.'],['budget','◫','Budget'],['dash','◈','Dash']].map(([k,i,l])=> <button key={k} className={tab===k?'active':''} onClick={()=>setTab(k)}><span className=\"nav-icon\">{i}</span><span className=\"nav-label\">{l}</span></button>)}</nav>"
s = s.replace(old_nav, new_nav, 1)

s = s.replace('<p>Conta independente do Base44.</p>', '', 1)
p.write_text(s)

m = Path('src/mobile.css')
css = r'''

/* LookLiP Finance visual redesign — stronger app hierarchy */
:root{
  --looklip-navy:#0f1623;
  --looklip-slate:#3b4559;
  --looklip-teal:#159b98;
  --looklip-teal-dark:#087976;
  --looklip-teal-soft:#e8f7f6;
  --looklip-green:#3f9b74;
  --looklip-green-soft:#eef9f3;
  --looklip-red:#d95454;
  --looklip-red-soft:#fff1f1;
}

body{background:#f3f5f8;color:var(--looklip-navy)}
.app{background:#f3f5f8}
.app header{padding-top:14px;padding-bottom:10px}
.brand b{color:var(--looklip-navy)}
.head-actions .ghost{background:#edf1f5;color:var(--looklip-slate);border:0;border-radius:14px;font-weight:800}

/* Make the month selector feel like a control, not a form field. */
.month-filter{border:0;border-radius:999px;padding:5px;background:#fff;box-shadow:0 6px 20px rgba(15,22,35,.06)}
.month-filter select{background:#f4f7fa;border:0;border-radius:999px;font-weight:700;color:var(--looklip-navy)}

/* KPI hierarchy: saldo is the hero, the other three are supporting metrics. */
.kpis{gap:10px}
.kpi{border:1px solid #e5eaf0;border-radius:18px;padding:16px 17px;background:#fff;box-shadow:0 8px 24px rgba(15,22,35,.055)}
.kpi span{color:#7b8798;font-size:10px;font-weight:800;letter-spacing:.12em;text-transform:uppercase}
.kpi strong{color:var(--looklip-navy);font-size:22px;letter-spacing:-.02em}
.kpi:nth-child(3){background:var(--looklip-navy);border-color:var(--looklip-navy);box-shadow:0 12px 28px rgba(15,22,35,.18)}
.kpi:nth-child(3) span{color:#9eabbd}
.kpi:nth-child(3) strong{color:#fff;font-size:28px}

/* Stronger income/expense sections: white cards with a clear semantic accent. */
.fluxo-card>.card{height:100%;margin-bottom:16px;border-radius:24px;padding:20px;background:#fff;border:1px solid #e3e8ee;box-shadow:0 12px 34px rgba(15,22,35,.065);overflow:hidden;position:relative}
.fluxo-card>.card:before{content:'';position:absolute;left:0;top:0;bottom:0;width:5px;border-radius:24px 0 0 24px;background:var(--looklip-teal)}
.fluxo-entries>.card{border-color:#dcebe3}
.fluxo-entries>.card:before{background:var(--looklip-green)}
.fluxo-entries>.card .section-title h2{color:var(--looklip-navy);font-size:21px}
.fluxo-entries>.card .total{border-top-color:#e7eee9;font-weight:600}
.fluxo-entries>.card .total b{color:var(--looklip-green);font-size:20px}
.fluxo-entries>.card .note{background:var(--looklip-green-soft);color:#47745f;border-radius:12px}
.fluxo-expenses>.card{border-color:#efdddd}
.fluxo-expenses>.card:before{background:var(--looklip-red)}
.fluxo-expenses>.card .section-title h2{color:var(--looklip-navy);font-size:21px}
.fluxo-expenses>.card .total{border-top-color:#f0e5e5}
.fluxo-expenses>.card .total b{color:var(--looklip-red);font-size:20px}
.fluxo-expenses>.card .note{background:#f8f4f4;color:#7d6767;border-radius:12px}

/* Make individual recurring lines feel like finance-app transactions. */
.fluxo-card .row{border-bottom:1px solid #edf0f3;min-height:58px;padding:9px 0}
.fluxo-card .row:last-of-type{border-bottom:0}
.fluxo-card .row input{border:0!important;background:#f7f8fa!important;border-radius:13px!important;font-weight:700;color:var(--looklip-navy)}
.fluxo-card .row input:focus{box-shadow:0 0 0 3px rgba(21,155,152,.12)!important;background:#fff!important}
.fluxo-card .secondary{background:var(--looklip-teal-soft);color:var(--looklip-teal-dark);border:0;border-radius:13px;font-weight:800}
.fluxo-card .primary{background:var(--looklip-teal);border:0;border-radius:13px;font-weight:800}

.card{border-radius:20px;box-shadow:0 10px 28px rgba(15,22,35,.055)}
.section-title h2{font-weight:850}
.primary{background:var(--looklip-teal);box-shadow:0 7px 18px rgba(21,155,152,.22)}
.secondary{background:var(--looklip-teal-soft);color:var(--looklip-teal-dark)}
.secondary:hover{background:#d9f1f0}

/* Dash */
.dashhead h1{color:var(--looklip-navy)}
.dash-tabs button.active{background:var(--looklip-teal);box-shadow:0 6px 16px rgba(21,155,152,.22)}
.dash-trend i{background:var(--looklip-teal)}

@media(max-width:800px){
  .app header{padding-top:12px;padding-bottom:8px}
  .app main{padding-top:2px}
  .toolbar{padding-top:2px;padding-bottom:9px}
  .kpis{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:9px;margin-bottom:14px}
  .kpi{min-height:72px;border-radius:17px;padding:13px!important}
  .kpi strong{font-size:18px!important;margin-top:5px;display:block}
  .kpi:nth-child(3){grid-column:1/-1;order:-1;min-height:102px;display:flex;flex-direction:column;justify-content:center;padding:17px!important}
  .kpi:nth-child(3) strong{font-size:31px!important}
  .kpi:nth-child(4){border-top:4px solid #8792a2}
  nav{position:fixed!important;display:flex!important;left:10px!important;right:10px!important;bottom:max(8px,env(safe-area-inset-bottom))!important;top:auto!important;width:auto!important;max-width:none!important;z-index:9999!important;background:rgba(255,255,255,.98)!important;backdrop-filter:blur(22px);-webkit-backdrop-filter:blur(22px);border:1px solid rgba(15,22,35,.10)!important;padding:6px!important;gap:4px!important;border-radius:22px!important;box-shadow:0 16px 42px rgba(15,22,35,.20)!important;margin:0!important;overflow:visible!important}
  nav button{position:relative!important;flex:1!important;min-width:0!important;width:auto!important;color:#7a8391!important;background:transparent!important;border:0!important;border-radius:15px!important;font-weight:800!important;white-space:nowrap!important;min-height:56px!important;padding:7px 2px!important}
  nav button:active{transform:scale(.96)}
  nav button:hover{background:#f7f9fc!important;color:var(--looklip-navy)!important}
  nav button.active{background:var(--looklip-teal-soft)!important;color:var(--looklip-teal-dark)!important;box-shadow:inset 0 0 0 1px rgba(21,155,152,.08)!important}
  nav button.active:after{content:'';position:absolute!important;bottom:3px!important;left:50%!important;width:22px!important;height:3px!important;border-radius:999px!important;background:var(--looklip-teal)!important;transform:translateX(-50%)!important}
  nav .nav-icon{display:block!important;font-size:16px!important;line-height:16px!important;margin-bottom:3px!important}
  nav .nav-label{display:block!important;font-size:9px!important;line-height:12px!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important;max-width:100%!important}
  main{padding-bottom:118px}
  .fluxo-card>.card{margin-bottom:12px!important;border-radius:22px!important;padding:17px!important}
  .fluxo-card .row{min-height:57px;padding:8px 0}
  .fluxo-card .row input{width:112px!important;min-height:43px!important;font-size:15px!important}
  .fluxo-entries>.card .section-title h2,.fluxo-expenses>.card .section-title h2{font-size:20px}
}
@media(max-width:520px){
  nav{left:8px!important;right:8px!important;bottom:max(7px,env(safe-area-inset-bottom))!important;padding:5px!important;border-radius:20px!important}
  nav button{min-height:54px!important;font-size:9px!important}
  .kpi span{font-size:9px}
  .kpi:nth-child(3){min-height:98px!important}
  .kpi:nth-child(3) strong{font-size:29px!important}
  .fluxo-card>.card{padding:16px!important;border-radius:20px!important}
  .fluxo-entries>.card{background:#fff}
  .fluxo-expenses>.card{background:#fff}
  .fluxo-card .row input{width:108px!important}
}
'''
text = m.read_text()
marker = '/* LookLiP Finance visual redesign —'
if marker in text:
    text = re.sub(r'/\* LookLiP Finance visual redesign —.*', css.strip()+"\n", text, flags=re.S)
else:
    m.write_text(text + css)
    text = m.read_text()
if marker in text:
    m.write_text(re.sub(r'/\* LookLiP Finance visual redesign —.*', css.strip()+"\n", text, flags=re.S))
print('LookLiP Finance stronger visual hierarchy applied')
