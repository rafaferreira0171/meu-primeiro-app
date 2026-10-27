import fs from 'node:fs'
import assert from 'node:assert/strict'
import {currentMonth,planningMonths,addMonths,calcFluxoMonth,calcPixMonth,calcTransfer,totalPrestador} from '../src/lib/finance.js'

const source=fs.readFileSync(new URL('../src/main.jsx',import.meta.url),'utf8')
const now=currentMonth()
const months=planningMonths(now,12)

assert.equal(months.length,12,'A janela de planejamento deve ter 12 meses')
assert.equal(months[0],now,'A janela deve começar no mês atual')
assert.equal(months.at(-1),addMonths(now,11),'A janela deve terminar 11 meses após o atual')
assert.match(source,/const now=currentMonth\(\),months=planningMonths\(now,12\)/,'normalizeData deve usar janela móvel de 12 meses')
assert.match(source,/x\.month>=next\?\{\.\.\.x,ativo:false\}/,'Encerramento deve desativar somente registros futuros')
assert.match(source,/m>now/,'A replicação automática deve atingir somente meses futuros')
assert.match(source,/Prestadores de Serviço/,'O Fluxo deve exibir Prestadores de Serviço, não 50% Prestadores')
assert.doesNotMatch(source,/label="50% Prestadores"/,'O Fluxo não deve lançar 50% de Prestadores como despesa')

const fluxo={salario:12000,va:700,condominio:1000}
const prestador={salario:1400,dias_uteis:40,passagem_scs:5,passagem_sp:5.9}
const extra={nome:'Comissão',valor:1000}
const despesa={nome:'Streaming',valor:50}
const fm=calcFluxoMonth(fluxo,[prestador],[despesa],[extra])
assert.equal(fm.entries,13700,'Entradas devem somar salário, VA e entradas extras')
assert.equal(fm.employeeTotal,totalPrestador(prestador),'Prestadores devem alimentar o Fluxo pelo total do card')
assert.equal(fm.expenses,1000+50+totalPrestador(prestador)+360,'Despesa Prestadores no Fluxo deve usar 100% do total')
const pix=calcPixMonth(fluxo,[prestador])
assert.equal(pix.employeeHalf,918,'50% deve permanecer disponível apenas para divisão/Pix')
assert.equal(fm.tax,360,'Imposto automático deve permanecer em R$ 360')
assert.equal(fm.balance,fm.entries-fm.expenses,'Saldo deve ser entradas menos despesas')

const transfer=calcTransfer({items:[{type:'fluxo',key:'condominio'},{type:'prestador_half',key:'p1'},{type:'despesa',key:'d1'}]},fluxo,[{...prestador,prestador_id:'p1'}],[{...despesa,id:'d1'}])
assert.equal(transfer,1000+totalPrestador(prestador)/2+50,'Transferência deve refletir os itens selecionados sem criar nova despesa')

console.log(`Planning guard OK: ${now} → ${months.at(-1)}`)
