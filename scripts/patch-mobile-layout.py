from pathlib import Path

p = Path('src/mobile.css')
s = p.read_text()
css = r'''
/* Final mobile layout refinement */
.provider-total-control{display:grid;grid-template-columns:minmax(0,1fr) 150px;gap:14px;align-items:end;margin-top:10px;padding:12px 0;border-top:1px solid #eef1f4}
.provider-total-control>div,.provider-total-control>label{display:flex;flex-direction:column;gap:5px;min-width:0}
.provider-total-control span{font-size:10px;color:var(--muted);line-height:1.25}
.provider-total-control strong{font-size:17px;white-space:nowrap}
.provider-total-control input{width:100%;min-height:42px;border:1px solid #dfe4eb;background:#f8f9fb;border-radius:10px;padding:8px 10px;text-align:right;font-size:16px;box-sizing:border-box}
.provider-total-control input:focus{outline:2px solid #3972e84d;background:#fff;border-color:#b9cbf6}
.danger{color:var(--danger)!important}
@media(max-width:520px){
  body{font-size:14px}
  .app main{padding-left:8px!important;padding-right:8px!important;padding-bottom:88px!important}
  .app header{padding:9px 8px!important}
  .card{padding:14px!important;margin-bottom:10px!important;border-radius:15px}
  .kpi{padding:11px!important}
  .kpi strong{font-size:16px!important}
  .row{min-height:46px;padding:6px 0}
  .row span{font-size:11px}
  .row input{width:96px;min-height:38px;font-size:14px;padding:7px}
  .provider-card{padding:12px!important}
  .provider-total-control{grid-template-columns:1fr 116px;gap:10px;padding:10px 0}
  .provider-total-control strong{font-size:15px}
  .provider-total-control input{min-height:38px;font-size:15px}
  .provider-total-control span{font-size:9px}
  .provider-card>.total{font-size:12px;padding:10px 0}
  .toolbar{margin-bottom:10px}
  .section-title h2{font-size:15px;margin-bottom:10px}
  nav{left:6px;right:6px;bottom:max(6px,env(safe-area-inset-bottom));padding:4px;border-radius:16px}
  nav button{min-height:50px;font-size:9px;padding:6px 2px}
}
@media(max-width:390px){.provider-total-control{grid-template-columns:1fr}.provider-total-control input{width:110px}.provider-total-control>label{align-items:flex-start}.budgetgrid .section-title{flex-wrap:wrap}}
'''
if '/* Final mobile layout refinement */' not in s:
    s += '\n' + css
p.write_text(s)
print('Mobile provider percentage layout and overall compact sizing applied')
