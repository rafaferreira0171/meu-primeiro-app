from pathlib import Path
p=Path('src/styles.css')
s=p.read_text()
css='''\n.provider-total-control{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 0;margin-top:4px;border-top:1px solid #e8ebef}.provider-total-control>div{display:flex;flex-direction:column;gap:3px}.provider-total-control>div span{font-size:12px;color:#697384}.provider-total-control>div strong{font-size:18px}.provider-total-control label{display:flex;align-items:center;gap:7px;font-size:11px;color:#697384}.provider-total-control input{width:72px;text-align:right;border:1px solid #dfe4eb;background:#f8f9fb;border-radius:9px;padding:9px;min-height:38px;font-variant-numeric:tabular-nums}.provider-total-control input:focus{outline:2px solid #3972e84d;background:#fff;border-color:#b9cbf6}@media(max-width:520px){.provider-total-control{align-items:flex-end}.provider-total-control label{flex-direction:column;align-items:flex-end;gap:4px}}\n'''
if '.provider-total-control{' not in s:
    p.write_text(s+css)
print('Provider percentage styles applied')
