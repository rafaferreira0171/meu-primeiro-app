from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()
start = s.find('function transferOptions(')
end = s.find('function transferValue(', start)
if start < 0 or end < 0:
    raise SystemExit('Transfer functions not found')

new = r'''function transferOptions(data,month){
  const f=data.fluxo.find(x=>x.month===month)||{}
  const fixed=FLUXO_FIELDS.map(([key,label])=>({id:`fluxo:${key}`,label,value:Number(f[key]||0)}))
  const custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false).map(x=>({id:`despesa:${x.id}`,label:x.nome,value:Number(x.valor||0)}))
  const prestadoresTotal=data.prestadores.filter(x=>x.month===month&&x.ativo!==false).reduce((s,p)=>{const bruto=totalPrestador(p);const pct=Math.min(100,Math.max(0,Number(p.fluxo_percent??100)));return s+bruto*pct/100},0)
  const prestadores=prestadoresTotal>0?[{id:'fluxo:prestadores',label:'Prestadores de Serviço',value:prestadoresTotal}]:[]
  return [...fixed,...prestadores,...custom].filter(x=>x.value>0)
}
'''
s = s[:start] + new + s[end:]
p.write_text(s)
print('Transferencias: Prestadores de Serviço is now selectable and valued from considered provider totals')
