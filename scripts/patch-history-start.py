# LookLiP Finance final history + clean-start patch
from pathlib import Path
p=Path('src/main.jsx')
s=p.read_text()

old="const baseFluxo={salario:12000,va:700,condominio:975,iptu:145,gas:430,internet:90,luz:160,mercado:3000,combustivel:700,seguro_carro:250,convenio:1651,cartao:1718,celular:69,cabelo:75,academia:149,contabilidade:250,pernambucanas:71,assin_chat:45,assin_apple:8,assin_ifood:19,assin_uber:19,outros:153}\nconst makeFluxo=m=>({month:m,...baseFluxo}),seed={fluxo:MONTHS.map(makeFluxo),entradas:[],prestadores:[],despesas:[],gastos:[],transferencias:[],budgetAccounts:[]}"
if old in s:
    s=s.replace(old,"const baseFluxo={salario:0,va:0,condominio:0,iptu:0,gas:0,internet:0,luz:0,mercado:0,combustivel:0,seguro_carro:0,convenio:0,cartao:0,celular:0,cabelo:0,academia:0,contabilidade:0,pernambucanas:0,assin_chat:0,assin_apple:0,assin_ifood:0,assin_uber:0,outros:0}\nconst makeFluxo=m=>({month:m,...baseFluxo}),seed={fluxo:[],entradas:[],prestadores:[],despesas:[],gastos:[],transferencias:[],budgetAccounts:[]}",1)

if 'const existingMonths=' not in s or 'd.startMonth=' not in s:
    raise SystemExit('history-aware normalizeData is not present; refusing clean reset')

p.write_text(s)
print('final clean seed applied; history-aware normalization verified')
