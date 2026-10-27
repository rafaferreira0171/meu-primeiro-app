from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()
old = "function Fluxo({data,month,setMonth,updateFlux,addSeries,updateSeries,stopSeries}){const f=data.fluxo.find(x=>x.month===month)||{},extras=data.entradas.filter(x=>x.month===month&&x.ativo!==false),custom=data.despesas.filter(x=>x.month===month&&x.ativo!==false),fm=calcFluxoMonth(f,data.prestadores.filter(p=>p.month===month&&p.ativo!==false),custom,extras);return <><div className=\"toolbar\"><MonthSelect month={month} setMonth={setMonth}/></div><div className=\"kpis\"><Kpi t=\"Entradas\" v={fm.entries}/><Kpi t=\"Despesas\" v={fm.expenses}/><Kpi t=\"Saldo\" v={fm.balance}/></div><div className=\"grid2\"><Section title=\"Entradas\"><Row label=\"Salário\" value={f.salario} onChange={v=>updateFlux({salario:v})}/><Row label=\"VA\" value={f.va} onChange={v=>updateFlux({va:v})}/>{extras.map(x=><Row key={x.id} label={x.nome} value={x.valor} onChange={v=>updateSeries('entradas',x.id,{valor:v})} action={<button className=\"ghost\" onClick={()=>stopSeries('entradas',x.series_id||x.id)}>Encerrar</button>}/>)}<button className=\"secondary\" onClick={()=>{const n=prompt('Nome da nova entrada');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('entradas',n,v)}}}>+ Nova entrada</button><div className=\"total\">Total <b>{BRL(fm.entries)}</b></div></Section><Section title=\"Despesas\"><div className=\"note\">Prestadores e imposto entram automaticamente. Encerrar não apaga histórico.</div>{FLUXO_FIELDS.map(([k,l])=><Row key={k} label={l} value={f[k]} onChange={v=>updateFlux({[k]:v})}/>)}{custom.map(x=><Row key={x.id} label={x.nome} value={x.valor} onChange={v=>updateSeries('despesas',x.id,{valor:v})} action={<button className=\"ghost\" onClick={()=>stopSeries('despesas',x.series_id||x.id)}>Encerrar</button>}/>)}<Row label=\"50% Prestadores\" value={fm.employeeHalf} auto/><Row label=\"Imposto\" value={fm.tax} auto/><button className=\"secondary\" onClick={()=>{const n=prompt('Nome da nova despesa');if(n){const v=prompt('Valor mensal');if(v!==null)addSeries('despesas',n,v)}}}>+ Nova conta</button></Section></div></>}"
new = old.replace('<Row label=\\"50% Prestadores\\" value={fm.employeeHalf} auto/>','<Row label=\\"Prestadores de Serviço\\" value={fm.employeeTotal} auto/>')
if old not in s:
    raise SystemExit('Fluxo component pattern not found')
s = s.replace(old, new, 1)
p.write_text(s)

f = Path('src/lib/finance.js')
s = f.read_text()
old = "export function calcFluxoMonth(fluxo,prestadores=[],despesas=[],entradas=[]){const entries=Number(fluxo?.salario||0)+Number(fluxo?.va||0)+entradas.reduce((s,x)=>s+Number(x.valor||0),0);const fixed=FLUXO_FIELDS.reduce((s,[k])=>s+Number(fluxo?.[k]||0),0);const custom=despesas.reduce((s,x)=>s+Number(x.valor||0),0);const employeeHalf=totalPrestadores(prestadores)/2;const expenses=fixed+custom+employeeHalf+AUTO_TAX;return{entries,expenses,balance:entries-expenses,employeeHalf,tax:AUTO_TAX}}"
new = "export function calcFluxoMonth(fluxo,prestadores=[],despesas=[],entradas=[]){const entries=Number(fluxo?.salario||0)+Number(fluxo?.va||0)+entradas.reduce((s,x)=>s+Number(x.valor||0),0);const fixed=FLUXO_FIELDS.reduce((s,[k])=>s+Number(fluxo?.[k]||0),0);const custom=despesas.reduce((s,x)=>s+Number(x.valor||0),0);const employeeTotal=totalPrestadores(prestadores);const expenses=fixed+custom+employeeTotal+AUTO_TAX;return{entries,expenses,balance:entries-expenses,employeeTotal,tax:AUTO_TAX}}"
if old not in s:
    raise SystemExit('calcFluxoMonth pattern not found')
f.write_text(s.replace(old,new,1))
print('Prestadores -> Fluxo patch applied')
