from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

# Recurrence: a record created in a future month must propagate from that
# month forward, while preserving any month-specific edits already present.
pattern = r"const ensure=\(rows,key\)=>\{.*?\};ensure\(d\.entradas,'series_id'\);"
match = re.search(pattern, s)
if not match:
    raise SystemExit('Recurring ensure pattern not found')

old = match.group(0)
new_ensure = "const ensure=(rows,key)=>{const groups=new Map();rows.forEach(r=>{const sid=r[key]||r.id;if(!groups.has(sid))groups.set(sid,[]);groups.get(sid).push(r)});for(const[sid,g]of groups){const cur=g.find(x=>x.month===now)||g.filter(x=>x.month<now).sort((a,b)=>b.month.localeCompare(a.month))[0]||g.filter(x=>x.month>now).sort((a,b)=>a.month.localeCompare(b.month))[0];if(!cur||cur.ativo===false)continue;for(const m of months)if(m>cur.month&&!rows.some(x=>(x[key]||x.id)===sid&&x.month===m))rows.push({...cur,id:crypto.randomUUID(),[key]:sid,month:m,ativo:true)}}};ensure(d.entradas,'series_id');"
s = s[:match.start()] + new_ensure + s[match.end():]

# Keep recurring transfer expense references stable across monthly copies.
old = "const custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false).map(x=>({id:`despesa:${x.id}`,label:x.nome,value:Number(x.valor||0)}))"
new = "const custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false).map(x=>({id:`despesa:${x.series_id||x.id}`,label:x.nome,value:Number(x.valor||0)}))"
if old in s:
    s = s.replace(old, new, 1)

p.write_text(s)
print('Future-month recurrence and stable transfer references applied')
