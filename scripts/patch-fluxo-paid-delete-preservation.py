from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

start = s.find('function Fluxo(')
end = s.find('\nfunction Prestadores(', start)
if start < 0 or end < 0:
    raise SystemExit('Fluxo component boundaries not found')

chunk = s[start:end]
if 'paid-check' not in chunk:
    raise SystemExit('Paid checkbox Fluxo is not present')

if 'series-delete' not in chunk:
    anchor = "const paidAction=key=><label className=\"paid-check\"><input type=\"checkbox\" checked={isPaid(key)} onChange={()=>togglePaid(key)}/><span>Pago</span></label>;"
    addition = anchor + "const removeFixed=k=>updateFlux({__delete:[k]});const deleteButton=(field,x)=><button type=\"button\" className=\"series-delete\" title=\"Excluir a partir deste mês\" aria-label={`Excluir ${x.nome} a partir deste mês`} onClick={()=>stopSeries(field,x.series_id||x.id)}>×</button>;"
    if anchor not in chunk:
        raise SystemExit('Paid action anchor not found')
    chunk = chunk.replace(anchor, addition, 1)

    old_fixed = 'action={paidAction(`fixed:${k}`)}'
    new_fixed = 'action={<>{paidAction(`fixed:${k}`)}<button type="button" className="series-delete" title="Excluir a partir deste mês" aria-label={`Excluir ${l} a partir deste mês`} onClick={()=>removeFixed(k)}>×</button></>}'
    if old_fixed not in chunk:
        raise SystemExit('Fixed Fluxo rows not found')
    chunk = chunk.replace(old_fixed, new_fixed, 1)

    old_custom = "action={<>{paidAction(`despesa:${x.id}`)}<button className=\"ghost\" onClick={()=>stopSeries('despesas',x.series_id||x.id)}>Encerrar</button></>}"
    new_custom = "action={<>{paidAction(`despesa:${x.id}`)}{deleteButton('despesas',x)}</>}"
    if old_custom not in chunk:
        raise SystemExit('Custom expense action pattern not found')
    chunk = chunk.replace(old_custom, new_custom, 1)

    s = s[:start] + chunk + s[end:]
    p.write_text(s)
    print('Fluxo paid checkbox preserved and recurring delete buttons restored.')
else:
    print('Fluxo already contains both paid checkbox and recurring delete buttons.')

cssp = Path('src/styles.css')
css = cssp.read_text()
if '.series-delete{' not in css:
    css += '\n.series-delete{border:0;background:transparent;font-size:18px;line-height:1;cursor:pointer;opacity:.7}.series-delete:hover{opacity:1}\n'
    cssp.write_text(css)
