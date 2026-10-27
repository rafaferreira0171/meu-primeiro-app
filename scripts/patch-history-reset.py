from pathlib import Path
import re

p=Path('src/main.jsx')
s=p.read_text()

# Final product must start empty; seed values are test-only.
s=re.sub(r"const baseFluxo=\{[^\n]*?\}\nconst makeFluxo", "const baseFluxo={salario:0,va:0,condominio:0,iptu:0,gas:0,internet:0,luz:0,mercado:0,combustivel:0,seguro_carro:0,convenio:0,cartao:0,celular:0,cabelo:0,academia:0,contabilidade:0,pernambucanas:0,assin_chat:0,assin_apple:0,assin_ifood:0,assin_uber:0,outros:0}\nconst makeFluxo", s, count=1)

# User-specific start month: history begins when the account enters the app.
s=s.replace("const d={...seed,...raw,fluxo:[...(raw.fluxo||[])],", "const d={...seed,...raw,start_month:raw.start_month||currentMonth(),fluxo:[...(raw.fluxo||[])],", 1)
s=s.replace("const now=currentMonth(),months=planningMonths(now,12),latest=", "const now=currentMonth(),startMonth=d.start_month,span=Math.max(0,(Number(now.slice(0,4))-Number(startMonth.slice(0,4)))*12+Number(now.slice(5,7))-Number(startMonth.slice(5,7))),months=planningMonths(startMonth,span+12),latest=", 1)

# Never expose or recreate periods before the user's start month.
needle="const isUuid=x=>typeof x==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(x);"
replacement=needle+"d.fluxo=d.fluxo.filter(x=>x.month>=startMonth);d.entradas=d.entradas.filter(x=>x.month>=startMonth);d.prestadores=d.prestadores.filter(x=>x.month>=startMonth);d.despesas=d.despesas.filter(x=>x.month>=startMonth);d.gastos=d.gastos.filter(x=>x.month>=startMonth);d.transferencias=d.transferencias.filter(x=>x.month>=startMonth);d.budgetAccounts=d.budgetAccounts.filter(x=>x.month>=startMonth);"
s=s.replace(needle,replacement,1)

p.write_text(s)
print('history/reset patch applied')
