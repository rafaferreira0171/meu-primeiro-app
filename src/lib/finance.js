const pad=n=>String(n).padStart(2,'0')
export function currentMonth(){const d=new Date();return `${d.getFullYear()}-${pad(d.getMonth()+1)}`}
export function addMonths(month,count){const [y,m]=month.split('-').map(Number);const d=new Date(y,m-1+count,1);return `${d.getFullYear()}-${pad(d.getMonth()+1)}`}
export function planningMonths(start=currentMonth(),count=12){return Array.from({length:count},(_,i)=>addMonths(start,i))}
export const MONTHS=planningMonths()
export const FLUXO_FIELDS=[['condominio','Condomínio'],['iptu','IPTU'],['gas','Gás'],['internet','Internet'],['luz','Luz'],['mercado','Mercado'],['combustivel','Combustível'],['seguro_carro','Seguro carro'],['convenio','Convênio'],['cartao','Cartão'],['celular','Celular'],['cabelo','Cabelo'],['academia','Academia'],['contabilidade','Contabilidade'],['pernambucanas','Pernambucanas'],['assin_chat','Assin. Chat'],['assin_apple','Assin. Apple'],['assin_ifood','Assin. iFood'],['assin_uber','Assin. Uber'],['outros','Outros']]
export const AUTO_TAX=360
export function totalPrestador(p){return !p?0:Number(p.salario||0)+Number(p.dias_uteis||0)*(Number(p.passagem_scs||0)+Number(p.passagem_sp||0))}
export function totalPrestadores(list=[]){return list.reduce((s,p)=>s+totalPrestador(p),0)}
export function calcFluxoMonth(fluxo,prestadores=[],despesas=[],entradas=[]){const entries=Number(fluxo?.salario||0)+Number(fluxo?.va||0)+entradas.reduce((s,x)=>s+Number(x.valor||0),0);const fixed=FLUXO_FIELDS.reduce((s,[k])=>s+Number(fluxo?.[k]||0),0);const custom=despesas.reduce((s,x)=>s+Number(x.valor||0),0);const employeeTotal=totalPrestadores(prestadores);const expenses=fixed+custom+employeeTotal+AUTO_TAX;return{entries,expenses,balance:entries-expenses,employeeTotal,tax:AUTO_TAX}}
export function calcPixMonth(fluxo,prestadores=[]){const employeeHalf=totalPrestadores(prestadores)/2;const convenio=Number(fluxo?.convenio||0);return{employeeHalf,convenio,total:employeeHalf+convenio}}
export function transferItemValue(item,fluxo,prestadores=[],despesas=[]){if(!item)return 0;if(item.type==='fluxo')return Number(fluxo?.[item.key]||0);if(item.type==='despesa')return Number(despesas.find(d=>(d.series_id||d.id)===item.key)?.valor||0);if(item.type==='prestador_half'){const p=prestadores.find(x=>(x.prestador_id||x.id)===item.key);return totalPrestador(p)/2}return 0}
export function calcTransfer(transfer,fluxo,prestadores=[],despesas=[]){return(transfer?.items||[]).reduce((s,item)=>s+transferItemValue(item,fluxo,prestadores,despesas),0)}
export function calcBudgetMonth(gastos,month){return['mercado','gasolina','avulso'].reduce((o,c)=>(o[c]=gastos.filter(g=>g.month===month&&g.conta===c).reduce((s,g)=>s+Number(g.valor||0),0),o),{})}
