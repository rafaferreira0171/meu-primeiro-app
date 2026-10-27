# LookLiP Finance history-aware planning patch
from pathlib import Path

p=Path('src/main.jsx')
s=p.read_text()

# Keep the development/demo values intact for validation.
if 'const baseFluxo={salario:12000' not in s:
    raise SystemExit('demo seed not found; refusing to alter seed')

# Replace normalizeData with history-safe rolling planning. Historical months are preserved;
# only months from the user's start month onward are exposed, with a rolling 12-month projection.
start=s.index('function normalizeData(')
end=s.index('function useFinance()',start)
new_normalize='''function normalizeData(raw={}){const d={...seed,...raw,fluxo:[...(raw.fluxo||[])],entradas:[...(raw.entradas||[])],prestadores:[...(raw.prestadores||[])],despesas:[...(raw.despesas||[])],gastos:[...(raw.gastos||[])],transferencias:[...(raw.transferencias||[])],budgetAccounts:[...(raw.budgetAccounts||[])]};const now=currentMonth();const existingMonths=[...new Set([...d.fluxo,...d.entradas,...d.prestadores,...d.despesas,...d.gastos,...d.transferencias,...d.budgetAccounts].map(x=>x.month).filter(Boolean))].sort();const inferredStart=d.startMonth||existingMonths[0]||now;d.startMonth=inferredStart<=now?inferredStart:now;const historyMonths=[...new Set(existingMonths.filter(m=>m>=d.startMonth&&m<=now))];if(!historyMonths.includes(now))historyMonths.push(now);const months=[...new Set([...historyMonths,...planningMonths(now,12)].filter(m=>m>=d.startMonth))].sort();const latest=(rows,m)=>rows.filter(x=>x.month<=m).sort((a,b)=>a.month.localeCompare(b.month)).at(-1);const isUuid=x=>typeof x==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(x);const stableId=(kind,value)=>{let h=2166136261;for(const c of `${kind}:${value}`){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}let hex='';for(let i=0;i<8;i++){h=Math.imul(h^(h>>>13),1274126177)>>>0;hex+=h.toString(16).padStart(8,'0')}hex=hex.slice(0,32);return `${hex.slice(0,8)}-${hex.slice(8,12)}-4${hex.slice(13,16)}-${(8+(parseInt(hex.slice(16,17),16)%4)).toString(16)}${hex.slice(17,20)}-${hex.slice(20,32)}`};const migrate=(rows,key,kind)=>{const ids=new Map();for(const r of rows){if(!isUuid(r[key]))continue;const value=String(r.nome||'registro').toLowerCase().trim();if(value&&!ids.has(`${kind}:${value}`))ids.set(`${kind}:${value}`,r[key])}for(const r of rows){if(isUuid(r[key]))continue;const value=String(r.nome||'registro').toLowerCase().trim();const mapKey=`${kind}:${value}`;if(!ids.has(mapKey))ids.set(mapKey,stableId(kind,value));r[key]=ids.get(mapKey)}};migrate(d.entradas,'series_id','entrada');migrate(d.despesas,'series_id','despesa');migrate(d.prestadores,'prestador_id','prestador');migrate(d.transferencias,'series_id','transferencia');for(const m of months)if(!d.fluxo.some(x=>x.month===m)){const src=latest(d.fluxo,now)||makeFluxo(m);d.fluxo.push({...src,month:m})};const ensure=(rows,key)=>{const groups=new Map();rows.forEach(r=>{const sid=r[key]||r.id;if(!groups.has(sid))groups.set(sid,[]);groups.get(sid).push(r)});for(const[sid,g]of groups){const cur=g.find(x=>x.month===now)||g.filter(x=>x.month<now).sort((a,b)=>b.month.localeCompare(a.month))[0];if(!cur||cur.ativo===false)continue;for(const m of months)if(m>now&&!rows.some(x=>(x[key]||x.id)===sid&&x.month===m))rows.push({...cur,id:crypto.randomUUID(),[key]:sid,month:m,ativo:true})}};ensure(d.entradas,'series_id');ensure(d.despesas,'series_id');ensure(d.prestadores,'prestador_id');ensure(d.transferencias,'series_id');for(const m of months)for(const[key,nome,budget]of DEFAULT_BUDGETS){const id=stableId('budget',`${m}:${key}`);if(!d.budgetAccounts.some(a=>a.id===id||(a.month===m&&a.legacy_key===key)))d.budgetAccounts.push({id,month:m,nome,budget,legacy_key:key,ativo:true})};const budgetIds=new Map(d.budgetAccounts.filter(a=>a.month&&a.legacy_key).map(a=>[`${a.month}:${a.legacy_key}`,a.id]));d.gastos.forEach(g=>{if(!g.budget_account_id&&budgetIds.has(`${g.month}:${g.conta}`))g.budget_account_id=budgetIds.get(`${g.month}:${g.conta}`)});d.fluxo=d.fluxo.filter(x=>x.month>=d.startMonth);d.fluxo.sort((a,b)=>a.month.localeCompare(b.month));return d}
'''
s=s[:start]+new_normalize+s[end:]

# Safety checks: history logic must be present and demo seed must remain.
if 'const existingMonths=' not in s or 'd.startMonth=' not in s or 'const historyMonths=' not in s:
    raise SystemExit('history-aware normalizeData was not applied')
if 'const baseFluxo={salario:12000' not in s or 'seed={fluxo:MONTHS.map(makeFluxo)' not in s:
    raise SystemExit('demo seed was changed unexpectedly')

p.write_text(s)
print('history-aware normalization applied; demo seed preserved')
