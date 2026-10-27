import fs from 'node:fs'
import assert from 'node:assert/strict'
import {currentMonth,planningMonths,addMonths,calcFluxoMonth,calcPixMonth,calcTransfer,totalPrestador,fluxoPrestadorPercent,calcBudgetMonth} from '../src/lib/finance.js'

const source=fs.readFileSync(new URL('../src/main.jsx',import.meta.url),'utf8')
const now=currentMonth()
const months=planningMonths(now,12)

assert.equal(months.length,12,'A janela de planejamento deve ter 12 meses')
assert.equal(months[0],now,'A janela deve começar no mês atual')
assert.equal(months.at(-1),addMonths(now,11),'A janela deve terminar 11 meses após o atual')
assert.match(source,/const now=currentMonth\(\)/,'normalizeData deve usar o mês atual como referência')
assert.match(source,/planningMonths\(now,12\)/,'normalizeData deve usar janela móvel de 12 meses')
assert.match(source,/x\.month>=next\?\{\.\.\.x,ativo:false\}/,'Encerramento deve desativar somente registros futuros')
assert.match(source,/m>now/,'A replicação automática deve atingir somente meses futuros')
assert.doesNotMatch(source,/label="50% Prestadores"/,'O Fluxo não deve lançar 50% de Prestadores como despesa')
assert.match(source,/fluxo_percent/,'Prestadores devem permitir percentual individual direcionado ao Fluxo')
assert.match(source,/Vai para Fluxo/,'A UI deve exibir o valor calculado direcionado ao Fluxo')
assert.match(source,/budgetAccounts/,'O modelo deve possuir contas de Budget dinâmicas')
assert.match(source,/\+ Adicionar conta/,'A UI deve permitir adicionar contas de Budget')
assert.match(source,/ativo:false/,'A exclusão de Budget deve ser lógica, não destrutiva')

const fluxo={salario:12000,va:700,condominio:1000}
const prestador={salario:1400,dias_uteis:40,passagem_scs:5,passagem_sp:5.9,fluxo_percent:30}
const extra={nome:'Comissão',valor:1000}
const despesa={nome:'Streaming',valor:50}
const total=totalPrestador(prestador)
assert.equal(total,1836,'Total do prestador deve considerar salário e passagens')
assert.equal(fluxoPrestadorPercent(prestador),550.8,'Percentual de 30% deve direcionar 30% do total ao Fluxo')
assert.equal(fluxoPrestadorPercent({...prestador,fluxo_percent:0}),0,'Percentual de 0% deve direcionar R$ 0 ao Fluxo')
assert.equal(fluxoPrestadorPercent({...prestador,fluxo_percent:100}),total,'Percentual de 100% deve direcionar 100% do total ao Fluxo')
const fm=calcFluxoMonth(fluxo,[prestador],[despesa],[extra])
assert.equal(fm.entries,13700,'Entradas devem somar salário, VA e entradas extras')
assert.equal(fm.employeeTotal,550.8,'O Fluxo deve usar o percentual individual do prestador')
assert.equal(fm.expenses,1000+50+550.8+360,'Despesa Prestadores no Fluxo deve usar o valor direcionado')
const pix=calcPixMonth(fluxo,[prestador])
assert.equal(pix.employeeHalf,918,'50% deve permanecer disponível apenas para divisão/Pix')
assert.equal(fm.tax,360,'Imposto automático deve permanecer em R$ 360')
assert.equal(fm.balance,fm.entries-fm.expenses,'Saldo deve ser entradas menos despesas')

const transfer=calcTransfer({items:[{type:'fluxo',key:'condominio'},{type:'prestador_half',key:'p1'},{type:'despesa',key:'d1'}]},fluxo,[{...prestador,prestador_id:'p1'}],[{...despesa,id:'d1'}])
assert.equal(transfer,1000+550.8+50,'Transferência deve refletir o percentual do prestador sem criar nova despesa')

const oct=`${now}:va`,nov=addMonths(now,1)
const va={id:'va-account',month:now,nome:'VA',budget:700,ativo:true}
const accounts=[{id:'mercado-account',month:now,nome:'Mercado',legacy_key:'mercado',budget:1000,ativo:true},va]
const gastos=[{id:'g1',month:now,conta:'va',budget_account_id:'va-account',valor:250},{id:'legacy',month:now,conta:'mercado',valor:100}]
const budget=calcBudgetMonth(gastos,now,accounts)
assert.equal(budget.find(a=>a.id==='va-account').spent,250,'VA deve controlar seus próprios lançamentos')
assert.equal(budget.find(a=>a.id==='va-account').balance,450,'Saldo do VA deve ser Budget menos realizado')
assert.equal(budget.find(a=>a.id==='mercado-account').spent,100,'Lançamento legado deve continuar compatível')
assert.equal(calcBudgetMonth(gastos,nov,[{id:'va-account',month:nov,nome:'VA',budget:700,ativo:true}]).length,1,'Contas de Budget devem ser independentes por mês')
assert.equal(gastos.length,2,'Remover uma conta de Budget não pode apagar lançamentos históricos')
assert.equal(oct.split(':')[1],'va','Teste de conta dinâmica executado')

console.log(`Planning/Budget guard OK: ${now} → ${months.at(-1)}`)
